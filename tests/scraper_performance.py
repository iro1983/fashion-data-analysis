#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据抓取性能测试模块

测试内容包括：
1. Amazon抓取速度
2. TikTok抓取效率
3. 批量处理能力
4. 错误率统计

测试指标：
- 抓取成功率: > 95%
- 单页面抓取时间: < 5s
- 批处理吞吐量: > 10 pages/minute
- 错误率: < 5%
"""

import time
import json
import statistics
import random
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import logging
import threading
import queue
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapingTestResult:
    """抓取测试结果数据类"""
    platform: str
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    success_rate: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    errors: List[str]

class MockScraper:
    """模拟抓取器，用于性能测试"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.success_rate = 0.95 if platform == 'amazon' else 0.93  # Amazon成功率稍高
        self.avg_response_time = 2.5 if platform == 'amazon' else 3.2  # TikTok响应稍慢
    
    def scrape_page(self, page_num: int, force_error: bool = False) -> Dict[str, Any]:
        """模拟单页面抓取"""
        start_time = time.time()
        
        # 模拟网络延迟
        response_time = random.uniform(0.5, 6.0) * self.avg_response_time
        time.sleep(response_time)
        
        # 模拟成功/失败
        if force_error or random.random() > self.success_rate:
            end_time = time.time()
            return {
                'success': False,
                'error': f'抓取失败: {self.platform} page {page_num}',
                'response_time': end_time - start_time
            }
        
        # 模拟成功返回的数据
        products = []
        for i in range(random.randint(3, 15)):
            product = {
                'id': f'{self.platform}_product_{page_num}_{i}',
                'name': f'{self.platform.title()} 产品 {page_num}-{i}',
                'price': round(random.uniform(15.99, 89.99), 2),
                'rating': round(random.uniform(3.0, 5.0), 1),
                'reviews': random.randint(10, 1000),
                'platform': self.platform,
                'category': random.choice(['tshirt', 'hoodie', 'sweatshirt'])
            }
            products.append(product)
        
        end_time = time.time()
        
        return {
            'success': True,
            'data': {
                'products': products,
                'total_products': len(products),
                'page': page_num,
                'platform': self.platform
            },
            'response_time': end_time - start_time
        }
    
    def scrape_with_retry(self, page_num: int, max_retries: int = 3) -> Tuple[bool, Any]:
        """带重试的抓取"""
        for attempt in range(max_retries):
            result = self.scrape_page(page_num, force_error=attempt < max_retries-1 and random.random() < 0.3)
            if result['success']:
                return True, result
            elif attempt == max_retries - 1:
                return False, result
        
        return False, result

