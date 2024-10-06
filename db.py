import os
import uuid
from sqlalchemy import Integer, create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Создаем базовый класс для всех моделей
Base = declarative_base()

# Определяем модель (таблицу)


class VideoPath(Base):
    __tablename__ = 'video_path'

    id = Column(String, primary_key=True, unique=True)
    path = Column(String, unique=True)
    duration = Column(Integer)
    frames = Column(Integer)
    frame = Column(Integer, nullable=True)
    status = Column(String)


class MediaPath(Base):
    __tablename__ = 'media_path'

    id = Column(String, primary_key=True, unique=True)
    path = Column(String, unique=True)
    type = Column(String)


class MainSettings(Base):
    __tablename__ = 'settings'

    name = Column(String, unique=True, primary_key=True)
    value = Column(String)


class DB():
    def __init__(self) -> None:
        # Имя базы
        db_name = "db.db"

        # Проверяем, существует ли база данных
        db_exists = os.path.exists(db_name)

        # Создание движка для SQLite
        self.engine = create_engine(f'sqlite:///{db_name}', echo=False)

        if not db_exists:
            Base.metadata.create_all(self.engine)
            self.initialize_default_settings()

        # Настраиваем сессию для взаимодействия с базой данных
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    # Инициализация дефолтных настройок
    def initialize_default_settings(self):
        # Создание новой сессии для добавления данных
        session = self.Session()

        # Список дефолтных настроек
        default_settings = [
            {'name': 'resolution', 'value': '720p'},
            {'name': 'scan_period', 'value': '300'},
            {'name': 'encoded_period', 'value': '600'},
        ]

        # Добавляем настройки только если их ещё нет в базе
        for setting in default_settings:
            existing_setting = session.query(
                MainSettings).filter_by(key=setting['name']).first()
            if not existing_setting:
                new_setting = MainSettings(
                    name=setting['name'], value=setting['value'])
                session.add(new_setting)

        default_media_path = [
            {'path': '/app/media', 'type': 'video'},
        ]
        # Добавляем медиа-пути только если их ещё нет в базе
        for path in default_media_path:
            existing_path = session.query(MediaPath).first()
            if not existing_path:
                new_path = MediaPath(
                    id=str(uuid.uuid4()), path=path['path'], type=path['type'])
                session.add(new_path)

        # Применяем изменения
        session.commit()
        session.close()

    def add_file(self, path: str, duration: int = 0, frames: int = 0):
        # Генерируем уникальный идентификатор для файла
        new_file = VideoPath(
            id=str(uuid.uuid4()),
            path=path,
            duration=duration,
            frames=frames,
            status="added")

        try:
            self.session.add(new_file)
            self.session.commit()
            return {'status': 'success', "id": new_file.id}
        except Exception as e:
            # Откатываем изменения, если произошла ошибка
            self.session.rollback()

            # Проверяем, была ли ошибка связана с уникальностью
            if 'UNIQUE constraint failed' in str(e):
                print(f"Файл с путем '{path}' уже существует в базе данных.")
                return {'status': 'error', "message": f"Файл с путем '{path}' уже существует в базе данных."}
            else:
                print(f"Ошибка при добавлении файла: {e}")
                return {'status': 'error', "message": f"Ошибка при добавлении файла: {e}"}

    def edit_encoded_frame(self, id: str, frame: int):
        media = self.session.query(VideoPath).filter_by(id=id).first()
        if media:
            media.frame = frame
            self.session.commit()

    def get_encode_files(self):
        files = self.session.query(VideoPath).filter_by(status="encode").all()
        if files:
            return files
        else:
            print("Нет файлов со статусом 'encode'.")
            return []

    def get_encoded_frame(self, id: str):
        media = self.session.query(VideoPath).filter_by(id=id).first()
        if media:
            return {'frame': media.frame, 'frames': media.frames}
        else:
            return None

    def get_added_files(self):
        # Получаем первый файл со статусом "added"
        files = self.session.query(VideoPath).filter_by(status="added").all()

        if files:
            return files  # Возвращаем весь объект VideoPath
        else:
            print("Нет файлов со статусом 'added'.")
            return []  # Возвращаем None, если файлов нет

    def get_files(self):
        files = self.session.query(VideoPath).all()
        if files:
            return files
        else:
            print("Нет файлов.")
            return []

    def get_encoded_files(self):
        # Получаем первый файл со статусом "added"
        files = self.session.query(VideoPath).filter_by(status="encoded").all()

        if files:
            return files  # Возвращаем весь объект VideoPath
        else:
            print("Нет файлов со статусом 'encoded'.")
            return []  # Возвращаем None, если файлов нет

    def set_file_status(self, id: str, status: str):
        # Находим файл по пути
        file_to_update = self.session.query(
            VideoPath).filter_by(id=id).first()

        if file_to_update:
            # Обновляем статус файла
            file_to_update.status = status
            self.session.commit()  # Сохраняем изменения в базе данных
            print(f"Статус файла '{id}' обновлен на '{status}'.")
        else:
            print(f"Файл '{id}' не найден в базе данных.")

    def set_media_path(self, path: str, type: str):
        # Генерируем уникальный идентификатор для пути файла
        new_path = MediaPath(id=str(uuid.uuid4()), path=path, type=type)

        try:
            self.session.add(new_path)
            self.session.commit()
            print(f"Путь '{path}' успешно добавлен в базу данных.")
            return {'status': 'success', "message": f"Путь '{path}' успешно добавлен в базу данных."}
        except Exception as e:
            # Откатываем изменения, если произошла ошибка
            self.session.rollback()

            # Проверяем, была ли ошибка связана с уникальностью
            if 'UNIQUE constraint failed' in str(e):
                print(f"Путь '{path}' уже существует в базе данных.")
                return {'status': 'error', "message": f"Путь '{path}' уже существует в базе данных."}
            else:
                print(f"Ошибка при добавлении файла: {e}")
                return {'status': 'error', "message": f"Ошибка при добавлении файла: {e}"}

    def get_media_paths(self):
        # Получаем первый медиа-путь
        paths = self.session.query(MediaPath).all()

        if paths:
            return paths  # Возвращаем весь объект MediaPath
        else:
            print("Нет медиа-путей в базе данных.")
            return []  # Возвращаем None, если путей нет

    def update_media_path_type(self, path_id: str, new_type: str):
        # Получаем медиа-путь по ID
        media_path = self.session.query(
            MediaPath).filter_by(id=path_id).first()

        if media_path:
            media_path.type = new_type  # Обновляем тип
            try:
                self.session.commit()  # Сохраняем изменения
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
        media_path = self.session.query(
            MediaPath).filter_by(id=path_id).first()

        if media_path:
            try:
                self.session.delete(media_path)  # Удаляем запись
                self.session.commit()  # Сохраняем изменения
                print(f"Медиа-путь с ID '{path_id}' успешно удален.")
                return {'status': 'success', "message": f"Медиа-путь с ID '{path_id}' успешно удален."}
            except Exception as e:
                self.session.rollback()  # Откатываем изменения в случае ошибки
                print(f"Ошибка при удалении медиа-пути: {e}")
                return {'status': 'error', "message": f"Ошибка при удалении медиа-пути: {e}"}
        else:
            print(f"Медиа-путь с ID '{path_id}' не найден.")
            return {'status': 'error', "message": f"Медиа-путь с ID '{path_id}' не найден."}

    def get_setting(self, setting_name: str):
        result = self.session.query(MainSettings.value).filter_by(
            name=setting_name).first()
        return result[0] if result else None

    def set_setting(self, setting_name: str, setting_value: str):
        result = self.session.query(MainSettings).filter_by(
            name=setting_name).first()
        if result:
            result.value = setting_value
            self.session.commit()
            return {'status': 'success', "message": f"Настройка '{setting_name}' успешно обновлена."}
        else:
            new_setting = MainSettings(name=setting_name, value=setting_value)
            self.session.add(new_setting)
            self.session.commit()
            return {'status': 'success', "message": f"Настройка '{setting_name}' успешно добавлена."}
