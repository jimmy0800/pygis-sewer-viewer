"""
StyleDialog - 樣式設定對話框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QRadioButton, QPushButton, QWidget,
    QScrollArea, QFrame, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette


# 預設調色板
COLOR_PALETTES = {
    "tab10": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
              "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
    "set2": ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", 
             "#ffd92f", "#e5c494", "#b3b3b3"],
    "viridis": ["#440154", "#482878", "#3e4a89", "#31688e", "#26828e", 
                "#1f9e89", "#35b779", "#6dcd59", "#b4de2c", "#fde725"],
    "plasma": ["#0d0887", "#46039f", "#7201a8", "#9c179e", "#bd3786", 
               "#d8576b", "#ed7953", "#fb9f3a", "#fdca26", "#f0f921"],
    "coolwarm": ["#3b4cc0", "#6788ee", "#9abbff", "#c9d7f0", "#e8e8e8",
                 "#f0c9c0", "#e29893", "#c75e62", "#b40426"]
}


class StyleDialog(QDialog):
    """樣式設定對話框"""

    styleApplied = pyqtSignal(dict)  # {field, mode, palette}

    def __init__(self, layer_id: str, fields: list, parent=None):
        super().__init__(parent)

        self.layer_id = layer_id
        self.fields = fields
        self.selected_field = None
        self.selected_mode = "categorical"
        self.selected_palette = "tab10"

        self.setWindowTitle("樣式設定")
        self.setFixedSize(400, 450)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background: #252526;
            }
            QLabel {
                color: #D4D4D4;
            }
            QComboBox, QListWidget {
                background: #2D2D2D;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
                padding: 6px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #888;
            }
            QRadioButton {
                color: #D4D4D4;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
            QPushButton {
                background: #2D8C4E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #3AAD63;
            }
            QPushButton[secondary="true"] {
                background: #3C3C3C;
            }
            QPushButton[secondary="true"]:hover {
                background: #4C4C4C;
            }
        """)

        layout = QVBoxLayout(self)

        # 屬性欄位選擇
        field_label = QLabel("選擇欄位")
        self.field_combo = QComboBox()
        self.field_combo.addItems(self.fields)
        self.field_combo.currentTextChanged.connect(self._on_field_changed)

        layout.addWidget(field_label)
        layout.addWidget(self.field_combo)

        # 配色模式
        mode_label = QLabel("配色模式")
        mode_layout = QHBoxLayout()

        self.radio_cat = QRadioButton("分類")
        self.radio_cat.setChecked(True)
        self.radio_cat.toggled.connect(lambda: self._on_mode_changed("categorical"))

        self.radio_grad = QRadioButton("漸變")
        self.radio_grad.toggled.connect(lambda: self._on_mode_changed("gradient"))

        mode_layout.addWidget(self.radio_cat)
        mode_layout.addWidget(self.radio_grad)
        mode_layout.addStretch()

        layout.addWidget(mode_label)
        layout.addLayout(mode_layout)

        # 調色板選擇
        palette_label = QLabel("調色板")
        
        self.palette_list = QListWidget()
        self.palette_list.setFixedHeight(150)
        for name in COLOR_PALETTES.keys():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.palette_list.addItem(item)
        self.palette_list.item(0).setSelected(True)
        self.palette_list.itemClicked.connect(self._on_palette_changed)

        layout.addWidget(palette_label)
        layout.addWidget(self.palette_list)

        # 預覽
        preview_label = QLabel("預覽")
        self.preview_widget = QWidget()
        self.preview_widget.setFixedHeight(40)
        self._update_preview()

        layout.addWidget(preview_label)
        layout.addWidget(self.preview_widget)

        layout.addStretch()

        # 按鈕
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)

        apply_btn = QPushButton("套用")
        apply_btn.clicked.connect(self._on_apply)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)

    def _on_field_changed(self, text):
        self.selected_field = text

    def _on_mode_changed(self, mode):
        self.selected_mode = mode
        self._update_preview()

    def _on_palette_changed(self, item):
        self.selected_palette = item.data(Qt.ItemDataRole.UserRole)
        self._update_preview()

    def _update_preview(self):
        """更新預覽"""
        palette = COLOR_PALETTES.get(self.selected_palette, COLOR_PALETTES["tab10"])
        
        colors = palette if self.selected_mode == "categorical" else palette[::2]
        
        # 建立漸變背景
        gradient = "linear-gradient(to right, " + ", ".join(colors) + ")"
        self.preview_widget.setStyleSheet(f"""
            QWidget {{
                background: {gradient};
                border-radius: 4px;
                border: 1px solid #3C3C3C;
            }}
        """)

    def _on_apply(self):
        """套用樣式"""
        if not self.selected_field:
            return

        result = {
            "field": self.selected_field,
            "mode": self.selected_mode,
            "palette": self.selected_palette,
            "colors": COLOR_PALETTES.get(self.selected_palette, COLOR_PALETTES["tab10"])
        }

        self.styleApplied.emit(result)
        self.accept()

    def get_style_config(self):
        """取得樣式設定"""
        return {
            "field": self.selected_field,
            "mode": self.selected_mode,
            "palette": self.selected_palette,
            "colors": COLOR_PALETTES.get(self.selected_palette, COLOR_PALETTES["tab10"])
        }
