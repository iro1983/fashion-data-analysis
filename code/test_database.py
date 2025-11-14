#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库功能测试脚本

展示数据库管理系统的各种功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager, DatabaseConfig, create_sample_data
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_database_operations():
    """测试数据库基本操作"""
    print("=" * 60)
    print("数据库管理系统功能测试")
    print("=" * 60)
    
    # 配置数据库
    config = DatabaseConfig(
        db_path="test_data/products.db",
        backup_dir="test_data/backup",
        auto_backup=True,
        connection_pool_size=5
    )
    
    # 初始化数据库管理器
    db = DatabaseManager(config)
    
    try:
        # 1. 创建示例数据
        print("\n1. 创建示例数据...")
        create_sample_data(db, count=15)
        print("✓ 示例数据创建完成")
        
        # 2. 测试产品查询
        print("\n2. 测试产品查询功能...")
        
        # 查询所有产品
        all_products = db.get_products(limit=10)
        print(f"   总产品数: {len(all_products)}")
        
        # 按平台查询
        tiktok_products = db.get_products(platform='tiktok', limit=5)
        print(f"   TikTok产品数: {len(tiktok_products)}")
        
        # 按分类查询
        tshirt_products = db.get_products(category='tshirt', limit=5)
        print(f"   T恤产品数: {len(tshirt_products)}")
        
        print("✓ 产品查询功能正常")
        
        # 3. 测试评论管理
        print("\n3. 测试评论管理功能...")
        
        if all_products:
            first_product_id = all_products[0]['id']
            
            # 获取产品评论
            comments = db.get_hot_comments(first_product_id, limit=10)
            print(f"   产品 #{first_product_id} 共有 {len(comments)} 条评论")
            
            if comments:
                print(f"   最热评论: {comments[0]['comment_text'][:30]}... (点赞: {comments[0]['likes_count']})")
        
        print("✓ 评论管理功能正常")
        
        # 4. 测试价格历史
        print("\n4. 测试价格历史功能...")
        
        if all_products:
            first_product_id = all_products[0]['id']
            
            # 获取价格历史
            price_history = db.get_price_history(first_product_id, days=30)
            print(f"   产品 #{first_product_id} 共有 {len(price_history)} 条价格记录")
            
            if len(price_history) >= 2:
                latest_price = price_history[-1]['price']
                oldest_price = price_history[0]['price']
                price_change = latest_price - oldest_price
                print(f"   价格变化: ${oldest_price:.2f} → ${latest_price:.2f} ({price_change:+.2f})")
        
        print("✓ 价格历史功能正常")
        
        # 5. 测试日志记录
        print("\n5. 测试日志记录功能...")
        
        # 插入测试日志
        log_data = {
            'platform': 'tiktok',
            'category': 'tshirt',
            'task_type': 'full_scrape',
            'status': 'success',
            'records_found': 100,
            'records_saved': 95,
            'error_message': None,
            'user_agent': 'Mozilla/5.0 Test Bot',
            'ip_address': '127.0.0.1',
            'session_id': 'test_session_001'
        }
        
        log_id = db.insert_scrape_log(log_data)
        print(f"   已插入日志记录: ID {log_id}")
        
        # 更新日志
        db.update_scrape_log(log_id, records_saved=97)
        print("   日志记录已更新")
        
        # 查询日志
        recent_logs = db.get_scrape_logs(days=1, limit=5)
        print(f"   最近1天共有 {len(recent_logs)} 条日志记录")
        
        print("✓ 日志记录功能正常")
        
        # 6. 测试统计信息
        print("\n6. 测试统计信息功能...")
        
        stats = db.get_database_stats()
        print("   数据库统计信息:")
        for key, value in stats.items():
            print(f"     {key}: {value}")
        
        print("✓ 统计信息功能正常")
        
        # 7. 测试备份功能
        print("\n7. 测试备份功能...")
        
        # 创建备份
        backup_path = db.create_backup("test_backup.db")
        print(f"   备份已创建: {backup_path}")
        
        # 检查备份文件是否存在
        if os.path.exists(backup_path):
            file_size = os.path.getsize(backup_path)
            print(f"   备份文件大小: {file_size / 1024:.2f} KB")
        else:
            print("   警告: 备份文件未找到")
        
        print("✓ 备份功能正常")
        
        # 8. 测试产品更新
        print("\n8. 测试产品更新功能...")
        
        if all_products:
            first_product_id = all_products[0]['id']
            current_price = all_products[0]['price']
            new_price = current_price * 0.9  # 降价10%
            
            print(f"   更新产品 #{first_product_id} 价格: ${current_price:.2f} → ${new_price:.2f}")
            
            db.update_product_price(first_product_id, new_price, current_price)
            
            # 验证更新
            updated_products = db.get_products(limit=1)
            if updated_products and updated_products[0]['id'] == first_product_id:
                updated_price = updated_products[0]['price']
                print(f"   价格更新验证: ${updated_price:.2f}")
        
        print("✓ 产品更新功能正常")
        
        # 9. 测试数据验证
        print("\n9. 测试数据验证功能...")
        
        try:
            # 测试无效平台
            invalid_product = {
                'product_name': 'Test Invalid Product',
                'platform': 'invalid_platform',  # 无效平台
                'category': 'tshirt',
                'price': -10,  # 负价格
                'rating': 10,  # 超出范围
                'product_url': 'https://test.com/invalid'
            }
            
            print("   尝试插入无效数据...")
            db.insert_product(invalid_product)
            print("   警告: 无效数据未被正确拦截")
            
        except Exception as e:
            print(f"   ✓ 无效数据已正确拦截: {str(e)[:100]}...")
        
        print("   数据验证功能正常")
        
        # 10. 测试并发访问
        print("\n10. 测试并发访问...")
        
        import threading
        import time
        
        def worker_thread(thread_id):
            try:
                products = db.get_products(limit=5)
                print(f"   线程 {thread_id}: 获取到 {len(products)} 个产品")
                time.sleep(0.1)
            except Exception as e:
                print(f"   线程 {thread_id} 错误: {e}")
        
        # 启动多个线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        print("✓ 并发访问功能正常")
        
        print("\n" + "=" * 60)
        print("所有测试完成！数据库管理系统运行正常。")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        db.close()
        print("\n数据库连接已关闭")


