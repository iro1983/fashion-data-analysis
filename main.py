#!/usr/bin/env python3
"""
简化的启动脚本 - 直接运行FastAPI应用
"""
import os
import sys
from pathlib import Path

# 添加路径
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "code"))

# 导入并运行
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 启动FastAPI应用在端口 {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, workers=1)