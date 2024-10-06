import os
import time
from db import DB
from video_decoder import VideoEncoder


class MediaScan():
    def __init__(self, db) -> None:
        self.db = db
        self.video_encoder = VideoEncoder(db)
        self.paths = self.db.get_media_paths()  # Получаем пути из базы данных
        self.video_extensions = ['.avi', '.mkv', '.mov', '.flv', '.wmv']

    def scan_paths(self):
        for path in self.paths:
            # Выводим текущий путь для сканирования
            print(f"Сканируем путь: {path.path}")
            if os.path.exists(path.path):  # Проверяем, существует ли путь
                return self.scan_path(path.path)
            else:
                print(f"Путь '{path.path}' не существует.")
                return {'status': 'error', 'message': f"Путь '{path.path}' не существует."}

    def scan_path(self, path):
        # Проходим по всем файлам в директории
        result = {}
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                _, ext = os.path.splitext(filename)
                if ext.lower() in self.video_extensions:
                    file_path = os.path.join(root, filename)

                    if self.db.check_file_by_path(file_path):
                        file_info = self.video_encoder.get_video_info(file_path)
                        # если данные о файле не получены по какой-то причине, то заменяем нулями
                        if file_info is None:
                            duration = 0
                            frames = 0
                        else:
                            duration = file_info['duration']
                            frames = file_info['frames']
                        db_result = self.db.add_file(file_path, duration, frames)  # Добавляем файл в базу данных
                        if db_result['status'] == 'success':
                            print(f"Добавлен видеофайл: {file_path}")
                            result[db_result['id']] = {'status': 'added', 'duration': duration, 'frames': frames}
        return result
    
    def start_periodical_scan(self):
        print("Периодическое сканирование запущено...")
        while True:
            self.scan_paths()
            scan_period = int(self.db.get_setting('scan_period'))
            time.sleep(scan_period)
                    


if __name__ == "__main__":
    db = DB()  # Создаем экземпляр DB
    media_scanner = MediaScan(db)  # Создаем экземпляр MediaScan
    media_scanner.start_periodical_scan()    # Запускаем сканирование путей
