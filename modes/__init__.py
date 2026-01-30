# 模式管理模块

class ModeManager:
    """
    模式管理器，用于管理不同游戏模式的处理逻辑
    """
    def __init__(self):
        self.modes = {
            '地下竞技场': 'undergroundarena'
        }
    
    def get_mode_key(self, mode_name):
        """
        获取模式对应的键值
        """
        return self.modes.get(mode_name, 'undergroundarena')
    
    def get_mode_handler(self, mode_name):
        """
        获取模式对应的处理器
        """
        mode_key = self.get_mode_key(mode_name)
        
        try:
            # 动态导入模式处理器
            if mode_key == 'undergroundarena':
                from modes.undergroundarena.handler import UndergroundArenaHandler
                return UndergroundArenaHandler()
            else:
                # 默认使用地下竞技场处理器
                from modes.undergroundarena.handler import UndergroundArenaHandler
                return UndergroundArenaHandler()
        except ImportError:
            # 如果导入失败，返回默认处理器
            from modes.undergroundarena.handler import UndergroundArenaHandler
            return UndergroundArenaHandler()
