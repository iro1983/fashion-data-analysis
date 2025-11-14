# Amazon爬虫配置文件
# 可以根据需要修改这些参数

# === 基本配置 ===
BASE_URL = "https://www.amazon.com"
DATABASE_PATH = "/workspace/code/amazon_products.db"
LOG_FILE = "/workspace/code/amazon_scraper.log"

# === 频率控制 ===
# 基于调研文档建议的合规频率控制
REQUEST_DELAY_MIN = 2  # 最小延迟2秒
REQUEST_DELAY_MAX = 3  # 最大延迟3秒
TIMEOUT = 10           # 请求超时时间(秒)
MAX_RETRIES = 3        # 最大重试次数
MAX_WORKERS = 3        # 最大并发工作线程数

# === 搜索类别配置 ===
# 支持的服装类别及其搜索关键词
SEARCH_CATEGORIES = {
    "print-tshirt": {
        "name": "印花T恤",
        "keywords": ["print", "tshirt", "tee"],
        "search_path": "/s?k=print+tshirt"
    },
    "graphic-shirt": {
        "name": "图形T恤", 
        "keywords": ["graphic", "shirt", "tee"],
        "search_path": "/s?k=graphic+shirt"
    },
    "logo-tshirt": {
        "name": "标志T恤",
        "keywords": ["logo", "tshirt", "branded"],
        "search_path": "/s?k=logo+tshirt"
    },
    "print-hoodie": {
        "name": "印花卫衣",
        "keywords": ["print", "hoodie", "sweatshirt"],
        "search_path": "/s?k=print+hoodie"
    },
    "fashion-hoodie": {
        "name": "时尚卫衣",
        "keywords": ["fashion", "hoodie", "style"],
        "search_path": "/s?k=fashion+hoodie"
    }
}

# === 反爬虫配置 ===
# User-Agent列表 - 用于模拟不同浏览器
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

# HTTP代理列表 (可选)
# 格式: "http://username:password@proxy_server:port"
PROXY_LIST = [
    # "http://user:pass@proxy1:port",
    # "http://user:pass@proxy2:port",
]

# === 合规配置 ===
# robots.txt禁止路径 - 基于调研文档
DISALLOWED_PATHS = [
    "/gp/sign-in",
    "/ap/signin", 
    "/gp/cart",
    "/gp/registry",
    "/wishlist",
    "/gp/handshake",
    "/yourstore/home",
    "/your-account"
]

# === 数据导出配置 ===
EXPORT_SETTINGS = {
    "json_indent": 2,
    "encoding": "utf-8",
    "date_format": "%Y%m%d_%H%M%S"
}

# === 抓取限制配置 ===
# 每日抓取限制（建议）
DAILY_LIMITS = {
    "max_products_per_category": 100,     # 每个类别最大抓取数
    "max_pages_per_search": 5,            # 每个搜索最大页数
    "max_bestsellers_per_day": 50,        # 每日最大热销品抓取数
}

# === 错误处理配置 ===
ERROR_HANDLING = {
    "retry_delay_base": 1,    # 基础重试延迟(秒)
    "retry_delay_factor": 2,   # 延迟倍增因子
    "max_consecutive_failures": 5,  # 最大连续失败次数
    "circuit_breaker_threshold": 10  # 熔断阈值
}

# === 日志配置 ===
LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "max_file_size": "10MB",    # 日志文件最大大小
    "backup_count": 5           # 备份文件数量
}

# === 异步配置 ===
ASYNC_SETTINGS = {
    "max_concurrent_tasks": 5,
    "task_timeout": 30,
    "semaphore_limit": 10
}

# === 数据质量配置 ===
DATA_VALIDATION = {
    "min_price": 0.01,
    "max_price": 1000.0,
    "min_rating": 0.0,
    "max_rating": 5.0,
    "max_title_length": 500,
    "required_fields": ["asin", "title", "price"]
}

# === 性能调优配置 ===
PERFORMANCE = {
    "connection_pool_size": 10,
    "connection_pool_maxsize": 20,
    "keep_alive": True,
    "chunk_size": 1024
}

def load_config():
    """加载配置（可以扩展为从文件读取配置）"""
    return {
        "base_url": BASE_URL,
        "database_path": DATABASE_PATH,
        "log_file": LOG_FILE,
        "request_delay_min": REQUEST_DELAY_MIN,
        "request_delay_max": REQUEST_DELAY_MAX,
        "timeout": TIMEOUT,
        "max_retries": MAX_RETRIES,
        "max_workers": MAX_WORKERS,
        "search_categories": SEARCH_CATEGORIES,
        "user_agents": USER_AGENTS,
        "proxy_list": PROXY_LIST,
        "disallowed_paths": DISALLOWED_PATHS,
        "export_settings": EXPORT_SETTINGS,
        "daily_limits": DAILY_LIMITS,
        "error_handling": ERROR_HANDLING,
        "logging": LOGGING,
        "async_settings": ASYNC_SETTINGS,
        "data_validation": DATA_VALIDATION,
        "performance": PERFORMANCE
    }

def validate_config():
    """验证配置参数的合理性"""
    config = load_config()
    
    assert config["request_delay_min"] >= 1, "请求延迟不能少于1秒"
    assert config["request_delay_max"] > config["request_delay_min"], "最大延迟应大于最小延迟"
    assert config["timeout"] > 0, "超时时间必须大于0"
    assert config["max_retries"] >= 0, "重试次数不能为负数"
    
    # 验证价格范围
    validation = config["data_validation"]
    assert validation["min_price"] < validation["max_price"], "最小价格应小于最大价格"
    assert validation["min_rating"] <= validation["max_rating"], "评分范围设置错误"
    
    print("✅ 配置验证通过")
    return True

if __name__ == "__main__":
    print("Amazon爬虫配置验证")
    print("=" * 30)
    
    try:
        config = load_config()
        validate_config()
        
        print(f"基础URL: {config['base_url']}")
        print(f"数据库路径: {config['database_path']}")
        print(f"请求延迟: {config['request_delay_min']}-{config['request_delay_max']}秒")
        print(f"超时时间: {config['timeout']}秒")
        print(f"支持类别数: {len(config['search_categories'])}")
        print(f"User-Agent数: {len(config['user_agents'])}")
        
        print("\n✅ 配置加载完成")
        
    except Exception as e:
        print(f"❌ 配置错误: {e}")