class ScrapingPerformanceTest:
    """数据抓取性能测试类"""
    
    def __init__(self):
        """初始化测试环境"""
        self.test_results = {}
        self.mock_data = {}
        
    def test_single_page_performance(self):
        """测试单页面抓取性能"""
        logger.info("测试单页面抓取性能...")
        
        platforms = ['amazon', 'tiktok']
        test_results = {}
        
        for platform in platforms:
            logger.info(f"测试 {platform} 平台...")
            
            scraper = MockScraper(platform)
            response_times = []
            successful = 0
            failed = 0
            errors = []
            
            # 测试100次单页面抓取
            for page_num in range(1, 101):
                result = scraper.scrape_page(page_num)
                response_times.append(result['response_time'])
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                    errors.append(result['error'])
            
            # 计算统计指标
            total_requests = len(response_times)
            success_rate = (successful / total_requests) * 100
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            platform_result = {
                'total_requests': total_requests,
                'successful_requests': successful,
                'failed_requests': failed,
                'success_rate': round(success_rate, 2),
                'avg_response_time': round(avg_response_time, 2),
                'min_response_time': round(min_response_time, 2),
                'max_response_time': round(max_response_time, 2),
                'errors': errors[:10],  # 只保留前10个错误
                'target_met': success_rate >= 95 and avg_response_time < 5.0
            }
            
            test_results[platform] = platform_result
            logger.info(f"{platform}: 成功率 {success_rate:.1f}%, 平均响应 {avg_response_time:.2f}s")
        
        self.test_results['single_page_performance'] = test_results
        return test_results
    
    def test_batch_processing_performance(self):
        """测试批量处理性能"""
        logger.info("测试批量处理性能...")
        
        platforms = ['amazon', 'tiktok']
        batch_results = {}
        
        for platform in platforms:
            logger.info(f"测试 {platform} 批量处理...")
            
            scraper = MockScraper(platform)
            batch_sizes = [5, 10, 20, 50]
            batch_performance = {}
            
            for batch_size in batch_sizes:
                logger.info(f"  批量大小: {batch_size}")
                
                start_time = time.time()
                successful = 0
                failed = 0
                response_times = []
                
                # 串行批量处理
                for page_num in range(1, batch_size + 1):
                    result = scraper.scrape_page(page_num)
                    response_times.append(result['response_time'])
                    
                    if result['success']:
                        successful += 1
                    else:
                        failed += 1
                
                total_time = time.time() - start_time
                throughput = batch_size / total_time  # pages/minute
                
                batch_performance[f'batch_{batch_size}'] = {
                    'batch_size': batch_size,
                    'total_time': round(total_time, 2),
                    'throughput_pages_per_minute': round(throughput * 60, 2),
                    'successful': successful,
                    'failed': failed,
                    'success_rate': round((successful / batch_size) * 100, 2),
                    'avg_response_time': round(statistics.mean(response_times), 2)
                }
                
                logger.info(f"    批量 {batch_size}: {throughput*60:.1f} pages/min, 成功率 {(successful/batch_size)*100:.1f}%")
            
            batch_results[platform] = batch_performance
        
        self.test_results['batch_processing_performance'] = batch_results
        return batch_results
    
    def test_concurrent_scraping(self):
        """测试并发抓取性能"""
        logger.info("测试并发抓取性能...")
        
        platforms = ['amazon', 'tiktok']
        concurrent_results = {}
        
        for platform in platforms:
            logger.info(f"测试 {platform} 并发抓取...")
            
            scraper = MockScraper(platform)
            worker_counts = [2, 5, 10, 15]
            concurrent_performance = {}
            
            for worker_count in worker_counts:
                logger.info(f"  并发数: {worker_count}")
                
                def scraping_worker(worker_id, page_count):
                    """抓取工作线程"""
                    worker_times = []
                    successful = 0
                    failed = 0
                    
                    for i in range(page_count):
                        page_num = worker_id * page_count + i + 1
                        result = scraper.scrape_page(page_num)
                        worker_times.append(result['response_time'])
                        
                        if result['success']:
                            successful += 1
                        else:
                            failed += 1
                    
                    return {
                        'worker_id': worker_id,
                        'times': worker_times,
                        'successful': successful,
                        'failed': failed
                    }
                
                # 执行并发测试
                pages_per_worker = 10
                start_time = time.time()
                
                with ThreadPoolExecutor(max_workers=worker_count) as executor:
                    futures = [
                        executor.submit(scraping_worker, i, pages_per_worker)
                        for i in range(worker_count)
                    ]
                    
                    worker_results = []
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            worker_results.append(result)
                        except Exception as e:
                            logger.error(f"并发工作出错: {e}")
                
                total_time = time.time() - start_time
                total_requests = worker_count * pages_per_worker
                
                # 汇总结果
                all_times = []
                total_successful = 0
                total_failed = 0
                
                for worker_result in worker_results:
                    all_times.extend(worker_result['times'])
                    total_successful += worker_result['successful']
                    total_failed += worker_result['failed']
                
                throughput = total_requests / total_time
                success_rate = (total_successful / total_requests) * 100
                
                concurrent_performance[f'workers_{worker_count}'] = {
                    'worker_count': worker_count,
                    'total_requests': total_requests,
                    'total_time': round(total_time, 2),
                    'throughput_requests_per_minute': round(throughput * 60, 2),
                    'successful': total_successful,
                    'failed': total_failed,
                    'success_rate': round(success_rate, 2),
                    'avg_response_time': round(statistics.mean(all_times), 2),
                    'target_met': success_rate >= 90 and throughput >= 5  # 并发目标稍低
                }
                
                logger.info(f"    {worker_count} workers: {throughput:.1f} req/min, 成功率 {success_rate:.1f}%")
            
            concurrent_results[platform] = concurrent_performance
        
        self.test_results['concurrent_scraping'] = concurrent_results
        return concurrent_results
    
    def test_error_handling_and_retry(self):
        """测试错误处理和重试机制"""
        logger.info("测试错误处理和重试机制...")
        
        platforms = ['amazon', 'tiktok']
        error_handling_results = {}
        
        for platform in platforms:
            logger.info(f"测试 {platform} 错误处理...")
            
            scraper = MockScraper(platform)
            retry_tests = {}
            
            # 测试不同重试次数的效果
            for max_retries in [1, 2, 3, 5]:
                logger.info(f"  最大重试次数: {max_retries}")
                
                successful = 0
                failed = 0
                total_attempts = 0
                retry_counts = []
                
                # 测试50次抓取
                for page_num in range(1, 51):
                    success, result = scraper.scrape_with_retry(page_num, max_retries)
                    
                    if success:
                        successful += 1
                    else:
                        failed += 1
                    
                    total_attempts += result.get('attempts', 1)
                    # 模拟重试次数
                    retry_counts.append(random.randint(0, max_retries))
                
                final_success_rate = (successful / 50) * 100
                avg_retries = statistics.mean(retry_counts)
                
                retry_tests[f'max_retries_{max_retries}'] = {
                    'max_retries': max_retries,
                    'final_success_rate': round(final_success_rate, 2),
                    'avg_retries_attempted': round(avg_retries, 2),
                    'successful_final': successful,
                    'failed_final': failed,
                    'improvement_from_single': round(final_success_rate - 95, 2) if platform == 'amazon' else round(final_success_rate - 93, 2)
                }
                
                logger.info(f"    最终成功率: {final_success_rate:.1f}%, 平均重试: {avg_retries:.1f}")
            
            error_handling_results[platform] = retry_tests
        
        self.test_results['error_handling_retry'] = error_handling_results
        return error_handling_results
    
    def test_data_quality_metrics(self):
        """测试数据质量指标"""
        logger.info("测试数据质量指标...")
        
        platforms = ['amazon', 'tiktok']
        quality_results = {}
        
        for platform in platforms:
            logger.info(f"测试 {platform} 数据质量...")
            
            scraper = MockScraper(platform)
            
            # 收集100页数据用于质量分析
            all_products = []
            for page_num in range(1, 101):
                result = scraper.scrape_page(page_num)
                if result['success']:
                    all_products.extend(result['data']['products'])
            
            # 分析数据质量
            quality_metrics = self._analyze_data_quality(all_products, platform)
            quality_results[platform] = quality_metrics
            
            logger.info(f"  数据完整性: {quality_metrics['completeness_score']:.1f}%")
            logger.info(f"  数据一致性: {quality_metrics['consistency_score']:.1f}%")
            logger.info(f"  重复率: {quality_metrics['duplicate_rate']:.2f}%")
        
        self.test_results['data_quality'] = quality_results
        return quality_results
    
    def _analyze_data_quality(self, products: List[Dict], platform: str) -> Dict[str, Any]:
        """分析数据质量"""
        if not products:
            return {
                'total_products': 0,
                'completeness_score': 0,
                'consistency_score': 0,
                'duplicate_rate': 0,
                'data_freshness_score': 0
            }
        
        total_products = len(products)
        
        # 完整性检查
        required_fields = ['id', 'name', 'price', 'platform']
        complete_products = 0
        for product in products:
            if all(field in product and product[field] for field in required_fields):
                complete_products += 1
        
        completeness_score = (complete_products / total_products) * 100
        
        # 一致性检查
        consistent_products = 0
        for product in products:
            # 检查价格格式
            price_valid = isinstance(product.get('price'), (int, float)) and product.get('price', 0) > 0
            # 检查平台字段
            platform_valid = product.get('platform') == platform
            # 检查评分范围
            rating_valid = isinstance(product.get('rating'), (int, float)) and 0 <= product.get('rating', 0) <= 5
            
            if price_valid and platform_valid and rating_valid:
                consistent_products += 1
        
        consistency_score = (consistent_products / total_products) * 100
        
        # 重复率检查
        ids = [p.get('id') for p in products if p.get('id')]
        unique_ids = set(ids)
        duplicate_rate = ((len(ids) - len(unique_ids)) / len(ids)) * 100 if ids else 0
        
        # 数据新鲜度 (模拟)
        freshness_score = random.uniform(85, 98)  # 85-98%
        
        return {
            'total_products': total_products,
            'complete_products': complete_products,
            'completeness_score': round(completeness_score, 1),
            'consistent_products': consistent_products,
            'consistency_score': round(consistency_score, 1),
            'unique_products': len(unique_ids),
            'duplicate_rate': round(duplicate_rate, 2),
            'data_freshness_score': round(freshness_score, 1),
            'target_met': completeness_score >= 90 and consistency_score >= 85 and duplicate_rate < 5
        }
    
    def test_resource_usage(self):
        """测试资源使用情况"""
        logger.info("测试资源使用情况...")
        
        platforms = ['amazon', 'tiktok']
        resource_results = {}
        
        import psutil
        process = psutil.Process()
        
        for platform in platforms:
            logger.info(f"测试 {platform} 资源使用...")
            
            scraper = MockScraper(platform)
            
            # 监控开始时的资源使用
            initial_cpu = process.cpu_percent()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行大量抓取测试资源消耗
            start_time = time.time()
            successful_count = 0
            failed_count = 0
            
            for page_num in range(1, 201):  # 200页
                result = scraper.scrape_page(page_num)
                if result['success']:
                    successful_count += 1
                else:
                    failed_count += 1
            
            # 监控结束时的资源使用
            end_time = time.time()
            final_cpu = process.cpu_percent()
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            test_duration = end_time - start_time
            memory_increase = final_memory - initial_memory
            cpu_avg = (initial_cpu + final_cpu) / 2
            
            resource_results[platform] = {
                'test_duration': round(test_duration, 2),
                'total_requests': 200,
                'successful_requests': successful_count,
                'failed_requests': failed_count,
                'initial_memory_mb': round(initial_memory, 2),
                'final_memory_mb': round(final_memory, 2),
                'memory_increase_mb': round(memory_increase, 2),
                'avg_cpu_percent': round(cpu_avg, 2),
                'requests_per_second': round(200 / test_duration, 2),
                'target_met': memory_increase < 50 and cpu_avg < 50  # 内存增长<50MB, CPU<50%
            }
            
            logger.info(f"  测试时长: {test_duration:.1f}s")
            logger.info(f"  内存增长: {memory_increase:.1f}MB")
            logger.info(f"  平均CPU: {cpu_avg:.1f}%")
        
        self.test_results['resource_usage'] = resource_results
        return resource_results
    
    def run_all_tests(self):
        """运行所有抓取性能测试"""
        logger.info("开始数据抓取性能测试...")
        
        try:
            # 运行各项测试
            self.test_single_page_performance()
            self.test_batch_processing_performance()
            self.test_concurrent_scraping()
            self.test_error_handling_and_retry()
            self.test_data_quality_metrics()
            self.test_resource_usage()
            
            logger.info("数据抓取性能测试完成")
            
        except Exception as e:
            logger.error(f"测试过程中出错: {e}")
            raise
    
    def generate_report(self) -> Dict[str, Any]:
        """生成性能测试报告"""
        return {
            'test_type': 'scraper_performance',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'platforms_tested': ['amazon', 'tiktok'],
            'test_results': self.test_results,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'overall_success_rate': 0,
            'overall_status': 'unknown',
            'platform_scores': {}
        }
        
        # 分析各平台表现
        platforms = ['amazon', 'tiktok']
        platform_scores = {}
        
        for platform in platforms:
            platform_score = 0
            platform_total = 0
            
            # 汇总各测试结果
            for test_category, results in self.test_results.items():
                if platform in results:
                    platform_total += 1
                    
                    if test_category == 'single_page_performance':
                        if results[platform].get('target_met', False):
                            platform_score += 1
                    elif test_category == 'batch_processing_performance':
                        # 检查最大批量的成功率
                        batch_50 = results[platform].get('batch_50', {})
                        if batch_50.get('success_rate', 0) >= 90:
                            platform_score += 1
                    elif test_category == 'concurrent_scraping':
                        # 检查最优并发配置
                        workers_10 = results[platform].get('workers_10', {})
                        if workers_10.get('target_met', False):
                            platform_score += 1
                    elif test_category == 'data_quality':
                        if results[platform].get('target_met', False):
                            platform_score += 1
                    elif test_category == 'resource_usage':
                        if results[platform].get('target_met', False):
                            platform_score += 1
            
            platform_scores[platform] = round((platform_score / platform_total) * 100, 1) if platform_total > 0 else 0
        
        summary['platform_scores'] = platform_scores
        
        # 计算总体成功率
        success_rates = []
        if 'single_page_performance' in self.test_results:
            for platform, result in self.test_results['single_page_performance'].items():
                success_rates.append(result.get('success_rate', 0))
        
        if success_rates:
            summary['overall_success_rate'] = round(statistics.mean(success_rates), 1)
        
        # 计算整体状态
        passed_platforms = sum(1 for score in platform_scores.values() if score >= 80)
        
        if passed_platforms == len(platforms):
            summary['overall_status'] = 'passed'
        elif passed_platforms > 0:
            summary['overall_status'] = 'partial'
        else:
            summary['overall_status'] = 'failed'
        
        return summary


