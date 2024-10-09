import os

from model import MediaPath, VideoPath


class DPFilePath:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.name, self.ext = os.path.splitext(os.path.basename(file_path))
        self.path_without_ext = os.path.join(os.path.dirname(file_path), self.name)
        
    def file_path(self) -> str:
        return self.file_path
    
    def file_name(self) -> str:
        return self.name
    
    def file_ext(self) -> str:
        return self.ext
    
    def path_without_ext(self) -> str:
        return self.path_without_ext


class DPMediaPath:
    def __init__(self, data: MediaPath) -> None:
        self.data = data
        self.name = os.path.basename(data.path)
        
    def name(self) -> str:
        return self.name
    
    def formatted_name(self) -> str:
        return self.name.capitalize()
    
    def data(self) -> MediaPath:
        return self.data





class DPVideoInfo:
    def __init__(self, duration: int = 0, frames: int = 0, error: str = None) -> None:
        self.duration = duration
        self.frames = frames
        self.error = error
    
    def duration(self) -> int:
        return self.duration
    
    def frames(self) -> int:
        return self.frames
    
    def error(self) -> str:
        return self.error

class DPVideoPath:
    def __init__(self, data: VideoPath = None,  error: str = None) -> None:
        self.data = data
        self.error = error
        if self.error is not None:
            print(self.error)
    
    def data(self) -> VideoPath:
        return self.data
    
    def error(self) -> str:
        return self.error