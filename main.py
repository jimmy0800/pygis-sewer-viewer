#!/usr/bin/env python3
"""
PyGIS Sewer Viewer - 主程式入口

使用方式:
    python main.py

依賴:
    pip install -r requirements.txt

注意:
    首次執行可能需要安裝 Qt WebEngine
    - macOS: brew install qt@6
    - Windows: 安裝 PyQt6-WebEngine 時會自動下載
"""

import sys
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow


def main():
    """主函數"""
    app = QApplication(sys.argv)
    app.setApplicationName("PyGIS Sewer Viewer")
    app.setOrganizationName("PyGIS")

    # 設定高 DPI 支援
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # 建立主視窗
    window = MainWindow()
    window.show()

    # 執行應用
    sys.exit(app.exec())


if __name__ == "__main__":
    from PyQt6.QtCore import Qt
    main()
