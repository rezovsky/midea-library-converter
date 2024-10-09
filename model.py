import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, Integer, Column, String
from sqlalchemy.orm import declarative_base, relationship

# Создаем базовый класс для всех моделей
Base = declarative_base()


class IdUsage(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True,
                unique=True, default=uuid.uuid4)


class MediaPath(IdUsage):
    __tablename__ = 'media_path'

    path = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    convert_resolution = Column(String, nullable=False)

    video_path = relationship('VideoPath', backref='media')


class VideoPath(IdUsage):
    __tablename__ = 'video_path'

    media_path_id = Column(UUID(as_uuid=True), ForeignKey('media_path.id'))
    path = Column(String, unique=True, nullable=False)
    file_extension = Column(String, nullable=False)
    duration = Column(Integer)
    frames = Column(Integer)
    frame = Column(Integer, nullable=True)
    status = Column(String)

    media_relation = relationship('MediaPath', backref='videos')


class MainSettings(Base):
    __tablename__ = 'settings'

    name = Column(String, unique=True, primary_key=True)
    value = Column(String)
