import os
import time
from data_processing import DPFilePath, DPMediaPath
from db import DB
from model import MediaPath
from video_decoder import VideoEncoder
import logging

logger = logging.getLogger(__name__)

class MediaScan():
    def __init__(self, db) -> None:
        self.db = db
        self.video_encoder = VideoEncoder(db)
        self.paths = self.db.get_media_paths()
        self.video_extensions = ['.avi', '.mkv', '.mov', '.flv', '.wmv']

    def scan_paths(self) -> None:
        for path in self.paths:
            if path.auto_scan:
                self.scan_path(path)

    def scan_path(self, path_data: MediaPath) -> None:
        media_path = DPMediaPath(path_data)
        logger.info(f"Сканируем медиатеку {media_path.formatted_name}")
        if os.path.exists(media_path.data.path):
            self.scan_file_path(media_path.data)

    def scan_file_path(self, path_data: MediaPath) -> dict:
        for root, _, filenames in os.walk(path_data.path):
            for filename in filenames:
                _, ext = os.path.splitext(filename)
                if ext.lower() in self.video_extensions:
                    file_data = DPFilePath(os.path.join(root, filename))

                    if self.db.check_file_by_path(file_data.path_without_ext):
                        file_info = self.video_encoder.get_video_info(
                            file_data.file_path)

                        db_result = self.db.add_file(path_data, file_data, file_info)
                        if not db_result.error:
                            logger.info(f"Добавлен видеофайл: {file_data.file_path}")

    def start_periodical_scan(self):
        logger.info("Периодическое сканирование запущено...")
        while True:
            self.scan_paths()
            scan_period = int(self.db.get_setting('scan_period'))
            time.sleep(scan_period)


if __name__ == "__main__":
    db = DB()
    media_scanner = MediaScan(db)
    media_scanner.start_periodical_scan()
