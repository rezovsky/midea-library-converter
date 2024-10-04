import os
import glob
import sqlite3
from moviepy.editor import VideoFileClip
from moviepy.video.fx import resize


# Конфигурация базы данных
DB_NAME = 'video_files.db'

# Форматы видеофайлов для поиска
VIDEO_EXTENSIONS = ('*.mp4', '*.avi', '*.mkv', '*.mov', '*.flv')

def create_db():
    """Создает базу данных и таблицу для хранения путей видеофайлов."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def scan_videos(directory):
    """Сканирует указанную директорию и её подпапки на наличие видеофайлов."""
    video_paths = []
    for root, _, files in os.walk(directory):
        for ext in VIDEO_EXTENSIONS:
            for file in glob.glob(os.path.join(root, ext)):
                video_paths.append(file)
    return video_paths


def save_video_paths(video_paths):
    """Сохраняет найденные пути видеофайлов в базу данных, проверяя на дубликаты."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for path in video_paths:
        # Проверка на существование пути в базе данных
        cursor.execute('SELECT COUNT(*) FROM videos WHERE path = ?', (path,))
        exists = cursor.fetchone()[0]
        
        if exists == 0:  # Если путь не существует, добавляем его
            cursor.execute('INSERT INTO videos (path) VALUES (?)', (path,))
    conn.commit()

def convert_video(input_path):
    """Конвертирует видеофайл в формат MP4 с разрешением 720p."""
    output_path = os.path.splitext(input_path)[0] + '_converted.mp4'
    try:
        with VideoFileClip(input_path) as video:
            # Убедитесь, что вы используете функцию resize правильно
            video_resized = resize(video, height=720)  # Здесь мы используем импортированную функцию
            video_resized.write_videofile(output_path, codec='libx264', audio_codec='aac')
    except Exception as e:
        print(f'Ошибка при обработке видео: {e}')
    return output_path

def process_videos():
    """Обрабатывает видеофайлы из базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM videos')
    rows = cursor.fetchall()
    
    for row in rows:
        input_path = row[0]
        print(f'Конвертация: {input_path}')
        try:
            output_path = convert_video(input_path)
            os.remove(input_path)  # Удаляет исходный файл после конвертации
            print(f'Успешно конвертировано в: {output_path}')
        except Exception as e:
            print(f'Ошибка при конвертации {input_path}: {e}')

    conn.close()

def main():
    create_db()
    directory = input("Введите путь к папке для сканирования: ")
    video_paths = scan_videos(directory)
    
    if video_paths:
        save_video_paths(video_paths)
        print(f'Найдено {len(video_paths)} видеофайлов. Начинаю обработку...')
        process_videos()
    else:
        print('Видео не найдены.')

if __name__ == '__main__':
    main()
