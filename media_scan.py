import os
from db import DB


class MediaScan():
    def __init__(self) -> None:
        self.db = DB()
        self.paths = self.db.get_media_paths()  # Получаем пути из базы данных
        self.video_extensions = ['.mp4', '.avi',
                                 '.mkv', '.mov', '.flv', '.wmv']

    def scan_paths(self):
        for path in self.paths:
            # Выводим текущий путь для сканирования
            print(f"Сканируем путь: {path.path}")
            if os.path.exists(path.path):  # Проверяем, существует ли путь
                self.scan_path(path.path)
            else:
                print(f"Путь '{path.path}' не существует.")

    def scan_path(self, path):
        # Проходим по всем файлам в директории
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                _, ext = os.path.splitext(filename)
                if ext.lower() in self.video_extensions:
                    file_path = os.path.join(root, filename)
                    self.db.add_file(file_path)  # Добавляем файл в базу данных
                    print(f"Добавлен видеофайл: {file_path}")


if __name__ == "__main__":
    media_scanner = MediaScan()  # Создаем экземпляр MediaScan
    media_scanner.scan_paths()    # Запускаем сканирование путей
