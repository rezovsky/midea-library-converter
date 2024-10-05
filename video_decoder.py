import ffmpeg
import os

from db import DB, VideoPath

class VideoEncoder:
    def __init__(self, db):
        self.db = db 
        self.quality_settings = {
            "720p": "1280x720",
            "480p": "854x480",
            "360p": "640x360"
        } #параметры для конвертации
        self.ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg.exe') #путь до ffmpeg

    def encode_video(self, video_file: VideoPath, quality: str):
        video_path = video_file.path

        #проверка на ошибки в передаче желаемого качества кодирования
        if quality not in self.quality_settings:
            print("Неподдерживаемое качество. Доступные варианты: 720p, 480p, 360p.")
            return

        #генерируем путь к перекодированному файлу
        output_path = f"{video_path.rsplit('.', 1)[0]}_converted.mp4"
        
        #если по такому пути уже есть файл - удаляем, возможно в прошлый раз была ошибка конвертации
        if os.path.exists(output_path):
            os.remove(output_path)


        print(f"Видео '{video_path}' конвертируется в '{output_path}'.")

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
            )#запускаем ffmoeg

            print(f"Видео '{video_path}' успешно сконвертировано в '{output_path}'.")

            #по завершению кодирования помечаем путь в бд как сконвертированный
            self.db.set_file_status(video_file.id, "encoded")
            #удаляем исходный файл
            os.remove(video_path)
            #генерируем новоем имя для сконвертированного файла, такое же как было у исходного
            new_name = os.video_path.splitext(video_path)[0] + ".mp4"
            #переименовываем новый файл
            os.rename(output_path, new_name)
        except ffmpeg.Error as e:
            print(f"Ошибка при кодировании видео: {e.stderr.decode()}")


if __name__ == "__main__":
    db = DB()
    video_encoder = VideoEncoder(db)  # Создаем экземпляр VideoEncoder
    
    video_files = db.get_added_files()
    for video_file in video_files:
        video_encoder.encode_video(video_file, "720p")
