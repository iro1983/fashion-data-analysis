#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主协调脚本使用示例
================

演示如何使用MainCoordinator进行数据抓取任务的创建、执行和监控。

作者：Claude
日期：2025-11-14
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from main import MainCoordinator, Platform


async def demo_basic_scraping():
    """演示基础抓取功能"""
    print("=== 演示基础抓取功能 ===")
    
    # 创建协调器
    coordinator = MainCoordinator()
    
    # 抓取Amazon平台
    print("1. 抓取Amazon平台...")
    amazon_results = await coordinator.scrape_platform(
        platform=Platform.AMAZON,
        categories=["T-Shirt", "Hoodie"],
        keywords=["print", "graphic"],
        max_pages=3
    )
    
    print(f"   完成 {len(amazon_results)} 个Amazon任务")
    
    # 抓取TikTok平台
    print("2. 抓取TikTok平台...")
    tiktok_results = await coordinator.scrape_platform(
        platform=Platform.TIKTOK,
        categories=["服装", "时尚"],
        keywords=["印花", "T恤"],
        max_pages=2
    )
    
    print(f"   完成 {len(tiktok_results)} 个TikTok任务")


async def demo_all_platforms():
    """演示所有平台抓取"""
    print("\n=== 演示所有平台抓取 ===")
    
    coordinator = MainCoordinator()
    
    print("开始并发抓取所有平台...")
    results = await coordinator.scrape_all_platforms(
        categories=["T-Shirt", "Hoodie"],
        keywords=["print", "graphic", "design"],
        max_pages=2
    )
    
    print("抓取结果汇总:")
    for platform, platform_results in results.items():
        successful = [r for r in platform_results if r.success]
        failed = [r for r in platform_results if not r.success]
        total_items = sum(r.items_found for r in successful)
        
        print(f"  {platform.value}:")
        print(f"    总任务: {len(platform_results)}")
        print(f"    成功: {len(successful)}")
        print(f"    失败: {len(failed)}")
        print(f"    总产品: {total_items}")


def demo_status_check():
    """演示状态检查"""
    print("\n=== 演示状态检查 ===")
    
    coordinator = MainCoordinator()
    status = coordinator.get_status()
    
    print("系统状态:")
    print(f"  时间: {status['timestamp']}")
    print("  配置状态:")
    for key, value in status['config_status'].items():
        print(f"    {key}: {value}")
    
    print("  性能统计:")
    if 'message' in status['performance']:
        print(f"    {status['performance']['message']}")
    else:
        for platform, stats in status['performance'].items():
            print(f"    {platform}:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"      {key}: {value:.2f}")
                else:
                    print(f"      {key}: {value}")


def demo_config_management():
    """演示配置管理"""
    print("\n=== 演示配置管理 ===")
    
    coordinator = MainCoordinator()
    
    # 显示当前配置
    print("当前配置:")
    config = coordinator.config.config
    
    def print_config_section(section, indent=0):
        for key, value in section.items():
            if isinstance(value, dict):
                print("  " * indent + f"{key}:")
                print_config_section(value, indent + 1)
            else:
                print("  " * indent + f"{key}: {value}")
    
    print_config_section(config)


async def demo_batch_tasks():
    """演示批量任务处理"""
    print("\n=== 演示批量任务处理 ===")
    
    coordinator = MainCoordinator()
    
    # 创建多个任务
    print("创建批量任务...")
    tasks = []
    
    categories = ["T-Shirt", "Hoodie"]
    keywords = ["print", "graphic", "design"]
    
    for category in categories:
        for keyword in keywords:
            task = coordinator.create_task(
                platform=Platform.AMAZON,
                category=category,
                keywords=[keyword],
                max_pages=2
            )
            tasks.append(task)
    
    print(f"创建了 {len(tasks)} 个任务")
    
    # 执行批量任务
    print("执行批量任务...")
    results = await coordinator.execute_multiple_tasks(tasks, max_workers=3)
    
    # 分析结果
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"批量任务结果:")
    print(f"  总任务: {len(results)}")
    print(f"  成功: {len(successful)}")
    print(f"  失败: {len(failed)}")
    print(f"  成功率: {len(successful)/len(results)*100:.1f}%")


def demo_data_integration():
    """演示数据整合"""
    print("\n=== 演示数据整合 ===")
    
    coordinator = MainCoordinator()
    
    # 模拟数据
    amazon_products = [
        {
            "product_id": "amz_001",
            "title": "印花T恤 A",
            "price": 19.99,
            "category": "T-Shirt",
            "rating": 4.5,
            "shop_name": "品牌A"
        },
        {
            "product_id": "amz_002", 
            "title": "印花T恤 B",
            "price": 24.99,
            "category": "T-Shirt",
            "rating": 4.8,
            "shop_name": "品牌B"
        }
    ]
    
    tiktok_products = [
        {
            "product_id": "tt_001",
            "title": "时尚T恤 A", 
            "price": 29.99,
            "category": "服装",
            "rating": 4.3,
            "shop_name": "店铺A"
        }
    ]
    
    # 整合数据
    integrated = coordinator.data_integrator.merge_platform_data(
        amazon_products, tiktok_products
    )
    
    print("整合结果:")
    print(f"  总产品数: {integrated['total_products']}")
    print(f"  Amazon产品: {integrated['amazon_products']}")
    print(f"  TikTok产品: {integrated['tiktok_products']}")
    print(f"  价格范围:")
    print(f"    Amazon: ${integrated['price_ranges']['amazon']['min']:.2f} - ${integrated['price_ranges']['amazon']['max']:.2f}")
    print(f"    TikTok: ${integrated['price_ranges']['tiktok']['min']:.2f} - ${integrated['price_ranges']['tiktok']['max']:.2f}")


async def main():
    """主函数"""
    print("Amazon与TikTok数据抓取协调器演示")
    print("=" * 50)
    
    # 确保必要的目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    try:
        # 运行各种演示
        await demo_basic_scraping()
        await demo_all_platforms()
        demo_status_check()
        demo_config_management()
        await demo_batch_tasks()
        demo_data_integration()
        
        print("\n=== 演示完成 ===")
        print("检查生成的报告和日志文件:")
        print("  - 数据库: data/scraping.db")
        print("  - 日志: logs/coordinator.log")
        print("  - 报告: reports/")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())