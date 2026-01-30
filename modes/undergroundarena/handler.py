# 地下竞技场模式处理器

class UndergroundArenaHandler:
    """
    地下竞技场模式的处理器，负责处理该模式的特定逻辑
    """
    
    def __init__(self):
        self.mode_name = 'undergroundarena'
        self.display_name = '地下竞技场'
    
    def get_api_params(self, season):
        """
        获取API请求参数
        """
        return {
            'mode_name': self.mode_name,
            'season_id': season
        }
    
    def get_table_headers(self):
        """
        获取表格头部标签
        """
        return ['排名', '玩家', '积分']
    
    def parse_api_data(self, data):
        """
        解析API返回的数据
        """
        parsed_data = []
        
        if data.get('code') == 0:
            for item in data.get('data', {}).get('list', []):
                rank = item.get('position')
                player_name = item.get('battle_tag')
                score = item.get('score')
                
                parsed_data.append([rank, player_name, score])
        
        return parsed_data
    
    def get_database_columns(self):
        """
        获取数据库表列名
        """
        return ['season', 'player', 'score']
