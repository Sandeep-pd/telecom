"""CRUD repository layer for telecom data operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.network import NetworkMeasurement
from app.schemas.network import NetworkMeasurementCreate


class CRUDRepository:
    """Repository for telecom network measurement database operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_measurement(self, payload: NetworkMeasurementCreate) -> NetworkMeasurement:
        measurement = NetworkMeasurement(
            cell_id=payload.cell_id,
            region=payload.region,
            network_type=payload.network_type,
            timestamp=payload.timestamp,
            rsrp=payload.rsrp,
            rsrq=payload.rsrq,
            rssi=payload.rssi,
            sinr=payload.sinr,
            download_speed=payload.download_speed,
            upload_speed=payload.upload_speed,
            latency=payload.latency,
            packet_loss=payload.packet_loss,
            connected_users=payload.connected_users,
            call_drop_rate=payload.call_drop_rate,
            handover_failure_rate=payload.handover_failure_rate,
        )
        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)
        return measurement

    def get_measurements(self, skip: int = 0, limit: int = 100) -> list[NetworkMeasurement]:
        statement = select(NetworkMeasurement).order_by(NetworkMeasurement.id).offset(skip).limit(limit)
        return list(self.db.execute(statement).scalars().all())

    def get_measurement_by_id(self, measurement_id: int) -> NetworkMeasurement | None:
        return self.db.get(NetworkMeasurement, measurement_id)

    def get_measurements_by_cell(self, cell_id: str) -> list[NetworkMeasurement]:
        statement = select(NetworkMeasurement).where(NetworkMeasurement.cell_id == cell_id).order_by(NetworkMeasurement.id)
        return list(self.db.execute(statement).scalars().all())
