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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_data(self, data, season, mode, server):
        # 保存数据到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for row in data:
            try:
                # 只存储赛季、玩家和积分数据
                cursor.execute('''
                INSERT INTO simplified_rank_data (season, player, score)
                VALUES (?, ?, ?)
                ''', (season, row[1], row[2]))
            except Exception as e:
                # 忽略重复数据
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