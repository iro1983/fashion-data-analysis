# TikTok热销服装数据抓取脚本

基于 `docs/tiktok_data_research.md` 调研结果开发的TikTok平台热销印花服装数据抓取脚本。

## 📋 项目概述

本脚本专门针对TikTok平台的热销服装数据抓取，采用多渠道数据获取策略，包括TikHub API和网页爬虫两种方式，支持合规且高效的数据采集。

### 🎯 主要功能

- **多渠道数据获取**: TikHub API + 网页爬虫双重保障
- **热门服装标签搜索**: 支持#tshirt #hoodie #fashion等服装标签
- **商品链接提取**: 自动识别和提取视频中的产品链接
- **博主信息抓取**: 作者信息、粉丝数、互动数据等
- **视频互动分析**: 点赞、评论、分享、播放量统计
- **数据去重和分类**: 基于哈希值的智能去重机制
- **产品链接验证**: 自动验证电商链接有效性
- **合规性保障**: 严格遵守平台条款，频率控制
- **OCR图像识别**: 可选的视频截图文字识别功能
- **详细日志记录**: 完整的操作日志和统计信息

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests selenium pillow pytesseract pandas schedule
```

### 2. OCR依赖安装（可选）

```bash
# Windows: 下载并安装 tesseract-ocr
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

### 3. 基础使用

```python
from tiktok_scraper import TikTokClothingScraper
from config import get_config

# 使用开发配置
config = get_config("dev")

# 创建抓取器
scraper = TikTokClothingScraper(config)

# 抓取服装视频数据
results = scraper.scrape_clothing_videos(
    target_sources=['tikhub_api', 'web_scraper'],
    max_videos_per_tag=50
)

print(f"抓取完成: {results['total_videos']} 个视频")
print(f"处理时间: {results['duration_seconds']:.2f} 秒")
```

### 4. 配置API密钥

```python
# 方法1: 直接配置
from tiktok_scraper import ScrapingConfig

config = ScrapingConfig(
    tiktok_api_key="your_actual_api_key_here"  # 从 https://api.tikhub.io 获取
)

# 方法2: 环境变量
import os
os.environ["TIKHUB_API_KEY"] = "your_actual_api_key_here"
config = get_config("prod")
```

## 📁 项目结构

```
code/
├── tiktok_scraper.py      # 主抓取脚本
├── config.py             # 配置文件
├── README.md             # 说明文档
├── requirements.txt      # 依赖包
├── tiktok_scraper.log    # 运行日志
└── tiktok_clothing_data.db  # SQLite数据库
```

## 🛠️ 技术实现

### 核心组件

1. **TikTokClothingScraper**: 主抓取器类
2. **TikHubAPIClient**: TikHub API客户端
3. **WebScraper**: 网页爬虫组件
4. **ProductLinkValidator**: 产品链接验证器
5. **DatabaseManager**: 数据库操作管理
6. **TikTokVideo**: 视频数据结构

### 数据来源策略

- **TikHub API**: 优先使用，稳定可靠
- **网页爬虫**: API补充，覆盖更多数据
- **数据去重**: 基于内容哈希的智能去重
- **链接验证**: 批量验证产品链接有效性

### 数据字段

抓取的视频信息包括：

| 字段 | 类型 | 描述 |
|------|------|------|
| video_id | str | 视频唯一标识 |
| title | str | 视频标题 |
| description | str | 视频描述 |
| author | str | 作者昵称 |
| author_id | str | 作者ID |
| author_followers | int | 作者粉丝数 |
| author_following | int | 作者关注数 |
| likes | int | 点赞数 |
| comments | int | 评论数 |
| shares | int | 分享数 |
| views | int | 播放量 |
| hashtags | List[str] | 标签列表 |
| music_info | str | 音乐信息 |
| product_links | List[str] | 产品链接 |
| product_images | List[str] | 产品图片 |
| upload_time | str | 上传时间 |
| region | str | 地区 |
| language | str | 语言 |
| source | str | 数据来源 |
| scraped_at | str | 抓取时间 |

## ⚙️ 配置说明

