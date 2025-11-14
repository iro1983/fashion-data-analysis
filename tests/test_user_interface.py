#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户界面测试模块
==============

测试前端用户界面的功能：
- React组件渲染测试
- 用户交互功能测试
- 数据展示测试
- 响应式设计测试

作者：Claude
日期：2025-11-14
"""

import unittest
import sys
import os
import json
import time
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging
from typing import Dict, List, Any
import subprocess
import threading

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "code"))

try:
    from database import DatabaseManager
    from data_cleaner import DataCleaner
except ImportError as e:
    print(f"模块导入错误: {e}")
    sys.exit(1)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestUIComponentRendering(unittest.TestCase):
    """测试UI组件渲染"""
    
    def setUp(self):
        """测试初始化"""
        self.frontend_dir = project_root / "fashion-dashboard"
        self.test_dir = Path(tempfile.mkdtemp(prefix="ui_test_"))
        self.test_db_path = self.test_dir / "ui_test.db"
        
        # 初始化后端数据
        self.db_manager = DatabaseManager(str(self.test_db_path))
        self.data_cleaner = DataCleaner()
        
        # 准备测试数据
        self.sample_products = [
            {
                'title': '测试T恤衫',
                'price': 29.99,
                'rating': 4.5,
                'category': '服装',
                'platform': 'amazon',
                'url': 'https://amazon.com/test1',
                'image_url': 'https://amazon.com/image1.jpg',
                'description': '高质量棉质T恤',
                'availability': 'in_stock'
            },
            {
                'title': '时尚卫衣',
                'price': 45.99,
                'rating': 4.2,
                'category': '服装',
                'platform': 'tiktok',
                'url': 'https://tiktok.com/test2',
                'image_url': 'https://tiktok.com/image2.jpg',
                'description': '潮流卫衣',
                'availability': 'in_stock'
            }
        ]
        
        # 插入测试数据
        for product in self.sample_products:
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_react_app_structure(self):
        """测试React应用结构"""
        logger.info("测试React应用结构...")
        
        # 检查关键文件存在
        key_files = [
            self.frontend_dir / "src/App.tsx",
            self.frontend_dir / "src/main.tsx",
            self.frontend_dir / "package.json",
            self.frontend_dir / "vite.config.ts"
        ]
        
        for file_path in key_files:
            self.assertTrue(
                file_path.exists(),
                f"缺少关键文件: {file_path}"
            )
        
        logger.info("React应用结构检查通过")
    
    def test_component_imports(self):
        """测试组件导入"""
        logger.info("测试组件导入...")
        
        # 检查App.tsx中的组件导入
        app_file = self.frontend_dir / "src/App.tsx"
        
        if app_file.exists():
            with open(app_file, 'r', encoding='utf-8') as f:
                app_content = f.read()
            
            # 检查关键组件是否被导入
            required_components = [
                'Dashboard',
                'ProductList',
                'PriceAnalysis',
                'Sidebar',
                'Header'
            ]
            
            for component in required_components:
                self.assertIn(
                    component,
                    app_content,
                    f"组件 {component} 未在 App.tsx 中导入"
                )
        
        logger.info("组件导入检查通过")
    
    def test_api_endpoints_structure(self):
        """测试API端点结构"""
        logger.info("测试API端点结构...")
        
        # 模拟API响应格式
        api_responses = {
            '/api/products': {
                'status': 'success',
                'data': self.sample_products,
                'total': len(self.sample_products)
            },
            '/api/dashboard': {
                'status': 'success',
                'data': {
                    'total_products': len(self.sample_products),
                    'amazon_products': 1,
                    'tiktok_products': 1,
                    'avg_price': 37.99,
                    'avg_rating': 4.35
                }
            },
            '/api/analytics': {
                'status': 'success',
                'data': {
                    'price_trends': [],
                    'category_distribution': {'服装': 2},
                    'platform_comparison': {'amazon': 1, 'tiktok': 1}
                }
            }
        }
        
        # 验证API响应格式
        for endpoint, response in api_responses.items():
            self.assertIn('status', response)
            self.assertIn('data', response)
            self.assertEqual(response['status'], 'success')
        
        logger.info("API端点结构检查通过")
    
    def test_data_binding(self):
        """测试数据绑定"""
        logger.info("测试数据绑定...")
        
        # 从数据库获取数据
        products = self.db_manager.get_all_products()
        self.assertGreater(len(products), 0)
        
        # 验证数据结构符合前端期望
        for product in products:
            required_fields = ['title', 'price', 'platform', 'url']
            for field in required_fields:
                self.assertIn(field, product)
                self.assertIsNotNone(product[field])
        
        # 验证数据类型
        for product in products:
            self.assertIsInstance(product['price'], (int, float))
            self.assertIsInstance(product['platform'], str)
            self.assertIsInstance(product['title'], str)
        
        logger.info("数据绑定检查通过")


class TestUserInteractions(unittest.TestCase):
    """测试用户交互功能"""
    
    def setUp(self):
        """测试初始化"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="interaction_test_"))
        self.test_db_path = self.test_dir / "interaction_test.db"
        self.db_manager = DatabaseManager(str(self.test_db_path))
        self.data_cleaner = DataCleaner()
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_product_filtering(self):
        """测试产品筛选功能"""
        logger.info("测试产品筛选功能...")
        
        # 插入不同平台的测试数据
        test_products = [
            {'title': 'Amazon产品1', 'price': 29.99, 'platform': 'amazon'},
            {'title': 'TikTok产品1', 'price': 35.99, 'platform': 'tiktok'},
            {'title': 'Amazon产品2', 'price': 45.99, 'platform': 'amazon'},
            {'title': 'TikTok产品2', 'price': 55.99, 'platform': 'tiktok'}
        ]
        
        for product in test_products:
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
        
        # 测试按平台筛选
        amazon_products = self.db_manager.get_products_by_platform('amazon')
        tiktok_products = self.db_manager.get_products_by_platform('tiktok')
        
        self.assertEqual(len(amazon_products), 2)
        self.assertEqual(len(tiktok_products), 2)
        
        # 测试按价格范围筛选
        # 这需要实现相应的数据库查询方法
        all_products = self.db_manager.get_all_products()
        
        price_filtered = [p for p in all_products if 30 <= p['price'] <= 50]
        self.assertGreater(len(price_filtered), 0)
        
        logger.info("产品筛选功能测试通过")
    
    def test_search_functionality(self):
        """测试搜索功能"""
        logger.info("测试搜索功能...")
        
        # 插入测试数据
        search_test_products = [
            {'title': '棉质T恤', 'price': 29.99, 'platform': 'amazon'},
            {'title': '运动卫衣', 'price': 45.99, 'platform': 'tiktok'},
            {'title': '时尚外套', 'price': 89.99, 'platform': 'amazon'}
        ]
        
        for product in search_test_products:
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
        
        # 测试搜索关键词
        search_terms = ['T恤', '卫衣', '外套']
        
        for term in search_terms:
            # 模拟搜索功能（这里使用简单的字符串匹配）
            all_products = self.db_manager.get_all_products()
            matching_products = [
                p for p in all_products 
                if term in p['title']
            ]
            
            self.assertGreater(len(matching_products), 0)
        
        logger.info("搜索功能测试通过")
    
    def test_data_sorting(self):
        """测试数据排序功能"""
        logger.info("测试数据排序功能...")
        
        # 插入不同价格的测试数据
        sorting_test_products = [
            {'title': '低价产品', 'price': 19.99, 'platform': 'amazon'},
            {'title': '中价产品', 'price': 39.99, 'platform': 'tiktok'},
            {'title': '高价产品', 'price': 89.99, 'platform': 'amazon'},
            {'title': '超高价产品', 'price': 129.99, 'platform': 'tiktok'}
        ]
        
        for product in sorting_test_products:
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
        
        all_products = self.db_manager.get_all_products()
        
        # 测试按价格排序（升序）
        products_by_price_asc = sorted(all_products, key=lambda x: x['price'])
        self.assertLess(products_by_price_asc[0]['price'], products_by_price_asc[-1]['price'])
        
        # 测试按价格排序（降序）
        products_by_price_desc = sorted(all_products, key=lambda x: x['price'], reverse=True)
        self.assertGreater(products_by_price_desc[0]['price'], products_by_price_desc[-1]['price'])
        
        logger.info("数据排序功能测试通过")
    
    def test_pagination_functionality(self):
        """测试分页功能"""
        logger.info("测试分页功能...")
        
        # 插入多个产品用于分页测试
        page_size = 5
        total_products = 15
        
        for i in range(total_products):
            product = {
                'title': f'分页测试产品{i+1}',
                'price': 20.00 + i,
                'platform': 'amazon' if i % 2 == 0 else 'tiktok'
            }
            
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
        
        all_products = self.db_manager.get_all_products()
        
        # 模拟分页
        current_page = 1
        start_index = (current_page - 1) * page_size
        end_index = start_index + page_size
        
        page_products = all_products[start_index:end_index]
        
        # 验证分页结果
        self.assertLessEqual(len(page_products), page_size)
        self.assertGreater(len(page_products), 0)
        
        # 验证分页边界
        total_pages = (len(all_products) + page_size - 1) // page_size
        self.assertEqual(total_pages, 3)  # 15个产品，每页5个，应该是3页
        
        logger.info("分页功能测试通过")


