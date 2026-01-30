import json
import os

# 配置管理模块

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """
        加载配置文件
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def get_default_config(self):
        """
        获取默认配置
        """
        return {
            'current_season': 5,
            'history_seasons': [1, 2, 3, 4]
        }
    
    def save_config(self):
        """
        保存配置文件
        """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_current_season(self):
        """
        获取当前赛季
        """
        return self.config.get('current_season', 5)
    
    def set_current_season(self, season):
        """
        设置当前赛季
        """
        self.config['current_season'] = season
        self.save_config()
    
    def get_history_seasons(self):
        """
        获取历史赛季列表
        """
        return self.config.get('history_seasons', [1, 2, 3, 4])
    
    def update_history_seasons(self, current_season):
        """
        更新历史赛季列表
        """
        self.config['history_seasons'] = list(range(1, current_season))
        self.save_config()
