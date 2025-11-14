#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理系统简单使用示例

演示基本的数据库操作
"""

from database import DatabaseManager, DatabaseConfig
import random


def simple_example():
    """简单示例：演示基本操作"""
    print("=" * 50)
    print("数据库管理系统简单示例")
    print("=" * 50)
    
    # 1. 配置数据库
    config = DatabaseConfig(
        db_path="example_data/products.db",
        backup_dir="example_data/backup"
    )
    
    # 2. 初始化数据库管理器
    db = DatabaseManager(config)
    print("✓ 数据库已初始化")
    
    try:
        # 3. 创建示例产品
        print("\n3. 创建示例产品...")
        product = {
            'product_name': '时尚印花T恤',
            'platform': 'tiktok',
            'category': 'tshirt',
            'price': 29.99,
            'original_price': 39.99,
            'currency': 'USD',
            'sales_count': 1500,
            'rating': 4.5,
            'review_count': 250,
            'product_url': 'https://tiktok.com/product/example',
            'store_url': 'https://tiktok.com/store/fashion_shop',
            'store_name': '时尚店铺',
            'main_image_url': 'https://cdn.example.com/tshirt.jpg',
            'like_count': 800,
            'share_count': 150,
            'comment_count': 45,
            'view_count': 5000,
            'data_source': 'web_scraper',
            'keywords': ['时尚', '印花', 'T恤'],
            'notes': '热销产品'
        }
        
        product_id = db.insert_product(product)
        print(f"✓ 产品已创建，ID: {product_id}")
        
        # 4. 添加评论
        print("\n4. 添加产品评论...")
        comments = [
            {
                'comment_text': '这个T恤质量很好，穿着很舒服！',
                'comment_author': '用户1',
                'author_followers': 1200,
                'likes_count': 50,
                'replies_count': 5
            },
            {
                'comment_text': '印花很清晰，颜色也很正',
                'comment_author': '用户2',
                'author_followers': 800,
                'likes_count': 35,
                'replies_count': 3
            }
        ]
        
        for comment in comments:
            db.insert_hot_comment(product_id, comment)
        print(f"✓ 已添加 {len(comments)} 条评论")
        
        # 5. 价格历史记录
        print("\n5. 价格历史记录...")
        price_updates = [
            (32.99, 39.99),
            (29.99, 39.99),
            (27.99, 35.99)
        ]
        
        for price, original_price in price_updates:
            db.update_product_price(product_id, price, original_price)
        print(f"✓ 已记录 {len(price_updates)} 次价格变化")
        
        # 6. 查询产品
        print("\n6. 查询产品信息...")
        products = db.get_products(platform='tiktok', limit=5)
        if products:
            product = products[0]
            print(f"产品名称: {product['product_name']}")
            print(f"平台: {product['platform']}")
            print(f"当前价格: ${product['price']}")
            print(f"评分: {product['rating']}/5")
            print(f"销量: {product['sales_count']}")
        
        # 7. 获取评论
        print("\n7. 获取热门评论...")
        comments = db.get_hot_comments(product_id, limit=10)
        print(f"共 {len(comments)} 条评论:")
        for i, comment in enumerate(comments[:3], 1):
            print(f"{i}. {comment['comment_text'][:30]}... (点赞: {comment['likes_count']})")
        
        # 8. 价格历史
        print("\n8. 价格历史...")
        price_history = db.get_price_history(product_id, days=30)
        print(f"共 {len(price_history)} 条价格记录:")
        for record in price_history[:3]:
            print(f"  {record['recorded_at']}: ${record['price']}")
        
        # 9. 记录日志
        print("\n9. 记录爬取任务...")
        log_data = {
            'platform': 'tiktok',
            'category': 'tshirt',
            'task_type': 'full_scrape',
            'status': 'success',
            'records_found': 100,
            'records_saved': 95,
            'user_agent': 'Mozilla/5.0 Example Bot'
        }
        
        log_id = db.insert_scrape_log(log_data)
        print(f"✓ 日志已记录，ID: {log_id}")
        
        # 10. 获取统计信息
        print("\n10. 数据库统计...")
        stats = db.get_database_stats()
        print("统计信息:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 11. 创建备份
        print("\n11. 创建备份...")
        backup_path = db.create_backup("example_backup.db")
        print(f"✓ 备份已创建: {backup_path}")
        
        print("\n" + "=" * 50)
        print("示例运行完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    
    finally:
        # 关闭数据库
        db.close()
        print("\n✓ 数据库连接已关闭")


def query_examples():
    """查询示例"""
    print("\n" + "=" * 50)
    print("查询示例")
    print("=" * 50)
    
    config = DatabaseConfig(db_path="example_data/products.db")
    db = DatabaseManager(config)
    
    try:
        # 查询不同平台的产品
        print("\n1. 按平台查询:")
        tiktok_products = db.get_products(platform='tiktok', limit=5)
        amazon_products = db.get_products(platform='amazon', limit=5)
        print(f"  TikTok产品: {len(tiktok_products)} 个")
        print(f"  Amazon产品: {len(amazon_products)} 个")
        
        # 查询不同分类的产品
        print("\n2. 按分类查询:")
        tshirt_products = db.get_products(category='tshirt', limit=5)
        hoodie_products = db.get_products(category='hoodie', limit=5)
        print(f"  T恤产品: {len(tshirt_products)} 个")
        print(f"  卫衣产品: {len(hoodie_products)} 个")
        
        # 获取所有活跃产品
        print("\n3. 所有活跃产品:")
        all_products = db.get_products(limit=100)
        print(f"  总数: {len(all_products)} 个")
        
        # 显示产品详情
        if all_products:
            print("\n4. 产品详情示例:")
            product = all_products[0]
            print(f"  产品名: {product['product_name']}")
            print(f"  价格: ${product['price']}")
            print(f"  评分: {product['rating']}/5")
            print(f"  销量: {product['sales_count']}")
            print(f"  评论数: {product['review_count']}")
        
    finally:
        db.close()


if __name__ == "__main__":
    # 运行简单示例
    simple_example()
    
    # 运行查询示例
    query_examples()
    
    print("\n所有示例完成！")