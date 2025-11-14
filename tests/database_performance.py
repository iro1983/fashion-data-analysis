#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库性能测试模块

测试内容包括：
1. SQLite数据库读写性能
2. 大量数据查询速度
3. 并发访问稳定性
4. 索引优化效果

测试指标：
- 数据库查询: < 100ms
- 数据插入速度: > 1000 records/second
- 并发连接数: > 50
"""

import sqlite3
import time
import threading
import random
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
import json
from contextlib import contextmanager
from pathlib import Path
import logging

# 导入数据库管理器
import sys
sys.path.append(str(Path(__file__).parent.parent / "code"))
from database import DatabaseManager, DatabaseConfig, create_sample_data

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabasePerformanceTest:
    """数据库性能测试类"""
    
    def __init__(self, test_db_path: str = "tests/test_performance.db"):
        """初始化测试环境"""
        self.test_db_path = Path(test_db_path)
        self.test_db_path.parent.mkdir(exist_ok=True)
        
        # 配置测试数据库
        self.config = DatabaseConfig(
            db_path=str(self.test_db_path),
            backup_dir=str(self.test_db_path.parent / "backup"),
            connection_pool_size=20
        )
        
        self.db_manager = DatabaseManager(self.config)
        self.test_results = {}
        
    def setup_test_data(self, data_sizes: List[int] = [50, 200, 500]):
        """设置测试数据"""
        logger.info("开始准备测试数据...")
        
        for size in data_sizes:
            logger.info(f"生成 {size} 条测试数据...")
            
            # 生成测试产品数据
            products = []
            for i in range(size):
                product = {
                    'product_name': f"测试产品 {i+1}",
                    'platform': random.choice(['tiktok', 'amazon']),
                    'category': random.choice(['tshirt', 'hoodie', 'sweatshirt']),
                    'price': round(random.uniform(15.99, 89.99), 2),
                    'original_price': round(random.uniform(20.99, 99.99), 2),
                    'currency': 'USD',
                    'sales_count': random.randint(100, 10000),
                    'rating': round(random.uniform(3.0, 5.0), 1),
                    'review_count': random.randint(10, 500),
                    'product_url': f"https://test.com/product/{i+1}",
                    'store_url': f"https://test.com/store/merchant_{i%10}",
                    'store_name': f"店铺 {i%10}",
                    'main_image_url': f"https://cdn.test.com/product_{i+1}.jpg",
                    'image_urls': json.dumps([f"https://cdn.test.com/product_{i+1}_{j}.jpg" for j in range(3)]),
                    'like_count': random.randint(50, 1000),
                    'share_count': random.randint(10, 200),
                    'comment_count': random.randint(5, 100),
                    'view_count': random.randint(500, 5000),
                    'data_source': 'performance_test',
                    'keywords': json.dumps(['hot', 'trending', 'fashion']),
                    'notes': f'性能测试数据 #{i+1}'
                }
                products.append(product)
            
            # 批量插入数据
            start_time = time.time()
            for product in products:
                self.db_manager.insert_product(product)
            
            insert_time = time.time() - start_time
            rate = size / insert_time
            
            logger.info(f"插入 {size} 条数据用时: {insert_time:.2f}s, 速率: {rate:.1f} records/s")
            
            # 记录结果
            self.test_results[f'insert_{size}_records'] = {
                'count': size,
                'time': insert_time,
                'rate': rate
            }
    
    def test_query_performance(self):
        """测试查询性能"""
        logger.info("开始测试查询性能...")
        
        test_queries = [
            ('按平台筛选', lambda: self.db_manager.get_products(platform='tiktok', limit=100)),
            ('按分类筛选', lambda: self.db_manager.get_products(category='hoodie', limit=100)),
            ('平台+分类筛选', lambda: self.db_manager.get_products(platform='amazon', category='tshirt', limit=100)),
            ('获取全部数据', lambda: self.db_manager.get_products(limit=1000)),
            ('获取统计信息', lambda: self.db_manager.get_database_stats())
        ]
        
        query_results = {}
        
        for query_name, query_func in test_queries:
            times = []
            for _ in range(10):  # 每个查询运行10次取平均
                start_time = time.time()
                result = query_func()
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times) * 1000  # 转换为毫秒
            min_time = min(times) * 1000
            max_time = max(times) * 1000
            std_dev = statistics.stdev(times) * 1000 if len(times) > 1 else 0
            
            query_results[query_name] = {
                'avg_time_ms': round(avg_time, 2),
                'min_time_ms': round(min_time, 2),
                'max_time_ms': round(max_time, 2),
                'std_dev_ms': round(std_dev, 2),
                'target_met': avg_time < 100  # < 100ms目标
            }
            
            logger.info(f"{query_name}: 平均 {avg_time:.2f}ms (目标: < 100ms)")
        
        self.test_results['query_performance'] = query_results
    
    def test_concurrent_access(self, max_workers: int = 10):
        """测试并发访问性能"""
        logger.info(f"开始测试并发访问 (最多 {max_workers} 个并发)...")
        
        concurrent_results = {}
        
        def concurrent_query_worker(worker_id):
            """并发查询工作函数"""
            times = []
            errors = 0
            
            for _ in range(20):  # 每个工作线程执行20次查询
                try:
                    start_time = time.time()
                    self.db_manager.get_products(platform='tiktok', limit=50)
                    end_time = time.time()
                    times.append(end_time - start_time)
                except Exception as e:
                    errors += 1
            
            return {
                'worker_id': worker_id,
                'times': times,
                'errors': errors,
                'success_rate': (20 - errors) / 20
            }
        
        # 执行并发测试
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(concurrent_query_worker, i) for i in range(max_workers)]
            
            worker_results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    worker_results.append(result)
                except Exception as e:
                    logger.error(f"并发测试出错: {e}")
        
        total_time = time.time() - start_time
        
        # 分析结果
        all_times = []
        total_errors = 0
        success_rates = []
        
        for result in worker_results:
            all_times.extend(result['times'])
            total_errors += result['errors']
            success_rates.append(result['success_rate'])
        
        concurrent_results = {
            'total_workers': max_workers,
            'total_time': total_time,
            'avg_query_time_ms': round(statistics.mean(all_times) * 1000, 2),
            'min_query_time_ms': round(min(all_times) * 1000, 2),
            'max_query_time_ms': round(max(all_times) * 1000, 2),
            'total_queries': len(all_times),
            'total_errors': total_errors,
            'overall_success_rate': (len(all_times) - total_errors) / len(all_times),
            'avg_worker_success_rate': statistics.mean(success_rates),
            'target_met': total_errors == 0 and statistics.mean(all_times) < 0.1
        }
        
        self.test_results['concurrent_access'] = concurrent_results
        
        logger.info(f"并发测试完成: {len(all_times)} 次查询, 成功率: {concurrent_results['overall_success_rate']:.2%}")
    
    def test_index_performance(self):
        """测试索引优化效果"""
        logger.info("测试索引优化效果...")
        
        # 创建无索引的测试表
        def test_without_index():
            with sqlite3.connect(':memory:') as conn:
                cursor = conn.cursor()
                
                # 创建无索引表
                cursor.execute("""
                    CREATE TABLE test_products (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        platform TEXT,
                        category TEXT,
                        price REAL
                    )
                """)
                
                # 插入大量数据
                for i in range(1000):
                    cursor.execute("""
                        INSERT INTO test_products (name, platform, category, price)
                        VALUES (?, ?, ?, ?)
                    """, (f"Product {i}", random.choice(['tiktok', 'amazon']), 
                         random.choice(['tshirt', 'hoodie', 'sweatshirt']), 
                         random.uniform(15, 89)))
                
                conn.commit()
                
                # 测试查询性能
                start_time = time.time()
                for _ in range(100):
                    cursor.execute("""
                        SELECT * FROM test_products 
                        WHERE platform = ? AND category = ?
                    """, ('tiktok', 'hoodie'))
                    cursor.fetchall()
                
                return time.time() - start_time
        
        # 创建有索引的测试表
        def test_with_index():
            with sqlite3.connect(':memory:') as conn:
                cursor = conn.cursor()
                
                # 创建有索引表
                cursor.execute("""
                    CREATE TABLE test_products (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        platform TEXT,
                        category TEXT,
                        price REAL
                    )
                """)
                
                # 创建索引
                cursor.execute("CREATE INDEX idx_platform_category ON test_products(platform, category)")
                
                # 插入相同数据
                for i in range(1000):
                    cursor.execute("""
                        INSERT INTO test_products (name, platform, category, price)
                        VALUES (?, ?, ?, ?)
                    """, (f"Product {i}", random.choice(['tiktok', 'amazon']), 
                         random.choice(['tshirt', 'hoodie', 'sweatshirt']), 
                         random.uniform(15, 89)))
                
                conn.commit()
                
                # 测试查询性能
                start_time = time.time()
                for _ in range(100):
                    cursor.execute("""
                        SELECT * FROM test_products 
                        WHERE platform = ? AND category = ?
                    """, ('tiktok', 'hoodie'))
                    cursor.fetchall()
                
                return time.time() - start_time
        
        # 执行测试
        time_without_index = test_without_index()
        time_with_index = test_with_index()
        
        improvement = ((time_without_index - time_with_index) / time_without_index) * 100
        
        index_results = {
            'time_without_index': round(time_without_index, 4),
            'time_with_index': round(time_with_index, 4),
            'improvement_percent': round(improvement, 2),
            'target_met': improvement > 50  # 目标提升50%以上
        }
        
        self.test_results['index_performance'] = index_results
        
        logger.info(f"索引优化: 性能提升 {improvement:.1f}%")
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        logger.info("测试内存使用情况...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行大量查询测试内存变化
        for _ in range(10):
            products = self.db_manager.get_products(limit=1000)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_results = {
            'initial_memory_mb': round(initial_memory, 2),
            'peak_memory_mb': round(peak_memory, 2),
            'memory_increase_mb': round(peak_memory - initial_memory, 2),
            'target_met': peak_memory - initial_memory < 100  # 增长不超过100MB
        }
        
        self.test_results['memory_usage'] = memory_results
        
        logger.info(f"内存使用: {initial_memory:.1f}MB -> {peak_memory:.1f}MB")
    
    def run_all_tests(self):
        """运行所有性能测试"""
        logger.info("开始数据库性能测试...")
        
        try:
            # 准备测试数据
            self.setup_test_data([50, 200, 500])
            
            # 运行各项测试
            self.test_query_performance()
            self.test_concurrent_access(10)
            self.test_index_performance()
            self.test_memory_usage()
            
            logger.info("数据库性能测试完成")
            
        except Exception as e:
            logger.error(f"测试过程中出错: {e}")
            raise
        
        finally:
            # 清理测试数据
            self.cleanup()
    
    def cleanup(self):
        """清理测试环境"""
        try:
            self.db_manager.close()
            if self.test_db_path.exists():
                self.test_db_path.unlink()
            logger.info("测试环境清理完成")
        except Exception as e:
            logger.warning(f"清理环境时出错: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """生成性能测试报告"""
        return {
            'test_type': 'database_performance',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'database_type': 'SQLite',
            'test_results': self.test_results,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'overall_status': 'unknown'
        }
        
        # 检查各项测试是否达标
        test_targets = {
            'query_performance': lambda results: all(
                result['target_met'] for result in results.values()
            ),
            'concurrent_access': lambda results: results['target_met'],
            'index_performance': lambda results: results['target_met'],
            'memory_usage': lambda results: results['target_met']
        }
        
        for test_name, target_func in test_targets.items():
            if test_name in self.test_results:
                summary['total_tests'] += 1
                try:
                    if target_func(self.test_results[test_name]):
                        summary['passed_tests'] += 1
                    else:
                        summary['failed_tests'] += 1
                except Exception:
                    summary['failed_tests'] += 1
        
        if summary['passed_tests'] == summary['total_tests']:
            summary['overall_status'] = 'passed'
        elif summary['passed_tests'] > 0:
            summary['overall_status'] = 'partial'
        else:
            summary['overall_status'] = 'failed'
        
        return summary


def run_database_performance_tests():
    """运行数据库性能测试的主函数"""
    print("=" * 60)
    print("数据库性能测试")
    print("=" * 60)
    
    tester = DatabasePerformanceTest()
    
    try:
        # 运行测试
        tester.run_all_tests()
        
        # 生成报告
        report = tester.generate_report()
        
        # 输出结果
        print("\n📊 测试结果摘要:")
        summary = report['summary']
        print(f"   总测试项: {summary['total_tests']}")
        print(f"   通过测试: {summary['passed_tests']}")
        print(f"   失败测试: {summary['failed_tests']}")
        print(f"   整体状态: {summary['overall_status']}")
        
        # 详细结果
        print("\n📈 详细测试结果:")
        for test_name, results in report['test_results'].items():
            print(f"\n{test_name}:")
            if isinstance(results, dict):
                for key, value in results.items():
                    if key.endswith('_met'):  # 跳过布尔结果
                        status = "✅" if value else "❌"
                        print(f"   {status} {key}: {value}")
                    else:
                        print(f"   {key}: {value}")
        
        # 保存详细报告
        report_file = Path("tests/database_performance_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        raise
    finally:
        tester.cleanup()


if __name__ == "__main__":
    run_database_performance_tests()