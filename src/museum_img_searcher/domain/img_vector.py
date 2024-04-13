from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, UUID

from db import Base


class ImgVector(Base):
    __tablename__ = "imgvectors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exhibit_id = Column(UUID(as_uuid=True), nullable=False)
    vector = Column(Vector(2048), nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
