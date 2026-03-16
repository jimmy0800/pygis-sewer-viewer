"""
GIS Engine - SHP 讀取、座標轉換、GeoJSON 序列化、樣式配色計算
"""

import json
import geopandas as gpd
import pandas as pd
from pathlib import Path
from typing import Optional
from pyproj import Transformer
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


class GisEngine:
    """GIS 資料處理引擎"""

    # 台灣常用座標系統
    CRS_TWD97 = "EPSG:3826"  # TWD97 / TM2
    CRS_WGS84 = "EPSG:4326"  # WGS84

    def __init__(self):
        self.transformer = Transformer.from_crs(
            self.CRS_TWD97, self.CRS_WGS84, always_xy=True
        )
        self.loaded_layers: dict[str, gpd.GeoDataFrame] = {}

    def load_shp(self, path: str) -> gpd.GeoDataFrame:
        """
        載入 SHP 檔案並自動偵測座標系統

        Args:
            path: SHP 檔案路徑

        Returns:
            GeoDataFrame
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"找不到檔案: {path}")

        # 讀取 SHP
        gdf = gpd.read_file(path)

        # 自動偵測並轉換座標系統
        if gdf.crs is None:
            # 假設為 TWD97（台灣常用）
            gdf = gdf.set_crs(self.CRS_TWD97)
        elif gdf.crs != self.CRS_WGS84:
            # 轉換至 WGS84
            gdf = gdf.to_crs(self.CRS_WGS84)

        # 記錄圖層
        layer_name = path.stem
        self.loaded_layers[layer_name] = gdf

        return gdf

    def to_geojson(
        self,
        gdf: gpd.GeoDataFrame,
        style_config: Optional[dict] = None
    ) -> str:
        """
        將 GeoDataFrame 轉換為 GeoJSON 字串

        Args:
            gdf: GeoDataFrame
            style_config: 樣式設定 {'field': '欄位名', 'colors': {值: 顏色}}

        Returns:
            GeoJSON 字串
        """
        # 複製避免修改原始資料
        gdf_copy = gdf.copy()

        # 座標精度截斷（減少傳輸量）
        def truncate_coords(geom):
            if geom is None:
                return None
            return geom.buffer(0).wkb  # 清理拓撲

        # 處理幾何類型
        geom_type = gdf_copy.geom_type.iloc[0] if len(gdf_copy) > 0 else "Unknown"

        # 根據類型給定預設樣式
        if geom_type in ["Point", "MultiPoint"]:
            default_color = "#2D8C4E"
            default_weight = 2
        else:  # LineString, MultiLineString
            default_color = "#569CD6"
            default_weight = 3

        # 轉換為 GeoJSON
        geojson = json.loads(gdf_copy.to_json())

        # 加入樣式資訊
        if style_config and "colors" in style_config:
            colors = style_config["colors"]
            field = style_config.get("field", None)

            for feature in geojson.get("features", []):
                props = feature.get("properties", {})

                if field and field in props:
                    value = props[field]
                    feature["style"] = {
                        "color": colors.get(value, default_color),
                        "weight": default_weight
                    }
                else:
                    feature["style"] = {
                        "color": default_color,
                        "weight": default_weight
                    }
        else:
            # 套用預設樣式
            for feature in geojson.get("features", []):
                feature["style"] = {
                    "color": default_color,
                    "weight": default_weight
                }

        return json.dumps(geojson, ensure_ascii=False)

    def get_style_colors(
        self,
        gdf: gpd.GeoDataFrame,
        field: str,
        mode: str = "categorical",
        color_palette: str = "tab10"
    ) -> dict:
        """
        根據屬性欄位計算配色

        Args:
            gdf: GeoDataFrame
            field: 屬性欄位名稱
            mode: 'categorical' (分類) 或 'gradient' (漸變)
            color_palette: 調色板名稱

        Returns:
            {欄位值: 顏色} 的字典
        """
        if field not in gdf.columns:
            raise ValueError(f"欄位不存在: {field}")

        unique_values = gdf[field].dropna().unique()
        result = {}

        if mode == "categorical":
            # 分類配色
            cmap = plt.get_cmap(color_palette)
            colors = [mcolors.to_hex(cmap(i / len(unique_values)))
                     for i in range(len(unique_values))]

            for i, value in enumerate(unique_values):
                result[str(value)] = colors[i]

        else:
            # 漸變配色
            values = gdf[field].dropna()
            norm = plt.Normalize(vmin=values.min(), vmax=values.max())
            cmap = plt.get_cmap(color_palette)

            for value in unique_values:
                if pd.notna(value):
                    rgba = cmap(norm(value))
                    result[str(value)] = mcolors.to_hex(rgba)

        return result

    def get_fields(self, gdf: gpd.GeoDataFrame) -> list[str]:
        """取得 GeoDataFrame 的所有屬性欄位"""
        return list(gdf.columns)

    def get_geom_type(self, gdf: gpd.GeoDataFrame) -> str:
        """取得幾何類型（Point/LineString）"""
        if len(gdf) > 0:
            return gdf.geom_type.iloc[0]
        return "Unknown"

    def get_bounds(self, gdf: gpd.GeoDataFrame) -> tuple:
        """取得圖層邊界 [minx, miny, maxx, maxy]"""
        if len(gdf) > 0:
            bounds = gdf.total_bounds
            return bounds.tolist()
        return [0, 0, 0, 0]
