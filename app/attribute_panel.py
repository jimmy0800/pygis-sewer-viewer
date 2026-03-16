"""
AttributePanel - 屬性查詢面板
"""

import json
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class AttributePanel(QDockWidget):
    """屬性查詢浮動視窗"""

    def __init__(self, parent=None):
        super().__init__("屬性查詢", parent)

        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures | 
                       QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFixedWidth(280)

        # 內容 widget
        self.content_widget = QWidget()
        self.setWidget(self.content_widget)

        # 標籤（顯示提示）
        self.hint_label = QLabel("請點擊地圖上的要素查看屬性")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("""
            color: #666;
            font-size: 12px;
            padding: 20px;
        """)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["欄位", "值"])
        self.table.setStyleSheet("""
            QTableWidget {
                background: #2D2D2D;
                color: #D4D4D4;
                border: none;
                gridline-color: #3C3C3C;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #3C3C3C;
            }
            QTableWidget::item:selected {
                background: #2D8C4E;
            }
            QHeaderView::section {
                background: #1E1E1E;
                color: #9CDCFE;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #3C3C3C;
                font-weight: bold;
            }
        """)

        # 表格樣式
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # 初始隱藏表格
        self.table.setVisible(False)

        # 佈局
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.hint_label)
        layout.addWidget(self.table)

        # 設定 Dock 樣式
        self.setStyleSheet("""
            QDockWidget {
                background: #252526;
                border-left: 1px solid #3C3C3C;
                titlebar-normal-icon: url(none);
            }
            QDockWidget::title {
                background: #1E1E1E;
                color: #D4D4D4;
                padding: 8px;
                border-bottom: 1px solid #3C3C3C;
            }
        """)

    def show_attributes(self, properties_json: str):
        """顯示要素屬性"""
        try:
            props = json.loads(properties_json)
            self._display_properties(props)
        except json.JSONDecodeError:
            pass

    def _display_properties(self, props: dict):
        """顯示屬性到表格"""
        # 隱藏提示，顯示表格
        self.hint_label.setVisible(False)
        self.table.setVisible(True)

        # 清空表格
        self.table.setRowCount(0)

        # 填入資料
        row = 0
        for key, value in props.items():
            if key in ['style', 'geometry']:
                continue

            self.table.insertRow(row)

            # 欄位名（藍色）
            key_item = QTableWidgetItem(str(key))
            key_item.setForeground(QColor("#9CDCFE"))
            key_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, key_item)

            # 值（白色）
            value_item = QTableWidgetItem(str(value) if value is not None else "-")
            value_item.setForeground(QColor("#D4D4D4"))
            value_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 1, value_item)

            row += 1

    def clear(self):
        """清除屬性顯示"""
        self.hint_label.setVisible(True)
        self.table.setVisible(False)
        self.table.setRowCount(0)
