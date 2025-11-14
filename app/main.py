#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时尚数据分析Web应用主入口
=====================================

使用FastAPI构建的Web应用，提供：
1. RESTful API接口
2. 静态文件服务
3. 数据抓取服务集成

作者：Claude
日期：2025-11-14
"""

import asyncio
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "code"))

# 导入数据抓取模块
from code.main import MainCoordinator, Platform
from code.database import DatabaseManager
from code.config import ConfigManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
coordinator = None
db_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global coordinator, db_manager
    
    # 启动时初始化
    logger.info("🚀 启动时尚数据分析Web应用")
    
    try:
        # 初始化核心组件
        config_manager = ConfigManager()
        db_manager = DatabaseManager(config_manager)
        coordinator = MainCoordinator()
        
        logger.info("✅ 核心组件初始化完成")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 应用启动失败: {e}")
        raise
    
    # 关闭时清理
    logger.info("🔄 应用关闭")

# 创建FastAPI应用
app = FastAPI(
    title="时尚数据分析API",
    description="TikTok和Amazon时尚数据抓取与分析系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API路由
from app.api.routes import router
app.include_router(router, prefix="/api/v1")

# 静态文件服务
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """主页 - 提供前端应用"""
    index_path = static_path / "index.html"
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """
        <html>
            <body>
                <h1>🚀 时尚数据分析系统</h1>
                <p>API服务正常运行</p>
                <p><a href="/docs">API文档</a></p>
            </body>
        </html>
        """

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "fashion-data-analysis",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # 本地开发模式
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )