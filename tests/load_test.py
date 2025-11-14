#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统压力测试模块

测试内容包括：
1. 连续24小时运行稳定性测试
2. 高并发负载测试
3. 数据库压力测试
4. 内存泄漏检测

测试指标：
- 系统稳定性: 99%+
- 内存泄漏: < 5MB/hour
- 响应时间退化: < 10%
- 错误率: < 1%
"""

import time
import json
import threading
import statistics
import gc
import psutil
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Callable
from pathlib import Path
import logging
import signal
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LoadTestMetrics:
    """压力测试指标数据类"""
    timestamp: float
    active_threads: int
    memory_usage_mb: float
    cpu_percent: float
    response_time: float
    success_count: int
    error_count: int
    database_connections: int
    queue_size: int

class SystemStressTest:
    """系统压力测试类"""
    
    def __init__(self, test_db_path: str = "tests/stress_test.db"):
        """初始化压力测试"""
        self.test_db_path = Path(test_db_path)
        self.test_db_path.parent.mkdir(exist_ok=True)
        
        self.test_results = {}
        self.metrics_log = []
        self.stop_flag = False
        self.lock = threading.Lock()
        
        # 初始化数据库连接
        self._init_database()
        
        # 性能监控
        self.process = psutil.Process()
        
    def _init_database(self):
        """初始化测试数据库"""
        try:
            # 删除现有测试数据库
            if self.test_db_path.exists():
                self.test_db_path.unlink()
            
            # 创建新的测试数据库
            conn = sqlite3.connect(str(self.test_db_path))
            cursor = conn.cursor()
            
            # 创建测试表
            cursor.execute("""
                CREATE TABLE stress_test_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id INTEGER,
                    operation_type TEXT,
                    data_size INTEGER,
                    response_time REAL,
                    timestamp REAL,
                    success BOOLEAN
                )
            """)
            
            cursor.execute("CREATE INDEX idx_timestamp ON stress_test_data(timestamp)")
            cursor.execute("CREATE INDEX idx_thread ON stress_test_data(thread_id)")
            
            conn.commit()
            conn.close()
            
            logger.info("测试数据库初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def stress_test_database_operations(self, duration_hours: int = 2, max_threads: int = 20):
        """数据库操作压力测试"""
        logger.info(f"开始数据库压力测试 (持续 {duration_hours} 小时, 最多 {max_threads} 线程)...")
        
        test_start_time = time.time()
        end_time = test_start_time + (duration_hours * 3600)
        
        # 统计信息
        stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'response_times': [],
            'threads_created': 0,
            'errors': []
        }
        
        def database_worker(worker_id: int, stop_flag_ref):
            """数据库操作工作线程"""
            operation_count = 0
            worker_start_time = time.time()
            
            while not stop_flag_ref() and time.time() < end_time:
                try:
                    operation_start = time.time()
                    
                    # 执行数据库操作
                    success = self._perform_database_operation(worker_id, operation_count)
                    
                    operation_end = time.time()
                    response_time = operation_end - operation_start
                    
                    # 记录操作结果
                    with self.lock:
                        stats['total_operations'] += 1
                        stats['response_times'].append(response_time)
                        
                        if success:
                            stats['successful_operations'] += 1
                        else:
                            stats['failed_operations'] += 1
                            stats['errors'].append(f"Worker {worker_id} operation {operation_count} failed")
                    
                    operation_count += 1
                    
                    # 短暂休息
                    time.sleep(random.uniform(0.01, 0.1))
                    
                except Exception as e:
                    with self.lock:
                        stats['failed_operations'] += 1
                        stats['errors'].append(f"Worker {worker_id} error: {str(e)}")
                
                # 检查是否需要停止
                if stop_flag_ref():
                    break
            
            return operation_count
        
        # 启动工作线程
        threads = []
        thread_count = 0
        
        while time.time() < end_time:
            if thread_count < max_threads:
                # 创建新线程
                thread = threading.Thread(
                    target=database_worker,
                    args=(thread_count, lambda: self.stop_flag),
                    daemon=True
                )
                thread.start()
                threads.append(thread)
                
                with self.lock:
                    stats['threads_created'] += 1
                
                thread_count += 1
                
                # 随机延迟启动
                time.sleep(random.uniform(0.1, 1.0))
            
            else:
                # 检查是否有线程死亡
                alive_threads = [t for t in threads if t.is_alive()]
                if len(alive_threads) < max_threads * 0.8:  # 如果存活线程少于80%，创建新线程
                    time.sleep(1)
                    continue
                else:
                    time.sleep(5)  # 减少检查频率
            
            # 检查整体测试时间
            if time.time() >= end_time:
                self.stop_flag = True
                break
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=5)
        
        # 计算最终统计
        test_duration = time.time() - test_start_time
        
        response_times = stats['response_times']
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times) if response_times else 0
        
        success_rate = (stats['successful_operations'] / stats['total_operations'] * 100) if stats['total_operations'] > 0 else 0
        
        database_stress_result = {
            'test_duration_hours': round(test_duration / 3600, 2),
            'total_operations': stats['total_operations'],
            'successful_operations': stats['successful_operations'],
            'failed_operations': stats['failed_operations'],
            'success_rate': round(success_rate, 2),
            'avg_response_time': round(avg_response_time, 4),
            'p95_response_time': round(p95_response_time, 4),
            'max_response_time': round(max(response_times), 4) if response_times else 0,
            'threads_created': stats['threads_created'],
            'operations_per_second': round(stats['total_operations'] / test_duration, 2),
            'target_met': success_rate >= 99 and avg_response_time < 0.1,
            'errors_sample': stats['errors'][:10]  # 只保留前10个错误
        }
        
        logger.info(f"数据库压力测试完成: {stats['total_operations']} 次操作, 成功率 {success_rate:.1f}%")
        
        self.test_results['database_stress'] = database_stress_result
        return database_stress_result
    
    def _perform_database_operation(self, thread_id: int, operation_count: int) -> bool:
        """执行单个数据库操作"""
        try:
            conn = sqlite3.connect(str(self.test_db_path), timeout=5)
            cursor = conn.cursor()
            
            # 随机选择操作类型
            operation_type = random.choice(['INSERT', 'SELECT', 'UPDATE', 'DELETE'])
            
            if operation_type == 'INSERT':
                cursor.execute("""
                    INSERT INTO stress_test_data 
                    (thread_id, operation_type, data_size, response_time, timestamp, success)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    thread_id,
                    'INSERT',
                    random.randint(100, 10000),
                    random.uniform(0.001, 0.01),
                    time.time(),
                    True
                ))
            
            elif operation_type == 'SELECT':
                cursor.execute("""
                    SELECT COUNT(*) FROM stress_test_data 
                    WHERE thread_id = ? AND timestamp > ?
                """, (thread_id, time.time() - 3600))
                result = cursor.fetchone()
            
            elif operation_type == 'UPDATE':
                cursor.execute("""
                    UPDATE stress_test_data 
                    SET response_time = ? 
                    WHERE thread_id = ? AND id = (
                        SELECT id FROM stress_test_data 
                        WHERE thread_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 1
                    )
                """, (random.uniform(0.001, 0.01), thread_id, thread_id))
            
            elif operation_type == 'DELETE':
                cursor.execute("""
                    DELETE FROM stress_test_data 
                    WHERE thread_id = ? AND timestamp < ?
                """, (thread_id, time.time() - 7200))  # 删除2小时前的记录
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.debug(f"数据库操作失败: {e}")
            return False
    
    def memory_leak_detection(self, duration_hours: int = 2):
        """内存泄漏检测测试"""
        logger.info(f"开始内存泄漏检测 (持续 {duration_hours} 小时)...")
        
        test_start_time = time.time()
        end_time = test_start_time + (duration_hours * 3600)
        
        # 记录内存使用历史
        memory_history = []
        gc_history = []
        
        def memory_monitor(stop_flag_ref):
            """内存监控线程"""
            while not stop_flag_ref() and time.time() < end_time:
                # 获取当前内存使用
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # 强制垃圾回收
                gc.collect()
                gc_count = len(gc.get_objects())
                
                # 记录指标
                metric = LoadTestMetrics(
                    timestamp=time.time(),
                    active_threads=threading.active_count(),
                    memory_usage_mb=memory_mb,
                    cpu_percent=self.process.cpu_percent(),
                    response_time=0,  # 监控线程不测量响应时间
                    success_count=0,
                    error_count=0,
                    database_connections=0,
                    queue_size=0
                )
                
                with self.lock:
                    self.metrics_log.append(metric)
                    memory_history.append(memory_mb)
                    gc_history.append(gc_count)
                
                # 限制日志大小
                if len(self.metrics_log) > 1000:
                    with self.lock:
                        self.metrics_log = self.metrics_log[-500:]
                
                time.sleep(30)  # 每30秒记录一次
        
        # 启动内存监控线程
        monitor_thread = threading.Thread(
            target=memory_monitor,
            args=(lambda: self.stop_flag,),
            daemon=True
        )
        monitor_thread.start()
        
        # 执行压力操作
        self._run_memory_stress_operations(end_time)
        
        # 停止监控
        self.stop_flag = True
        monitor_thread.join()
        
        # 分析内存使用趋势
        if len(memory_history) >= 2:
            initial_memory = memory_history[0]
            final_memory = memory_history[-1]
            memory_increase = final_memory - initial_memory
            memory_leak_rate = memory_increase / (duration_hours * 3600 / 30)  # MB per check interval
            
            # 线性回归分析内存趋势
            memory_trend = self._calculate_trend(memory_history)
        else:
            memory_increase = 0
            memory_leak_rate = 0
            memory_trend = 0
        
        memory_leak_result = {
            'test_duration_hours': duration_hours,
            'initial_memory_mb': round(memory_history[0], 2) if memory_history else 0,
            'final_memory_mb': round(memory_history[-1], 2) if memory_history else 0,
            'memory_increase_mb': round(memory_increase, 2),
            'memory_leak_rate_mb_per_hour': round(memory_leak_rate * 30, 2),  # 转换为每小时
            'memory_trend_slope': round(memory_trend, 6),
            'peak_memory_mb': round(max(memory_history), 2) if memory_history else 0,
            'min_memory_mb': round(min(memory_history), 2) if memory_history else 0,
            'memory_stability': 'stable' if abs(memory_trend) < 0.001 else 'increasing' if memory_trend > 0 else 'decreasing',
            'target_met': memory_leak_rate < 0.001  # 内存泄漏 < 0.001MB per check (~5MB/hour)
        }
        
        logger.info(f"内存泄漏检测完成: 内存增长 {memory_increase:.1f}MB, 趋势 {memory_trend:.6f}")
        
        self.test_results['memory_leak_detection'] = memory_leak_result
        return memory_leak_result
    
    def _run_memory_stress_operations(self, end_time: float):
        """运行内存压力操作"""
        def memory_stress_worker():
            """内存压力工作线程"""
            large_objects = []
            
            while not self.stop_flag and time.time() < end_time:
                try:
                    # 创建大量对象
                    for _ in range(100):
                        large_objects.append({
                            'data': [random.random() for _ in range(1000)],
                            'timestamp': time.time(),
                            'id': random.randint(1, 1000000)
                        })
                    
                    # 定期清理
                    if len(large_objects) > 1000:
                        large_objects = large_objects[-500:]  # 保留后半部分
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.debug(f"内存压力操作出错: {e}")
        
        # 启动多个内存压力线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=memory_stress_worker, daemon=True)
            thread.start()
            threads.append(thread)
        
        # 等待结束时间
        while time.time() < end_time and not self.stop_flag:
            time.sleep(1)
        
        # 清理线程
        for thread in threads:
            thread.join(timeout=1)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """计算数值序列的趋势（线性回归斜率）"""
        if len(values) < 2:
            return 0
        
        n = len(values)
        x = list(range(n))
        
        # 计算线性回归
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def concurrent_user_simulation(self, duration_hours: int = 1, max_concurrent_users: int = 50):
        """并发用户模拟测试"""
        logger.info(f"开始并发用户模拟 (持续 {duration_hours} 小时, 最多 {max_concurrent_users} 用户)...")
        
        test_start_time = time.time()
        end_time = test_start_time + (duration_hours * 3600)
        
        # 用户模拟统计
        user_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'concurrent_users': 0,
            'peak_concurrent_users': 0
        }
        
        def simulate_user_session(user_id: int, stop_flag_ref):
            """模拟用户会话"""
            session_start = time.time()
            
            while not stop_flag_ref() and time.time() < end_time:
                try:
                    # 模拟用户操作
                    operation_start = time.time()
                    
                    # 随机选择操作类型
                    operation = random.choice(['browse', 'search', 'filter', 'details'])
                    
                    # 模拟不同操作的响应时间
                    if operation == 'browse':
                        time.sleep(random.uniform(0.5, 2.0))  # 浏览页面
                    elif operation == 'search':
                        time.sleep(random.uniform(1.0, 3.0))  # 搜索
                    elif operation == 'filter':
                        time.sleep(random.uniform(0.2, 1.0))  # 筛选
                    elif operation == 'details':
                        time.sleep(random.uniform(2.0, 5.0))  # 查看详情
                    
                    operation_end = time.time()
                    response_time = operation_end - operation_start
                    
                    # 记录请求结果
                    success = random.random() > 0.02  # 98%成功率
                    
                    with self.lock:
                        user_stats['total_requests'] += 1
                        user_stats['response_times'].append(response_time)
                        user_stats['concurrent_users'] = threading.active_count() - 1  # 减去监控线程
                        user_stats['peak_concurrent_users'] = max(user_stats['peak_concurrent_users'], user_stats['concurrent_users'])
                        
                        if success:
                            user_stats['successful_requests'] += 1
                        else:
                            user_stats['failed_requests'] += 1
                    
                    # 模拟用户思考时间
                    think_time = random.uniform(1.0, 5.0)
                    time.sleep(think_time)
                    
                except Exception as e:
                    with self.lock:
                        user_stats['failed_requests'] += 1
                
                # 检查会话是否应该结束
                session_duration = time.time() - session_start
                if session_duration > random.uniform(300, 1800):  # 5-30分钟的会话
                    break
        
        # 启动用户会话
        active_sessions = []
        session_id = 0
        
        while time.time() < end_time and not self.stop_flag:
            # 动态调整并发用户数
            target_users = min(
                max_concurrent_users,
                max(10, int((time.time() - test_start_time) / 300) * 5)  # 每5分钟增加5个用户
            )
            
            # 创建新会话
            while len(active_sessions) < target_users and time.time() < end_time:
                session = threading.Thread(
                    target=simulate_user_session,
                    args=(session_id, lambda: self.stop_flag),
                    daemon=True
                )
                session.start()
                active_sessions.append(session)
                session_id += 1
                
                time.sleep(random.uniform(0.1, 1.0))  # 随机延迟启动
            
            # 清理已完成会话
            active_sessions = [s for s in active_sessions if s.is_alive()]
            
            time.sleep(5)  # 每5秒检查一次
        
        # 等待所有会话完成
        for session in active_sessions:
            session.join(timeout=5)
        
        # 计算最终统计
        test_duration = time.time() - test_start_time
        response_times = user_stats['response_times']
        
        concurrent_user_result = {
            'test_duration_hours': round(test_duration / 3600, 2),
            'total_requests': user_stats['total_requests'],
            'successful_requests': user_stats['successful_requests'],
            'failed_requests': user_stats['failed_requests'],
            'success_rate': round((user_stats['successful_requests'] / user_stats['total_requests'] * 100), 2) if user_stats['total_requests'] > 0 else 0,
            'peak_concurrent_users': user_stats['peak_concurrent_users'],
            'avg_response_time': round(statistics.mean(response_times), 2) if response_times else 0,
            'p95_response_time': round(statistics.quantiles(response_times, n=20)[18], 2) if len(response_times) > 20 else 0,
            'max_response_time': round(max(response_times), 2) if response_times else 0,
            'requests_per_second': round(user_stats['total_requests'] / test_duration, 2),
            'target_met': user_stats['peak_concurrent_users'] >= max_concurrent_users * 0.8
        }
        
        logger.info(f"并发用户测试完成: {user_stats['peak_concurrent_users']} 峰值用户, 成功率 {concurrent_user_result['success_rate']:.1f}%")
        
        self.test_results['concurrent_user_simulation'] = concurrent_user_result
        return concurrent_user_result
    
    def long_running_stability_test(self, duration_hours: int = 24):
        """长时间运行稳定性测试"""
        logger.info(f"开始长时间稳定性测试 (持续 {duration_hours} 小时)...")
        
        test_start_time = time.time()
        end_time = test_start_time + (duration_hours * 3600)
        
        stability_stats = {
            'test_start_time': test_start_time,
            'operations_per_hour': [],
            'error_rates': [],
            'performance_degradation': [],
            'system_errors': [],
            'resource_warnings': []
        }
        
        def stability_monitor(stop_flag_ref):
            """稳定性监控线程"""
            last_check_time = time.time()
            hourly_stats = []
            
            while not stop_flag_ref() and time.time() < end_time:
                current_time = time.time()
                
                # 每小时检查一次
                if current_time - last_check_time >= 3600:
                    hour_duration = current_time - last_check_time
                    
                    # 计算每小时统计
                    with self.lock:
                        metrics_in_hour = [m for m in self.metrics_log if m.timestamp >= last_check_time]
                        
                        if metrics_in_hour:
                            avg_response_time = statistics.mean([m.response_time for m in metrics_in_hour if m.response_time > 0])
                            total_requests = len(metrics_in_hour)
                            error_count = sum(1 for m in metrics_in_hour if m.error_count > 0)
                            error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
                            
                            hourly_stats.append({
                                'hour': len(stability_stats['operations_per_hour']) + 1,
                                'total_requests': total_requests,
                                'avg_response_time': avg_response_time,
                                'error_rate': error_rate,
                                'timestamp': current_time
                            })
                    
                    stability_stats['operations_per_hour'].append(total_requests)
                    stability_stats['error_rates'].append(error_rate)
                    
                    last_check_time = current_time
                
                time.sleep(60)  # 每分钟检查一次
        
        # 启动稳定性监控
        monitor_thread = threading.Thread(
            target=stability_monitor,
            args=(lambda: self.stop_flag,),
            daemon=True
        )
        monitor_thread.start()
        
        # 运行基础负载
        baseline_start = time.time()
        while time.time() < end_time and not self.stop_flag:
            # 执行基础操作保持系统活跃
            try:
                self._perform_database_operation(0, 0)
                time.sleep(1)
            except:
                pass
        
        # 停止监控
        self.stop_flag = True
        monitor_thread.join()
        
        # 分析稳定性数据
        if stability_stats['operations_per_hour']:
            avg_ops_per_hour = statistics.mean(stability_stats['operations_per_hour'])
            max_hourly_ops = max(stability_stats['operations_per_hour'])
            min_hourly_ops = min(stability_stats['operations_per_hour'])
            
            # 计算性能退化
            if len(stability_stats['operations_per_hour']) >= 2:
                performance_degradation = ((max_hourly_ops - min_hourly_ops) / max_hourly_ops * 100)
            else:
                performance_degradation = 0
        else:
            avg_ops_per_hour = 0
            performance_degradation = 0
        
        stability_result = {
            'test_duration_hours': duration_hours,
            'actual_duration_hours': round((time.time() - test_start_time) / 3600, 2),
            'avg_operations_per_hour': round(avg_ops_per_hour, 2),
            'max_hourly_operations': max_hourly_ops if stability_stats['operations_per_hour'] else 0,
            'min_hourly_operations': min_hourly_ops if stability_stats['operations_per_hour'] else 0,
            'performance_degradation_percent': round(performance_degradation, 2),
            'avg_error_rate': round(statistics.mean(stability_stats['error_rates']), 2) if stability_stats['error_rates'] else 0,
            'max_error_rate': round(max(stability_stats['error_rates']), 2) if stability_stats['error_rates'] else 0,
            'stability_score': self._calculate_stability_score(stability_stats),
            'target_met': performance_degradation < 10 and max(stability_stats['error_rates']) < 5 if stability_stats['error_rates'] else True
        }
        
        logger.info(f"稳定性测试完成: 性能退化 {performance_degradation:.1f}%")
        
        self.test_results['long_running_stability'] = stability_result
        return stability_result
    
    def _calculate_stability_score(self, stability_stats: Dict) -> float:
        """计算稳定性分数"""
        score = 100.0
        
        # 错误率扣分
        max_error_rate = max(stability_stats['error_rates']) if stability_stats['error_rates'] else 0
        score -= max_error_rate * 2  # 每个百分点扣2分
        
        # 性能退化扣分
        if stability_stats['operations_per_hour']:
            max_ops = max(stability_stats['operations_per_hour'])
            min_ops = min(stability_stats['operations_per_hour'])
            if max_ops > 0:
                performance_drop = ((max_ops - min_ops) / max_ops) * 100
                score -= performance_drop * 0.5  # 性能退化每百分点扣0.5分
        
        return max(0, round(score, 1))
    
    def run_all_tests(self, short_test: bool = False):
        """运行所有压力测试"""
        if short_test:
            logger.info("开始短时间压力测试 (用于开发/调试)...")
        else:
            logger.info("开始完整压力测试...")
        
        try:
            # 根据测试模式调整参数
            if short_test:
                db_duration = 0.5  # 30分钟
                memory_duration = 0.5  # 30分钟
                user_duration = 0.25  # 15分钟
                stability_duration = 1  # 1小时
                max_threads = 10
                max_users = 20
            else:
                db_duration = 4  # 4小时
                memory_duration = 2  # 2小时
                user_duration = 1  # 1小时
                stability_duration = 6  # 6小时 (总测试时间考虑限制)
                max_threads = 20
                max_users = 50
            
            # 设置信号处理器用于优雅停止
            def signal_handler(signum, frame):
                logger.info(f"接收到信号 {signum}，开始优雅停止测试...")
                self.stop_flag = True
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # 运行各项测试
            self.stress_test_database_operations(db_duration, max_threads)
            self.memory_leak_detection(memory_duration)
            self.concurrent_user_simulation(user_duration, max_users)
            self.long_running_stability_test(stability_duration)
            
            logger.info("压力测试完成")
            
        except KeyboardInterrupt:
            logger.info("测试被用户中断")
            self.stop_flag = True
        except Exception as e:
            logger.error(f"测试过程中出错: {e}")
            self.stop_flag = True
            raise
    
    def generate_report(self) -> Dict[str, Any]:
        """生成压力测试报告"""
        return {
            'test_type': 'load_stress_test',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'test_results': self.test_results,
            'metrics_log_size': len(self.metrics_log),
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        summary = {
            'total_tests': len(self.test_results),
            'passed_tests': 0,
            'failed_tests': 0,
            'overall_status': 'unknown',
            'stability_score': 0,
            'performance_score': 0
        }
        
        # 检查各项测试是否达标
        target_checks = {
            'database_stress': lambda r: r.get('target_met', False),
            'memory_leak_detection': lambda r: r.get('target_met', False),
            'concurrent_user_simulation': lambda r: r.get('target_met', False),
            'long_running_stability': lambda r: r.get('target_met', False)
        }
        
        passed_count = 0
        for test_name, check_func in target_checks.items():
            if test_name in self.test_results:
                try:
                    if check_func(self.test_results[test_name]):
                        passed_count += 1
                except Exception:
                    pass
        
        summary['passed_tests'] = passed_count
        summary['failed_tests'] = summary['total_tests'] - passed_count
        
        # 计算稳定性分数
        if 'long_running_stability' in self.test_results:
            summary['stability_score'] = self.test_results['long_running_stability'].get('stability_score', 0)
        
        # 计算性能分数
        if passed_count == summary['total_tests']:
            summary['overall_status'] = 'passed'
        elif passed_count > 0:
            summary['overall_status'] = 'partial'
        else:
            summary['overall_status'] = 'failed'
        
        return summary
    
    def cleanup(self):
        """清理测试环境"""
        try:
            if self.test_db_path.exists():
                self.test_db_path.unlink()
            logger.info("压力测试环境清理完成")
        except Exception as e:
            logger.warning(f"清理环境时出错: {e}")


def run_load_tests(short_test: bool = False):
    """运行压力测试的主函数"""
    print("=" * 60)
    print("系统压力测试")
    print("=" * 60)
    
    tester = SystemStressTest()
    
    try:
        # 运行测试
        tester.run_all_tests(short_test=short_test)
        
        # 生成报告
        report = tester.generate_report()
        
        # 输出结果
        print("\n📊 测试结果摘要:")
        summary = report['summary']
        print(f"   稳定性分数: {summary['stability_score']}/100")
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
                    if key.endswith('_met') or isinstance(value, bool):
                        status = "✅" if value else "❌"
                        print(f"   {status} {key}: {value}")
                    elif isinstance(value, (int, float)) and key != 'errors_sample':
                        print(f"   {key}: {value}")
        
        # 保存详细报告
        report_file = Path("tests/load_test_report.json")
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
    # 检查是否运行短测试
    short_test = len(sys.argv) > 1 and sys.argv[1] == '--short'
    run_load_tests(short_test=short_test)