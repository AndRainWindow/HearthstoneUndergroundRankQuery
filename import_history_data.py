import requests
import sqlite3

# 历史赛季数据导入脚本
def import_season_data(season, season_id):
    """
    导入指定赛季的数据
    """
    # 连接数据库
    conn = sqlite3.connect('hs_rank.db')
    cursor = conn.cursor()
    
    # 检查该赛季的数据是否已存在
    cursor.execute('''
    SELECT COUNT(*) FROM simplified_rank_data WHERE season = ?
    ''', (season,))
    
    count = cursor.fetchone()[0]
    if count > 0:
        print(f'{season} 数据已存在，跳过导入')
        conn.close()
        return False
    
    # API地址
    api_url = "https://webapi.blizzard.cn/hs-rank-api-server/api/game/ranks"
    
    # 初始化数据列表
    all_data = []
    
    # 分页获取数据
    page = 1
    page_size = 25
    
    while True:
        try:
            # 构建API请求参数
            params = {
                'page': page,
                'page_size': page_size,
                'mode_name': 'undergroundarena',
                'season_id': season_id
            }
            
            # 发送API请求
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            
            # 解析响应数据
            data = response.json()
            
            if data.get('code') == 0:
                items = data.get('data', {}).get('list', [])
                
                if not items:
                    break  # 没有更多数据
                
                # 处理数据
                for item in items:
                    rank = item.get('position')
                    player = item.get('battle_tag')
                    score = item.get('score')
                    
                    # 添加到数据列表
                    all_data.append([rank, player, '', score, score])  # 职业留空
                
                # 下一页
                page += 1
            else:
                break
                
        except Exception as e:
            print(f'API调用失败: {e}')
            break
    
    # 保存数据到数据库
    print(f'保存 {season} 数据，共 {len(all_data)} 条...')
    
    for row in all_data:
        try:
            # 只存储赛季、玩家和积分数据
            cursor.execute('''
            INSERT INTO simplified_rank_data (season, player, score)
            VALUES (?, ?, ?)
            ''', (season, row[1], row[3]))
        except Exception as e:
            print(f'存储失败: {e}')
            # 忽略重复数据
            pass
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print(f'{season} 数据导入完成！')
    return True

def import_history_data():
    """
    导入所有历史赛季数据
    """
    # 赛季列表
    seasons = ['第1赛季', '第2赛季', '第3赛季', '第4赛季']
    season_ids = [1, 2, 3, 4]  # 假设赛季ID对应
    
    # 为每个赛季导入数据
    for season, season_id in zip(seasons, season_ids):
        import_season_data(season, season_id)
    
    print('所有历史数据导入完成！')

if __name__ == '__main__':
    import_history_data()
