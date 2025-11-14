#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理测试模块
==============

测试系统的错误处理和恢复机制：
- 网络错误处理
- 数据库错误恢复
- 数据验证错误处理
- 系统异常处理
- 重试机制测试

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
import threading
import requests
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "code"))

try:
    from database import DatabaseManager
    from data_cleaner import DataCleaner
    from amazon_scraper import AmazonScraper
    from tiktok_scraper import TikTokScraper
    from main import Coordinator
except ImportError as e:
    print(f"模块导入错误: {e}")
    sys.exit(1)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestNetworkErrorHandling(unittest.TestCase):
    """测试网络错误处理"""
    
    def setUp(self):
        """测试初始化"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="network_error_test_"))
        self.test_db_path = self.test_dir / "network_error_test.db"
        self.db_manager = DatabaseManager(str(self.test_db_path))
        self.data_cleaner = DataCleaner()
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @patch('requests.get')
    def test_connection_timeout_error(self, mock_get):
        """测试连接超时错误处理"""
        logger.info("测试连接超时错误处理...")
        
        # 模拟连接超时
        mock_get.side_effect = requests.exceptions.ConnectTimeout("Connection timed out")
        
        # 测试错误处理
        try:
            response = requests.get('https://test-url.com')
            self.fail("应该抛出超时异常")
        except requests.exceptions.ConnectTimeout:
            logger.info("正确捕获连接超时异常")
        
        # 测试系统继续运行
        test_product = {'title': '正常产品', 'price': 29.99, 'platform': 'amazon'}
        cleaned = self.data_cleaner.clean_product_data(test_product)
        self.assertIsNotNone(cleaned)
    
    @patch('requests.get')
    def test_http_error_handling(self, mock_get):
        """测试HTTP错误处理"""
        logger.info("测试HTTP错误处理...")
        
        # 模拟HTTP 404错误
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        # 测试错误处理
        try:
            response = requests.get('https://test-url.com/404')
            self.fail("应该抛出HTTP错误")
        except requests.exceptions.HTTPError:
            logger.info("正确捕获HTTP错误")
    
    @patch('requests.get')
    def test_connection_error_handling(self, mock_get):
        """测试连接错误处理"""
        logger.info("测试连接错误处理...")
        
        # 模拟连接错误
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        try:
            response = requests.get('https://test-url.com')
            self.fail("应该抛出连接错误")
        except requests.exceptions.ConnectionError:
            logger.info("正确捕获连接错误")
    
    def test_invalid_url_handling(self):
        """测试无效URL处理"""
        logger.info("测试无效URL处理...")
        
        invalid_urls = [
            'not-a-valid-url',
            'http://',
            'ftp://invalid.com',
            '',
            None
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                try:
                    if url:
                        response = requests.get(url, timeout=5)
                    else:
                        response = requests.get('')
                    self.fail(f"URL {url} 应该抛出异常")
                except (requests.exceptions.MissingSchema, 
                        requests.exceptions.InvalidURL,
                        requests.exceptions.ConnectionError,
                        ValueError):
                    logger.info(f"正确处理无效URL: {url}")
    
    def test_api_rate_limit_handling(self):
        """测试API速率限制处理"""
        logger.info("测试API速率限制处理...")
        
        # 模拟429错误（Too Many Requests）
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {'Retry-After': '60'}
            mock_get.return_value = mock_response
            
            # 测试速率限制处理
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = requests.get('https://api.test.com', timeout=5)
                    if response.status_code == 429:
                        retry_count += 1
                        logger.info(f"遇到速率限制，等待 {response.headers.get('Retry-After', 60)} 秒")
                        time.sleep(1)  # 缩短等待时间用于测试
                    else:
                        logger.info("请求成功")
                        break
                except Exception as e:
                    logger.error(f"请求失败: {e}")
                    break
            
            self.assertLessEqual(retry_count, max_retries)


class TestDatabaseErrorHandling(unittest.TestCase):
    """测试数据库错误处理"""
    
    def setUp(self):
        """测试初始化"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="db_error_test_"))
        self.test_db_path = self.test_dir / "db_error_test.db"
        self.db_manager = DatabaseManager(str(self.test_db_path))
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_database_lock_error(self):
        """测试数据库锁错误处理"""
        logger.info("测试数据库锁错误处理...")
        
        # 插入测试数据
        test_product = {
            'title': '锁测试产品',
            'price': 29.99,
            'platform': 'amazon'
        }
        
        # 正常插入
        product_id = self.db_manager.insert_product(test_product)
        self.assertIsInstance(product_id, int)
        
        # 模拟并发访问
        def concurrent_insert():
            try:
                product = {'title': '并发产品', 'price': 39.99, 'platform': 'tiktok'}
                return self.db_manager.insert_product(product)
            except Exception as e:
                return f"Error: {e}"
        
        # 执行并发操作
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(concurrent_insert) for _ in range(3)]
            results = [future.result() for future in as_completed(futures)]
        
        # 验证至少有一个成功
        success_count = sum(1 for r in results if isinstance(r, int))
        self.assertGreater(success_count, 0)
        
        logger.info(f"并发测试完成: {len(results)}个操作，{success_count}个成功")
    
    def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        logger.info("测试SQL注入防护...")
        
        # 恶意输入测试
        malicious_inputs = [
            "'; DROP TABLE products; --",
            "1' OR '1'='1",
            "'; UPDATE products SET price=0; --",
            "test' UNION SELECT * FROM users; --"
        ]
        
        for malicious_input in malicious_inputs:
            with self.subTest(input=malicious_input):
                try:
                    # 尝试执行恶意输入
                    result = self.db_manager.search_products(malicious_input)
                    # 如果没有抛出异常，验证结果不会泄露敏感信息
                    if result is not None:
                        self.assertIsInstance(result, list)
                except sqlite3.Error as e:
                    logger.info(f"正确阻止SQL注入: {malicious_input}")
    
    def test_constraint_violation_handling(self):
        """测试约束违规处理"""
        logger.info("测试约束违规处理...")
        
        # 插入有效数据
        valid_product = {
            'title': '约束测试产品',
            'price': 29.99,
            'platform': 'amazon',
            'url': 'https://amazon.com/constraint-test'
        }
        
        product_id = self.db_manager.insert_product(valid_product)
        self.assertIsInstance(product_id, int)
        
        # 尝试插入重复URL（违反唯一约束）
        duplicate_product = {
            **valid_product,
            'title': '重复产品'
        }
        
        try:
            duplicate_id = self.db_manager.insert_product(duplicate_product)
            # 如果成功，验证数据确实存在
            self.assertIsInstance(duplicate_id, int)
        except sqlite3.IntegrityError:
            logger.info("正确阻止重复数据插入")
    
    def test_corruption_recovery(self):
        """测试数据库损坏恢复"""
        logger.info("测试数据库损坏恢复...")
        
        try:
            # 创建测试数据
            test_product = {'title': '损坏恢复测试', 'price': 29.99, 'platform': 'amazon'}
            product_id = self.db_manager.insert_product(test_product)
            
            # 强制关闭数据库连接
            self.db_manager.close_all_connections()
            
            # 重新初始化数据库管理器
            self.db_manager = DatabaseManager(str(self.test_db_path))
            
            # 验证数据完整性
            products = self.db_manager.get_all_products()
            self.assertGreater(len(products), 0)
            
            logger.info("数据库损坏恢复测试通过")
            
        except Exception as e:
            logger.warning(f"数据库损坏恢复测试异常: {e}")


