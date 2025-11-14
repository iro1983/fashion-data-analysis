# 集成测试配置
# =================

# 测试环境配置
TEST_ENVIRONMENT = {
    'debug_mode': True,
    'verbose_logging': True,
    'test_data_size': 'medium',  # small, medium, large
    'concurrent_workers': 5,
    'timeout_seconds': 30
}

# 数据库配置
DATABASE_CONFIG = {
    'test_db_path': 'tests/temp/test_products.db',
    'backup_dir': 'tests/temp/backup',
    'connection_pool_size': 10,
    'auto_backup': False,  # 测试环境不需要自动备份
    'backup_interval_hours': 24
}

# 抓取器配置（测试环境）
SCRAPER_CONFIG = {
    'amazon': {
        'max_pages': 2,  # 限制页数避免长时间运行
        'delay_range': (0.5, 1.5),  # 缩短延迟用于测试
        'timeout_seconds': 10,
        'max_retries': 3
    },
    'tiktok': {
        'max_posts': 5,  # 限制帖子数量
        'delay_range': (1, 2),  # 缩短延迟用于测试
        'timeout_seconds': 10,
        'max_retries': 3
    }
}

# 数据清洗配置
DATA_CLEANER_CONFIG = {
    'price_range': (0, 10000),  # 扩大价格范围用于测试
    'rating_range': (0, 5),
    'title_max_length': 500,
    'description_max_length': 2000,
    'validate_images': False,  # 测试环境跳过图像验证
    'remove_duplicates': True
}

# 错误处理配置
ERROR_HANDLING_CONFIG = {
    'max_retry_attempts': 3,
    'retry_delay_base': 1,  # 秒
    'circuit_breaker_threshold': 5,
    'circuit_breaker_timeout': 30,
    'log_all_errors': True,
    'continue_on_error': True  # 测试环境继续执行其他测试
}

# 性能测试配置
PERFORMANCE_CONFIG = {
    'batch_size': 100,
    'concurrent_operations': 5,
    'memory_limit_mb': 500,
    'response_time_threshold': 2.0,  # 秒
    'throughput_threshold': 50  # 每秒处理项目数
}

# UI测试配置
UI_TEST_CONFIG = {
    'headless_browser': True,  # 无头模式运行
    'browser_type': 'chrome',
    'screenshot_on_failure': True,
    'wait_timeout': 10,  # 秒
    'responsive_test_sizes': [
        {'width': 320, 'height': 568},   # 手机
        {'width': 768, 'height': 1024},  # 平板
        {'width': 1920, 'height': 1080}  # 桌面
    ]
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'tests/logs/integration_test.log',
    'max_file_size': '10MB',
    'backup_count': 5,
    'console_output': True
}

# 测试数据配置
TEST_DATA_CONFIG = {
    'generate_sample_data': True,
    'sample_product_count': 50,
    'platforms': ['amazon', 'tiktok'],
    'categories': ['服装', '配件', '鞋子'],
    'price_range': (10, 200),
    'rating_range': (1, 5)
}