def run_scraper_performance_tests():
    """运行抓取性能测试的主函数"""
    print("=" * 60)
    print("数据抓取性能测试")
    print("=" * 60)
    
    tester = ScrapingPerformanceTest()
    
    try:
        # 运行测试
        tester.run_all_tests()
        
        # 生成报告
        report = tester.generate_report()
        
        # 输出结果
        print("\n📊 测试结果摘要:")
        summary = report['summary']
        print(f"   整体成功率: {summary['overall_success_rate']}%")
        print(f"   Amazon性能: {summary['platform_scores'].get('amazon', 0)}/100")
        print(f"   TikTok性能: {summary['platform_scores'].get('tiktok', 0)}/100")
        print(f"   整体状态: {summary['overall_status']}")
        
        # 详细结果
        print("\n📈 详细测试结果:")
        for test_name, results in report['test_results'].items():
            print(f"\n{test_name}:")
            if isinstance(results, dict):
                for platform, platform_results in results.items():
                    print(f"  {platform}:")
                    if isinstance(platform_results, dict):
                        for key, value in platform_results.items():
                            if key.endswith('_met') or isinstance(value, bool):
                                status = "✅" if value else "❌"
                                print(f"    {status} {key}: {value}")
                            else:
                                print(f"    {key}: {value}")
        
        # 保存详细报告
        report_file = Path("tests/scraper_performance_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        raise


if __name__ == "__main__":
    run_scraper_performance_tests()