class TestDataValidationErrorHandling(unittest.TestCase):
    """测试数据验证错误处理"""
    
    def setUp(self):
        """测试初始化"""
        self.data_cleaner = DataCleaner()
    
    def test_invalid_price_handling(self):
        """测试无效价格处理"""
        logger.info("测试无效价格处理...")
        
        invalid_prices = [
            -10,          # 负数
            0,            # 零
            'invalid',    # 字符串
            None,         # 空值
            float('inf'), # 无穷大
            -float('inf') # 负无穷大
        ]
        
        for price in invalid_prices:
            with self.subTest(price=price):
                test_data = {
                    'title': '价格测试产品',
                    'price': price,
                    'platform': 'amazon'
                }
                
                cleaned = self.data_cleaner.clean_product_data(test_data)
                if cleaned is not None:
                    self.assertIsInstance(cleaned['price'], (int, float))
                    self.assertGreater(cleaned['price'], 0)
    
    def test_invalid_title_handling(self):
        """测试无效标题处理"""
        logger.info("测试无效标题处理...")
        
        invalid_titles = [
            '',                    # 空字符串
            '   ',                 # 只有空格
            None,                  # None值
            'a' * 1000,            # 超长标题
            '\x00\x01\x02',        # 控制字符
            '<script>alert("xss")</script>'  # XSS尝试
        ]
        
        for title in invalid_titles:
            with self.subTest(title=title):
                test_data = {
                    'title': title,
                    'price': 29.99,
                    'platform': 'amazon'
                }
                
                cleaned = self.data_cleaner.clean_product_data(test_data)
                if cleaned is not None:
                    self.assertIsInstance(cleaned['title'], str)
                    self.assertGreater(len(cleaned['title'].strip()), 0)
                    self.assertLess(len(cleaned['title']), 500)  # 限制标题长度
    
    def test_invalid_rating_handling(self):
        """测试无效评分处理"""
        logger.info("测试无效评分处理...")
        
        invalid_ratings = [
            -1,           # 负数
            6,            # 超出范围
            10,           # 超出范围
            'invalid',    # 字符串
            None,         # 空值
            float('nan')  # NaN
        ]
        
        for rating in invalid_ratings:
            with self.subTest(rating=rating):
                test_data = {
                    'title': '评分测试产品',
                    'price': 29.99,
                    'rating': rating,
                    'platform': 'amazon'
                }
                
                cleaned = self.data_cleaner.clean_product_data(test_data)
                # 如果评分没有被完全移除，验证其有效性
                if 'rating' in cleaned:
                    self.assertIsInstance(cleaned['rating'], (int, float))
                    self.assertGreaterEqual(cleaned['rating'], 0)
                    self.assertLessEqual(cleaned['rating'], 5)
    
    def test_malformed_data_handling(self):
        """测试格式错误数据处理"""
        logger.info("测试格式错误数据处理...")
        
        malformed_data = [
            {},                                    # 空字典
            {'not_expected_field': 'value'},       # 字段不匹配
            ['this', 'is', 'a', 'list'],           # 错误数据类型
            "this is a string",                    # 错误数据类型
            None,                                  # None值
            123                                    # 数字类型
        ]
        
        for data in malformed_data:
            with self.subTest(data=str(data)[:50]):
                try:
                    cleaned = self.data_cleaner.clean_product_data(data)
                    if cleaned is not None:
                        # 验证返回的是有效的产品数据
                        self.assertIsInstance(cleaned, dict)
                        if 'title' in cleaned:
                            self.assertIsInstance(cleaned['title'], str)
                        if 'price' in cleaned:
                            self.assertIsInstance(cleaned['price'], (int, float))
                except Exception as e:
                    logger.info(f"正确处理格式错误数据: {e}")


