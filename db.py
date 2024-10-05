import os
import uuid
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Создаем базовый класс для всех моделей
Base = declarative_base()

# Определяем модель (таблицу)


class VideoPath(Base):
    __tablename__ = 'video_path'

    id = Column(String, primary_key=True, unique=True)
    path = Column(String, unique=True)  # Исправлено имя поля

    status = Column(String)


class MediaPath(Base):
    __tablename__ = 'media_path'

    id = Column(String, primary_key=True, unique=True)
    path = Column(String, unique=True)
    type = Column(String)


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

        # Настраиваем сессию для взаимодействия с базой данных
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def add_file(self, path: str):
        # Генерируем уникальный идентификатор для файла
        new_file = VideoPath(id=str(uuid.uuid4()), path=path, status="added")

        try:
            self.session.add(new_file)
            self.session.commit()
            print(f"Файл с путем '{path}' успешно добавлен в базу данных.")
        except Exception as e:
            # Откатываем изменения, если произошла ошибка
            self.session.rollback()

            # Проверяем, была ли ошибка связана с уникальностью
            if 'UNIQUE constraint failed' in str(e):
                print(f"Файл с путем '{path}' уже существует в базе данных.")
            else:
                print(f"Ошибка при добавлении файла: {e}")

    def get_added_files(self):
        # Получаем первый файл со статусом "added"
        files = self.session.query(VideoPath).filter_by(status="added").all()

        if files:
            return files  # Возвращаем весь объект VideoPath
        else:
            print("Нет файлов со статусом 'added'.")
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
        except Exception as e:
            # Откатываем изменения, если произошла ошибка
            self.session.rollback()

            # Проверяем, была ли ошибка связана с уникальностью
            if 'UNIQUE constraint failed' in str(e):
                print(f"Путь '{path}' уже существует в базе данных.")
            else:
                print(f"Ошибка при добавлении файла: {e}")

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
            except Exception as e:
                self.session.rollback()  # Откатываем изменения в случае ошибки
                print(f"Ошибка при обновлении типа: {e}")
        else:
            print(f"Медиа-путь с ID '{path_id}' не найден.")

    def delete_media_path(self, path_id: str):
        # Получаем медиа-путь по ID
        media_path = self.session.query(
            MediaPath).filter_by(id=path_id).first()

        if media_path:
            try:
                self.session.delete(media_path)  # Удаляем запись
                self.session.commit()  # Сохраняем изменения
                print(f"Медиа-путь с ID '{path_id}' успешно удален.")
            except Exception as e:
                self.session.rollback()  # Откатываем изменения в случае ошибки
                print(f"Ошибка при удалении медиа-пути: {e}")
        else:
            print(f"Медиа-путь с ID '{path_id}' не найден.")
