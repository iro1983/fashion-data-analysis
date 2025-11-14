#!/usr/bin/env python3
"""
时尚数据分析系统 - Railway部署入口点
==================================
主启动脚本，确保Railway能正确识别Python项目
"""
import os
import sys
from pathlib import Path

# 设置正确的Python路径
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))

try:
    # 导入FastAPI应用
    from app.main import app
    print("✅ FastAPI应用导入成功")
    
    # 启动应用
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 8000))
        print(f"🚀 启动时尚数据分析系统 - 端口 {port}")
        print(f"📁 项目根目录: {project_root}")
        print(f"🔗 访问地址: http://0.0.0.0:{port}")
        print(f"📚 API文档: http://0.0.0.0:{port}/docs")
        
        import uvicorn
        uvicorn.run(
            "app.main:app", 
            host="0.0.0.0", 
            port=port, 
            log_level="info",
            reload=False,
            workers=1
        )
        
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("🔧 请确保所有依赖已正确安装")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动失败: {e}")
    sys.exit(1)