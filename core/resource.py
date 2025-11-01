# project/core/resource.py
# 提供跨平台、與執行位置無關的專案根路徑與資源查找工具
from pathlib import Path

# core/ 資料夾的父層就是專案根 (project/)
BASE_DIR = Path(__file__).resolve().parents[1]

def proj_path(*parts) -> Path:
    """回傳相對於專案根的路徑: proj_path('assets','images','player.png')"""
    return BASE_DIR.joinpath(*parts)

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)
    return p
