from PyQt5.QtCore import QThread, pyqtSignal
from api_handler import APIHandler

class QueryThread(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    
    def __init__(self, mode, server, player_class, rank_range, season):
        super().__init__()
        self.mode = mode
        self.server = server
        self.player_class = player_class
        self.rank_range = rank_range
        self.season = season
        self.api_handler = APIHandler()
    
    def run(self):
        try:
            # 模拟API调用进度
            self.progress.emit(25)
            
            # 获取数据
            data = self.api_handler.get_rank_data(self.mode, self.server, self.player_class, self.rank_range, self.season)
            
            self.progress.emit(75)
            
            self.progress.emit(100)
            
            self.finished.emit(data)
        except Exception as e:
            print(f"查询出错: {e}")
            self.finished.emit([])