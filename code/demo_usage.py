#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗器使用示例
演示如何使用DataCleaner类处理TikTok和Amazon数据
"""

import json
import sys
import os

# 添加代码路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_cleaner import DataCleaner


def demo_basic_cleaning():
    """演示基础数据清洗功能"""
    print("=" * 60)
    print("基础数据清洗功能演示")
    print("=" * 60)
    
    cleaner = DataCleaner()
    
    # 模拟从Amazon抓取的原始数据
    amazon_data = {
        'title': "Nike Men's Dri-FIT <b>Premium</b> T-Shirt - 黑色/Large",
        'price': '$39.99',
        'original_price': '$49.99 Sale!',
        'category': 'Clothing, Shoes & Jewelry > Men > Shirts & Tops > T-Shirts',
        'rating': 4.5,
        'review_count': '2,847 reviews',
        'image_url': 'https://m.media-amazon.com/images/I/81-xyz123.jpg',
        'product_url': 'https://amazon.com/dp/B08N5WRWNW/ref=sr_1_1',
        'brand': 'NIKE',
        'description': "Men's Nike Dri-FIT Premium T-Shirt. The lightweight fabric keeps you dry and comfortable. Perfect for workouts or casual wear.",
        'colors': 'Black, White, Navy Blue, Gray',
        'sizes': 'Small, Medium, Large, X-Large, XX-Large',
        'source': 'amazon',
        'source_id': 'B08N5WRWNW'
    }
    
    # 模拟从TikTok抓取的原始数据
    tiktok_data = {
        'title': '时尚卫衣 灰色连帽衫 宽松版型',
        'price': '89.99美元',
        'category': '服装 > 卫衣',
        'rating': '4.2/5.0',
        'review_count': 1234,
        'product_url': 'https://www.tiktok.com/@shop/product/456?ref=sharing',
        'brand': 'Fashion Brand',
        'description': '舒适宽松的连帽卫衣，采用优质棉质材料，适合春秋季节穿着',
        'colors': '灰色, 黑色, 白色',
        'sizes': 'M, L, XL',
        'source': 'tiktok',
        'source_id': 'tt456789'
    }
    
    print("\n1. 处理Amazon数据:")
    amazon_cleaned = cleaner.clean_product_data(amazon_data)
    print(f"   - 原始标题: {amazon_data['title']}")
    print(f"   - 清洗后标题: {amazon_cleaned['title']}")
    print(f"   - 原始价格: {amazon_data['price']}")
    print(f"   - 清洗后价格: ${amazon_cleaned['price']}")
    print(f"   - 原始分类: {amazon_data['category']}")
    print(f"   - 清洗后分类: {amazon_cleaned['category']}")
    print(f"   - 关键词: {amazon_cleaned['keywords']}")
    print(f"   - Slug: {amazon_cleaned['slug']}")
    print(f"   - 热度分数: {amazon_cleaned['popularity_score']}")
    
    print("\n2. 处理TikTok数据:")
    tiktok_cleaned = cleaner.clean_product_data(tiktok_data)
    print(f"   - 原始标题: {tiktok_data['title']}")
    print(f"   - 清洗后标题: {tiktok_cleaned['title']}")
    print(f"   - 原始价格: {tiktok_data['price']}")
    print(f"   - 清洗后价格: ${tiktok_cleaned['price']}")
    print(f"   - 原始分类: {tiktok_data['category']}")
    print(f"   - 清洗后分类: {tiktok_cleaned['category']}")
    print(f"   - 颜色: {tiktok_cleaned['colors']}")
    print(f"   - 尺寸: {tiktok_cleaned['sizes']}")


def demo_batch_processing():
    """演示批量处理功能"""
    print("\n" + "=" * 60)
    print("批量数据处理功能演示")
    print("=" * 60)
    
    cleaner = DataCleaner()
    
    # 模拟批量原始数据
    batch_data = [
        # 有效的Amazon数据
        {
            'title': 'Cotton T-Shirt - Blue Medium',
            'price': '$24.99',
            'category': 'T-Shirts',
            'rating': 4.2,
            'review_count': 456,
            'product_url': 'https://amazon.com/product/1',
            'source': 'amazon',
            'source_id': 'A1'
        },
        # 有效的TikTok数据
        {
            'title': '连帽卫衣 - 黑色 L码',
            'price': '79.99',
            'category': '卫衣',
            'rating': 4.5,
            'review_count': 234,
            'product_url': 'https://tiktok.com/product/2',
            'source': 'tiktok',
            'source_id': 'T2'
        },
        # 有问题的数据（缺少必填字段）
        {
            'title': '毛衣',
            'price': '',  # 缺少价格
            'category': '毛衣',
            'source': 'tiktok',
            'source_id': 'T3'
        },
        # 重复数据（URL重复）
        {
            'title': '蓝色T恤 - 中号',
            'price': '$24.99',
            'category': 'T-Shirts',
            'product_url': 'https://amazon.com/product/1',  # 重复URL
            'source': 'amazon',
            'source_id': 'A4'
        },
        # 重复数据（相似名称）
        {
            'title': 'Cotton T-Shirt - Blue Medium Size',
            'price': '$25.99',
            'category': 'T-Shirts',
            'product_url': 'https://amazon.com/product/5',  # 不同的URL但相似的名称
            'source': 'amazon',
            'source_id': 'A5'
        }
    ]
    
    print(f"\n处理 {len(batch_data)} 条原始数据...")
    
    # 执行批量清洗
    result = cleaner.clean_batch(batch_data)
    
    print(f"\n处理结果:")
    print(f"- 原始数据量: {len(batch_data)}")
    print(f"- 清洗后数据量: {len(result['products'])}")
    print(f"- 有效数据: {len(result['valid_products'])}")
    print(f"- 无效数据: {len(result['invalid_products'])}")
    print(f"- 移除的重复数据: {len(batch_data) - len(result['products'])}")
    
    print(f"\n质量统计:")
    stats = result['quality_report']['summary']
    print(f"- 有效率: {stats['valid_rate']}%")
    print(f"- 错误率: {stats['error_rate']}%")
    print(f"- 数据质量分数: {stats['data_quality_score']}")
    
    # 显示错误分析
    if result['quality_report']['error_analysis']['total_errors'] > 0:
        print(f"\n错误分析:")
        error_types = result['quality_report']['error_analysis']['error_types']
        for error_type, count in error_types.items():
            print(f"- {error_type}: {count} 次")


def demo_data_validation():
    """演示数据验证功能"""
    print("\n" + "=" * 60)
    print("数据验证功能演示")
    print("=" * 60)
    
    cleaner = DataCleaner()
    
    # 测试各种边界情况
    test_cases = [
        {
            'name': '正常数据',
            'data': {
                'title': 'Test Product',
                'price': '$29.99',
                'category': 'T-Shirt',
                'product_url': 'https://example.com/product/1',
                'rating': 4.5
            }
        },
        {
            'name': '价格超出范围',
            'data': {
                'title': 'Expensive Product',
                'price': '$1500.00',  # 超出1000上限
                'category': 'T-Shirt',
                'product_url': 'https://example.com/product/2'
            }
        },
        {
            'name': '价格过低',
            'data': {
                'title': 'Cheap Product',
                'price': '$-5.00',  # 负价格
                'category': 'T-Shirt',
                'product_url': 'https://example.com/product/3'
            }
        },
        {
            'name': '评分超出范围',
            'data': {
                'title': 'Bad Product',
                'price': '$29.99',
                'category': 'T-Shirt',
                'product_url': 'https://example.com/product/4',
                'rating': 8.5  # 超出5.0上限
            }
        },
        {
            'name': '无效URL',
            'data': {
                'title': 'Product with Bad URL',
                'price': '$29.99',
                'category': 'T-Shirt',
                'product_url': 'not-a-valid-url'
            }
        },
        {
            'name': '缺少必填字段',
            'data': {
                'title': '',  # 空标题
                'price': '$29.99',
                'category': '',
                'product_url': ''
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        cleaned = cleaner.clean_product_data(test_case['data'])
        print(f"- 数据质量分数: {cleaned['data_quality_score']}")
        print(f"- 验证错误: {cleaned['validation_errors']}")
        print(f"- 是否有效: {'是' if not cleaned['validation_errors'] else '否'}")


def demo_export_functionality():
    """演示数据导出功能"""
    print("\n" + "=" * 60)
    print("数据导出功能演示")
    print("=" * 60)
    
    cleaner = DataCleaner()
    
    # 准备示例数据
    sample_data = {
        'title': 'Sample Product',
        'price': 29.99,
        'category': 'tshirt',
        'rating': 4.5,
        'product_url': 'https://example.com/product/1',
        'source': 'amazon'
    }
    
    # 清洗数据
    cleaned_data = cleaner.clean_product_data(sample_data)
    
    # 导出为JSON
    json_output = cleaner.export_cleaned_data(cleaned_data, 'json')
    
    print("导出的JSON数据:")
    print(json_output[:200] + "..." if len(json_output) > 200 else json_output)


def main():
    """主函数"""
    print("数据清洗器功能演示")
    print("=" * 60)
    
    try:
        # 基础清洗演示
        demo_basic_cleaning()
        
        # 批量处理演示
        demo_batch_processing()
        
        # 数据验证演示
        demo_data_validation()
        
        # 导出功能演示
        demo_export_functionality()
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()