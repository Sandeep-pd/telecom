"""Network data API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_access_token
from app.database.connection import get_db
from app.schemas.network import NetworkMeasurementCreate, NetworkMeasurementResponse
from app.services.local_network_service import get_local_network_status
from app.services.network_service import NetworkService

router = APIRouter(prefix="/network", tags=["network"])


@router.get("/local-status")
def local_network_status(
    _: str = Depends(require_access_token),
) -> dict[str, object]:
    return get_local_network_status()


@router.post("/data", response_model=NetworkMeasurementResponse, status_code=status.HTTP_201_CREATED)
def create_measurement(
    payload: NetworkMeasurementCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_access_token),
) -> NetworkMeasurementResponse:
    service = NetworkService(db)
    measurement = service.create_measurement(payload)
    return NetworkMeasurementResponse.model_validate(measurement)


@router.get("/data", response_model=list[NetworkMeasurementResponse])
def get_measurements(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: str = Depends(require_access_token),
) -> list[NetworkMeasurementResponse]:
    service = NetworkService(db)
    measurements = service.get_measurements(skip=skip, limit=limit)
    return [NetworkMeasurementResponse.model_validate(item) for item in measurements]


@router.get("/data/{measurement_id}", response_model=NetworkMeasurementResponse)
def get_measurement_by_id(
    measurement_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_access_token),
) -> NetworkMeasurementResponse:
    service = NetworkService(db)
    measurement = service.get_measurement_by_id(measurement_id)
    if measurement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with id {measurement_id} not found",
        )
    return NetworkMeasurementResponse.model_validate(measurement)


@router.get("/cell/{cell_id}", response_model=list[NetworkMeasurementResponse])
def get_measurements_by_cell(
    cell_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_access_token),
) -> list[NetworkMeasurementResponse]:
    service = NetworkService(db)
    measurements = service.get_measurements_by_cell(cell_id)
    return [NetworkMeasurementResponse.model_validate(item) for item in measurements]


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
