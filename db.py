import logging
from dotenv import load_dotenv
from data_processing import DPFilePath, DPMediaPath, DPVideoInfo, DPVideoPath
from model import Base, MainSettings, MediaPath, VideoPath
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DB():
    def __init__(self) -> None:
        load_dotenv()        
        
        db_user = os.getenv("POSTGRES_USER")
        db_password = os.getenv("POSTGRES_PASSWORD")
        db_host = os.getenv("POSTGRES_HOST")
        db_port = os.getenv("POSTGRES_HOST_PORT")
        db_name = os.getenv("POSTGRES_DB")

        self.logger = logging.getLogger(__name__)

        self.engine = create_engine(
            f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}',
            echo=False
        )

        Base.metadata.create_all(self.engine)

        self.session = sessionmaker(bind=self.engine)

        self.initialize_default_settings()

    # Инициализация дефолтных настройок
    def initialize_default_settings(self):
        self.logger.info('Инициализация дефолтных настройок...')

        default_settings = [
            {'name': 'resolution', 'value': '720p'},
            {'name': 'scan_period', 'value': '300'},
            {'name': 'encoded_period', 'value': '600'},
        ]
        
        with self.session() as session:
            try:
                for setting in default_settings:
                    existing_setting = session.query(
                        MainSettings).filter_by(name=setting['name']).first()
                    if not existing_setting:
                        new_setting = MainSettings(
                            name=setting['name'], value=setting['value'])
                        session.add(new_setting)
                session.commit()
            except Exception as e:
                session.rollback()
                self.logger.error(f"Ошибка при инициализации настроек: {e}")

    def add_file(self, media_path_data: MediaPath, file_data: DPFilePath, video_info: DPVideoInfo) -> DPVideoPath:
        with self.session() as session:
            try:
                new_file = VideoPath(
                    media_path_id=media_path_data.id,
                    path=file_data.path_without_ext,
                    file_extension=file_data.file_ext,
                    duration=video_info.duration,
                    frames=video_info.frames,
                    status="added")

                session.add(new_file)
                session.commit()
                return DPVideoPath(data=new_file)
            except Exception as e:
                session.rollback()
                # Проверяем, была ли ошибка связана с уникальностью
                if 'UNIQUE constraint failed' in str(e):
                    return DPVideoPath(error=f"Файл с путем '{file_data.path}' уже существует в базе данных.")
                else:
                    return DPVideoPath(error=f"Ошибка при добавлении файла: {e}")

    def check_file_by_path(self, path: str):
        with self.session() as session:
            media = session.query(VideoPath).filter_by(path=path).first()
            if not media:
                return True
            else:
                return False

    def edit_encoded_frame(self, id: str, frame: int):
        with self.session() as session:
            media = session.query(VideoPath).filter_by(id=id).first()
            if media:
                media.frame = frame
                session.commit()

    def get_encode_files(self):
        with self.session() as session:
            files = session.query(VideoPath).filter_by(status="encode").all()
            if files:
                return files
            else:
                self.logger.info("Нет файлов со статусом 'encode'.")
                return []

    def get_encoded_frame(self, id: str):
        with self.session() as session:
            media = session.query(VideoPath).filter_by(id=id).first()
            if media:
                return {'frame': media.frame, 'frames': media.frames}
            else:
                return None

    def get_added_files(self):
        with self.session() as session:
            files = session.query(VideoPath).filter_by(status="added").all()

            if files:
                return files
            else:
                self.logger.info("Нет файлов со статусом 'added'.")
                return []

    def get_files(self):
        with self.session() as session:
            files = session.query(VideoPath).all()
            if files:
                return files
            else:
                print("Нет файлов.")
                return []

    def get_encoded_files(self):
        # Получаем первый файл со статусом "added"
        with self.session() as session:
            files = session.query(VideoPath).filter_by(status="encoded").all()

            if files:
                return files  # Возвращаем весь объект VideoPath
            else:
                self.logger.info("Нет файлов со статусом 'encoded'.")
                return []  # Возвращаем None, если файлов нет

    def set_file_status(self, id: uuid.UUID, status: str):
        # Находим файл по пути
        with self.session() as session:
            file_to_update = session.query(
                VideoPath).filter_by(id=id).first()

            if file_to_update:
                file_to_update.status = status
                session.commit()
                self.logger.info(f"Статус файла '{id}' обновлен на '{status}'.")
            else:
                self.logger.error(f"Файл '{id}' не найден в базе данных.")

    def add_media_path(
        self, 
        path: str, 
        type: str, 
        name: str = None, 
        convert_resolution: str = None, 
        auto_scan: bool = None, 
        auto_convert: bool = None
        ) -> DPMediaPath:
        with self.session() as session:
            try:
                new_path = MediaPath(
                        path=path, 
                        type=type, 
                        name=name, 
                        convert_resolution=convert_resolution, 
                        auto_scan=auto_scan, 
                        auto_convert=auto_convert
                    )
                new_path_data = DPMediaPath(data=new_path)
                if new_path.name is None:
                    new_path.name = DPMediaPath.formatted_name
                
                session.add(new_path)
                session.commit()
                return DPMediaPath(data=new_path)
            except Exception as e:
                session.rollback()
                if 'UNIQUE constraint failed' in str(e):
                    return DPMediaPath(error=f"Путь '{path}' уже существует в базе данных.")
                else:
                    return DPMediaPath(error=f"Ошибка при добавлении файла: {e}")

    def get_media_paths(self) -> list:
        with self.session() as session:
            paths = session.query(MediaPath).all()
            if paths:
                return paths
            else:
                self.logger.info("Нет медиатек в базе данных.")
                return []

    def update_media_path_type(self, path_id: uuid.UUID, new_type: str):
        # Получаем медиа-путь по ID
        with self.session() as session:
            media_path = session.query(MediaPath).filter_by(id=path_id).first()

            if media_path:
                media_path.type = new_type
                try:
                    session.commit()
                    self.logger.info(
                        f"Тип медиа-пути с ID '{path_id}' успешно обновлен на '{new_type}'.")
                    return {'status': 'success', "message": f"Тип медиа-пути с ID '{path_id}' успешно обновлен на '{new_type}'."}
                except Exception as e:
                    self.session.rollback()  # Откатываем изменения в случае ошибки
                    self.logger.error(f"Ошибка при обновлении типа: {e}")
                    return {'status': 'error', "message": f"Ошибка при обновлении типа: {e}"}
            else:
                self.logger.error(f"Медиа-путь с ID '{path_id}' не найден.")
                return {'status': 'error', "message": f"Медиа-путь с ID '{path_id}' не найден."}

    def delete_media_path(self, path_id: uuid.UUID):
        # Получаем медиа-путь по ID
        with self.session() as session:
            media_path = session.query(
                MediaPath).filter_by(id=path_id).first()

            if media_path:
                try:
                    session.delete(media_path)  # Удаляем запись
                    session.commit()  # Сохраняем изменения
                    self.logger.info(f"Медиа-путь с ID '{path_id}' успешно удален.")
                    return {'status': 'success', "message": f"Медиа-путь с ID '{path_id}' успешно удален."}
                except Exception as e:
                    self.logger.error(f"Ошибка при удалении медиа-пути: {e}")
                    return {'status': 'error', "message": f"Ошибка при удалении медиа-пути: {e}"}
            else:
                self.logger.error(f"Медиа-путь с ID '{path_id}' не найден.")
                return {'status': 'error', "message": f"Медиа-путь с ID '{path_id}' не найден."}

    def get_setting(self, setting_name: str):
        with self.session() as session:
            result = session.query(MainSettings.value).filter_by(
                name=setting_name).first()
            return result[0] if result else None

    def set_setting(self, setting_name: str, setting_value: str):
        with self.session() as session:
            result = session.query(MainSettings).filter_by(
                name=setting_name).first()
            if result:
                result.value = setting_value
                session.commit()
                return {'status': 'success', "message": f"Настройка '{setting_name}' успешно обновлена."}
            else:
                new_setting = MainSettings(
                    name=setting_name, value=setting_value)
                session.add(new_setting)
                session.commit()
                return {'status': 'success', "message": f"Настройка '{setting_name}' успешно добавлена."}
