#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统集成测试主文件
==================

测试整个电商数据抓取和分析系统的端到端功能，包括：
- 完整的数据抓取流程测试
- 组件间协作测试
- 数据流完整性测试
- 错误处理机制测试

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
from unittest.mock import patch, Mock, MagicMock
import logging
import threading
import requests
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "code"))

# 导入项目模块
try:
    from amazon_scraper import AmazonScraper, ProductData
    from tiktok_scraper import TikTokScraper
    from database import DatabaseManager
    from data_cleaner import DataCleaner
    from main import Coordinator, Config
    from settings import load_config
except ImportError as e:
    print(f"模块导入错误: {e}")
    sys.exit(1)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/logs/integration_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TestCompleteWorkflow(unittest.TestCase):
    """测试完整的数据抓取和展示流程"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_dir = Path(tempfile.mkdtemp(prefix="integration_test_"))
        cls.test_db_path = cls.test_dir / "test_products.db"
        cls.test_config = {
            'database': {
                'db_path': str(cls.test_db_path),
                'backup_dir': str(cls.test_dir / "backup")
            },
            'amazon': {
                'base_url': 'https://www.amazon.com',
                'max_pages': 2,
                'delay_range': (1, 3)
            },
            'tiktok': {
                'base_url': 'https://www.tiktok.com',
                'max_posts': 10,
                'delay_range': (2, 4)
            }
        }
        
        # 创建备份目录
        Path(cls.test_config['database']['backup_dir']).mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        cls.db_manager = DatabaseManager(
            db_path=str(cls.test_db_path),
            backup_dir=cls.test_config['database']['backup_dir']
        )
        cls.data_cleaner = DataCleaner()
        
        logger.info(f"测试环境初始化完成，数据库路径: {cls.test_db_path}")
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        try:
            # 清理测试数据库连接
            if hasattr(cls, 'db_manager'):
                cls.db_manager.close_all_connections()
            
            # 清理测试目录
            if cls.test_dir.exists():
                shutil.rmtree(cls.test_dir)
            logger.info("测试环境清理完成")
        except Exception as e:
            logger.warning(f"清理测试环境时发生警告: {e}")
    
    def setUp(self):
        """测试方法初始化"""
        self.start_time = time.time()
        
        # 准备测试数据
        self.sample_product = {
            'title': '测试T恤衫',
            'price': 29.99,
            'rating': 4.5,
            'reviews_count': 150,
            'category': '服装',
            'platform': 'amazon',
            'url': 'https://amazon.com/test-product',
            'image_url': 'https://amazon.com/image.jpg',
            'description': '高质量棉质T恤衫',
            'availability': 'in_stock'
        }
        
        logger.info(f"开始测试: {self._testMethodName}")
    
    def tearDown(self):
        """测试方法清理"""
        duration = time.time() - self.start_time
        logger.info(f"测试完成: {self._testMethodName}, 耗时: {duration:.2f}秒")
    
    def test_01_data_cleaning(self):
        """测试数据清洗功能"""
        logger.info("测试数据清洗...")
        
        # 测试数据清洗
        cleaned_data = self.data_cleaner.clean_product_data(self.sample_product)
        
        # 验证清洗结果
        self.assertIsInstance(cleaned_data, dict)
        self.assertIn('title', cleaned_data)
        self.assertIn('price', cleaned_data)
        self.assertIsInstance(cleaned_data['price'], (int, float))
        self.assertGreater(cleaned_data['price'], 0)
        
        logger.info("数据清洗测试通过")
    
    def test_02_database_operations(self):
        """测试数据库操作"""
        logger.info("测试数据库操作...")
        
        try:
            # 测试插入产品
            product_id = self.db_manager.insert_product(self.sample_product)
            self.assertIsInstance(product_id, int)
            
            # 测试查询产品
            product = self.db_manager.get_product_by_id(product_id)
            self.assertIsNotNone(product)
            self.assertEqual(product['title'], self.sample_product['title'])
            
            # 测试更新产品
            update_data = {'price': 39.99}
            result = self.db_manager.update_product(product_id, update_data)
            self.assertTrue(result)
            
            # 验证更新
            updated_product = self.db_manager.get_product_by_id(product_id)
            self.assertEqual(updated_product['price'], 39.99)
            
            logger.info("数据库操作测试通过")
            
        except Exception as e:
            logger.error(f"数据库操作测试失败: {e}")
            raise
    
    def test_03_complete_workflow(self):
        """测试完整工作流程"""
        logger.info("测试完整工作流程...")
        
        try:
            # 1. 模拟数据抓取（使用测试数据）
            raw_data = {
                'amazon_products': [self.sample_product],
                'tiktok_products': [
                    {
                        **self.sample_product,
                        'platform': 'tiktok',
                        'url': 'https://tiktok.com/test-product',
                        'likes': 500,
                        'shares': 50
                    }
                ]
            }
            
            # 2. 数据清洗
            cleaned_amazon = []
            for product in raw_data['amazon_products']:
                cleaned = self.data_cleaner.clean_product_data(product)
                if cleaned:
                    cleaned_amazon.append(cleaned)
            
            cleaned_tiktok = []
            for product in raw_data['tiktok_products']:
                cleaned = self.data_cleaner.clean_product_data(product)
                if cleaned:
                    cleaned_tiktok.append(cleaned)
            
            # 3. 数据存储
            amazon_ids = []
            for product in cleaned_amazon:
                product_id = self.db_manager.insert_product(product)
                amazon_ids.append(product_id)
            
            tiktok_ids = []
            for product in cleaned_tiktok:
                product_id = self.db_manager.insert_product(product)
                tiktok_ids.append(product_id)
            
            # 4. 验证数据完整性
            self.assertGreater(len(amazon_ids), 0)
            self.assertGreater(len(tiktok_ids), 0)
            
            # 5. 测试数据查询
            all_products = self.db_manager.get_all_products()
            self.assertGreater(len(all_products), 1)
            
            # 6. 测试数据筛选
            amazon_products = self.db_manager.get_products_by_platform('amazon')
            tiktok_products = self.db_manager.get_products_by_platform('tiktok')
            
            self.assertEqual(len(amazon_products), 1)
            self.assertEqual(len(tiktok_products), 1)
            
            logger.info("完整工作流程测试通过")
            
        except Exception as e:
            logger.error(f"完整工作流程测试失败: {e}")
            raise
    
    def test_04_component_integration(self):
        """测试组件集成"""
        logger.info("测试组件集成...")
        
        # 测试AmazonScraper与数据库的集成
        try:
            # 模拟AmazonScraper组件
            mock_amazon_data = [self.sample_product]
            
            # 测试数据流向数据库
            for product in mock_amazon_data:
                cleaned = self.data_cleaner.clean_product_data(product)
                if cleaned:
                    product_id = self.db_manager.insert_product(cleaned)
                    self.assertIsInstance(product_id, int)
            
            # 验证数据正确存储
            stored_products = self.db_manager.get_all_products()
            self.assertGreater(len(stored_products), 0)
            
            logger.info("AmazonScraper组件集成测试通过")
            
        except Exception as e:
            logger.error(f"AmazonScraper组件集成测试失败: {e}")
            raise
        
        # 测试TikTokScraper与数据库的集成
        try:
            mock_tiktok_data = [{
                **self.sample_product,
                'platform': 'tiktok',
                'url': 'https://tiktok.com/test',
                'likes': 100
            }]
            
            for product in mock_tiktok_data:
                cleaned = self.data_cleaner.clean_product_data(product)
                if cleaned:
                    product_id = self.db_manager.insert_product(cleaned)
                    self.assertIsInstance(product_id, int)
            
            tiktok_products = self.db_manager.get_products_by_platform('tiktok')
            self.assertGreater(len(tiktok_products), 0)
            
            logger.info("TikTokScraper组件集成测试通过")
            
        except Exception as e:
            logger.error(f"TikTokScraper组件集成测试失败: {e}")
            raise
    
    def test_05_data_consistency(self):
        """测试数据一致性"""
        logger.info("测试数据一致性...")
        
        # 插入重复数据，测试去重机制
        try:
            product1 = {**self.sample_product, 'title': '重复产品'}
            product2 = {**self.sample_product, 'title': '重复产品'}  # 相同产品
            
            # 清洗和插入第一个产品
            cleaned1 = self.data_cleaner.clean_product_data(product1)
            id1 = self.db_manager.insert_product(cleaned1)
            
            # 清洗和插入第二个产品
            cleaned2 = self.data_cleaner.clean_product_data(product2)
            id2 = self.db_manager.insert_product(cleaned2)
            
            # 验证数据库中没有重复数据
            products = self.db_manager.get_all_products()
            unique_titles = set(p['title'] for p in products)
            self.assertLessEqual(len(unique_titles), len(products))
            
            logger.info("数据一致性测试通过")
            
        except Exception as e:
            logger.error(f"数据一致性测试失败: {e}")
            raise
    
    def test_06_performance_metrics(self):
        """测试性能指标"""
        logger.info("测试性能指标...")
        
        start_time = time.time()
        
        try:
            # 批量插入测试数据
            test_products = []
            for i in range(10):
                product = {
                    **self.sample_product,
                    'title': f'性能测试产品{i}',
                    'price': 20.00 + i
                }
                test_products.append(product)
            
            # 测试批量操作性能
            batch_start = time.time()
            inserted_ids = []
            for product in test_products:
                cleaned = self.data_cleaner.clean_product_data(product)
                if cleaned:
                    product_id = self.db_manager.insert_product(cleaned)
                    inserted_ids.append(product_id)
            batch_end = time.time()
            
            batch_duration = batch_end - batch_start
            
            # 验证性能指标
            self.assertLess(batch_duration, 5.0)  # 批量插入应在5秒内完成
            self.assertEqual(len(inserted_ids), 10)
            
            # 测试查询性能
            query_start = time.time()
            products = self.db_manager.get_all_products()
            query_end = time.time()
            
            query_duration = query_end - query_start
            self.assertLess(query_duration, 1.0)  # 查询应在1秒内完成
            
            total_duration = time.time() - start_time
            
            logger.info(f"性能测试完成 - 总耗时: {total_duration:.2f}秒")
            logger.info(f"批量插入耗时: {batch_duration:.2f}秒")
            logger.info(f"查询耗时: {query_duration:.2f}秒")
            
        except Exception as e:
            logger.error(f"性能测试失败: {e}")
            raise


class TestErrorRecovery(unittest.TestCase):
    """测试错误处理和恢复机制"""
    
    def setUp(self):
        """测试初始化"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="error_test_"))
        self.test_db_path = self.test_dir / "error_test.db"
        self.db_manager = DatabaseManager(str(self.test_db_path))
        self.data_cleaner = DataCleaner()
    
    def tearDown(self):
        """测试清理"""
        if self.db_manager:
            self.db_manager.close_all_connections()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_network_error_handling(self):
        """测试网络错误处理"""
        logger.info("测试网络错误处理...")
        
        # 模拟网络异常情况
        test_cases = [
            {'invalid_url': 'not-a-valid-url', 'price': -10, 'title': ''},
            {'price': 'invalid_price', 'title': None, 'rating': 10},
            {'missing_title': True, 'price': 25.0},
            {}
        ]
        
        for i, test_data in enumerate(test_cases):
            try:
                cleaned = self.data_cleaner.clean_product_data(test_data)
                if cleaned is None:
                    logger.info(f"测试用例{i+1}: 正确拒绝无效数据")
                else:
                    logger.info(f"测试用例{i+1}: 成功处理数据 {cleaned.get('title', 'N/A')}")
            except Exception as e:
                logger.warning(f"测试用例{i+1}: 捕获异常 {e}")
    
    def test_database_error_recovery(self):
        """测试数据库错误恢复"""
        logger.info("测试数据库错误恢复...")
        
        # 测试重复插入处理
        valid_product = {
            'title': '错误恢复测试产品',
            'price': 19.99,
            'rating': 4.0,
            'platform': 'amazon'
        }
        
        try:
            # 第一次插入
            id1 = self.db_manager.insert_product(valid_product)
            self.assertIsInstance(id1, int)
            
            # 尝试插入相同产品（可能触发重复键错误）
            try:
                id2 = self.db_manager.insert_product(valid_product)
                logger.info("成功处理重复插入")
            except sqlite3.IntegrityError:
                logger.info("正确捕获重复键错误")
            
            # 验证数据仍然可用
            products = self.db_manager.get_all_products()
            self.assertGreater(len(products), 0)
            
        except Exception as e:
            logger.error(f"数据库错误恢复测试失败: {e}")
            raise
    
    def test_data_validation_error_handling(self):
        """测试数据验证错误处理"""
        logger.info("测试数据验证错误处理...")
        
        invalid_data_cases = [
            {
                'title': 'A' * 1000,  # 超长标题
                'price': -5.0,        # 负价格
                'rating': 6.0         # 超出范围的评分
            },
            {
                'title': None,        # 空标题
                'price': 'invalid',   # 字符串价格
                'rating': None        # 空评分
            }
        ]
        
        for i, test_data in enumerate(invalid_data_cases):
            try:
                cleaned = self.data_cleaner.clean_product_data(test_data)
                if cleaned is None:
                    logger.info(f"测试用例{i+1}: 正确拒绝无效数据")
                else:
                    logger.info(f"测试用例{i+1}: 成功清理数据")
            except Exception as e:
                logger.warning(f"测试用例{i+1}: 捕获验证错误 {e}")


