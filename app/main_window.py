"""
MainWindow - 主視窗
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QLabel, QComboBox, QPushButton, QStatusBar,
    QDockWidget, QMessageBox, QFileDialog, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from .map_view import MapView
from .layer_panel import LayerPanel
from .attribute_panel import AttributePanel
from .style_dialog import StyleDialog
from .gis_engine import GisEngine


class MainWindow(QMainWindow):
    """主視窗"""

    def __init__(self):
        super().__init__()

        self.gis_engine = GisEngine()
        self.layers_data = {}  # {layer_id: gdf}

        self._init_ui()
        self._apply_styles()

    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("PyGIS Sewer Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # 中央地圖視圖
        self.map_view = MapView(self)
        self.setCentralWidget(self.map_view)

        # 圖層面板（左側）
        self.layer_panel = LayerPanel(self)
        self.layer_panel.layerVisibilityChanged.connect(self._on_layer_visibility_changed)
        self.layer_panel.layerStyleClicked.connect(self._on_layer_style_clicked)
        self.layer_panel.layerRemoveClicked.connect(self._on_layer_remove_clicked)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.layer_panel)

        # 屬性面板（右側）
        self.attribute_panel = AttributePanel(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.attribute_panel)

        # 工具列
        self._create_toolbar()

        # 狀態列
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("就緒")
        self.coord_label = QLabel("經度: - | 緯度: -")
        self.layer_count_label = QLabel("圖層: 0")
        
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.coord_label)
        self.status_bar.addPermanentWidget(self.layer_count_label)

    def _create_toolbar(self):
        """建立工具列"""
        toolbar = QToolBar("主工具列")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        # 開啟人孔 SHP
        self.manhole_action = QAction("開啟人孔 SHP", self)
        self.manhole_action.setShortcut(QKeySequence.StandardKey.Open)
        self.manhole_action.triggered.connect(lambda: self._open_shp("manhole"))
        toolbar.addAction(self.manhole_action)

        # 開啟管線 SHP
        self.pipe_action = QAction("開啟管線 SHP", self)
        self.pipe_action.triggered.connect(lambda: self._open_shp("pipe"))
        toolbar.addAction(self.pipe_action)

        toolbar.addSeparator()

        # 底圖切換
        basemap_label = QLabel("底圖: ")
        basemap_label.setStyleSheet("color: #D4D4D4; padding: 0 4px;")
        toolbar.addWidget(basemap_label)

        self.basemap_combo = QComboBox()
        self.basemap_combo.addItems(["OpenStreetMap", "Google Maps 街道", "Google Maps 衛星"])
        self.basemap_combo.setCurrentIndex(0)
        self.basemap_combo.currentIndexChanged.connect(self._on_basemap_changed)
        toolbar.addWidget(self.basemap_combo)

        toolbar.addSeparator()

        # 全圖適應
        fit_action = QAction("全圖適應", self)
        fit_action.triggered.connect(self._on_fit_bounds)
        toolbar.addAction(fit_action)

    def _apply_styles(self):
        """套用樣式"""
        self.setStyleSheet("""
            QMainWindow {
                background: #1E1E1E;
            }

            /* ── 工具列本體 ── */
            QToolBar {
                background: #2C2C2C;
                border-bottom: 2px solid #3A8C5C;
                spacing: 6px;
                padding: 4px 8px;
            }
            QToolBar::separator {
                background: #555;
                width: 1px;
                margin: 4px 8px;
            }

            /* ── 工具列按鈕（QAction 渲染為 QToolButton）── */
            QToolBar QToolButton {
                color: #E8E8E8;
                background: #3C3C3C;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 13px;
                font-weight: 500;
                min-width: 60px;
            }
            QToolBar QToolButton:hover {
                background: #2D8C4E;
                border-color: #3DA866;
                color: #FFFFFF;
            }
            QToolBar QToolButton:pressed {
                background: #1E6B38;
                border-color: #2D8C4E;
            }

            /* ── 狀態列 ── */
            QStatusBar {
                background: #252526;
                color: #AAAAAA;
                border-top: 1px solid #3C3C3C;
                font-size: 12px;
            }

            /* ── 工具列標籤（底圖文字）── */
            QToolBar QLabel {
                color: #CCCCCC;
                font-size: 13px;
                padding: 0 4px;
            }

            /* ── 底圖下拉選單 ── */
            QComboBox {
                background: #3C3C3C;
                color: #E8E8E8;
                border: 1px solid #555;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 13px;
                min-width: 140px;
            }
            QComboBox:hover {
                border-color: #3DA866;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background: #2D2D2D;
                color: #E8E8E8;
                selection-background-color: #2D8C4E;
                border: 1px solid #555;
            }

            /* ── DockWidget 標題列 ── */
            QDockWidget::title {
                background: #2A2A2A;
                color: #D4D4D4;
                padding: 6px 10px;
                border-bottom: 1px solid #3C3C3C;
                font-size: 13px;
                font-weight: bold;
            }
        """)

    def _open_shp(self, layer_type: str):
        """開啟 SHP 檔案"""
        file_filter = "Shapefile (*.shp);;All Files (*)"
        
        if layer_type == "manhole":
            caption = "選擇人孔 SHP 檔案"
        else:
            caption = "選擇管線 SHP 檔案"

        path, _ = QFileDialog.getOpenFileName(self, caption, "", file_filter)

        if not path:
            return

        try:
            # 載入 SHP
            gdf = self.gis_engine.load_shp(path)
            
            # 取得圖層資訊
            layer_name = os.path.basename(path).replace(".shp", "")
            geom_type = self.gis_engine.get_geom_type(gdf)
            feature_count = len(gdf)
            
            # 設定顏色
            color = "#2D8C4E" if geom_type == "Point" else "#569CD6"

            # 轉換為 GeoJSON
            geojson = self.gis_engine.to_geojson(gdf)

            # 新增圖層到地圖
            self.map_view.add_geojson_layer(layer_name, geojson, True)

            # 新增圖層到面板
            self.layer_panel.add_layer(layer_name, layer_name, geom_type, 
                                       feature_count, color)

            # 儲存資料
            self.layers_data[layer_name] = gdf

            # 更新狀態
            self.status_label.setText(f"已載入: {layer_name}")
            self._update_layer_count()

            # 全圖適應
            self.map_view.fit_bounds(layer_name)

        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法載入 SHP 檔案:\n{str(e)}")

    def _on_basemap_changed(self, index: int):
        """底圖切換"""
        layer_map = {
            0: "osm",
            1: "google-street",
            2: "google-satellite"
        }
        
        layer_id = layer_map.get(index, "osm")
        self.map_view.switch_basemap(layer_id)
        
        name = self.basemap_combo.currentText()
        self.status_label.setText(f"底圖: {name}")

    def _on_layer_visibility_changed(self, layer_id: str, visible: bool):
        """圖層顯示/隱藏"""
        self.map_view.toggle_layer(layer_id, visible)

    def _on_layer_style_clicked(self, layer_id: str):
        """點擊樣式設定"""
        if layer_id not in self.layers_data:
            return

        gdf = self.layers_data[layer_id]
        fields = self.gis_engine.get_fields(gdf)

        dialog = StyleDialog(layer_id, fields, self)
        dialog.styleApplied.connect(lambda config: self._apply_style(layer_id, config))
        dialog.exec()

    def _apply_style(self, layer_id: str, config: dict):
        """套用樣式"""
        if layer_id not in self.layers_data:
            return

        gdf = self.layers_data[layer_id]

        # 計算顏色
        colors = self.gis_engine.get_style_colors(
            gdf, 
            config["field"], 
            config["mode"],
            config["palette"]
        )

        # 更新 GeoJSON
        style_config = {"field": config["field"], "colors": colors}
        geojson = self.gis_engine.to_geojson(gdf, style_config)

        # 更新地圖
        self.map_view.update_layer_style(layer_id, geojson)

        self.status_label.setText(f"樣式已套用: {config['field']}")

    def _on_layer_remove_clicked(self, layer_id: str):
        """移除圖層"""
        if layer_id == "_all_":
            # 移除所有圖層
            for lid in list(self.layers_data.keys()):
                self.map_view.remove_layer(lid)
                self.layer_panel.remove_layer(lid)
            self.layers_data.clear()
        else:
            # 移除單一圖層
            if layer_id in self.layers_data:
                del self.layers_data[layer_id]
            self.map_view.remove_layer(layer_id)
            self.layer_panel.remove_layer(layer_id)

        self._update_layer_count()
        self.status_label.setText("圖層已移除")

    def _on_fit_bounds(self):
        """全圖適應"""
        self.map_view.fit_bounds()

    def _update_layer_count(self):
        """更新圖層數量"""
        count = len(self.layers_data)
        self.layer_count_label.setText(f"圖層: {count}")

    # ===== MapView 回调 =====
    def on_feature_clicked(self, properties_json: str):
        """要素被點擊"""
        self.attribute_panel.show_attributes(properties_json)

    def on_map_clicked(self, lat: float, lng: float):
        """地圖被點擊"""
        pass

    def on_mouse_moved(self, lat: float, lng: float):
        """滑鼠移動"""
        self.coord_label.setText(f"經度: {lng:.6f} | 緯度: {lat:.6f}")

    def on_map_ready(self):
        """地圖準備完成"""
        self.status_label.setText("地圖就緒")
