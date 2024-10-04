import ffmpeg
import os

from db import DB

class VideoEncoder:
    def __init__(self, db):
        self.db = db
        self.quality_settings = {
            "720p": "1280x720",
            "480p": "854x480",
            "360p": "640x360"
        }
        self.ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg.exe')

    def encode_video(self, video_path: str, quality: str):
        if quality not in self.quality_settings:
            print("Неподдерживаемое качество. Доступные варианты: 720p, 480p, 360p.")
            return

        output_path = f"{video_path.rsplit('.', 1)[0]}_converted.mp4"

        try:
            (
                ffmpeg
                .input(video_path)
                .output(
                    output_path,
                    vf=f"scale={self.quality_settings[quality]}",
                    vcodec='libx264',
                    acodec='aac',
                    strict='experimental'
                )
                .run(cmd=self.ffmpeg_path, quiet=True)
            )
            print(f"Видео '{video_path}' успешно сконвертировано в '{output_path}'.")
            self.db.set_file_status(video_path, "encoded")
            os.remove(video_path)
        except ffmpeg.Error as e:
            print(f"Ошибка при кодировании видео: {e.stderr.decode()}")


if __name__ == "__main__":
    db = DB()
    video_encoder = VideoEncoder(db)  # Создаем экземпляр VideoEncoder
    
    video_file = db.get_added_file()
    video_encoder.encode_video(video_file.path, "720p")