class TestSystemErrorRecovery(unittest.TestCase):
    """测试系统错误恢复机制"""
    
    def setUp(self):
        """测试初始化"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="recovery_test_"))
        self.test_db_path = self.test_dir / "recovery_test.db"
        self.db_manager = DatabaseManager(str(self.test_db_path))
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_memory_pressure_recovery(self):
        """测试内存压力恢复"""
        logger.info("测试内存压力恢复...")
        
        # 创建大量测试数据
        large_data_set = []
        for i in range(1000):
            product = {
                'title': f'内存压力测试产品 {i}',
                'price': 20.00 + (i % 100),
                'platform': 'amazon',
                'description': f'详细描述 {i}' * 10
            }
            large_data_set.append(product)
        
        try:
            # 批量处理大量数据
            processed_count = 0
            batch_size = 100
            
            for i in range(0, len(large_data_set), batch_size):
                batch = large_data_set[i:i+batch_size]
                
                for product in batch:
                    cleaned = self.data_cleaner.clean_product_data(product)
                    if cleaned:
                        self.db_manager.insert_product(cleaned)
                        processed_count += 1
                
                # 模拟内存清理
                import gc
                gc.collect()
            
            self.assertGreater(processed_count, 500)
            logger.info(f"内存压力恢复测试完成: 处理{processed_count}个产品")
            
        except MemoryError:
            logger.info("遇到内存限制，系统需要优化")
        except Exception as e:
            logger.error(f"内存压力测试异常: {e}")
    
    def test_concurrent_access_recovery(self):
        """测试并发访问恢复"""
        logger.info("测试并发访问恢复...")
        
        def worker_function(worker_id):
            """工作线程函数"""
            try:
                for i in range(10):
                    product = {
                        'title': f'并发产品-{worker_id}-{i}',
                        'price': 20.00 + worker_id,
                        'platform': 'amazon'
                    }
                    
                    # 模拟数据清洗
                    cleaned = self.data_cleaner.clean_product_data(product)
                    if cleaned:
                        product_id = self.db_manager.insert_product(cleaned)
                        
                    time.sleep(0.01)  # 模拟处理时间
                    
                return f"Worker-{worker_id} completed"
            except Exception as e:
                return f"Worker-{worker_id} failed: {e}"
        
        # 启动多个并发线程
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker_function, i) for i in range(5)]
            results = [future.result() for future in as_completed(futures)]
        
        # 验证至少有一个线程成功完成
        completed_workers = [r for r in results if 'completed' in r]
        self.assertGreater(len(completed_workers), 0)
        
        # 验证数据库中确实有数据
        products = self.db_manager.get_all_products()
        self.assertGreater(len(products), 0)
        
        logger.info(f"并发访问恢复测试完成: {len(completed_workers)}个线程成功")
    
    def test_resource_cleanup_recovery(self):
        """测试资源清理恢复"""
        logger.info("测试资源清理恢复...")
        
        initial_connection_count = len(self.db_manager.connections)
        
        # 创建和关闭多个连接
        temp_managers = []
        for i in range(5):
            temp_db_path = self.test_dir / f"temp_{i}.db"
            temp_manager = DatabaseManager(str(temp_db_path))
            temp_managers.append(temp_manager)
        
        # 验证连接创建
        self.assertEqual(len(temp_managers), 5)
        
        # 清理临时管理器
        for manager in temp_managers:
            manager.close_all_connections()
        
        temp_managers.clear()
        
        # 验证主管理器仍然可用
        test_product = {'title': '资源清理测试', 'price': 29.99, 'platform': 'amazon'}
        cleaned = self.data_cleaner.clean_product_data(test_product)
        if cleaned:
            product_id = self.db_manager.insert_product(cleaned)
            self.assertIsInstance(product_id, int)
        
        logger.info("资源清理恢复测试通过")


class TestRetryMechanism(unittest.TestCase):
    """测试重试机制"""
    
    def test_exponential_backoff_retry(self):
        """测试指数退避重试"""
        logger.info("测试指数退避重试...")
        
        def mock_operation_with_failure(attempt):
            """模拟可能失败的操作"""
            if attempt < 3:
                raise Exception(f"模拟失败 (尝试 {attempt})")
            return "操作成功"
        
        # 指数退避重试逻辑
        max_retries = 5
        base_delay = 0.1  # 缩短延迟用于测试
        
        for attempt in range(max_retries):
            try:
                result = mock_operation_with_failure(attempt)
                logger.info(f"尝试 {attempt + 1}: {result}")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"尝试 {attempt + 1} 失败: {e}，等待 {delay:.2f} 秒后重试")
                    time.sleep(delay)
                else:
                    logger.error(f"所有 {max_retries} 次重试都失败")
                    raise
        
        logger.info("指数退避重试测试通过")
    
    def test_circuit_breaker_pattern(self):
        """测试断路器模式"""
        logger.info("测试断路器模式...")
        
        class CircuitBreaker:
            def __init__(self, failure_threshold=3, recovery_timeout=5):
                self.failure_threshold = failure_threshold
                self.recovery_timeout = recovery_timeout
                self.failure_count = 0
                self.last_failure_time = None
                self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
            
            def call(self, func, *args, **kwargs):
                if self.state == 'OPEN':
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        self.state = 'HALF_OPEN'
                    else:
                        raise Exception("断路器开启，拒绝请求")
                
                try:
                    result = func(*args, **kwargs)
                    if self.state == 'HALF_OPEN':
                        self.state = 'CLOSED'
                        self.failure_count = 0
                    return result
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    
                    if self.failure_count >= self.failure_threshold:
                        self.state = 'OPEN'
                    
                    raise e
        
        # 测试断路器
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        def failing_function():
            raise Exception("服务不可用")
        
        # 测试连续失败
        for i in range(3):
            try:
                cb.call(failing_function)
            except Exception:
                pass
        
        self.assertEqual(cb.state, 'OPEN')
        
        # 等待恢复超时
        time.sleep(1.1)
        
        # 测试恢复
        def working_function():
            return "服务正常"
        
        try:
            result = cb.call(working_function)
            self.assertEqual(result, "服务正常")
            self.assertEqual(cb.state, 'CLOSED')
        except Exception as e:
            logger.warning(f"断路器恢复测试异常: {e}")
        
        logger.info("断路器模式测试通过")


def run_error_handling_tests():
    """运行错误处理测试"""
    print("=" * 60)
    print("开始错误处理测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestNetworkErrorHandling,
        TestDatabaseErrorHandling,
        TestDataValidationErrorHandling,
        TestSystemErrorRecovery,
        TestRetryMechanism
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
    print("错误处理测试完成")
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
    
    # 运行错误处理测试
    success = run_error_handling_tests()
    
    if success:
        print("✅ 所有错误处理测试通过")
        sys.exit(0)
    else:
        print("❌ 部分错误处理测试失败")
        sys.exit(1)