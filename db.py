from model import Base
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DB():
    def __init__(self) -> None:
        # Параметры подключения к базе PostgreSQL
        db_user = os.getenv("POSTGRES_USER")
        db_password = os.getenv("POSTGRES_PASSWORD")
        db_host = os.getenv("POSTGRES_HOST")
        db_port = os.getenv("POSTGRES_HOST_PORT")
        db_name = os.getenv("POSTGRES_DB")

        # Создание движка для PostgreSQL
        self.engine = create_engine(
            f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}',
            echo=False
        )

        # Автоматическое создание таблиц, если их нет
        Base.metadata.create_all(self.engine)

        # Настройка сессии для взаимодействия с базой данных
        self.session = sessionmaker(bind=self.engine)

        # Инициализация дефолтных настроек
        self.initialize_default_settings()

    # Инициализация дефолтных настройок
    def initialize_default_settings(self):
        print('Инициализация дефолтных настройок...')

        # Список дефолтных настроек
        default_settings = [
            {'name': 'resolution', 'value': '720p'},
            {'name': 'scan_period', 'value': '300'},
            {'name': 'encoded_period', 'value': '600'},
        ]

        # Добавляем настройки только если их ещё нет в базе
        for setting in default_settings:
            with self.session() as session:
                existing_setting = session.query(
                    MainSettings).filter_by(name=setting['name']).first()
                if not existing_setting:
                    new_setting = MainSettings(
                        name=setting['name'], value=setting['value'])
                    session.add(new_setting)
                    session.commit()

        # default_media_path = [
        #     {'path': '/app/media', 'type': 'video'},
        # ]
        # # Добавляем медиа-пути только если их ещё нет в базе
        # for path in default_media_path:
        #     with self.session() as session:
        #         existing_path = session.query(MediaPath).first()
        #         if not existing_path:
        #             new_path = MediaPath(id=str(uuid.uuid4()), path=path['path'], type=path['type'])
        #             session.add(new_path)
        #             session.commit()

    def add_file(self, path: str, duration: int = 0, frames: int = 0):
        with self.session() as session:
            try:
                new_file = VideoPath(
                    id=str(uuid.uuid4()),
                    path=path,
                    duration=duration,
                    frames=frames,
                    status="added")

                session.add(new_file)
                session.commit()
                return {'status': 'success', "id": new_file.id}
            except Exception as e:
                session.rollback()
                # Проверяем, была ли ошибка связана с уникальностью
                if 'UNIQUE constraint failed' in str(e):
                    print(f"Файл с путем '{
                          path}' уже существует в базе данных.")
                    return {'status': 'error', "message": f"Файл с путем '{path}' уже существует в базе данных."}
                else:
                    print(f"Ошибка при добавлении файла: {e}")
                    return {'status': 'error', "message": f"Ошибка при добавлении файла: {e}"}

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
                print("Нет файлов со статусом 'encode'.")
                return []

    def get_encoded_frame(self, id: str):
        with self.session() as session:
            media = session.query(VideoPath).filter_by(id=id).first()
            if media:
                return {'frame': media.frame, 'frames': media.frames}
            else:
                return None

    def get_added_files(self):
        # Получаем первый файл со статусом "added"
        with self.session() as session:
            files = session.query(VideoPath).filter_by(status="added").all()

            if files:
                return files  # Возвращаем весь объект VideoPath
            else:
                print("Нет файлов со статусом 'added'.")
                return []  # Возвращаем None, если файлов нет

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
                print("Нет файлов со статусом 'encoded'.")
                return []  # Возвращаем None, если файлов нет

    def set_file_status(self, id: str, status: str):
        # Находим файл по пути
        with self.session() as session:
            file_to_update = session.query(
                VideoPath).filter_by(id=id).first()

            if file_to_update:
                file_to_update.status = status
                session.commit()
                print(f"Статус файла '{id}' обновлен на '{status}'.")
            else:
                print(f"Файл '{id}' не найден в базе данных.")

    def set_media_path(self, path: str, type: str):

        with self.session() as session:
            try:
                new_path = MediaPath(id=str(uuid.uuid4()),
                                     path=path, type=type)
                session.add(new_path)
                session.commit()
                print(f"Путь '{path}' успешно добавлен в базу данных.")
                return {'status': 'success', "message": f"Путь '{path}' успешно добавлен в базу данных."}
            except Exception as e:
                session.rollback()
                # Проверяем, была ли ошибка связана с уникальностью
                if 'UNIQUE constraint failed' in str(e):
                    print(f"Путь '{path}' уже существует в базе данных.")
                    return {'status': 'error', "message": f"Путь '{path}' уже существует в базе данных."}
                else:
                    print(f"Ошибка при добавлении файла: {e}")
                    return {'status': 'error', "message": f"Ошибка при добавлении файла: {e}"}

    def get_media_paths(self):
        # Получаем первый медиа-путь
        with self.session() as session:
            paths = session.query(MediaPath).all()

            if paths:
                return paths  # Возвращаем весь объект MediaPath
            else:
                print("Нет медиа-путей в базе данных.")
                return []  # Возвращаем None, если путей нет

    def update_media_path_type(self, path_id: str, new_type: str):
        # Получаем медиа-путь по ID
        with self.session() as session:
            media_path = session.query(MediaPath).filter_by(id=path_id).first()

            if media_path:
                media_path.type = new_type
                try:
                    session.commit()
                    print(
                        f"Тип медиа-пути с ID '{path_id}' успешно обновлен на '{new_type}'.")
                    return {'status': 'success', "message": f"Тип медиа-пути с ID '{path_id}' успешно обновлен на '{new_type}'."}
                except Exception as e:
                    self.session.rollback()  # Откатываем изменения в случае ошибки
                    print(f"Ошибка при обновлении типа: {e}")
                    return {'status': 'error', "message": f"Ошибка при обновлении типа: {e}"}
            else:
                print(f"Медиа-путь с ID '{path_id}' не найден.")
                return {'status': 'error', "message": f"Медиа-путь с ID '{path_id}' не найден."}

    def delete_media_path(self, path_id: str):
        # Получаем медиа-путь по ID
        with self.session() as session:
            media_path = session.query(
                MediaPath).filter_by(id=path_id).first()

            if media_path:
                try:
                    session.delete(media_path)  # Удаляем запись
                    session.commit()  # Сохраняем изменения
                    print(f"Медиа-путь с ID '{path_id}' успешно удален.")
                    return {'status': 'success', "message": f"Медиа-путь с ID '{path_id}' успешно удален."}
                except Exception as e:
                    print(f"Ошибка при удалении медиа-пути: {e}")
                    return {'status': 'error', "message": f"Ошибка при удалении медиа-пути: {e}"}
            else:
                print(f"Медиа-путь с ID '{path_id}' не найден.")
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
