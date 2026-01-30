import sqlite3
import os


class DatabaseManager:
    def __init__(self, db_path='hs_rank.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        # 初始化数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建简化的排行榜表（只保留核心数据）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS simplified_rank_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season TEXT,
            player TEXT,
            score INTEGER,
            rank INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        
        # 检查并更新数据库结构
        self.check_and_update_db_structure()
    
    def check_and_update_db_structure(self):
        """
        检查并更新数据库结构，确保rank列存在
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查simplified_rank_data表结构
        cursor.execute('PRAGMA table_info(simplified_rank_data)')
        table_info = cursor.fetchall()
        
        # 检查是否存在rank列
        has_rank_column = any(column[1] == 'rank' for column in table_info)
        
        # 如果不存在rank列，添加它
        if not has_rank_column:
            try:
                cursor.execute('ALTER TABLE simplified_rank_data ADD COLUMN rank INTEGER')
                conn.commit()
            except Exception as e:
                # 忽略错误
                pass
        
        conn.close()
    
    def save_data(self, data, season, mode, server):
        # 保存数据到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 先删除该赛季的所有旧数据
        cursor.execute('DELETE FROM simplified_rank_data WHERE season = ?', (season,))
        
        for row in data:
            try:
                # 存储赛季、玩家、积分和排名数据
                cursor.execute('''
                INSERT INTO simplified_rank_data (season, player, score, rank)
                VALUES (?, ?, ?, ?)
                ''', (season, row[1], row[2], row[0]))
            except Exception as e:
                # 忽略错误
                pass
        
        conn.commit()
        conn.close()
    
    def get_data(self, mode, server):
        # 从数据库获取数据
        conn = sqlite3.connect(self.db_path)
        query = '''
        SELECT season, player, score
        FROM simplified_rank_data
        '''
        
        import pandas as pd
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def check_season_exists(self, season):
        # 检查指定赛季的数据是否已存在
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT COUNT(*) FROM simplified_rank_data WHERE season = ?
        ''', (season,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def get_player_data(self, player_name):
        """
        根据玩家名字模糊搜索玩家数据
        """
        conn = sqlite3.connect(self.db_path)
        query = '''
        SELECT season, player, score, rank
        FROM simplified_rank_data
        WHERE player LIKE ?
        ORDER BY season, score DESC
        '''
        
        import pandas as pd
        df = pd.read_sql_query(query, conn, params=(f'%{player_name}%',))
        conn.close()
        
        # 处理赛季名称，将数字格式和文本格式的赛季合并
        if not df.empty:
            # 创建赛季映射，将文本格式的赛季转换为数字格式
            season_map = {}
            for season in df['season'].unique():
                if isinstance(season, str) and season.startswith('第') and season.endswith('赛季'):
                    # 提取数字部分
                    try:
                        season_num = season.replace('第', '').replace('赛季', '')
                        season_map[season] = season_num
                    except:
                        pass
            
            # 替换赛季名称
            df['season'] = df['season'].replace(season_map)
            
            # 去重，保留每个赛季中积分最高的记录
            df = df.sort_values('score', ascending=False).drop_duplicates(['season', 'player'])
            
            # 重新排序
            df = df.sort_values(['season', 'score'], ascending=[True, False])
        
        return df