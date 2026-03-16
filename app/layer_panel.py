"""
LayerPanel - 圖層控制面板
"""

from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor


class LayerItem(QFrame):
    """單一圖層項目"""

    visibilityChanged = pyqtSignal(str, bool)  # layer_id, visible
    styleClicked = pyqtSignal(str)  # layer_id
    removeClicked = pyqtSignal(str)  # layer_id

    def __init__(self, layer_id: str, name: str, geom_type: str, 
                 feature_count: int, color: str = "#2D8C4E", parent=None):
        super().__init__(parent)

        self.layer_id = layer_id
        self._visible = True

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shape.NoFrame)
        self.setStyleSheet("""
            LayerItem {
                background: #2D2D2D;
                border-radius: 4px;
                padding: 8px;
                margin: 2px 0;
            }
            LayerItem:hover {
                background: #3C3C3C;
            }
        """)

        # 勾選框
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        self.checkbox.setStyleSheet("""
            QCheckBox { color: #D4D4D4; }
            QCheckBox::indicator { width: 16px; height: 16px; }
        """)
        self.checkbox.stateChanged.connect(self._on_check_changed)

        # 顏色標記
        color_label = QLabel()
        color_label.setFixedSize(16, 16)
        color_label.setStyleSheet(f"""
            background: {color};
            border-radius: 4px;
            border: 1px solid #555;
        """)

        # 名稱
        name_label = QLabel(name)
        name_label.setStyleSheet("color: #D4D4D4; font-size: 12px;")

        # 幾何類型
        type_label = QLabel("●" if geom_type == "Point" else "━")
        type_label.setStyleSheet(f"color: {color}; font-size: 14px;")

        # 要素數量
        count_label = QLabel(f"{feature_count}")
        count_label.setStyleSheet("""
            color: #888;
            font-size: 10px;
            background: #1E1E1E;
            padding: 2px 6px;
            border-radius: 8px;
        """)

        # 樣式按鈕
        style_btn = QPushButton("⚙")
        style_btn.setFixedSize(24, 24)
        style_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #888;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #4EC9B0;
            }
        """)
        style_btn.clicked.connect(lambda: self.styleClicked.emit(self.layer_id))

        # 佈局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        layout.addWidget(self.checkbox)
        layout.addWidget(type_label)
        layout.addWidget(color_label)
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(count_label)
        layout.addWidget(style_btn)

    def _on_check_changed(self, state):
        self._visible = state == Qt.CheckState.Checked.value
        self.visibilityChanged.emit(self.layer_id, self._visible)

    def setVisible(self, visible: bool):
        self._visible = visible
        self.checkbox.setChecked(visible)


class LayerPanel(QDockWidget):
    """圖層控制面板"""

    layerVisibilityChanged = pyqtSignal(str, bool)  # layer_id, visible
    layerStyleClicked = pyqtSignal(str)  # layer_id
    layerRemoveClicked = pyqtSignal(str)  # layer_id

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layer_items = {}

        self.setWindowTitle("圖層")
        self.setFixedWidth(260)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures | 
                        QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.setTitleBarWidget(QLabel(" 圖層 "))
        
        # 內容 widget
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background: #252526;
        """)

        # 標題
        title = QLabel("圖層")
        title.setStyleSheet("""
            color: #D4D4D4;
            font-size: 14px;
            font-weight: bold;
            padding: 12px;
        """)

        # 圖層列表區域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1E1E1E;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #3C3C3C;
                border-radius: 4px;
            }
        """)

        self.layer_container = QWidget()
        self.layer_layout = QVBoxLayout(self.layer_container)
        self.layer_layout.setContentsMargins(4, 4, 4, 4)
        self.layer_layout.setSpacing(2)
        self.layer_layout.addStretch()

        scroll.setWidget(self.layer_container)

        # 移除圖層按鈕
        remove_btn = QPushButton("移除所有圖層")
        remove_btn.setStyleSheet("""
            QPushButton {
                background: #3C3C3C;
                color: #D4D4D4;
                border: none;
                padding: 8px;
                margin: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #F44747;
            }
        """)
        remove_btn.clicked.connect(self._on_remove_all)

        # 主佈局
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(title)
        layout.addWidget(scroll)
        layout.addWidget(remove_btn)
        
        # 設置內容 widget
        self.setWidget(content_widget)

    def add_layer(self, layer_id: str, name: str, geom_type: str, 
                  feature_count: int, color: str = "#2D8C4E"):
        """新增圖層"""
        if layer_id in self.layer_items:
            return

        item = LayerItem(layer_id, name, geom_type, feature_count, color)
        item.visibilityChanged.connect(self.layerVisibilityChanged)
        item.styleClicked.connect(self.layerStyleClicked)
        item.removeClicked.connect(self.layerRemoveClicked)

        # 插入到倒數第二個位置（stretch 之前）
        self.layer_layout.insertWidget(
            self.layer_layout.count() - 1, item
        )
        self.layer_items[layer_id] = item

    def remove_layer(self, layer_id: str):
        """移除圖層"""
        if layer_id in self.layer_items:
            item = self.layer_items.pop(layer_id)
            item.deleteLater()

    def clear_layers(self):
        """清除所有圖層"""
        for item in list(self.layer_items.values()):
            item.deleteLater()
        self.layer_items.clear()

    def _on_remove_all(self):
        """移除所有圖層"""
        self.layerRemoveClicked.emit("_all_")

    def set_layer_visible(self, layer_id: str, visible: bool):
        """設定圖層可見性"""
        if layer_id in self.layer_items:
            self.layer_items[layer_id].setVisible(visible)
