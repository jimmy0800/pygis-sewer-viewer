# PyGIS Sewer Viewer

一套基於 Python 開發的**污水管網 GIS 桌面檢視工具**，支援載入 Shapefile、互動式地圖瀏覽、圖層樣式設定與屬性查詢。

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.7.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 功能特色

- 📂 **載入 Shapefile** — 支援人孔（點位）與管線（線段）SHP 檔案
- 🗺️ **互動式地圖** — 基於 Leaflet，支援縮放、平移、全圖適應
- 🌍 **多種底圖切換** — OpenStreetMap、Google Maps 街道圖、Google Maps 衛星圖
- 📊 **屬性查詢** — 點擊地圖要素即可查看屬性資料
- 🎨 **樣式設定** — 支援分類配色（categorical）與漸層配色（gradient）
- 📐 **自動座標轉換** — 自動偵測 TWD97 / WGS84，無需手動設定
- 🗂️ **圖層管理** — 圖層顯示/隱藏、移除、多圖層疊加

---

## 畫面截圖

> 啟動後即可看到內嵌地圖主介面，左側為圖層面板，右側為屬性面板。

---

## 安裝與執行

### 系統需求

- Python 3.9 以上
- macOS / Windows / Linux

### 1. 複製專案

```bash
git clone https://github.com/jimmy0800/pygis-sewer-viewer.git
cd pygis-sewer-viewer
```

### 2. 建立虛擬環境（建議）

```bash
python3 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

> macOS 使用者若遇到 Qt WebEngine 問題，可另外安裝：
> ```bash
> brew install qt@6
> ```

### 4. 執行程式

```bash
python main.py
```

---

## 使用方式

1. **啟動程式** — 執行 `python main.py`，地圖視窗將自動開啟
2. **載入資料**
   - 點擊工具列「**開啟人孔 SHP**」載入人孔點位資料（`.shp`）
   - 點擊工具列「**開啟管線 SHP**」載入管線線段資料（`.shp`）
3. **切換底圖** — 工具列右側下拉選單可切換 OSM / Google 街道 / Google 衛星
4. **查看屬性** — 點擊地圖上的要素，右側屬性面板會顯示詳細資料
5. **設定樣式** — 在左側圖層面板點擊樣式圖示，可依屬性欄位設定配色
6. **全圖適應** — 點擊工具列「**全圖適應**」讓地圖自動縮放至所有資料範圍

---

## 技術棧

| 類別 | 套件 | 版本 | 用途 |
|------|------|------|------|
| **GUI 框架** | [PyQt6](https://pypi.org/project/PyQt6/) | 6.7.0 | 主視窗、工具列、面板等 UI 元件 |
| **WebEngine** | [PyQt6-WebEngine](https://pypi.org/project/PyQt6-WebEngine/) | 6.7.0 | 內嵌 Chromium 渲染 Leaflet 地圖 |
| **GIS 資料處理** | [GeoPandas](https://geopandas.org/) | 0.14.4 | 讀取 Shapefile、GeoDataFrame 操作 |
| **座標投影** | [PyProj](https://pyproj4.github.io/pyproj/) | 3.6.1 | TWD97 ↔ WGS84 座標轉換 |
| **配色計算** | [Matplotlib](https://matplotlib.org/) | 3.8.3 | 分類 / 漸層調色板產生 |
| **地圖渲染** | [Leaflet.js](https://leafletjs.com/) | CDN | 前端互動式地圖 |
| **JS ↔ Python 橋接** | QWebChannel | PyQt6 內建 | JavaScript 與 Python 雙向通訊 |

---

## 專案結構

```
pygis-sewer-viewer/
├── main.py                 # 程式入口
├── requirements.txt        # Python 依賴套件
├── app/
│   ├── __init__.py
│   ├── main_window.py      # 主視窗
│   ├── map_view.py         # Leaflet 地圖 WebEngineView
│   ├── gis_engine.py       # GIS 資料處理引擎（SHP 讀取、座標轉換、配色）
│   ├── layer_panel.py      # 左側圖層管理面板
│   ├── attribute_panel.py  # 右側屬性查詢面板
│   ├── style_dialog.py     # 樣式設定對話框
│   └── bridge.py           # JS ↔ Python 通訊橋接
├── assets/
│   └── leaflet_map.html    # Leaflet 地圖 HTML 模板
└── data/                   # 放置 SHP 資料（預設為空）
```

---

## 支援的 Shapefile 格式

| 幾何類型 | 說明 | 預設顏色 |
|----------|------|----------|
| Point / MultiPoint | 人孔、設施點位 | 綠色 `#2D8C4E` |
| LineString / MultiLineString | 管線、渠道 | 藍色 `#569CD6` |

---

## 常見問題

**Q: 載入 SHP 後地圖沒有顯示資料？**
> 請確認 SHP 檔案的座標系統為 TWD97（EPSG:3826）或 WGS84（EPSG:4326），其他座標系統需手動轉換。

**Q: 程式啟動時出現 Qt WebEngine 相關錯誤？**
> macOS 請執行 `brew install qt@6`；Windows 請確認 `PyQt6-WebEngine` 已正確安裝。

**Q: 屬性面板沒有顯示資料？**
> 請確認點擊的是地圖上的要素（人孔點或管線），點擊空白地圖區域不會觸發。

---

## License

MIT License — 歡迎自由使用與修改。
