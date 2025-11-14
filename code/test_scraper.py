#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon爬虫测试脚本
用于验证各个组件的功能
"""

import sys
import os
import json
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from amazon_scraper import AmazonScraper, ProductData, Config
from settings import load_config


def test_config():
    """测试配置加载"""
    print("=" * 40)
    print("测试配置加载")
    print("=" * 40)
    
    try:
        config = load_config()
        
        print("✅ 配置加载成功")
        print(f"基础URL: {config['base_url']}")
        print(f"数据库路径: {config['database_path']}")
        print(f"请求延迟: {config['request_delay_min']}-{config['request_delay_max']}秒")
        print(f"支持类别: {list(config['search_categories'].keys())}")
        
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


def test_scraper_initialization():
    """测试爬虫初始化"""
    print("\n" + "=" * 40)
    print("测试爬虫初始化")
    print("=" * 40)
    
    try:
        scraper = AmazonScraper()
        print("✅ 爬虫初始化成功")
        print(f"请求头: {list(scraper.headers.keys())}")
        print(f"会话状态: 已配置")
        
        return True
    except Exception as e:
        print(f"❌ 爬虫初始化失败: {e}")
        return False


def test_product_data_structure():
    """测试产品数据结构"""
    print("\n" + "=" * 40)
    print("测试产品数据结构")
    print("=" * 40)
    
    try:
        # 创建测试产品数据
        test_product = ProductData(
            asin="TEST1234567",
            title="测试印花T恤",
            price=19.99,
            original_price=29.99,
            rating=4.5,
            review_count=128,
            brand="Test Brand",
            category="print-tshirt",
            availability="有库存",
            image_url="https://example.com/image.jpg",
            detail_page_url="https://www.amazon.com/dp/TEST1234567",
            seller_name="Test Seller",
            seller_link="https://seller.example.com",
            features=["100%棉质", "舒适透气", "印花设计"],
            description="这是一个测试产品描述",
            rank=12345,
            bestseller_flag=True,
            timestamp=datetime.now().isoformat()
        )
        
        # 测试字典转换
        product_dict = test_product.to_dict()
        print("✅ 产品数据对象创建成功")
        print(f"ASIN: {test_product.asin}")
        print(f"标题: {test_product.title}")
        print(f"价格: ${test_product.price}")
        print(f"评分: {test_product.rating}/5.0")
        
        return True
    except Exception as e:
        print(f"❌ 产品数据结构测试失败: {e}")
        return False


def test_database_operations():
    """测试数据库操作"""
    print("\n" + "=" * 40)
    print("测试数据库操作")
    print("=" * 40)
    
    try:
        scraper = AmazonScraper()
        
        # 创建测试产品
        test_product = ProductData(
            asin="TEST1234567",
            title="测试印花T恤",
            price=19.99,
            original_price=29.99,
            rating=4.5,
            review_count=128,
            brand="Test Brand",
            category="print-tshirt",
            availability="有库存",
            image_url="https://example.com/image.jpg",
            detail_page_url="https://www.amazon.com/dp/TEST1234567",
            seller_name="Test Seller",
            seller_link="https://seller.example.com",
            features=["100%棉质", "舒适透气"],
            description="测试产品描述",
            rank=12345,
            bestseller_flag=True,
            timestamp=datetime.now().isoformat()
        )
        
        # 保存到数据库
        result = scraper.db_manager.save_product(test_product)
        if result:
            print("✅ 产品数据保存成功")
        else:
            print("❌ 产品数据保存失败")
            return False
        
        # 查询数据
        products = scraper.db_manager.get_products()
        print(f"数据库中产品数量: {len(products)}")
        
        # 查询特定类别
        tshirt_products = scraper.db_manager.get_products(category="print-tshirt")
        print(f"印花T恤产品数量: {len(tshirt_products)}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库操作测试失败: {e}")
        return False


def test_anti_crawler():
    """测试反爬虫功能"""
    print("\n" + "=" * 40)
    print("测试反爬虫功能")
    print("=" * 40)
    
    try:
        scraper = AmazonScraper()
        
        # 测试User-Agent生成
        user_agent = scraper.anti_crawler.get_random_user_agent()
        print(f"✅ 随机User-Agent生成成功: {user_agent[:50]}...")
        
        # 测试请求头生成
        headers = scraper.anti_crawler.get_random_headers()
        print(f"✅ 随机请求头生成成功")
        print(f"请求头数量: {len(headers)}")
        
        # 测试代理获取
        proxy = scraper.anti_crawler.get_random_proxy()
        print(f"✅ 代理获取成功: {'已配置代理' if proxy else '使用默认连接'}")
        
        return True
    except Exception as e:
        print(f"❌ 反爬虫功能测试失败: {e}")
        return False


def test_export_functionality():
    """测试导出功能"""
    print("\n" + "=" * 40)
    print("测试导出功能")
    print("=" * 40)
    
    try:
        scraper = AmazonScraper()
        
        # 创建测试数据（如果数据库为空）
        test_products = scraper.db_manager.get_products()
        if not test_products:
            print("数据库为空，跳过导出测试")
            return True
        
        # 测试JSON导出
        json_filename = "/workspace/code/test_export.json"
        result = scraper.export_data("json", json_filename)
        
        if result and os.path.exists(result):
            print(f"✅ JSON导出成功: {result}")
            
            # 验证文件内容
            with open(result, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"导出记录数量: {len(data)}")
        else:
            print("❌ JSON导出失败")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 导出功能测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("Amazon爬虫组件测试")
    print("基于调研文档要求开发")
    print(f"测试时间: {datetime.now()}")
    
    tests = [
        ("配置加载", test_config),
        ("爬虫初始化", test_scraper_initialization),
        ("产品数据结构", test_product_data_structure),
        ("数据库操作", test_database_operations),
        ("反爬虫功能", test_anti_crawler),
        ("导出功能", test_export_functionality)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n运行测试: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                failed += 1
                print(f"❌ {test_name} 失败")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 异常: {e}")
    
    # 测试总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"总测试数: {len(tests)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {passed/len(tests)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试通过！爬虫功能正常。")
    else:
        print(f"\n⚠️  {failed} 个测试失败，请检查相关功能。")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)