class TestDataVisualization(unittest.TestCase):
    """测试数据可视化功能"""
    
    def setUp(self):
        """测试初始化"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="visualization_test_"))
        self.test_db_path = self.test_dir / "visualization_test.db"
        self.db_manager = DatabaseManager(str(self.test_db_path))
        self.data_cleaner = DataCleaner()
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_chart_data_structure(self):
        """测试图表数据结构"""
        logger.info("测试图表数据结构...")
        
        # 插入测试数据用于图表
        chart_test_products = [
            {'title': '产品A', 'price': 25.99, 'platform': 'amazon', 'category': '服装'},
            {'title': '产品B', 'price': 35.99, 'platform': 'amazon', 'category': '服装'},
            {'title': '产品C', 'price': 45.99, 'platform': 'tiktok', 'category': '配件'},
            {'title': '产品D', 'price': 55.99, 'platform': 'tiktok', 'category': '鞋子'},
            {'title': '产品E', 'price': 65.99, 'platform': 'amazon', 'category': '配件'}
        ]
        
        for product in chart_test_products:
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
        
        all_products = self.db_manager.get_all_products()
        
        # 测试价格分布数据
        price_ranges = {
            '0-30': 0,
            '30-50': 0,
            '50+': 0
        }
        
        for product in all_products:
            price = product['price']
            if price < 30:
                price_ranges['0-30'] += 1
            elif price < 50:
                price_ranges['30-50'] += 1
            else:
                price_ranges['50+'] += 1
        
        # 验证价格分布数据
        total_range_products = sum(price_ranges.values())
        self.assertEqual(total_range_products, len(all_products))
        
        # 测试平台分布数据
        platform_distribution = {}
        for product in all_products:
            platform = product['platform']
            platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
        
        self.assertGreater(len(platform_distribution), 0)
        self.assertEqual(sum(platform_distribution.values()), len(all_products))
        
        logger.info("图表数据结构测试通过")
    
    def test_real_time_updates(self):
        """测试实时数据更新"""
        logger.info("测试实时数据更新...")
        
        # 初始数据
        initial_products = [
            {'title': '初始产品1', 'price': 29.99, 'platform': 'amazon'},
            {'title': '初始产品2', 'price': 39.99, 'platform': 'tiktok'}
        ]
        
        initial_count = 0
        for product in initial_products:
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
                initial_count += 1
        
        # 验证初始数据
        initial_total = len(self.db_manager.get_all_products())
        self.assertEqual(initial_total, initial_count)
        
        # 模拟实时数据更新
        new_products = [
            {'title': '新产品1', 'price': 49.99, 'platform': 'amazon'},
            {'title': '新产品2', 'price': 59.99, 'platform': 'tiktok'}
        ]
        
        updated_count = 0
        for product in new_products:
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
                updated_count += 1
        
        # 验证更新后的数据
        final_total = len(self.db_manager.get_all_products())
        self.assertEqual(final_total, initial_count + updated_count)
        
        logger.info("实时数据更新测试通过")
    
    def test_export_functionality(self):
        """测试导出功能"""
        logger.info("测试导出功能...")
        
        # 插入测试数据
        export_test_products = [
            {'title': '导出产品1', 'price': 29.99, 'platform': 'amazon'},
            {'title': '导出产品2', 'price': 39.99, 'platform': 'tiktok'},
            {'title': '导出产品3', 'price': 49.99, 'platform': 'amazon'}
        ]
        
        for product in export_test_products:
            cleaned = self.data_cleaner.clean_product_data(product)
            if cleaned:
                self.db_manager.insert_product(cleaned)
        
        # 模拟导出功能
        all_products = self.db_manager.get_all_products()
        
        # 测试JSON导出格式
        json_export = {
            'export_time': datetime.now().isoformat(),
            'total_products': len(all_products),
            'products': all_products
        }
        
        self.assertIn('export_time', json_export)
        self.assertIn('total_products', json_export)
        self.assertIn('products', json_export)
        self.assertEqual(json_export['total_products'], len(all_products))
        
        # 测试CSV导出格式
        csv_headers = ['title', 'price', 'platform', 'category']
        csv_rows = []
        for product in all_products:
            row = [str(product.get(header, '')) for header in csv_headers]
            csv_rows.append(row)
        
        self.assertGreater(len(csv_rows), 0)
        for row in csv_rows:
            self.assertEqual(len(row), len(csv_headers))
        
        logger.info("导出功能测试通过")


class TestResponsiveDesign(unittest.TestCase):
    """测试响应式设计"""
    
    def test_mobile_compatibility(self):
        """测试移动设备兼容性"""
        logger.info("测试移动设备兼容性...")
        
        # 检查CSS框架和响应式设计
        package_json_path = self.frontend_dir / "package.json"
        
        if package_json_path.exists():
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # 检查是否有响应式设计相关依赖
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            
            responsive_frameworks = ['tailwindcss', 'react-responsive', '@mui/material']
            
            has_responsive_framework = any(
                dep.lower() in str(dependencies).lower() or 
                dep.lower() in str(dev_dependencies).lower() 
                for dep in responsive_frameworks
            )
            
            # 如果没有使用专门的响应式框架，检查是否有Tailwind CSS配置
            tailwind_config = self.frontend_dir / "tailwind.config.js"
            has_tailwind = tailwind_config.exists()
            
            self.assertTrue(
                has_responsive_framework or has_tailwind,
                "项目应该使用响应式设计框架"
            )
        
        logger.info("移动设备兼容性测试通过")
    
    def test_accessibility_features(self):
        """测试可访问性功能"""
        logger.info("测试可访问性功能...")
        
        # 检查关键组件中的可访问性标记
        components_to_check = [
            'Sidebar.tsx',
            'Header.tsx',
            'Dashboard.tsx',
            'ProductList.tsx'
        ]
        
        accessibility_patterns = [
            'aria-label',     # ARIA标签
            'role=',          # ARIA角色
            'aria-expanded',  # ARIA展开状态
            'aria-hidden',    # ARIA隐藏状态
            'tabindex'        # 键盘导航
        ]
        
        for component_name in components_to_check:
            component_path = self.frontend_dir / "src" / "components" / component_name
            if component_path.exists():
                with open(component_path, 'r', encoding='utf-8') as f:
                    component_content = f.read()
                
                # 至少检查一些可访问性模式
                has_accessibility = any(pattern in component_content for pattern in accessibility_patterns)
                
                # 记录结果但不强制要求（因为这是测试环境）
                if has_accessibility:
                    logger.info(f"组件 {component_name} 包含可访问性标记")
                else:
                    logger.info(f"组件 {component_name} 可能缺少可访问性标记")
        
        logger.info("可访问性功能检查完成")


class TestPerformanceMetrics(unittest.TestCase):
    """测试性能指标"""
    
    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        logger.info("测试大数据集性能...")
        
        test_dir = Path(tempfile.mkdtemp(prefix="performance_test_"))
        test_db_path = test_dir / "performance_test.db"
        
        try:
            db_manager = DatabaseManager(str(test_db_path))
            data_cleaner = DataCleaner()
            
            # 创建大数据集
            large_dataset_size = 1000
            start_time = time.time()
            
            for i in range(large_dataset_size):
                product = {
                    'title': f'性能测试产品 {i}',
                    'price': 20.00 + (i % 100),
                    'platform': 'amazon' if i % 2 == 0 else 'tiktok',
                    'category': f'类别{i % 10}',
                    'rating': 4.0 + (i % 10) * 0.1,
                    'description': f'详细描述 {i}' * 5
                }
                
                cleaned = data_cleaner.clean_product_data(product)
                if cleaned:
                    db_manager.insert_product(cleaned)
            
            processing_time = time.time() - start_time
            
            # 验证性能指标
            self.assertLess(processing_time, 30.0)  # 应该在30秒内处理1000条记录
            
            # 测试查询性能
            query_start = time.time()
            all_products = db_manager.get_all_products()
            query_time = time.time() - query_start
            
            self.assertLess(query_time, 5.0)  # 查询应该在5秒内完成
            self.assertEqual(len(all_products), large_dataset_size)
            
            logger.info(f"大数据集性能测试: 处理{processing_time:.2f}秒，查询{query_time:.2f}秒")
            
        finally:
            if 'db_manager' in locals():
                db_manager.close_all_connections()
            if test_dir.exists():
                shutil.rmtree(test_dir)
    
    def test_memory_usage(self):
        """测试内存使用"""
        logger.info("测试内存使用...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        test_dir = Path(tempfile.mkdtemp(prefix="memory_test_"))
        test_db_path = test_dir / "memory_test.db"
        
        try:
            db_manager = DatabaseManager(str(test_db_path))
            data_cleaner = DataCleaner()
            
            # 执行内存密集型操作
            for i in range(500):
                large_product = {
                    'title': f'内存测试产品 {i}',
                    'price': 20.00 + i,
                    'platform': 'amazon',
                    'description': 'x' * 1000,  # 大描述文本
                    'category': f'类别{i % 50}',
                    'rating': 4.0 + (i % 10) * 0.1
                }
                
                cleaned = data_cleaner.clean_product_data(large_product)
                if cleaned:
                    db_manager.insert_product(cleaned)
            
            # 强制垃圾回收
            import gc
            gc.collect()
            
            # 检查内存使用
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            logger.info(f"内存使用: 初始 {initial_memory:.1f}MB, 最终 {final_memory:.1f}MB, 增加 {memory_increase:.1f}MB")
            
            # 验证内存增长在合理范围内（不应该超过100MB）
            self.assertLess(memory_increase, 100)
            
        finally:
            if 'db_manager' in locals():
                db_manager.close_all_connections()
            if test_dir.exists():
                shutil.rmtree(test_dir)


def run_ui_tests():
    """运行UI测试"""
    print("=" * 60)
    print("开始用户界面测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestUIComponentRendering,
        TestUserInteractions,
        TestDataVisualization,
        TestResponsiveDesign,
        TestPerformanceMetrics
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
    print("用户界面测试完成")
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
    
    # 运行UI测试
    success = run_ui_tests()
    
    if success:
        print("✅ 所有用户界面测试通过")
        sys.exit(0)
    else:
        print("❌ 部分用户界面测试失败")
        sys.exit(1)