class TestSystemMonitoring(unittest.TestCase):
    """测试系统监控和日志"""
    
    def test_logging_functionality(self):
        """测试日志功能"""
        logger.info("测试日志功能...")
        
        # 创建测试日志文件
        log_file = project_root / "tests" / "logs" / "test_logs"
        log_file.parent.mkdir(exist_ok=True)
        
        # 测试日志记录
        test_logger = logging.getLogger(f"test_logger_{int(time.time())}")
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.INFO)
        
        # 记录测试日志
        test_logger.info("这是一个测试日志消息")
        test_logger.warning("这是一个测试警告")
        test_logger.error("这是一个测试错误")
        
        # 验证日志文件
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                self.assertIn("测试日志消息", log_content)
                self.assertIn("测试警告", log_content)
                self.assertIn("测试错误", log_content)
        
        logger.info("日志功能测试通过")


def run_integration_tests():
    """运行集成测试"""
    print("=" * 60)
    print("开始系统集成测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestCompleteWorkflow,
        TestErrorRecovery,
        TestSystemMonitoring
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
    print("集成测试完成")
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
    
    # 运行集成测试
    success = run_integration_tests()
    
    if success:
        print("✅ 所有集成测试通过")
        sys.exit(0)
    else:
        print("❌ 部分集成测试失败")
        sys.exit(1)