import os
import uuid
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Создаем базовый класс для всех моделей
Base = declarative_base()

# Определяем модель (таблицу)


class VideoPath(Base):
    __tablename__ = 'video_path'  # Исправлено имя таблицы

    id = Column(String, primary_key=True)
    path = Column(String)  # Исправлено имя поля
    status = Column(String)


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
        # Проверяем, существует ли уже файл с таким путем
        existing_file = self.session.query(
            VideoPath).filter_by(path=path).first()

        if existing_file:
            print(f"Файл с путем '{path}' уже существует в базе данных.")
            return  # Прерываем выполнение, если файл уже существует

        # Генерируем уникальный идентификатор для файла
        new_file = VideoPath(id=str(uuid.uuid4()), path=path, status="added")
        self.session.add(new_file)
        self.session.commit()
        print(f"Файл с путем '{path}' успешно добавлен в базу данных.")

    def get_added_file(self):
        # Получаем первый файл со статусом "added"
        file = self.session.query(VideoPath).filter_by(status="added").first()
        return file  # Возвращаем весь объект VideoPath

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
