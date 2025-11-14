#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import asyncio
import json
from datetime import datetime

# 导入全局变量依赖
from app.main import coordinator, db_manager

router = APIRouter()

async def get_coordinator():
    """获取协调器依赖"""
    if coordinator is None:
        raise HTTPException(status_code=503, detail="Service not available")
    return coordinator

async def get_db_manager():
    """获取数据库管理器依赖"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return db_manager

@router.get("/status")
async def get_status(coordinator=Depends(get_coordinator)):
    """获取系统状态"""
    try:
        status = coordinator.get_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape/platform")
async def scrape_platform(
    platform: str,
    categories: List[str],
    keywords: List[str],
    max_pages: int = 5,
    background_tasks: BackgroundTasks = None,
    coordinator=Depends(get_coordinator)
):
    """执行指定平台的数据抓取"""
    try:
        # 验证平台
        from code.main import Platform
        if platform.lower() not in [p.value for p in Platform]:
            raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")
        
        # 执行抓取
        platform_enum = Platform(platform.lower())
        results = await coordinator.scrape_platform(
            platform_enum, categories, keywords, max_pages
        )
        
        return {
            "success": True,
            "message": f"{platform}平台抓取任务已启动",
            "data": {
                "platform": platform,
                "categories": categories,
                "keywords": keywords,
                "max_pages": max_pages,
                "tasks_created": len(results)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape/all")
async def scrape_all_platforms(
    categories: List[str],
    keywords: List[str],
    max_pages: int = 5,
    coordinator=Depends(get_coordinator)
):
    """执行所有平台的数据抓取"""
    try:
        results = await coordinator.scrape_all_platforms(categories, keywords, max_pages)
        
        total_tasks = sum(len(platform_results) for platform_results in results.values())
        
        return {
            "success": True,
            "message": "所有平台抓取任务已启动",
            "data": {
                "platforms": {platform.value: len(platform_results) for platform, platform_results in results.items()},
                "total_tasks": total_tasks,
                "categories": categories,
                "keywords": keywords,
                "max_pages": max_pages
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products")
async def get_products(
    platform: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db_manager=Depends(get_db_manager)
):
    """获取产品数据"""
    try:
        # 这里可以添加数据库查询逻辑
        # 暂时返回示例数据
        sample_products = []
        
        return {
            "success": True,
            "data": {
                "products": sample_products,
                "total": len(sample_products),
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_statistics(
    days: int = 7,
    db_manager=Depends(get_db_manager)
):
    """获取统计数据"""
    try:
        stats = db_manager.get_statistics(days)
        
        return {
            "success": True,
            "data": {
                "statistics": stats,
                "period_days": days
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config")
async def update_config(
    key: str,
    value: Any,
    coordinator=Depends(get_coordinator)
):
    """更新配置"""
    try:
        coordinator.config.config[key] = value
        coordinator.config.save()
        
        return {
            "success": True,
            "message": "配置已更新",
            "data": {
                "key": key,
                "value": value
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_config(coordinator=Depends(get_coordinator)):
    """获取配置"""
    try:
        return {
            "success": True,
            "data": coordinator.config.config,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))