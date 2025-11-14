# TikTok热销服装数据抓取脚本
# 配置文件示例

import os
from typing import List
from tiktok_scraper import ScrapingConfig

# 基础配置
BASE_CONFIG = ScrapingConfig(
    # TikHub API 配置 (必填)
    tiktok_api_key="your_actual_api_key_here",  # 从 https://api.tikhub.io 获取
    tiktok_api_url="https://api.tikhub.io",
    
    # 爬虫配置
    use_proxy=True,  # 是否使用代理
    request_delay=2.0,  # 请求间隔(秒)
    max_retries=3,  # 最大重试次数
    timeout=30,  # 请求超时
    
    # 目标配置
    target_hashtags=[
        # 基础服装类别
        "#tshirt", "#hoodie", "#sweatshirt", "#pullover", 
        "#dress", "#top", "#blouse", "#shirt",
        "#pants", "#jeans", "#shorts", "#skirt",
        "#jacket", "#coat", "#sweater", "#cardigan",
        
        # 风格标签
        "#streetwear", "#casual", "#formal", "#vintage",
        "#minimalist", "#bohemian", "#edgy", "#preppy",
        
        # 场景标签
        "#workwear", "#athletic", "#loungewear", "#sleepwear",
        "#party", "#date", "#travel", "#vacation",
        
        # 通用时尚标签
        "#fashion", "#ootd", "#style", "#outfit", "#clothes",
        "#clothing", "#trendy", "#fashionista", "#styleinspo"
    ],
    
    target_languages=["en", "zh", "es", "fr", "de", "ja", "ko"],
    target_regions=["US", "UK", "CA", "AU", "DE", "FR", "JP", "KR"],
    
    # 数据库配置
    database_path="tiktok_clothing_data.db",
    
    # OCR配置
    enable_ocr=True,  # 启用OCR功能
    ocr_languages="eng+chi_sim"  # OCR语言设置
)

# 代理配置列表
PROXY_LIST = [
    # 格式: "ip:port" 或 "username:password@ip:port"
    # "192.168.1.1:8080",
    # "user:pass@10.10.10.1:3128",
    
    # 推荐使用住宅代理或高质量代理服务
    # 示例（替换为真实代理）:
    # "residential-proxy-1.example.com:8000",
    # "residential-proxy-2.example.com:8000",
]

# 开发环境配置
DEV_CONFIG = ScrapingConfig(
    tiktok_api_key="",  # 开发环境不使用真实API
    use_proxy=False,
    request_delay=1.0,  # 开发环境可以更快
    target_hashtags=["#tshirt", "#hoodie", "#fashion"],  # 少量标签
    database_path="dev_tiktok_data.db",
    enable_ocr=False  # 开发环境关闭OCR
)

# 生产环境配置
PROD_CONFIG = ScrapingConfig(
    tiktok_api_key=os.getenv("TIKHUB_API_KEY", ""),
    tiktok_api_url="https://api.tikhub.io",
    use_proxy=True,
    proxy_list=PROXY_LIST,
    request_delay=3.0,  # 生产环境更保守
    max_retries=5,
    target_hashtags=BASE_CONFIG.target_hashtags,  # 完整标签列表
    database_path="prod_tiktok_clothing_data.db",
    enable_ocr=True,
    timeout=60  # 生产环境超时更长
)

# 高频抓取配置 (适用于趋势监控)
FREQUENT_CONFIG = ScrapingConfig(
    tiktok_api_key=os.getenv("TIKHUB_API_KEY", ""),
    use_proxy=True,
    proxy_list=PROXY_LIST,
    request_delay=1.5,  # 较短延迟
    max_retries=2,
    target_hashtags=[
        "#trending", "#viral", "#fashiontrends", "#hot", 
        "#bestseller", "#popular", "#fashion"
    ],
    database_path="frequent_tiktok_data.db",
    enable_ocr=False  # 高频模式关闭OCR
)

# 配置选择器
def get_config(env: str = "dev") -> ScrapingConfig:
    """根据环境获取配置"""
    configs = {
        "dev": DEV_CONFIG,
        "prod": PROD_CONFIG,
        "frequent": FREQUENT_CONFIG,
        "base": BASE_CONFIG
    }
    
    config = configs.get(env, DEV_CONFIG)
    
    # 如果配置了代理列表，添加到config中
    if env in ["prod", "frequent"] and PROXY_LIST:
        config.proxy_list = PROXY_LIST
    
    return config

# 标签分类配置
HASHTAG_CATEGORIES = {
    "基础服装": [
        "#tshirt", "#shirt", "#blouse", "#top", 
        "#pants", "#jeans", "#shorts", "#skirt",
        "#dress", "#jacket", "#coat", "#sweater"
    ],
    "运动休闲": [
        "#athletic", "#sportswear", "#workout", "#gym",
        "#athleisure", "#loungewear", "#casual", "#comfortable"
    ],
    "正装商务": [
        "#formal", "#business", "#workwear", "#professional",
        "#office", "#suit", "#blazer", "#dress"
    ],
    "时尚风格": [
        "#streetwear", "#trendy", "#fashion", "#style",
        "#outfit", "#ootd", "#fashionista", "#stylish"
    ],
    "特定场景": [
        "#party", "#date", "#wedding", "#vacation",
        "#travel", "#beach", "#winter", "#summer"
    ]
}

# 数据验证规则
VALIDATION_RULES = {
    "video_data": {
        "required_fields": ["video_id", "title", "author"],
        "optional_fields": ["likes", "comments", "views", "product_links"],
        "max_title_length": 150,
        "min_title_length": 5
    },
    "product_links": {
        "valid_domains": [
            "amazon.com", "ebay.com", "shopify.com", "etsy.com",
            "aliexpress.com", "temu.com", "shein.com", "zara.com",
            "h&m.com", "uniqlo.com", "nike.com", "adidas.com"
        ],
        "suspicious_domains": [
            "bit.ly", "tinyurl.com", "cutt.ly", "t.co"
        ]
    },
    "author_data": {
        "min_followers": 1000,  # 过滤小号
        "max_followers": 10000000  # 过滤超大号（可选）
    }
}

# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s"
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler"
        },
        "file": {
            "level": "DEBUG",
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": "logs/tiktok_scraper.log",
            "encoding": "utf-8"
        },
        "error_file": {
            "level": "ERROR",
            "formatter": "detailed", 
            "class": "logging.FileHandler",
            "filename": "logs/tiktok_scraper_error.log",
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "": {
            "handlers": ["default", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

if __name__ == "__main__":
    # 测试配置
    print("TikTok抓取脚本配置测试")
    
    config = get_config("dev")
    print(f"数据库路径: {config.database_path}")
    print(f"标签数量: {len(config.target_hashtags)}")
    print(f"请求延迟: {config.request_delay}秒")
    print(f"OCR启用: {config.enable_ocr}")