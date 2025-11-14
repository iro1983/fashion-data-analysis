#!/usr/bin/env python3
"""
时尚数据分析系统 - Railway部署入口点
==================================
"""
import os
import sys
from pathlib import Path

# 设置正确的Python路径
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))

# 导入FastAPI应用
from app.main import app
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 启动时尚数据分析系统 - 端口 {port}")
    print(f"📁 项目根目录: {project_root}")
    print(f"🔗 访问地址: http://0.0.0.0:{port}")
    
    # 启动应用
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=port, 
        log_level="info",
        reload=False,
        workers=1
    )