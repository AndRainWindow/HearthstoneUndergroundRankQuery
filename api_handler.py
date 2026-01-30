import requests
import pandas as pd
import sqlite3
from config import ConfigManager
from modes import ModeManager

class APIHandler:
    def __init__(self):
        # 使用国服地下竞技场API地址
        self.api_base_url = "https://webapi.blizzard.cn/hs-rank-api-server/api/game/ranks"
        self.config_manager = ConfigManager()
        self.mode_manager = ModeManager()
    
    def get_rank_data(self, mode, server, player_class, rank_range, season):
        """
        获取排行榜数据
        """
        current_season = self.config_manager.get_current_season()
        history_seasons = self.config_manager.get_history_seasons()
        
        # 检查是否为历史赛季
        if int(season) in history_seasons:
            return self.get_data_from_database(mode, server, season)
        
        try:
            # 解析排名范围
            start, end = map(int, rank_range.split('-'))
            
            # 计算需要的页数
            page_size = 25
            pages = (end - start + 1 + page_size - 1) // page_size
            
            # 获取模式处理器
            mode_handler = self.mode_manager.get_mode_handler(mode)
            
            # 获取模式对应的API参数
            api_params = mode_handler.get_api_params(current_season)
            mode_name = api_params.get('mode_name', 'undergroundarena')
            
            # 存储所有数据
            all_data = []
            
            # 分页获取数据
            for page in range(1, pages + 1):
                # 构建API请求参数
                params = {
                    'page': page,
                    'page_size': page_size,
                    'mode_name': mode_name,
                    'season_id': current_season  # 使用配置中的当前赛季
                }
                
                # 发送API请求
                response = requests.get(self.api_base_url, params=params)
                response.raise_for_status()  # 检查请求是否成功
                
                # 解析响应数据
                data = response.json()
                
                # 使用模式处理器解析数据
                parsed_data = mode_handler.parse_api_data(data)
                
                # 过滤排名范围内的数据
                for item in parsed_data:
                    if item and len(item) > 0:
                        rank = item[0]
                        if start <= rank <= end:
                            all_data.append(item)
            
            # 按排名排序
            all_data.sort(key=lambda x: x[0])
            
            return all_data
            
        except Exception as e:
            print(f"API调用失败: {e}")
            # API调用失败时返回空数据
            return []
    
    def get_data_from_database(self, mode, server, season):
        """
        从数据库获取历史赛季数据
        """
        try:
            # 连接数据库
            conn = sqlite3.connect('hs_rank.db')
            
            # 构建赛季名称（两种格式）
            season_name1 = f'第{season}赛季'  # 文本格式
            season_name2 = season  # 数字格式
            
            # 查询指定赛季的数据（同时查询两种格式）
            query = '''
            SELECT rank, player, score
            FROM simplified_rank_data
            WHERE season = ? OR season = ?
            ORDER BY score DESC
            LIMIT 500
            '''
            
            # 执行查询
            cursor = conn.cursor()
            cursor.execute(query, (season_name1, season_name2))
            
            # 获取数据并转换格式
            db_data = cursor.fetchall()
            
            conn.close()
            
            # 转换数据格式为 [rank, player, score]
            formatted_data = []
            for idx, row in enumerate(db_data, 1):
                # 使用数据库中存储的排名，如果没有则使用行号
                rank = row[0] if row[0] else idx
                formatted_data.append([rank, row[1], row[2]])
            
            return formatted_data
            
        except Exception as e:
            print(f"数据库查询失败: {e}")
            return []
    
