# 炉石传说排行榜查询工具

这是一款用于查询炉石传说排行榜相关信息的桌面GUI程序。

## 功能特点

-支持地下竞技场历史赛季和过往赛季查询
-支持玩家信息搜索
-支持历史赛季数据信息存入数据库

## 环境要求

- Python 3.7+
- PyQt5
- requests
- pandas

## 安装说明

1. 克隆或下载本项目到本地
2. 进入项目目录
3. 创建虚拟环境：
   ```
   python -m venv venv
   ```
4. 激活虚拟环境：
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. 安装依赖：
   ```
   pip install pyqt5 requests pandas
   ```

## 使用方法

1. 运行程序：
   ```
   python main.py
   ```
2. 在界面上选择要查询的模式、服务器、职业和排名范围
3. 点击"查询"按钮开始查询
4. 等待查询完成后，结果会显示在表格中

## 注意事项

- 由于炉石传说官方API的限制，可能需要使用第三方API或爬虫来获取真实数据
- 请遵守相关服务的使用条款，不要过度请求数据
