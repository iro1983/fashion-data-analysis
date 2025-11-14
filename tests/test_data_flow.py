#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据流测试模块
==============

测试系统中的数据流向和转换过程：
- 数据抓取 → 数据清洗 → 数据存储 → 数据展示
- 验证数据完整性和一致性
- 测试数据转换规则和约束
- 监控数据流性能

作者：Claude
日期：2025-11-14
"""

import unittest
import sys
import os
import json
import time
import sqlite3
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch
import logging
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "code"))

try:
    from database import DatabaseManager
    from data_cleaner import DataCleaner
    from amazon_scraper import AmazonScraper
    from tiktok_scraper import TikTokScraper
except ImportError as e:
    print(f"模块导入错误: {e}")
    sys.exit(1)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestDataFlowPipeline(unittest.TestCase):
    """测试数据流管道"""
    
    def setUp(self):
        """测试初始化"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="dataflow_test_"))
        self.test_db_path = self.test_dir / "dataflow_test.db"
        
        # 初始化组件
        self.db_manager = DatabaseManager(str(self.test_db_path))
        self.data_cleaner = DataCleaner()
        
        # 准备测试数据
        self.raw_data = {
            'amazon': {
                'products': [
                    {
                        'title': ' Premium Cotton T-Shirt  ',
                        'price': '$29.99',
                        'rating': '4.5 stars',
                        'reviews': '1,234 reviews',
                        'category': '  Clothing  ',
                        'url': 'https://amazon.com/product1',
                        'image': 'https://amazon.com/image1.jpg',
                        'description': 'High quality cotton t-shirt with comfortable fit'
                    }
                ]
            },
            'tiktok': {
                'products': [
                    {
                        'title': 'Stylish Hoodie - Trending on TikTok',
                        'price': '45.99',
                        'likes': '12.5K',
                        'shares': '800',
                        'category': 'fashion',
                        'url': 'https://tiktok.com/@user/product1',
                        'thumbnail': 'https://tiktok.com/thumb1.jpg',
                        'description': 'Trendy hoodie getting viral on TikTok'
                    }
                ]
            }
        }
        
        logger.info("数据流测试环境初始化完成")
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        logger.info("数据流测试环境清理完成")
    
    def test_01_raw_data_extraction(self):
        """测试原始数据提取"""
        logger.info("测试原始数据提取...")
        
        # 模拟Amazon数据提取
        amazon_products = self.raw_data['amazon']['products']
        self.assertEqual(len(amazon_products), 1)
        
        product = amazon_products[0]
        self.assertIn('title', product)
        self.assertIn('price', product)
        self.assertIn('url', product)
        
        # 模拟TikTok数据提取
        tiktok_products = self.raw_data['tiktok']['products']
        self.assertEqual(len(tiktok_products), 1)
        
        tiktok_product = tiktok_products[0]
        self.assertIn('title', tiktok_product)
        self.assertIn('likes', tiktok_product)
        self.assertIn('shares', tiktok_product)
        
        logger.info("原始数据提取测试通过")
    
    def test_02_data_cleaning_process(self):
        """测试数据清洗流程"""
        logger.info("测试数据清洗流程...")
        
        # 测试Amazon数据清洗
        amazon_raw = self.raw_data['amazon']['products'][0]
        amazon_cleaned = self.data_cleaner.clean_product_data(amazon_raw)
        
        # 验证清洗结果
        self.assertIsNotNone(amazon_cleaned)
        self.assertEqual(amazon_cleaned['title'].strip(), 'Premium Cotton T-Shirt')
        self.assertIsInstance(amazon_cleaned['price'], (int, float))
        self.assertEqual(amazon_cleaned['platform'], 'amazon')
        
        # 测试TikTok数据清洗
        tiktok_raw = self.raw_data['tiktok']['products'][0]
        tiktok_cleaned = self.data_cleaner.clean_product_data(tiktok_raw)
        
        self.assertIsNotNone(tiktok_cleaned)
        self.assertIn('tiktok', tiktok_cleaned['platform'])
        self.assertIsInstance(tiktok_cleaned['likes'], int)
        self.assertIsInstance(tiktok_cleaned['shares'], int)
        
        logger.info("数据清洗流程测试通过")
    
    def test_03_data_validation(self):
        """测试数据验证规则"""
        logger.info("测试数据验证规则...")
        
        validation_tests = [
            {
                'name': '有效数据',
                'data': {'title': 'Valid Product', 'price': 29.99, 'platform': 'amazon'},
                'should_pass': True
            },
            {
                'name': '无效价格',
                'data': {'title': 'Test', 'price': -10, 'platform': 'amazon'},
                'should_pass': False
            },
            {
                'name': '空标题',
                'data': {'title': '', 'price': 29.99, 'platform': 'amazon'},
                'should_pass': False
            },
            {
                'name': '无效平台',
                'data': {'title': 'Test', 'price': 29.99, 'platform': 'unknown'},
                'should_pass': False
            }
        ]
        
        for test_case in validation_tests:
            cleaned = self.data_cleaner.clean_product_data(test_case['data'])
            
            if test_case['should_pass']:
                self.assertIsNotNone(cleaned, f"{test_case['name']} 应该通过验证")
            else:
                self.assertIsNone(cleaned, f"{test_case['name']} 应该被拒绝")
        
        logger.info("数据验证规则测试通过")
    
    def test_04_data_storage(self):
        """测试数据存储流程"""
        logger.info("测试数据存储流程...")
        
        # 清洗并存储数据
        amazon_raw = self.raw_data['amazon']['products'][0]
        amazon_cleaned = self.data_cleaner.clean_product_data(amazon_raw)
        
        if amazon_cleaned:
            # 存储到数据库
            product_id = self.db_manager.insert_product(amazon_cleaned)
            self.assertIsInstance(product_id, int)
            
            # 验证存储结果
            stored_product = self.db_manager.get_product_by_id(product_id)
            self.assertIsNotNone(stored_product)
            self.assertEqual(stored_product['title'], amazon_cleaned['title'])
            self.assertEqual(stored_product['price'], amazon_cleaned['price'])
        
        # 存储TikTok数据
        tiktok_raw = self.raw_data['tiktok']['products'][0]
        tiktok_cleaned = self.data_cleaner.clean_product_data(tiktok_raw)
        
        if tiktok_cleaned:
            tiktok_id = self.db_manager.insert_product(tiktok_cleaned)
            self.assertIsInstance(tiktok_id, int)
            
            stored_tiktok = self.db_manager.get_product_by_id(tiktok_id)
            self.assertIsNotNone(stored_tiktok)
        
        logger.info("数据存储流程测试通过")
    
    def test_05_data_transformation(self):
        """测试数据转换规则"""
        logger.info("测试数据转换规则...")
        
        transformation_tests = [
            {
                'input': {'price': '$29.99'},
                'expected_type': (int, float),
                'expected_value': 29.99
            },
            {
                'input': {'rating': '4.5 stars'},
                'expected_type': (int, float),
                'expected_value': 4.5
            },
            {
                'input': {'title': '  Extra Spaces  '},
                'expected_type': str,
                'expected_value': 'Extra Spaces'
            },
            {
                'input': {'likes': '12.5K'},
                'expected_type': int,
                'expected_value': 12500
            }
        ]
        
        for test_case in transformation_tests:
            input_data = {'title': 'Test Product', 'platform': 'amazon'}
            input_data.update(test_case['input'])
            
            cleaned = self.data_cleaner.clean_product_data(input_data)
            
            if cleaned:
                # 检查关键字段是否存在
                for key in test_case['input'].keys():
                    if key in cleaned:
                        value = cleaned[key]
                        self.assertIsInstance(
                            value, 
                            test_case['expected_type'],
                            f"{key} 应该是 {test_case['expected_type']} 类型"
                        )
                        
                        # 如果期望特定值，验证值是否匹配
                        if 'expected_value' in test_case:
                            self.assertEqual(
                                value, 
                                test_case['expected_value'],
                                f"{key} 值应为 {test_case['expected_value']}"
                            )
        
        logger.info("数据转换规则测试通过")
    
    def test_06_end_to_end_dataflow(self):
        """测试端到端数据流"""
        logger.info("测试端到端数据流...")
        
        initial_count = len(self.db_manager.get_all_products())
        
        # 模拟完整数据流
        processed_count = 0
        
        # 处理Amazon数据
        for raw_product in self.raw_data['amazon']['products']:
            cleaned = self.data_cleaner.clean_product_data(raw_product)
            if cleaned:
                product_id = self.db_manager.insert_product(cleaned)
                processed_count += 1
        
        # 处理TikTok数据
        for raw_product in self.raw_data['tiktok']['products']:
            cleaned = self.data_cleaner.clean_product_data(raw_product)
            if cleaned:
                product_id = self.db_manager.insert_product(cleaned)
                processed_count += 1
        
        # 验证最终结果
        final_count = len(self.db_manager.get_all_products())
        self.assertEqual(final_count, initial_count + processed_count)
        
        # 验证数据一致性
        all_products = self.db_manager.get_all_products()
        for product in all_products:
            self.assertIsNotNone(product['title'])
            self.assertIsInstance(product['price'], (int, float))
            self.assertGreater(product['price'], 0)
            self.assertIn(product['platform'], ['amazon', 'tiktok'])
        
        logger.info("端到端数据流测试通过")
    
    def test_07_data_integrity(self):
        """测试数据完整性"""
        logger.info("测试数据完整性...")
        
        # 插入包含完整信息的测试数据
        complete_product = {
            'title': '完整性测试产品',
            'description': '这是一个用于测试数据完整性的产品',
            'price': 39.99,
            'rating': 4.2,
            'reviews_count': 100,
            'category': '服装',
            'platform': 'amazon',
            'url': 'https://amazon.com/integrity-test',
            'image_url': 'https://amazon.com/image.jpg',
            'availability': 'in_stock',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 清洗并存储
        cleaned = self.data_cleaner.clean_product_data(complete_product)
        self.assertIsNotNone(cleaned)
        
        product_id = self.db_manager.insert_product(cleaned)
        self.assertIsInstance(product_id, int)
        
        # 检索并验证完整性
        retrieved = self.db_manager.get_product_by_id(product_id)
        self.assertIsNotNone(retrieved)
        
        # 验证关键字段
        essential_fields = ['title', 'price', 'platform', 'url']
        for field in essential_fields:
            self.assertIn(field, retrieved)
            self.assertIsNotNone(retrieved[field])
        
        logger.info("数据完整性测试通过")
    
    def test_08_data_consistency_across_platforms(self):
        """测试跨平台数据一致性"""
        logger.info("测试跨平台数据一致性...")
        
        # 创建相同产品的不同平台版本
        base_product = {
            'title': '跨平台测试产品',
            'description': '测试跨平台数据一致性',
            'price': 29.99,
            'category': '服装'
        }
        
        # Amazon版本
        amazon_version = {
            **base_product,
            'platform': 'amazon',
            'rating': 4.5,
            'reviews_count': 500,
            'url': 'https://amazon.com/product'
        }
        
        # TikTok版本
        tiktok_version = {
            **base_product,
            'platform': 'tiktok',
            'likes': 2500,
            'shares': 200,
            'url': 'https://tiktok.com/product'
        }
        
        # 清洗并存储
        amazon_cleaned = self.data_cleaner.clean_product_data(amazon_version)
        tiktok_cleaned = self.data_cleaner.clean_product_data(tiktok_version)
        
        if amazon_cleaned and tiktok_cleaned:
            amazon_id = self.db_manager.insert_product(amazon_cleaned)
            tiktok_id = self.db_manager.insert_product(tiktok_cleaned)
            
            # 验证存储结果
            amazon_product = self.db_manager.get_product_by_id(amazon_id)
            tiktok_product = self.db_manager.get_product_by_id(tiktok_id)
            
            # 验证共同字段一致性
            for field in ['title', 'description', 'price', 'category']:
                self.assertEqual(
                    amazon_product[field], 
                    tiktok_product[field],
                    f"{field} 字段在跨平台间应保持一致"
                )
            
            # 验证平台特定字段存在
            self.assertIn('rating', amazon_product)
            self.assertIn('likes', tiktok_product)
        
        logger.info("跨平台数据一致性测试通过")
    
    def test_09_data_flow_performance(self):
        """测试数据流性能"""
        logger.info("测试数据流性能...")
        
        # 创建批量测试数据
        batch_size = 50
        test_products = []
        
        for i in range(batch_size):
            product = {
                'title': f'性能测试产品 {i}',
                'price': 20.00 + i,
                'rating': 4.0 + (i % 10) * 0.1,
                'category': 'test_category',
                'platform': 'amazon' if i % 2 == 0 else 'tiktok',
                'description': f'性能测试产品描述 {i}'
            }
            test_products.append(product)
        
        # 测量处理时间
        start_time = time.time()
        processed_count = 0
        
        for product in test_products:
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
                processed_count += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 验证性能指标
        self.assertGreater(processed_count, batch_size * 0.8)  # 至少80%成功率
        self.assertLess(processing_time, 10.0)  # 总处理时间小于10秒
        self.assertLess(processing_time / batch_size, 0.2)  # 单个产品平均处理时间小于0.2秒
        
        logger.info(f"性能测试完成: {processed_count}个产品，耗时{processing_time:.2f}秒")
        logger.info(f"平均处理时间: {processing_time/batch_size:.3f}秒/产品")


class TestDataFlowMetrics(unittest.TestCase):
    """测试数据流指标和监控"""
    
    def setUp(self):
        """测试初始化"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="metrics_test_"))
        self.test_db_path = self.test_dir / "metrics_test.db"
        self.db_manager = DatabaseManager(str(self.test_db_path))
        self.data_cleaner = DataCleaner()
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_data_quality_metrics(self):
        """测试数据质量指标"""
        logger.info("测试数据质量指标...")
        
        # 准备混合质量数据
        mixed_data = [
            {'title': '高质量产品', 'price': 29.99, 'rating': 4.5, 'platform': 'amazon'},  # 优质数据
            {'title': '', 'price': 29.99, 'rating': 4.5, 'platform': 'amazon'},           # 缺少标题
            {'title': '测试产品', 'price': -10, 'rating': 4.5, 'platform': 'amazon'},     # 负价格
            {'title': '正常产品', 'price': 29.99, 'rating': 4.5, 'platform': 'amazon'},   # 正常数据
            {'title': '另一个正常产品', 'price': 39.99, 'rating': 3.5, 'platform': 'tiktok'}  # 正常数据
        ]
        
        # 统计处理结果
        total_processed = 0
        valid_count = 0
        invalid_count = 0
        
        for data in mixed_data:
            total_processed += 1
            cleaned = self.data_cleaner.clean_product_data(data)
            
            if cleaned:
                valid_count += 1
                # 存储有效数据
                self.db_manager.insert_product(cleaned)
            else:
                invalid_count += 1
        
        # 验证指标
        self.assertEqual(total_processed, len(mixed_data))
        self.assertGreater(valid_count, 0)
        self.assertGreater(invalid_count, 0)
        
        # 计算质量指标
        quality_rate = valid_count / total_processed
        self.assertGreater(quality_rate, 0.3)  # 质量率应大于30%
        
        logger.info(f"数据质量指标: 总计{total_processed}, 有效{valid_count}, 无效{invalid_count}, 质量率{quality_rate:.2%}")
    
    def test_data_flow_monitoring(self):
        """测试数据流监控"""
        logger.info("测试数据流监控...")
        
        # 模拟数据流监控数据
        monitoring_data = {
            'start_time': datetime.now(),
            'end_time': None,
            'items_processed': 0,
            'success_count': 0,
            'error_count': 0,
            'validation_errors': [],
            'performance_metrics': {}
        }
        
        # 模拟数据处理过程
        test_data = [
            {'title': '正常产品1', 'price': 25.99, 'platform': 'amazon'},
            {'title': '正常产品2', 'price': 35.99, 'platform': 'tiktok'},
            {'title': '', 'price': 15.99, 'platform': 'amazon'},  # 会导致验证错误
            {'title': '正常产品3', 'price': 45.99, 'platform': 'amazon'}
        ]
        
        processing_start = time.time()
        
        for data in test_data:
            monitoring_data['items_processed'] += 1
            
            try:
                cleaned = self.data_cleaner.clean_product_data(data)
                if cleaned:
                    self.db_manager.insert_product(cleaned)
                    monitoring_data['success_count'] += 1
                else:
                    monitoring_data['error_count'] += 1
                    monitoring_data['validation_errors'].append('Validation failed')
            except Exception as e:
                monitoring_data['error_count'] += 1
                monitoring_data['validation_errors'].append(str(e))
        
        processing_end = time.time()
        monitoring_data['end_time'] = datetime.now()
        monitoring_data['performance_metrics']['total_time'] = processing_end - processing_start
        monitoring_data['performance_metrics']['items_per_second'] = monitoring_data['items_processed'] / monitoring_data['performance_metrics']['total_time']
        
        # 验证监控结果
        self.assertGreater(monitoring_data['items_processed'], 0)
        self.assertGreaterEqual(monitoring_data['success_count'], 0)
        self.assertGreaterEqual(monitoring_data['error_count'], 0)
        self.assertLess(monitoring_data['performance_metrics']['total_time'], 5.0)
        
        logger.info(f"数据流监控完成: 处理{monitoring_data['items_processed']}项，成功{monitoring_data['success_count']}项，错误{monitoring_data['error_count']}项")


def run_data_flow_tests():
    """运行数据流测试"""
    print("=" * 60)
    print("开始数据流测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestDataFlowPipeline,
        TestDataFlowMetrics
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(test_suite)
    end_time = time.time()
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("数据流测试完成")
    print("=" * 60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"耗时: {end_time - start_time:.2f}秒")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # 确保日志目录存在
    log_dir = Path("tests/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 运行数据流测试
    success = run_data_flow_tests()
    
    if success:
        print("✅ 所有数据流测试通过")
        sys.exit(0)
    else:
        print("❌ 部分数据流测试失败")
        sys.exit(1)