### ScrapingConfig 主要参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tiktok_api_key` | str | "" | TikHub API密钥 |
| `use_proxy` | bool | False | 是否使用代理 |
| `proxy_list` | List[str] | None | 代理列表 |
| `request_delay` | float | 2.0 | 请求间隔(秒) |
| `max_retries` | int | 3 | 最大重试次数 |
| `timeout` | int | 30 | 请求超时 |
| `target_hashtags` | List[str] | 服装标签 | 目标标签列表 |
| `target_languages` | List[str] | ["en", "zh"] | 目标语言 |
| `target_regions` | List[str] | ["US", "UK"] | 目标地区 |
| `database_path` | str | "tiktok_clothing_data.db" | 数据库路径 |
| `enable_ocr` | bool | False | 启用OCR功能 |

### 预定义配置

脚本提供了几种预定义配置：

- **DEV_CONFIG**: 开发环境配置
- **PROD_CONFIG**: 生产环境配置
- **FREQUENT_CONFIG**: 高频抓取配置

```python
from config import get_config

# 开发环境
dev_config = get_config("dev")

# 生产环境
prod_config = get_config("prod")

# 高频抓取
frequent_config = get_config("frequent")
```

## 📊 使用示例

### 1. 数据抓取

```python
from tiktok_scraper import TikTokClothingScraper
from config import get_config

config = get_config("prod")
scraper = TikTokClothingScraper(config)

# 抓取所有配置标签
results = scraper.scrape_clothing_videos(
    target_sources=['tikhub_api', 'web_scraper'],
    max_videos_per_tag=100
)

print(f"抓取结果: {results['total_videos']} 个视频")
```

### 2. 产品链接验证

```python
# 验证所有产品链接
validation_results = scraper.validate_product_links()

print(f"有效链接: {validation_results['valid_links']}")
print(f"总链接数: {validation_results['total_links']}")
print(f"验证率: {validation_results['validation_rate']:.2%}")

# 按平台统计
platform_stats = validation_results['platform_stats']
for platform, stats in platform_stats.items():
    print(f"{platform}: {stats['valid']}/{stats['total']}")
```

### 3. 时尚趋势分析

```python
# 获取特定地区的时尚趋势
trending_us = scraper.extract_trending_fashion("US")
trending_uk = scraper.extract_trending_fashion("UK")

if 'error' not in trending_us:
    print(f"美国地区时尚标签: {trending_us['trending_fashion_hashtags']}")
```

### 4. 数据统计

```python
# 获取抓取统计信息
stats = scraper.get_scraping_statistics()

print(f"总视频数: {stats['total_videos']}")
print(f"今日新增: {stats['today_videos']}")
print(f"来源分布: {stats['source_distribution']}")

# 热门标签统计
top_hashtags = stats['top_hashtags']
for tag, count in list(top_hashtags.items())[:10]:
    print(f"{tag}: {count}")
```

### 5. 数据导出

```python
import json
import pandas as pd

# 获取最近24小时的视频
videos = scraper._get_recent_videos(hours=24)

# 导出为JSON
video_data = [asdict(video) for video in videos]
with open('exported_videos.json', 'w', encoding='utf-8') as f:
    json.dump(video_data, f, ensure_ascii=False, indent=2)

# 导出为CSV
df = pd.DataFrame(video_data)
df.to_csv('exported_videos.csv', index=False, encoding='utf-8')
```

### 6. 定时任务

```python
import schedule
import time

def daily_scrape():
    """每日定时抓取"""
    config = get_config("frequent")
    scraper = TikTokClothingScraper(config)
    results = scraper.scrape_clothing_videos()
    print(f"每日抓取完成: {results['total_videos']} 个视频")

# 设置定时任务
schedule.every().day.at("09:00").do(daily_scrape)
schedule.every().day.at("21:00").do(daily_scrape)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🔧 高级功能

### 代理配置

```python
from config import get_config

# 启用代理
config = get_config("prod")
config.proxy_list = [
    "proxy1.example.com:8080",
    "proxy2.example.com:8080"
]
config.use_proxy = True
```

### 自定义标签分类

```python
from config import HASHTAG_CATEGORIES

# 只抓取运动休闲类服装
config.target_hashtags = HASHTAG_CATEGORIES["运动休闲"]

# 组合多个类别
all_fashion_tags = []
for category in HASHTAG_CATEGORIES.values():
    all_fashion_tags.extend(category)

config.target_hashtags = list(set(all_fashion_tags))
```

### OCR功能启用

```python
# 启用OCR功能识别视频中的产品信息
config = ScrapingConfig(
    enable_ocr=True,
    ocr_languages="eng+chi_sim"
)

