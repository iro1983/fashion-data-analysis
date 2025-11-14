#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok热销服装数据抓取脚本 - 使用示例

演示如何使用TikTok抓取脚本进行服装数据采集，包括：
1. 基础抓取流程
2. 配置管理
3. 数据验证和分析
4. 定时任务
5. 高级功能

基于 docs/tiktok_data_research.md 调研结果开发
"""

import os
import sys
import time
import json
import pandas as pd
from datetime import datetime, timedelta
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tiktok_scraper import TikTokClothingScraper, ScrapingConfig, TikTokVideo
from config import get_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def example_1_basic_scraping():
    """示例1: 基础抓取流程"""
    print("=" * 60)
    print("示例1: 基础抓取流程")
    print("=" * 60)
    
    try:
        # 使用开发配置（不需要真实API密钥）
        config = get_config("dev")
        config.target_hashtags = ["#tshirt", "#hoodie", "#fashion"]  # 减少标签数量
        
        # 创建抓取器
        scraper = TikTokClothingScraper(config)
        print(f"✓ 抓取器创建成功")
        print(f"  - 数据库路径: {config.database_path}")
        print(f"  - 目标标签: {config.target_hashtags}")
        print(f"  - 请求延迟: {config.request_delay}秒")
        
        # 执行抓取
        print("\n开始抓取数据...")
        results = scraper.scrape_clothing_videos(
            target_sources=['web_scraper'],  # 只使用网页爬虫
            max_videos_per_tag=10  # 每个标签最多10个视频
        )
        
        print(f"\n✓ 抓取完成!")
        print(f"  - 处理视频数: {results['total_videos']}")
        print(f"  - 错误数量: {results['total_errors']}")
        print(f"  - 耗时: {results['duration_seconds']:.2f}秒")
        
        return results
        
    except Exception as e:
        print(f"✗ 抓取失败: {e}")
        logger.error(f"基础抓取示例失败: {e}")
        return None

def example_2_data_validation():
    """示例2: 数据验证和分析"""
    print("\n" + "=" * 60)
    print("示例2: 数据验证和分析")
    print("=" * 60)
    
    try:
        # 使用生产配置（需要真实API密钥）
        config = get_config("dev")  # 使用dev配置避免API调用
        
        # 创建抓取器
        scraper = TikTokClothingScraper(config)
        
        # 获取统计信息
        print("获取数据库统计信息...")
        stats = scraper.get_scraping_statistics()
        
        if 'error' not in stats:
            print(f"✓ 统计信息获取成功:")
            print(f"  - 总视频数: {stats['total_videos']}")
            print(f"  - 今日新增: {stats['today_videos']}")
            
            # 来源分布
            if stats.get('source_distribution'):
                print(f"  - 数据来源分布:")
                for source, count in stats['source_distribution'].items():
                    print(f"    {source}: {count}")
            
            # 热门标签
            if stats.get('top_hashtags'):
                print(f"  - 热门标签TOP5:")
                top_tags = sorted(stats['top_hashtags'].items(), 
                                key=lambda x: x[1], reverse=True)[:5]
                for tag, count in top_tags:
                    print(f"    {tag}: {count}")
            
            # 产品链接统计
            product_stats = stats.get('product_links', {})
            if product_stats:
                print(f"  - 产品链接:")
                print(f"    总数: {product_stats['total']}")
                print(f"    有效: {product_stats['valid']}")
                print(f"    验证率: {product_stats['validation_rate']:.2%}")
        else:
            print(f"✗ 统计信息获取失败: {stats['error']}")
        
        return stats
        
    except Exception as e:
        print(f"✗ 数据验证失败: {e}")
        logger.error(f"数据验证示例失败: {e}")
        return None

def example_3_product_link_validation():
    """示例3: 产品链接验证"""
    print("\n" + "=" * 60)
    print("示例3: 产品链接验证")
    print("=" * 60)
    
    try:
        config = get_config("dev")
        scraper = TikTokClothingScraper(config)
        
        # 模拟一些测试链接
        test_links = [
            "https://www.amazon.com/dp/B08N5WRWNW",
            "https://www.ebay.com/itm/123456789",
            "https://shop.example.com/product/123",
            "https://invalid-domain-12345.com/product",
            "https://www.shein.com/us/flash-sale.html"
        ]
        
        print(f"验证 {len(test_links)} 个测试链接...")
        
        # 手动验证链接
        validation_results = []
        for link in test_links:
            result = scraper.link_validator.validate_link(link)
            validation_results.append(result)
            
            print(f"  {result['url']}")
            print(f"    有效: {'✓' if result['is_valid'] else '✗'}")
            print(f"    平台: {result['platform']}")
            print(f"    置信度: {result['confidence_score']:.2%}")
            if 'error' in result:
                print(f"    错误: {result['error']}")
            print()
        
        # 统计结果
        valid_count = sum(1 for r in validation_results if r['is_valid'])
        total_count = len(validation_results)
        
        print(f"✓ 验证完成:")
        print(f"  - 有效链接: {valid_count}/{total_count}")
        print(f"  - 成功率: {valid_count/total_count:.2%}")
        
        # 按平台统计
        platform_stats = {}
        for result in validation_results:
            platform = result['platform']
            if platform not in platform_stats:
                platform_stats[platform] = {'total': 0, 'valid': 0}
            platform_stats[platform]['total'] += 1
            if result['is_valid']:
                platform_stats[platform]['valid'] += 1
        
        print(f"  - 平台分布:")
        for platform, stats in platform_stats.items():
            print(f"    {platform}: {stats['valid']}/{stats['total']}")
        
        return validation_results
        
    except Exception as e:
        print(f"✗ 链接验证失败: {e}")
        logger.error(f"链接验证示例失败: {e}")
        return None

def example_4_fashion_trends():
    """示例4: 时尚趋势分析"""
    print("\n" + "=" * 60)
    print("示例4: 时尚趋势分析")
    print("=" * 60)
    
    try:
        # 检查是否有API密钥
        api_key = os.getenv("TIKHUB_API_KEY")
        if not api_key:
            print("⚠️  未设置TIKHUB_API_KEY环境变量，跳过API相关示例")
            print("如需测试API功能，请:")
            print("1. 注册TikHub账号: https://api.tikhub.io")
            print("2. 获取API密钥")
            print("3. 设置环境变量: export TIKHUB_API_KEY='your_api_key'")
            return None
        
        config = get_config("dev")
        config.tiktok_api_key = api_key
        scraper = TikTokClothingScraper(config)
        
        print("获取美国地区时尚趋势...")
        trending_us = scraper.extract_trending_fashion("US")
        
        if 'error' not in trending_us:
            print(f"✓ 趋势分析成功:")
            print(f"  - 地区: {trending_us['region']}")
            print(f"  - 时尚标签数量: {trending_us['fashion_count']}")
            print(f"  - 总趋势标签: {trending_us['total_trending']}")
            
            if trending_us.get('trending_fashion_hashtags'):
                print(f"  - 时尚趋势标签:")
                for tag in trending_us['trending_fashion_hashtags'][:10]:
                    print(f"    {tag}")
        else:
            print(f"✗ 趋势分析失败: {trending_us['error']}")
        
        return trending_us
        
    except Exception as e:
        print(f"✗ 趋势分析失败: {e}")
        logger.error(f"趋势分析示例失败: {e}")
        return None

def example_5_data_export():
    """示例5: 数据导出"""
    print("\n" + "=" * 60)
    print("示例5: 数据导出")
    print("=" * 60)
    
    try:
        config = get_config("dev")
        scraper = TikTokClothingScraper(config)
        
        # 获取最近的视频数据（最近1小时）
        print("获取最近的视频数据...")
        videos = scraper._get_recent_videos(hours=1)
        
        if videos:
            print(f"✓ 获取到 {len(videos)} 个视频")
            
            # 转换为字典列表
            video_data = []
            for video in videos:
                video_dict = {
                    'video_id': video.video_id,
                    'title': video.title,
                    'author': video.author,
                    'likes': video.likes,
                    'comments': video.comments,
                    'shares': video.shares,
                    'views': video.views,
                    'hashtags': ', '.join(video.hashtags),
                    'product_links_count': len(video.product_links),
                    'source': video.source,
                    'scraped_at': video.scraped_at
                }
                video_data.append(video_dict)
            
            # 导出为JSON
            json_file = f"exported_videos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(video_data, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON导出完成: {json_file}")
            
            # 导出为CSV
            csv_file = f"exported_videos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df = pd.DataFrame(video_data)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"✓ CSV导出完成: {csv_file}")
            
            # 显示数据预览
            print(f"\n数据预览:")
            print(df.head().to_string())
            
            return video_data
        else:
            print("⚠️  没有找到最近的视频数据")
            return None
            
    except Exception as e:
        print(f"✗ 数据导出失败: {e}")
        logger.error(f"数据导出示例失败: {e}")
        return None

def example_6_scheduled_scraping():
    """示例6: 定时抓取演示"""
    print("\n" + "=" * 60)
    print("示例6: 定时抓取演示")
    print("=" * 60)
    
    try:
        import schedule
        
        def demo_scrape_job():
            """演示抓取任务"""
            print(f"执行定时抓取任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 这里可以调用实际的抓取函数
            # results = scraper.scrape_clothing_videos()
            # print(f"抓取完成: {results['total_videos']} 个视频")
            
            print("✓ 定时任务执行完成")
        
        # 设置定时任务（每小时执行一次）
        schedule.every().hour.do(demo_scrape_job)
        
        print("✓ 定时任务已设置:")
        print("  - 任务类型: 每小时执行一次")
        print("  - 任务内容: 演示抓取流程")
        print("  - 执行次数: 演示模式下只执行1次")
        
        # 执行一次作为演示
        print("\n执行演示任务...")
        demo_scrape_job()
        
        print("\n⚠️  定时任务需要在生产环境中持续运行:")
        print("  schedule.run_pending()")
        print("  time.sleep(1)")
        
        return True
        
    except Exception as e:
        print(f"✗ 定时任务演示失败: {e}")
        logger.error(f"定时任务示例失败: {e}")
        return None

def run_all_examples():
    """运行所有示例"""
    print("🚀 TikTok热销服装数据抓取脚本 - 使用示例")
    print("基于 docs/tiktok_data_research.md 调研结果")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n")
    
    # 检查依赖
    try:
        import selenium
        import pandas as pd
        print("✓ 核心依赖检查通过")
    except ImportError as e:
        print(f"✗ 依赖检查失败: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    examples = [
        ("基础抓取流程", example_1_basic_scraping),
        ("数据验证和分析", example_2_data_validation),
        ("产品链接验证", example_3_product_link_validation),
        ("时尚趋势分析", example_4_fashion_trends),
        ("数据导出", example_5_data_export),
        ("定时抓取演示", example_6_scheduled_scraping)
    ]
    
    results = {}
    
    for name, func in examples:
        try:
            result = func()
            results[name] = result
        except Exception as e:
            print(f"✗ 示例执行失败: {name} - {e}")
            results[name] = None
        
        # 示例间隔
        time.sleep(1)
    
    # 总结
    print("\n" + "=" * 60)
    print("示例执行总结")
    print("=" * 60)
    
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)
    
    print(f"成功执行: {success_count}/{total_count} 个示例")
    
    for name, result in results.items():
        status = "✓ 成功" if result is not None else "✗ 失败"
        print(f"  {name}: {status}")
    
    print("\n🎯 后续步骤:")
    print("1. 设置真实的TikHub API密钥")
    print("2. 配置代理（如需要）")
    print("3. 根据需求调整抓取参数")
    print("4. 设置定时任务进行持续监控")
    print("5. 查看文档: README.md")
    
    print("\n📚 相关文档:")
    print("  - 调研报告: docs/tiktok_data_research.md")
    print("  - 使用说明: code/README.md")
    print("  - 配置参考: code/config.py")

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        example_name = sys.argv[1].lower()
        
        examples_map = {
            "basic": example_1_basic_scraping,
            "validation": example_2_data_validation,
            "links": example_3_product_link_validation,
            "trends": example_4_fashion_trends,
            "export": example_5_data_export,
            "scheduled": example_6_scheduled_scraping,
            "all": run_all_examples
        }
        
        if example_name in examples_map:
            examples_map[example_name]()
        else:
            print(f"未知示例: {example_name}")
            print(f"可用示例: {', '.join(examples_map.keys())}")
    else:
        # 运行所有示例
        run_all_examples()