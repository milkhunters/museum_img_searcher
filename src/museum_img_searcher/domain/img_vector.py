from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, UUID

from museum_img_searcher.db import Base


class ImgVector(Base):
    __tablename__ = "imgvectors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exhibit_id = Column(UUID(as_uuid=True), nullable=False)
    vector = Column(Vector(1000), nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
