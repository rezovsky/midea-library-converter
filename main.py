import os
from threading import Thread
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from db import DB
from media_scan import MediaScan
from video_decoder import VideoEncoder


app = FastAPI()

# Настройка CORS
origins = [
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешенные методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешенные заголовки
)

# Указываем папку со статическими файлами
css_directory = os.path.join(os.getcwd(), "midea_web_ui", "dist", "css")
app.mount("/css", StaticFiles(directory=css_directory), name="css")
js_directory = os.path.join(os.getcwd(), "midea_web_ui", "dist", "js")
app.mount("/js", StaticFiles(directory=js_directory), name="js")
static_directory = os.path.join(os.getcwd(), "midea_web_ui", "dist")


# Обработка запроса на корень
@app.get("/", response_class=HTMLResponse)  # Указываем, что возвращаем HTML
async def read_root():
    # Можно вернуть основной HTML файл
    html_file_path = os.path.join(static_directory, "index.html")
    if os.path.exists(html_file_path):
        with open(html_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return HTMLResponse(content=content)  # Возвращаем HTMLResponse
    return HTMLResponse(content="Index file not found.", status_code=404)  # Возвращаем ошибку 404 в случае отсутствия файла


db = DB()
scanner = MediaScan(db)
encoder = VideoEncoder(db)

# автоматический запуск сканирования медиа папок


def start_periodical_scan():
    period_scanner_db = DB()
    period_scanner = MediaScan(period_scanner_db)
    period_scanner.start_periodical_scan()


scanner_thread = Thread(target=start_periodical_scan)
scanner_thread.start()

# автоматический запуск кодирования файлов


def start_periodical_encoded():
    period_encoded_db = DB()
    period_encoded = VideoEncoder(period_encoded_db)
    period_encoded.encoded_start()


encoded_thread = Thread(target=start_periodical_encoded)
encoded_thread.start()


# получаем все файлы из базы данных

@app.get("/db/files")
def get_files():
    return db.get_files()

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
