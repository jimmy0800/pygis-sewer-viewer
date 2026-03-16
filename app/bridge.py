"""
JsBridge - Python ↔ JavaScript 橋接介面
"""

from PyQt6.QtCore import QObject, pyqtSignal


class JsBridge(QObject):
    """QWebChannel JavaScript 橋接器"""

    # 訊號定義
    featureClicked = pyqtSignal(str)  # 點擊要素時發送屬性 JSON
    mapClicked = pyqtSignal(float, float)  # 點擊地圖時發送座標
    mouseMoved = pyqtSignal(float, float)  # 滑鼠移動時發送座標
    mapReady = pyqtSignal()  # 地圖初始化完成

    def __init__(self, parent=None):
        super().__init__(parent)

    def onFeatureClick(self, properties_json: str):
        """JavaScript 呼叫：要素被點擊"""
        self.featureClicked.emit(properties_json)

    def onMapClick(self, coord: dict):
        """JavaScript 呼叫：地圖被點擊"""
        self.mapClicked.emit(coord['lat'], coord['lng'])

    def onMouseMove(self, coord: dict):
        """JavaScript 呼叫：滑鼠移動"""
        self.mouseMoved.emit(coord['lat'], coord['lng'])

    def onMapReady(self):
        """JavaScript 呼叫：地圖準備完成"""
        self.mapReady.emit()
