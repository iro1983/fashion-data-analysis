#!/usr/bin/env python3
"""
SQLite到JSON数据导出脚本
将SQLite数据库中的数据导出为JSON格式，供前端使用
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

def export_data(db_path, output_dir):
    """导出数据库数据到JSON文件"""
    
    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print(f"正在导出数据库: {db_path}")
        
        # 1. 导出产品数据
        print("导出产品数据...")
        cursor.execute("""
            SELECT * FROM products 
            WHERE is_active = 1
            ORDER BY last_updated_at DESC
        """)
        products = []
        for row in cursor.fetchall():
            product = dict(row)
            # 处理JSON字段
            if product.get('image_urls'):
                try:
                    product['image_urls'] = json.loads(product['image_urls'])
                except:
                    product['image_urls'] = []
            if product.get('keywords'):
                try:
                    product['keywords'] = json.loads(product['keywords'])
                except:
                    product['keywords'] = []
            products.append(product)
        
        with open(output_path / "products.json", "w", encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2, default=str)
        
        # 2. 导出平台统计
        print("导出平台统计...")
        cursor.execute("""
            SELECT platform, category, 
                   COUNT(*) as count,
                   ROUND(AVG(price), 2) as avg_price,
                   ROUND(AVG(rating), 1) as avg_rating,
                   SUM(sales_count) as total_sales
            FROM products 
            WHERE is_active = 1
            GROUP BY platform, category
            ORDER BY platform, category
        """)
        platform_stats = [dict(row) for row in cursor.fetchall()]
        
        with open(output_path / "platform_stats.json", "w", encoding='utf-8') as f:
            json.dump(platform_stats, f, ensure_ascii=False, indent=2)
        
        # 3. 导出热门产品排行
        print("导出热门产品...")
        cursor.execute("""
            SELECT id, product_name, platform, category, price, original_price,
                   sales_count, rating, review_count, main_image_url, store_name,
                   like_count, share_count
            FROM products 
            WHERE is_active = 1
            ORDER BY (sales_count * 0.6 + rating * 0.4) DESC
            LIMIT 50
        """)
        top_products = [dict(row) for row in cursor.fetchall()]
        
        with open(output_path / "top_products.json", "w", encoding='utf-8') as f:
            json.dump(top_products, f, ensure_ascii=False, indent=2, default=str)
        
        # 4. 导出价格历史趋势
        print("导出价格趋势...")
        cursor.execute("""
            SELECT DATE(ph.recorded_at) as date,
                   ROUND(AVG(ph.price), 2) as avg_price,
                   COUNT(ph.id) as product_count,
                   ROUND(AVG(ph.discount_percent), 1) as avg_discount
            FROM price_history ph
            WHERE ph.recorded_at >= date('now', '-30 days')
            GROUP BY DATE(ph.recorded_at)
            ORDER BY date ASC
        """)
        price_trends = [dict(row) for row in cursor.fetchall()]
        
        with open(output_path / "price_trends.json", "w", encoding='utf-8') as f:
            json.dump(price_trends, f, ensure_ascii=False, indent=2)
        
        # 5. 导出数据库统计信息
        print("导出数据库统计...")
        stats = {}
        
        # 产品总数
        cursor.execute("SELECT COUNT(*) FROM products")
        stats['total_products'] = cursor.fetchone()[0]
        
        # 活跃产品数
        cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
        stats['active_products'] = cursor.fetchone()[0]
        
        # 今日新增
        cursor.execute("SELECT COUNT(*) FROM products WHERE DATE(first_seen_at) = DATE('now')")
        stats['today_new_products'] = cursor.fetchone()[0]
        
        # 平台分布
        cursor.execute("""
            SELECT platform, COUNT(*) as count
            FROM products WHERE is_active = 1
            GROUP BY platform
        """)
        stats['platform_distribution'] = [dict(row) for row in cursor.fetchall()]
        
        # 分类分布
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM products WHERE is_active = 1
            GROUP BY category
        """)
        stats['category_distribution'] = [dict(row) for row in cursor.fetchall()]
        
        # 数据库大小
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        stats['database_size_mb'] = round((page_count * page_size) / 1024 / 1024, 2)
        
        with open(output_path / "database_stats.json", "w", encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        # 6. 导出热门评论
        print("导出热门评论...")
        cursor.execute("""
            SELECT hc.*, p.product_name, p.platform
            FROM hot_comments hc
            JOIN products p ON hc.product_id = p.id
            WHERE p.is_active = 1
            ORDER BY hc.likes_count DESC
            LIMIT 100
        """)
        hot_comments = [dict(row) for row in cursor.fetchall()]
        
        with open(output_path / "hot_comments.json", "w", encoding='utf-8') as f:
            json.dump(hot_comments, f, ensure_ascii=False, indent=2, default=str)
        
        conn.close()
        
        print(f"数据导出完成！文件保存在: {output_path}")
        print(f"导出的文件:")
        print(f"- products.json: {len(products)} 个产品")
        print(f"- platform_stats.json: 平台统计")
        print(f"- top_products.json: {len(top_products)} 个热门产品")
        print(f"- price_trends.json: 价格趋势数据")
        print(f"- database_stats.json: 数据库统计")
        print(f"- hot_comments.json: {len(hot_comments)} 条热门评论")
        
        return True
        
    except Exception as e:
        print(f"导出失败: {e}")
        return False

if __name__ == "__main__":
    # 默认路径
    db_path = "/workspace/code/amazon_products.db"
    output_dir = "/workspace/fashion-dashboard/public/data"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # 执行导出
    export_data(db_path, output_dir)
