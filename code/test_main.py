#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主协调脚本测试用例
================

验证主协调脚本的基本功能和核心组件。

作者：Claude
日期：2025-11-14
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch
import asyncio

# 添加项目根目录到Python路径
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from main import (
    MainCoordinator, Platform, TaskStatus, 
    ScrapingTask, ScrapingResult, 
    ConfigManager, DatabaseManager, DataIntegrator
)


class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
    
    def tearDown(self):
        # 清理临时文件
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_creation(self):
        """测试配置创建"""
        config_manager = ConfigManager(self.config_file)
        
        # 检查默认配置已创建
        self.assertTrue(os.path.exists(self.config_file))
        
        # 检查配置内容
        self.assertTrue(config_manager.get("scraping.amazon.enabled"))
        self.assertEqual(config_manager.get("scraping.amazon.max_concurrent"), 3)
    
    def test_config_update(self):
        """测试配置更新"""
        config_manager = ConfigManager(self.config_file)
        
        # 更新配置
        config_manager.config["test_key"] = "test_value"
        config_manager.save()
        
        # 重新加载并验证
        new_manager = ConfigManager(self.config_file)
        self.assertEqual(new_manager.get("test_key"), "test_value")
    
    def test_config_get_default(self):
        """测试获取不存在的配置项"""
        config_manager = ConfigManager(self.config_file)
        
        self.assertIsNone(config_manager.get("non.existent.key"))
        self.assertEqual(config_manager.get("non.existent.key", "default"), "default")


class TestDatabaseManager(unittest.TestCase):
    """测试数据库管理器"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
        # 创建测试配置
        config = Mock()
        config.get.return_value = self.db_path
        
        self.db_manager = DatabaseManager(config)
    
    def tearDown(self):
        # 清理临时文件
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_initialization(self):
        """测试数据库初始化"""
        # 检查数据库文件是否存在
        self.assertTrue(os.path.exists(self.db_path))
        
        # 检查数据表是否存在
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ["tasks", "results", "products", "statistics"]
            for table in expected_tables:
                self.assertIn(table, tables)
    
    def test_save_and_load_task(self):
        """测试任务保存和加载"""
        task = ScrapingTask(
            task_id="test_task_001",
            platform=Platform.AMAZON,
            category="T-Shirt",
            keywords=["print", "graphic"],
            max_pages=5
        )
        
        # 保存任务
        self.db_manager.save_task(task)
        
        # 验证任务已保存（通过查询数据库）
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task.task_id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row[1], "amazon")  # platform
            self.assertEqual(row[2], "T-Shirt")  # category
    
    def test_save_products(self):
        """测试产品数据保存"""
        products = [
            {
                "product_id": "test_001",
                "title": "测试产品",
                "price": 19.99,
                "category": "T-Shirt"
            }
        ]
        
        # 保存产品
        self.db_manager.save_products(products, Platform.AMAZON)
        
        # 验证产品已保存
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE product_id = ?", ("test_001",))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row[2], "测试产品")
            self.assertEqual(row[3], 19.99)


class TestDataIntegrator(unittest.TestCase):
    """测试数据整合器"""
    
    def setUp(self):
        # 创建临时数据库路径
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
        config = Mock()
        config.get.return_value = self.db_path
        
        self.db_manager = DatabaseManager(config)
        self.integrator = DataIntegrator(self.db_manager)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_deduplicate_products(self):
        """测试产品去重"""
        products = [
            {"product_id": "001", "title": "产品1"},
            {"product_id": "001", "title": "产品1_重复"},
            {"product_id": "002", "title": "产品2"}
        ]
        
        deduplicated = self.integrator.deduplicate_products(products, Platform.AMAZON)
        
        self.assertEqual(len(deduplicated), 2)
        self.assertEqual(deduplicated[0]["product_id"], "amazon_001")
        self.assertEqual(deduplicated[1]["product_id"], "amazon_002")
    
    def test_validate_data_quality(self):
        """测试数据质量验证"""
        products = [
            {"title": "有效产品", "price": 19.99, "product_id": "001"},
            {"title": "", "price": -1, "product_id": "002"},  # 无效数据
            {"price": 0, "product_id": "003"}  # 缺少标题
        ]
        
        is_valid, issues = self.integrator.validate_data_quality(products)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
    
    def test_merge_platform_data(self):
        """测试平台数据合并"""
        amazon_data = [
            {"product_id": "amz_001", "title": "Amazon产品", "price": 20.0, "rating": 4.5},
            {"product_id": "amz_002", "title": "Amazon产品2", "price": 25.0, "rating": 4.8}
        ]
        
        tiktok_data = [
            {"product_id": "tt_001", "title": "TikTok产品", "price": 30.0, "rating": 4.3}
        ]
        
        merged = self.integrator.merge_platform_data(amazon_data, tiktok_data)
        
        self.assertEqual(merged["total_products"], 3)
        self.assertEqual(merged["amazon_products"], 2)
        self.assertEqual(merged["tiktok_products"], 1)
        self.assertEqual(merged["price_ranges"]["amazon"]["min"], 20.0)
        self.assertEqual(merged["price_ranges"]["amazon"]["max"], 25.0)


class TestMainCoordinator(unittest.TestCase):
    """测试主协调器"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
        # 模拟配置
        with patch('main.ConfigManager') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.config = {
                "database": {"path": self.db_path},
                "scraping": {
                    "amazon": {"enabled": True, "max_concurrent": 3, "request_delay": 1.0},
                    "tiktok": {"enabled": True, "max_concurrent": 2, "request_delay": 2.0}
                },
                "retry": {"max_retries": 3, "backoff_factor": 2, "retry_delay": 5},
                "monitoring": {"alert_thresholds": {"failure_rate": 0.3, "avg_response_time": 30}}
            }
            mock_config.return_value = mock_config_instance
            
            self.coordinator = MainCoordinator()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_task(self):
        """测试任务创建"""
        task = self.coordinator.create_task(
            platform=Platform.AMAZON,
            category="T-Shirt",
            keywords=["print"],
            max_pages=5
        )
        
        self.assertIsInstance(task, ScrapingTask)
        self.assertEqual(task.platform, Platform.AMAZON)
        self.assertEqual(task.category, "T-Shirt")
        self.assertEqual(task.keywords, ["print"])
        self.assertEqual(task.max_pages, 5)
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    @patch('main.AmazonScraper.scrape')
    async def test_execute_single_task_success(self, mock_scrape):
        """测试成功执行单个任务"""
        # 模拟抓取成功
        mock_scrape.return_value = ScrapingResult(
            task_id="test_task",
            platform=Platform.AMAZON,
            success=True,
            data=[{"product_id": "001", "title": "测试产品"}],
            items_found=1
        )
        
        task = self.coordinator.create_task(
            platform=Platform.AMAZON,
            category="T-Shirt",
            keywords=["test"]
        )
        
        result = await self.coordinator.execute_single_task(task)
        
        self.assertTrue(result.success)
        self.assertEqual(result.items_found, 1)
        self.assertEqual(task.status, TaskStatus.SUCCESS)
    
    @patch('main.AmazonScraper.scrape')
    async def test_execute_single_task_failure(self, mock_scrape):
        """测试任务执行失败"""
        # 模拟抓取失败
        mock_scrape.side_effect = Exception("网络错误")
        
        task = self.coordinator.create_task(
            platform=Platform.AMAZON,
            category="T-Shirt",
            keywords=["test"]
        )
        
        result = await self.coordinator.execute_single_task(task)
        
        self.assertFalse(result.success)
        self.assertIn("网络错误", result.error_message)
        self.assertEqual(task.status, TaskStatus.FAILED)
    
    def test_get_status(self):
        """测试获取系统状态"""
        status = self.coordinator.get_status()
        
        self.assertIn("timestamp", status)
        self.assertIn("config_status", status)
        self.assertIn("performance", status)
        self.assertIn("recent_statistics", status)
        
        # 检查配置状态
        config_status = status["config_status"]
        self.assertIn("amazon_enabled", config_status)
        self.assertIn("tiktok_enabled", config_status)


