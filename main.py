import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QLabel, QLineEdit, QMessageBox, QProgressBar, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import DatabaseManager
from query_thread import QueryThread
from config import ConfigManager
from import_history_data import import_season_data
from modes import ModeManager

class HsRankQuery(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.config_manager = ConfigManager()
        self.mode_manager = ModeManager()
        self.initUI()
    
    def initUI(self):
        # 加载QSS样式文件
        try:
            with open('style.qss', 'r', encoding='utf-8') as f:
                style_sheet = f.read()
                self.setStyleSheet(style_sheet)
        except Exception as e:
            print(f"加载样式文件失败: {e}")
        
        # 设置窗口标题和大小
        self.setWindowTitle('炉石传说排行榜查询工具')
        self.setGeometry(100, 100, 1200, 700)
        
        # 创建字体
        font = QFont()
        font.setPointSize(18)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建查询选项区域
        query_layout = QHBoxLayout()
        query_layout.setContentsMargins(10, 10, 10, 10)
        
        # 模式选择
        self.mode_label = QLabel('模式:')
        self.mode_label.setFont(font)
        self.mode_combo = QComboBox()
        self.mode_combo.setFont(font)
        self.mode_combo.addItems(['地下竞技场'])
        
        # 服务器选择
        self.server_label = QLabel('服务器:')
        self.server_label.setFont(font)
        self.server_combo = QComboBox()
        self.server_combo.setFont(font)
        self.server_combo.addItems(['国服', '欧服', '美服', '亚服'])
        
        # 赛季选择
        self.season_label = QLabel('赛季:')
        self.season_label.setFont(font)
        self.season_combo = QComboBox()
        self.season_combo.setFont(font)
        
        # 更新赛季选择下拉框
        self.update_season_combo()
        
        # 查询按钮
        self.query_btn = QPushButton('查询')
        self.query_btn.setFont(font)
        self.query_btn.clicked.connect(self.start_query)
        
        # 导出按钮
        self.export_btn = QPushButton('导出数据')
        self.export_btn.setFont(font)
        self.export_btn.clicked.connect(self.export_data)
        
        # 搜索功能
        self.search_label = QLabel('搜索:')
        self.search_label.setFont(font)
        self.search_input = QLineEdit()
        self.search_input.setFont(font)
        self.search_input.setPlaceholderText('输入玩家名字')
        self.search_btn = QPushButton('搜索')
        self.search_btn.setFont(font)
        self.search_btn.clicked.connect(self.search_player)
        self.reset_btn = QPushButton('重置')
        self.reset_btn.setFont(font)
        self.reset_btn.clicked.connect(self.reset_search)
        
        # 设置按钮
        self.settings_btn = QPushButton('设置')
        self.settings_btn.setFont(font)
        self.settings_btn.clicked.connect(self.open_settings)
        
        # 添加到查询布局
        query_layout.addWidget(self.mode_label)
        query_layout.addWidget(self.mode_combo)
        query_layout.addWidget(self.server_label)
        query_layout.addWidget(self.server_combo)
        query_layout.addWidget(self.season_label)
        query_layout.addWidget(self.season_combo)
        query_layout.addWidget(self.query_btn)
        query_layout.addWidget(self.export_btn)
        query_layout.addWidget(self.search_label)
        query_layout.addWidget(self.search_input)
        query_layout.addWidget(self.search_btn)
        query_layout.addWidget(self.reset_btn)
        query_layout.addWidget(self.settings_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(['玩家', '积分'])
        header_font = QFont('Arial', 18, QFont.Bold)
        self.result_table.horizontalHeader().setFont(header_font)
        self.result_table.setAlternatingRowColors(True)
        # 设置列宽自动填充
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        # 添加到主布局
        main_layout.addLayout(query_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.result_table)
    
    def start_query(self):
        # 获取查询参数
        mode = self.mode_combo.currentText()
        server = self.server_combo.currentText()
        rank_range = '1-500'  # 默认排名范围
        season = self.season_combo.currentText()
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 创建线程进行查询
        self.query_thread = QueryThread(mode, server, '全部', rank_range, season)
        self.query_thread.finished.connect(self.handle_query_result)
        self.query_thread.progress.connect(self.update_progress)
        self.query_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def handle_query_result(self, data):
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        if not data:
            QMessageBox.information(self, '提示', '未查询到数据')
            return
        
        # 获取当前模式的处理器
        mode = self.mode_combo.currentText()
        mode_handler = self.mode_manager.get_mode_handler(mode)
        
        # 获取表格头部标签
        headers = mode_handler.get_table_headers()
        
        # 设置表格列数和表头
        self.result_table.setColumnCount(len(headers))
        self.result_table.setHorizontalHeaderLabels(headers)
        
        # 重新设置列宽自动填充
        for i in range(len(headers)):
            self.result_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 填充表格
        self.result_table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            # 填充数据
            for col_idx, col_data in enumerate(row_data):
                if col_idx < len(headers):
                    item = QTableWidgetItem(str(col_data))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 设置为只读
                    self.result_table.setItem(row_idx, col_idx, item)
        
        # 调整列宽
        self.result_table.resizeColumnsToContents()
        
        # 重新设置列宽自动填充
        for i in range(len(headers)):
            self.result_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 保存到数据库
        self.save_to_database(data)
    
    def save_to_database(self, data):
        # 保存数据到数据库
        mode = self.mode_combo.currentText()
        server = self.server_combo.currentText()
        season = self.season_combo.currentText()
        
        self.db_manager.save_data(data, season, mode, server)
    
    def export_data(self):
        # 导出数据到Excel
        mode = self.mode_combo.currentText()
        server = self.server_combo.currentText()
        season = self.season_combo.currentText()
        
        # 从数据库获取数据
        df = self.db_manager.get_data(mode, server)
        
        if df.empty:
            QMessageBox.information(self, '提示', '没有数据可导出')
            return
        
        # 导出到Excel
        filename = f'{mode}_{server}_{season}.xlsx'
        df.to_excel(filename, index=False)
        
        QMessageBox.information(self, '提示', f'数据已导出到 {filename}')
    
    def open_settings(self):
        # 打开设置对话框
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle('设置')
        dialog.setGeometry(300, 300, 400, 200)
        
        layout = QVBoxLayout(dialog)
        
        # 当前赛季设置
        season_layout = QHBoxLayout()
        season_label = QLabel('当前赛季:')
        season_label.setFont(QFont('Arial', 14))
        
        season_spinbox = QSpinBox()
        season_spinbox.setFont(QFont('Arial', 14))
        season_spinbox.setMinimum(1)
        season_spinbox.setMaximum(20)
        season_spinbox.setValue(self.config_manager.get_current_season())
        
        season_layout.addWidget(season_label)
        season_layout.addWidget(season_spinbox)
        layout.addLayout(season_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # 执行对话框
        if dialog.exec_() == QDialog.Accepted:
            new_season = season_spinbox.value()
            self.config_manager.set_current_season(new_season)
            self.config_manager.update_history_seasons(new_season)
            
            # 自动导入缺失的历史赛季数据
            self.import_missing_history_data(new_season)
            
            # 更新赛季选择下拉框
            self.update_season_combo()
            
            QMessageBox.information(self, '提示', f'当前赛季已设置为: {new_season}\n历史赛季已更新为: 1-{new_season-1}')
    
    def update_season_combo(self):
        # 更新赛季选择下拉框
        current_season = self.config_manager.get_current_season()
        seasons = [str(i) for i in range(1, current_season + 1)]
        
        # 保存当前选中的赛季
        current_selection = self.season_combo.currentText()
        
        # 清空并重新添加赛季选项
        self.season_combo.clear()
        self.season_combo.addItems(seasons)
        
        # 恢复之前的选择（如果存在）
        if current_selection in seasons:
            self.season_combo.setCurrentText(current_selection)
        else:
            self.season_combo.setCurrentText(str(current_season))
    
    def import_missing_history_data(self, new_season):
        """
        自动导入缺失的历史赛季数据
        """
        from PyQt5.QtCore import QThread, pyqtSignal
        from PyQt5.QtWidgets import QProgressDialog
        
        # 计算需要导入的历史赛季数量
        history_seasons = list(range(1, new_season))
        if not history_seasons:
            return
        
        # 创建导入线程
        class ImportThread(QThread):
            progress_update = pyqtSignal(int, str)
            finished = pyqtSignal(int)
            
            def __init__(self, seasons, parent=None):
                super().__init__(parent)
                self.seasons = seasons
                self.db_manager = DatabaseManager()
            
            def run(self):
                imported_count = 0
                
                # 遍历所有历史赛季
                for i, season_num in enumerate(self.seasons):
                    season_name = f'第{season_num}赛季'
                    self.progress_update.emit(i, f'正在检查 {season_name}...')
                    
                    # 检查该赛季的数据是否已存在
                    if not self.db_manager.check_season_exists(season_name):
                        # 导入该赛季的数据
                        self.progress_update.emit(i, f'正在导入 {season_name}...')
                        import_season_data(season_name, season_num)
                        imported_count += 1
                
                self.progress_update.emit(len(self.seasons), '导入完成！')
                self.finished.emit(imported_count)
        
        # 创建进度对话框
        progress = QProgressDialog(self)
        progress.setWindowTitle('导入历史数据')
        progress.setLabelText('正在检查并导入历史赛季数据...')
        progress.setMinimum(0)
        progress.setMaximum(len(history_seasons))
        progress.setValue(0)
        progress.setModal(True)
        
        # 创建并启动导入线程
        import_thread = ImportThread(history_seasons)
        
        # 连接信号
        import_thread.progress_update.connect(lambda i, text: (progress.setValue(i), progress.setLabelText(text)))
        import_thread.finished.connect(lambda count: (progress.setValue(len(history_seasons)), 
                                                     progress.close(), 
                                                     QMessageBox.information(self, '提示', 
                                                                             f'成功导入 {count} 个历史赛季的数据！' if count > 0 else 
                                                                             '所有历史赛季的数据已存在，无需重复导入。')))
        
        # 启动线程
        import_thread.start()
        
        # 显示进度对话框
        progress.exec_()
    
    def search_player(self):
        """
        根据玩家名字进行模糊搜索，隐藏不匹配的行
        """
        search_text = self.search_input.text().strip()
        
        if not search_text:
            QMessageBox.information(self, '提示', '请输入玩家名字')
            return
        
        # 搜索匹配的玩家
        matched_rows = []
        
        for row in range(self.result_table.rowCount()):
            player_item = self.result_table.item(row, 0)
            if player_item:
                player_name = player_item.text()
                if search_text.lower() in player_name.lower():
                    matched_rows.append(row)
                    # 显示匹配的行
                    self.result_table.setRowHidden(row, False)
                    # 高亮显示匹配的行
                    for col in range(self.result_table.columnCount()):
                        item = self.result_table.item(row, col)
                        if item:
                            item.setBackground(Qt.yellow)
                else:
                    # 隐藏不匹配的行
                    self.result_table.setRowHidden(row, True)
        
        # 显示搜索结果
        if matched_rows:
            # 滚动到第一个匹配的行
            self.result_table.scrollToItem(self.result_table.item(matched_rows[0], 0))
            QMessageBox.information(self, '搜索结果', f'找到 {len(matched_rows)} 个匹配的玩家')
        else:
            QMessageBox.information(self, '搜索结果', '未找到匹配的玩家')
    
    def reset_search(self):
        """
        重置搜索，显示所有行
        """
        # 清空搜索输入框
        self.search_input.clear()
        
        # 显示所有行
        for row in range(self.result_table.rowCount()):
            self.result_table.setRowHidden(row, False)
            # 重置背景色
            for col in range(self.result_table.columnCount()):
                item = self.result_table.item(row, col)
                if item:
                    item.setBackground(self.result_table.palette().base())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HsRankQuery()
    window.show()
    sys.exit(app.exec_())