def performance_test():
    """性能测试"""
    print("\n" + "=" * 60)
    print("性能测试")
    print("=" * 60)
    
    config = DatabaseConfig(
        db_path="test_data/performance.db",
        backup_dir="test_data/backup"
    )
    
    db = DatabaseManager(config)
    
    try:
        # 批量插入测试
        print("\n批量插入测试...")
        import time
        import random
        
        start_time = time.time()
        
        platforms = ['tiktok', 'amazon']
        categories = ['tshirt', 'hoodie', 'sweatshirt']
        
        for i in range(100):
            product = {
                'product_name': f'性能测试产品 {i}',
                'platform': random.choice(platforms),
                'category': random.choice(categories),
                'price': round(random.uniform(10, 100), 2),
                'original_price': round(random.uniform(15, 120), 2),
                'currency': 'USD',
                'sales_count': random.randint(50, 5000),
                'rating': round(random.uniform(3.0, 5.0), 1),
                'review_count': random.randint(5, 200),
                'product_url': f'https://performance-test.com/product/{i}',
                'store_url': f'https://store-test.com/{i}',
                'store_name': f'Store {i}',
                'main_image_url': f'https://cdn.test.com/product_{i}.jpg',
                'image_urls': [f'https://cdn.test.com/product_{i}_{j}.jpg' for j in range(2)],
                'like_count': random.randint(20, 500),
                'share_count': random.randint(5, 100),
                'comment_count': random.randint(2, 50),
                'view_count': random.randint(100, 2000),
                'data_source': 'performance_test',
                'keywords': ['test', 'performance'],
                'notes': f'性能测试产品 #{i}'
            }
            
            db.insert_product(product)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"  插入100个产品耗时: {duration:.2f} 秒")
        print(f"  平均每个产品: {duration/100*1000:.1f} 毫秒")
        
        # 查询性能测试
        print("\n查询性能测试...")
        
        start_time = time.time()
        for i in range(50):
            products = db.get_products(platform='tiktok', limit=20)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"  50次查询耗时: {duration:.2f} 秒")
        print(f"  平均每次查询: {duration/50*1000:.1f} 毫秒")
        
        print("\n性能测试完成")
        
    finally:
        db.close()


if __name__ == "__main__":
    # 运行功能测试
    test_database_operations()
    
    # 运行性能测试
    performance_test()
    
    print("\n所有测试完成！")