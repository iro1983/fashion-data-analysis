#!/usr/bin/env python3
"""
时尚数据分析系统 - Railway部署专用启动脚本
=====================================
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

def main():
    """主启动函数"""
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print("🚀 时尚数据分析系统启动中...")
    print(f"📍 项目路径: {project_root}")
    print(f"🌐 监听地址: {host}:{port}")
    print(f"🔗 访问地址: http://localhost:{port}")
    print(f"📚 API文档: http://localhost:{port}/docs")
    
    # 启动应用
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level="info",
        reload=False,
        workers=1
    )

if __name__ == "__main__":
    main()