scraper = TikTokClothingScraper(config)
```

## ⚠️ 合规说明

### 合规特性

- **平台条款遵守**: 严格遵守TikTok开发者平台条款
- **频率控制**: 请求间隔控制，避免对服务器造成压力
- **数据最小化**: 只收集必要的公开信息
- **隐私保护**: 不存储敏感个人信息
- **错误处理**: 完善的错误处理和重试机制

### 使用建议

1. **遵守法律**: 仅用于合法的数据收集和分析
2. **尊重版权**: 不要用于商业竞争或恶意用途
3. **控制频率**: 设置合理的请求间隔和并发数
4. **合规检查**: 使用前请确认当地法律法规

## 🔍 监控和告警

### 健康检查

```python
def check_scraper_health():
    """检查抓取器健康状态"""
    try:
        stats = scraper.get_scraping_statistics()
        
        # 检查错误率
        if stats.get('errors_rate', 0) > 0.1:
            logger.error("错误率过高，需要检查")
        
        # 检查数据新鲜度
        if stats.get('latest_scraped', 0) > 3600:  # 超过1小时
            logger.warning("数据可能过期")
        
        return True
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return False
```

### 自定义告警

```python
def send_alert(message, level="WARNING"):
    """发送告警"""
    if level == "ERROR":
        logger.error(f"ALERT: {message}")
        # 发送邮件/短信/钉钉等
    elif level == "WARNING":
        logger.warning(f"ALERT: {message}")

# 使用示例
if error_rate > 0.2:
    send_alert(f"错误率过高: {error_rate:.2%}", "ERROR")
```

## 📈 性能优化

### 并发控制

```python
from concurrent.futures import ThreadPoolExecutor

def process_video_batch(videos):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_single_video, videos))
    return results
```

### 内存优化

```python
# 分批处理大数据集
def process_large_dataset(all_videos, batch_size=100):
    for i in range(0, len(all_videos), batch_size):
        batch = all_videos[i:i+batch_size]
        process_video_batch(batch)
        # 清理内存
        import gc
        gc.collect()
```

### 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_author_profile(author_id):
    """缓存作者信息"""
    # API调用或数据库查询
    pass
```

## 🐛 故障排除

### 常见问题

1. **API调用失败**: 检查API密钥配置和网络连接
2. **网页爬虫被反爬**: 增加请求延迟、使用代理
3. **OCR功能不工作**: 检查tesseract安装和语言包
4. **数据库锁定**: 确保正确关闭数据库连接

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
from tiktok_scraper import TikTokClothingScraper
scraper = TikTokClothingScraper(config)
```

### 错误处理

脚本包含完善的错误处理机制：

1. **网络错误**: 自动重试（最多3次）
2. **API限制**: 指数退避策略
3. **反爬检测**: 代理轮换和请求延迟
4. **数据验证**: 链接有效性检查
5. **日志记录**: 详细错误日志

## 📝 日志说明

日志文件位置: `/workspace/code/tiktok_scraper.log`

日志级别：
- `INFO`: 正常操作信息
- `WARNING`: 警告信息（限速、重试等）
- `ERROR`: 错误信息（失败请求、异常等）

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

1. Fork本项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目基于TikTok数据调研文档开发，仅用于学习和研究目的。请遵守TikTok的服务条款和当地法律法规。

## 📞 支持

如果遇到问题或有改进建议，请：

1. 查看[文档](docs/tiktok_data_research.md)了解详细调研结果
2. 检查运行日志`tiktok_scraper.log`
3. 提交Issue描述问题
4. 查看示例代码了解使用方法

## 🔄 更新日志

- **v1.0** (2025-11-14): 初始版本，支持TikHub API和网页爬虫
  - 多渠道数据获取（TikHub API + 网页爬虫）
  - 热门服装标签搜索与视频分析
  - 产品链接提取与验证
  - 数据去重和分类存储
  - 合规性检查与错误处理
  - 支持代理和频率控制
  - OCR图像识别功能

---

**注意**: 本脚本严格遵守调研文档中的合规要求，采用"第三方API优先 + 小规模网页采集为辅"的策略，仅用于合法的数据收集和分析目的。使用前请确保符合当地法律法规和TikTok的服务条款。