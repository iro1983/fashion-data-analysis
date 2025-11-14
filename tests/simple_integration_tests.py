#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统集成测试（简化版）
====================

用于演示集成测试功能，不依赖外部模块

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

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "code"))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleDataCleaner:
    """简化的数据清洗器"""
    
    def __init__(self):
        self.price_range = (0, 10000)
        self.rating_range = (0, 5)
    
    def clean_product_data(self, data):
        """清洗产品数据"""
        if not isinstance(data, dict):
            return None
        
        try:
            cleaned = {}
            
            # 清洗标题
            title = data.get('title', '')
            if title:
                cleaned['title'] = str(title).strip()
            else:
                return None
            
            # 清洗价格
            price = data.get('price', 0)
            try:
                if isinstance(price, str):
                    # 移除货币符号和逗号
                    price = price.replace('$', '').replace(',', '').strip()
                price = float(price)
                if self.price_range[0] <= price <= self.price_range[1]:
                    cleaned['price'] = price
                else:
                    return None
            except (ValueError, TypeError):
                return None
            
            # 清洗评分
            rating = data.get('rating', 0)
            try:
                if isinstance(rating, str):
                    rating = rating.replace('stars', '').replace('星', '').strip()
                rating = float(rating)
                if self.rating_range[0] <= rating <= self.rating_range[1]:
                    cleaned['rating'] = rating
            except (ValueError, TypeError):
                cleaned['rating'] = None
            
            # 清洗平台
            platform = data.get('platform', 'unknown')
            if platform in ['amazon', 'tiktok']:
                cleaned['platform'] = platform
            else:
                return None
            
            # 其他字段
            cleaned['category'] = data.get('category', '')
            cleaned['url'] = data.get('url', '')
            cleaned['image_url'] = data.get('image_url', '')
            cleaned['description'] = data.get('description', '')
            cleaned['created_at'] = datetime.now().isoformat()
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"数据清洗失败: {e}")
            return None


class SimpleDatabaseManager:
    """简化的数据库管理器"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.connections = []
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    rating REAL,
                    category TEXT,
                    platform TEXT NOT NULL,
                    url TEXT,
                    image_url TEXT,
                    description TEXT,
                    created_at TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def insert_product(self, product_data):
        """插入产品"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO products (title, price, rating, category, platform, url, image_url, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product_data.get('title'),
                    product_data.get('price'),
                    product_data.get('rating'),
                    product_data.get('category'),
                    product_data.get('platform'),
                    product_data.get('url'),
                    product_data.get('image_url'),
                    product_data.get('description'),
                    product_data.get('created_at')
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入产品失败: {e}")
            raise
    
    def get_all_products(self):
        """获取所有产品"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products')
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"查询产品失败: {e}")
            return []
    
    def get_products_by_platform(self, platform):
        """按平台获取产品"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products WHERE platform = ?', (platform,))
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"按平台查询失败: {e}")
            return []
    
    def get_product_by_id(self, product_id):
        """根据ID获取产品"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            logger.error(f"根据ID查询失败: {e}")
            return None
    
    def update_product(self, product_id, update_data):
        """更新产品"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
                values = list(update_data.values()) + [product_id]
                cursor.execute(f'UPDATE products SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?', values)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新产品失败: {e}")
            return False
    
    def close_all_connections(self):
        """关闭所有连接"""
        self.connections.clear()


class TestCompleteWorkflow(unittest.TestCase):
    """测试完整工作流程"""
    
    def setUp(self):
        """测试初始化"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="simple_integration_test_"))
        self.test_db_path = self.test_dir / "test_products.db"
        
        # 初始化组件
        self.db_manager = SimpleDatabaseManager(str(self.test_db_path))
        self.data_cleaner = SimpleDataCleaner()
        
        # 准备测试数据
        self.sample_product = {
            'title': '测试T恤衫',
            'price': 29.99,
            'rating': 4.5,
            'category': '服装',
            'platform': 'amazon',
            'url': 'https://amazon.com/test-product',
            'image_url': 'https://amazon.com/image.jpg',
            'description': '高质量棉质T恤衫'
        }
        
        logger.info(f"测试环境初始化完成，数据库路径: {self.test_db_path}")
    
    def tearDown(self):
        """测试清理"""
        try:
            # 清理测试数据库连接
            if hasattr(self, 'db_manager'):
                self.db_manager.close_all_connections()
            
            # 清理测试目录
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
            logger.info("测试环境清理完成")
        except Exception as e:
            logger.warning(f"清理测试环境时发生警告: {e}")
    
    def test_01_data_cleaning(self):
        """测试数据清洗功能"""
        logger.info("测试数据清洗...")
        
        # 测试数据清洗
        cleaned_data = self.data_cleaner.clean_product_data(self.sample_product)
        
        # 验证清洗结果
        self.assertIsNotNone(cleaned_data)
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
                        'title': 'TikTok热门T恤'
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
    
    def test_04_data_consistency(self):
        """测试数据一致性"""
        logger.info("测试数据一致性...")
        
        # 插入数据，测试数据完整性
        try:
            product1 = {**self.sample_product, 'title': '一致性测试产品'}
            product2 = {**self.sample_product, 'title': '一致性测试产品2'}
            
            # 清洗和插入产品
            cleaned1 = self.data_cleaner.clean_product_data(product1)
            cleaned2 = self.data_cleaner.clean_product_data(product2)
            
            if cleaned1:
                id1 = self.db_manager.insert_product(cleaned1)
                self.assertIsInstance(id1, int)
            
            if cleaned2:
                id2 = self.db_manager.insert_product(cleaned2)
                self.assertIsInstance(id2, int)
            
            # 验证数据正确存储
            products = self.db_manager.get_all_products()
            self.assertGreater(len(products), 0)
            
            logger.info("数据一致性测试通过")
            
        except Exception as e:
            logger.error(f"数据一致性测试失败: {e}")
            raise
    
    def test_05_performance_metrics(self):
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


def run_simple_integration_tests():
    """运行简化版集成测试"""
    print("=" * 60)
    print("开始系统集成测试（简化版）")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [TestCompleteWorkflow]
    
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
    success = run_simple_integration_tests()
    
    if success:
        print("✅ 所有集成测试通过")
        sys.exit(0)
    else:
        print("❌ 部分集成测试失败")
        sys.exit(1)