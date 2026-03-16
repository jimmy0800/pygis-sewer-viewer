"""
MapView - QWebEngineView 封裝 Leaflet 地圖
"""

import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, pyqtSlot
from .bridge import JsBridge


class MapView(QWebEngineView):
    """內嵌 Leaflet 地圖的 WebEngineView"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.js_bridge = JsBridge(self)
        self.loaded_layers = {}

        # 設定 WebChannel
        self.page().setWebChannel(QWebChannel(self))
        self.page().webChannel().registerObject("pybridge", self.js_bridge)

        # 連接訊號
        self.js_bridge.featureClicked.connect(self._on_feature_clicked)
        self.js_bridge.mapClicked.connect(self._on_map_clicked)
        self.js_bridge.mouseMoved.connect(self._on_mouse_moved)
        self.js_bridge.mapReady.connect(self._on_map_ready)

        # 載入 HTML
        self._load_html()

    def _load_html(self):
        """載入 Leaflet 地圖 HTML"""
        # 取得 assets 目錄路徑
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        html_path = os.path.join(base_dir, "assets", "leaflet_map.html")

        # 轉為 file:// URL
        self.setUrl(QUrl.fromLocalFile(os.path.abspath(html_path)))

    @pyqtSlot(str)
    def _on_feature_clicked(self, properties_json: str):
        """處理要素點擊事件"""
        # 轉發給父視窗處理
        self.parent().on_feature_clicked(properties_json) if hasattr(self.parent(), 'on_feature_clicked') else None

    @pyqtSlot(float, float)
    def _on_map_clicked(self, lat: float, lng: float):
        """處理地圖點擊事件"""
        self.parent().on_map_clicked(lat, lng) if hasattr(self.parent(), 'on_map_clicked') else None

    @pyqtSlot(float, float)
    def _on_mouse_moved(self, lat: float, lng: float):
        """處理滑鼠移動事件"""
        self.parent().on_mouse_moved(lat, lng) if hasattr(self.parent(), 'on_mouse_moved') else None

    @pyqtSlot()
    def _on_map_ready(self):
        """處理地圖準備完成事件"""
        self.parent().on_map_ready() if hasattr(self.parent(), 'on_map_ready') else None

    def add_geojson_layer(self, layer_id: str, geojson: str, visible: bool = True):
        """新增 GeoJSON 圖層"""
        js_code = f"""
            (function() {{
                const geojson = {geojson};
                addGeoJSONLayer('{layer_id}', JSON.stringify(geojson), {str(visible).lower()});
            }})();
        """
        self.page().runJavaScript(js_code)
        self.loaded_layers[layer_id] = geojson

    def toggle_layer(self, layer_id: str, visible: bool):
        """切換圖層顯示"""
        js_code = f"toggleLayerVisibility('{layer_id}', {str(visible).lower()});"
        self.page().runJavaScript(js_code)

    def remove_layer(self, layer_id: str):
        """移除圖層"""
        js_code = f"removeLayer('{layer_id}');"
        self.page().runJavaScript(js_code)
        if layer_id in self.loaded_layers:
            del self.loaded_layers[layer_id]

    def fit_bounds(self, layer_id: str = None):
        """全圖適應"""
        if layer_id:
            js_code = f"fitBounds('{layer_id}');"
        else:
            js_code = "fitAllLayers();"
        self.page().runJavaScript(js_code)

    def switch_basemap(self, layer_id: str):
        """切換底圖"""
        js_code = f"switchBaseLayer('{layer_id}');"
        self.page().runJavaScript(js_code)

    def update_layer_style(self, layer_id: str, geojson: str):
        """更新圖層樣式"""
        js_code = f"""
            (function() {{
                const geojson = {geojson};
                updateLayerStyle('{layer_id}', JSON.stringify(geojson));
            }})();
        """
        self.page().runJavaScript(js_code)
        self.loaded_layers[layer_id] = geojson
