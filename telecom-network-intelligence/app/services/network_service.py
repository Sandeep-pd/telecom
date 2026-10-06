"""Network service layer."""

from sqlalchemy.orm import Session

from app.database.crud import CRUDRepository
from app.models.network import NetworkMeasurement
from app.schemas.network import NetworkMeasurementCreate


class NetworkService:
    """Business logic for telecom network measurement operations."""

    def __init__(self, db: Session) -> None:
        self.repository = CRUDRepository(db)

    def create_measurement(self, payload: NetworkMeasurementCreate) -> NetworkMeasurement:
        return self.repository.create_measurement(payload)

    def get_measurements(self, skip: int = 0, limit: int = 100) -> list[NetworkMeasurement]:
        return self.repository.get_measurements(skip=skip, limit=limit)

    def get_measurement_by_id(self, measurement_id: int) -> NetworkMeasurement | None:
        return self.repository.get_measurement_by_id(measurement_id)

    def get_measurements_by_cell(self, cell_id: str) -> list[NetworkMeasurement]:
        return self.repository.get_measurements_by_cell(cell_id)
