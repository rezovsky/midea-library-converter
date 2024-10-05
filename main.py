from threading import Thread
from fastapi import FastAPI

from db import DB
from media_scan import MediaScan
from video_decoder import VideoEncoder


app = FastAPI()
db = DB()
scanner = MediaScan(db)
encoder = VideoEncoder(db)

# автоматический запуск сканирования медиа папок
def start_periodical_scan():
    period_db = DB()
    period_scanner = MediaScan(period_db)
    period_scanner.start_periodical_scan()

scanner_thread = Thread(target=start_periodical_scan)
scanner_thread.start()

# запуск сканирования медиа папок
@app.get("/scan/path")
def open_main_page():
    result = scanner.scan_paths()
    return {"status": "run", "result": result}

# запуск декодирования видео


@app.get("/encoded/start")
def start_encode():
    encoder.encoded_start()

# получение настройки


@app.get("/db/setting/{setting_name}")
def get_setting(setting_name: str):
    return db.get_setting(setting_name)

# получение списка добавленных файлов


@app.get("/db/added/files")
def get_added_files():
    return db.get_added_files()

# получение списка кодированных файлов


@app.get("/db/encoded/files")
def get_encoded_files():
    return db.get_encoded_files()

# получение списка кодируемых файлов


@app.get("/db/encode/files")
def get_encode_files():
    return db.get_encode_files()


# получение текущей позиции кодирования файла
@app.get("/db/encode/frame/{id}")
def get_encoded_frame(id: str):
    return db.get_encoded_frame(id)

# получение списка медиа папок


@app.get("/db/paths")
def get_media_paths():
    return db.get_media_paths()

# добавление медиа папки


@app.post("/db/path")
def add_media_path(path: str, type: str):
    return db.set_media_path(path, type)

# изменение типа медиа папки


@app.put("/db/path/{path_id}")
def update_media_path_type(path_id: str, new_type: str):
    return db.update_media_path_type(path_id, new_type)

# удаление медиа папки


@app.delete("/db/path/{path_id}")
def delete_media_path(path_id: str):
    return db.delete_media_path(path_id)
