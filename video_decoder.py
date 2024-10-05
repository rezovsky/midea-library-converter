import re
import subprocess
import os
import time

from db import DB, VideoPath


class VideoEncoder:
    def __init__(self, db):
        self.db = db
        self.quality_settings = {
            "1080p": "1920x1080",
            "720p": "1280x720",
            "480p": "854x480",
            "360p": "640x360"
        }  # параметры для конвертации
        self.ffmpeg_path = os.path.join(
            os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg.exe')  # путь до ffmpeg
        # Указываем путь до ffprobe
        self.ffprobe_path = os.path.join(
            os.getcwd(), 'ffmpeg', 'bin', 'ffprobe.exe'
        )
        self.total_frames = 0
        self.duration_seconds = 0
        self.frame_rate = 0

    def get_video_info(self, video_path):
        cmd = [
            self.ffprobe_path,
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=duration,nb_frames,r_frame_rate',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        try:
            output = subprocess.check_output(
                cmd, universal_newlines=True).strip().splitlines()
            # Перебор вывода и замена N/A на 0
            for i in range(len(output)):
                if output[i] == 'N/A':
                    output[i] = 0  # Заменяем N/A на 0

            self.frame_rate = float(
                int(output[0].split('/')[0])/int(output[0].split('/')[1]))
            self.duration_seconds = float(output[1])  # Длительность в секундах
            self.total_frames = round(self.duration_seconds * self.frame_rate)
            return {'duration': round(self.duration_seconds), 'frames': round(self.total_frames)}

        except subprocess.CalledProcessError as e:
            print(f"Ошибка при получении информации о видео: {e}")
            return None
        except ValueError as e:
            print(f"Ошибка при преобразовании данных: {e}")
            return None

    def encode_video(self, video_file: 'VideoPath', quality: str):
        video_path = video_file.path

        # Проверка на ошибки в передаче желаемого качества кодирования
        if quality not in self.quality_settings:
            print("Неподдерживаемое качество. Доступные варианты: 1080p, 720p, 480p, 360p.")
            return

        # Генерируем путь к перекодированному файлу
        output_path = f"{video_path.rsplit('.', 1)[0]}_converted.mp4"

        # Если по такому пути уже есть файл — удаляем
        if os.path.exists(output_path):
            os.remove(output_path)

        print(f"Видео '{video_path}' конвертируется в '{output_path}'.")

        # Сначала получаем информацию о видео
        self.get_video_info(video_path)

        try:
            # Команда для ffmpeg
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-vf', f"scale={self.quality_settings[quality]}",
                '-map', '0:v',  # Копируем видеодорожку
                '-map', '0:a',  # Копируем все аудиодорожки
                '-vcodec', 'libx264',
                '-acodec', 'aac',
                '-strict', 'experimental',
                output_path
            ]
            self.db.set_file_status(video_file.id, "encode")
            # Запуск ffmpeg через subprocess и вывод в реальном времени
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

            # Печатаем вывод ffmpeg построчно
            for line in process.stdout:
                # print(line, end='')

                # Поиск строки с длительностью
                duration_match = re.search(
                    r'Duration: (\d+):(\d+):(\d+\.\d+)', line)
                if duration_match:
                    hours, minutes, seconds = map(
                        float, duration_match.groups())
                    self.duration_seconds = hours * 3600 + minutes * 60 + seconds

                # Поиск строки с текущим кадром
                frame_match = re.search(r'frame=\s*(\d+)', line)
                if frame_match:
                    current_frame = int(frame_match.group(1))
                    self.db.edit_encoded_frame(video_file.id, current_frame)
                    

            process.wait()  # Ожидание завершения процесса

            if process.returncode == 0:
                print(f"Видео '{video_path}' успешно сконвертировано в '{
                      output_path}'.")
                # Помечаем путь в БД как сконвертированный
                self.db.set_file_status(video_file.id, "encoded")
                # Удаляем исходный файл
                os.remove(video_path)
                # Генерируем новое имя для сконвертированного файла
                new_name = os.path.splitext(video_path)[0] + ".mp4"
                # Переименовываем новый файл
                os.rename(output_path, new_name)
            else:
                print(f"Ошибка при кодировании видео. Код завершения: {
                      process.returncode}")

        except Exception as e:
            print(f"Ошибка при кодировании видео: {e}")


    def encoded_start(self):
        print('Запущено периодическое кодирование...')
        encode_files = self.db.get_encode_files()
        if encode_files:
            for encode_file in encode_files:
                self.db.set_file_status(encode_file.id, "added")
        while True:
            video_files = self.db.get_added_files()
            for video_file in video_files:
                resolution = str(self.db.get_setting("resolution"))
                self.encode_video(video_file, resolution)
            encoded_period = int(self.db.get_setting('encoded_period'))
            time.sleep(encoded_period)

if __name__ == "__main__":
    db = DB()
    video_encoder = VideoEncoder(db)  # Создаем экземпляр VideoEncoder

    video_encoder.encoded_start()