class TestAsyncFunctions(unittest.TestCase):
    """测试异步功能"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
        with patch('main.ConfigManager') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.config = {
                "database": {"path": self.db_path},
                "scraping": {
                    "amazon": {"enabled": True, "max_concurrent": 3, "request_delay": 1.0},
                    "tiktok": {"enabled": True, "max_concurrent": 2, "request_delay": 2.0}
                },
                "retry": {"max_retries": 3, "backoff_factor": 2, "retry_delay": 5},
                "monitoring": {"alert_thresholds": {"failure_rate": 0.3, "avg_response_time": 30}}
            }
            mock_config.return_value = mock_config_instance
            
            self.coordinator = MainCoordinator()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('main.AmazonScraper.scrape')
    async def test_execute_multiple_tasks(self, mock_scrape):
        """测试批量任务执行"""
        # 模拟多个任务结果
        results = [
            ScrapingResult("task1", Platform.AMAZON, True, [{"id": 1}], items_found=1),
            ScrapingResult("task2", Platform.AMAZON, True, [{"id": 2}], items_found=1),
            ScrapingResult("task3", Platform.AMAZON, False, [], error_message="失败")
        ]
        mock_scrape.side_effect = results
        
        # 创建任务
        tasks = []
        for i in range(3):
            task = self.coordinator.create_task(
                platform=Platform.AMAZON,
                category=f"Category{i}",
                keywords=[f"keyword{i}"]
            )
            tasks.append(task)
        
        # 执行批量任务
        execution_results = await self.coordinator.execute_multiple_tasks(tasks, max_workers=2)
        
        self.assertEqual(len(execution_results), 3)
        
        # 检查结果统计
        successful = [r for r in execution_results if r.success]
        failed = [r for r in execution_results if not r.success]
        
        self.assertEqual(len(successful), 2)
        self.assertEqual(len(failed), 1)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestConfigManager,
        TestDatabaseManager,
        TestDataIntegrator,
        TestMainCoordinator,
        TestAsyncFunctions
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("运行主协调脚本测试...")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
        exit(0)
    else:
        print("\n❌ 部分测试失败！")
        exit(1)