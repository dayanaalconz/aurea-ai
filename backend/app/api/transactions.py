"""Transaction ingestion API routes."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.data.database import get_db_session
from app.data.repositories.transaction import TransactionRepository
from app.schemas.transactions_api import TransactionUploadResponse
from app.services.transaction_ingestion import TransactionIngestionService


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.post(
    "/upload",
    response_model=TransactionUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload financial transactions",
)
async def upload_transactions(
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
) -> TransactionUploadResponse:
    """Validate and persist transactions from an uploaded CSV file."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported.",
        )

    content = await file.read()

    repository = TransactionRepository(session)
    ingestion_service = TransactionIngestionService(repository)

    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".csv",
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        imported_count = ingestion_service.ingest_csv(temp_path)

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The CSV contains invalid transaction data.",
        ) from exc

    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The CSV contains transactions that conflict with existing records.",
        ) from exc

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return TransactionUploadResponse(
        status="success",
        imported_transactions=imported_count,
    )