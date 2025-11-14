# API参考文档

本文档详细介绍了TikTok & Amazon服装数据系统的程序化访问接口，包括REST API、命令行接口和SDK使用说明。

## 📋 目录

- [API概述](#api概述)
- [REST API接口](#rest-api接口)
- [命令行接口](#命令行接口)
- [Python SDK](#python-sdk)
- [数据模型](#数据模型)
- [错误处理](#错误处理)
- [认证授权](#认证授权)
- [限流策略](#限流策略)
- [SDK示例](#sdk示例)
- [最佳实践](#最佳实践)

## API概述

### 接口架构

系统提供三种API访问方式：

1. **REST API**：标准的HTTP接口，适合Web应用集成
2. **CLI接口**：命令行接口，适合脚本和自动化任务
3. **Python SDK**：程序库，适合复杂的数据处理和分析

### 基础URL

```
生产环境: https://api.scraper-system.com/v1
开发环境: http://localhost:8000/api/v1
```

### 数据格式

- **请求格式**：JSON
- **响应格式**：JSON
- **字符编码**：UTF-8
- **日期格式**：ISO 8601 (2025-11-14T10:30:00Z)

### 版本控制

API使用URL版本控制，当前版本为v1。向后兼容的更改会在同一版本中发布，破坏性更改会发布新版本。

## REST API接口

### 认证

所有API请求需要在Header中包含认证信息：

```bash
Authorization: Bearer <your-api-token>
Content-Type: application/json
```

### 基础响应格式

#### 成功响应
```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "meta": {
    "timestamp": "2025-11-14T10:30:00Z",
    "request_id": "req_123456789",
    "version": "v1"
  }
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数无效",
    "details": {
      "field": "platform",
      "issue": "必须是'amazon'或'tiktok'"
    }
  },
  "meta": {
    "timestamp": "2025-11-14T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### 产品相关接口

#### 获取产品列表

```http
GET /api/v1/products
```

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|-----|------|------|--------|------|
| platform | string | 否 | all | 平台筛选: `amazon`, `tiktok`, `all` |
| category | string | 否 | - | 分类筛选 |
| price_min | number | 否 | - | 最低价格 |
| price_max | number | 否 | - | 最高价格 |
| brand | string | 否 | - | 品牌筛选 |
| limit | integer | 否 | 50 | 返回数量限制 (1-1000) |
| offset | integer | 否 | 0 | 偏移量 |
| sort | string | 否 | created_at | 排序字段: `created_at`, `price`, `rating` |
| order | string | 否 | desc | 排序方向: `asc`, `desc` |

**请求示例**：
```bash
curl -X GET "http://localhost:8000/api/v1/products?platform=amazon&category=T-Shirt&price_min=20&price_max=100&limit=10" \
  -H "Authorization: Bearer your-api-token"
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "id": "prod_12345",
        "platform": "amazon",
        "product_id": "B08N5WRWNW",
        "title": "Classic Cotton T-Shirt",
        "brand": "BrandName",
        "price": 29.99,
        "currency": "USD",
        "category": "T-Shirt",
        "rating": 4.5,
        "review_count": 1250,
        "sales_rank": 15,
        "availability": "In Stock",
        "url": "https://amazon.com/dp/B08N5WRWNW",
        "image_url": "https://m.media-amazon.com/images/I/...",
        "created_at": "2025-11-14T10:30:00Z",
        "updated_at": "2025-11-14T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 1250,
      "limit": 10,
      "offset": 0,
      "has_more": true
    }
  }
}
```

#### 获取单个产品详情

```http
GET /api/v1/products/{product_id}
```

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| product_id | string | 是 | 产品ID |

**请求示例**：
```bash
curl -X GET "http://localhost:8000/api/v1/products/prod_12345" \
  -H "Authorization: Bearer your-api-token"
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "product": {
      "id": "prod_12345",
      "platform": "amazon",
      "product_id": "B08N5WRWNW",
      "title": "Classic Cotton T-Shirt",
      "brand": "BrandName",
      "price": 29.99,
      "currency": "USD",
      "category": "T-Shirt",
      "subcategory": "Basic Tees",
      "rating": 4.5,
      "review_count": 1250,
      "sales_rank": 15,
      "availability": "In Stock",
      "url": "https://amazon.com/dp/B08N5WRWNW",
      "image_url": "https://m.media-amazon.com/images/I/...",
      "description": "High quality cotton t-shirt...",
      "features": ["100% Cotton", "Machine Washable", "Available in Multiple Colors"],
      "specifications": {
        "material": "100% Cotton",
        "care": "Machine wash cold",
        "origin": "Made in USA"
      },
      "created_at": "2025-11-14T10:30:00Z",
      "updated_at": "2025-11-14T10:30:00Z",
      "last_scraped": "2025-11-14T10:25:00Z"
    }
  }
}
```

#### 搜索产品

```http
GET /api/v1/products/search
```

**查询参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| q | string | 是 | 搜索关键词 |
| platform | string | 否 | 平台筛选 |
| category | string | 否 | 分类筛选 |
| price_range | string | 否 | 价格范围，如 "20-100" |
| sort_by | string | 否 | 排序方式: `relevance`, `price_low`, `price_high`, `rating` |
| limit | integer | 否 | 返回数量 (1-100) |

**请求示例**：
```bash
curl -X GET "http://localhost:8000/api/v1/products/search?q=graphic%20tee&platform=amazon&sort_by=price_low&limit=20" \
  -H "Authorization: Bearer your-api-token"
```

### 统计和分析接口

#### 获取数据概览

```http
GET /api/v1/analytics/overview
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_products": 15640,
      "amazon_products": 8932,
      "tiktok_products": 6708,
      "today_new_products": 156,
      "categories_count": 28,
      "brands_count": 456
    },
    "trends": {
      "products_trend": [
        {"date": "2025-11-14", "count": 156},
        {"date": "2025-11-13", "count": 142}
      ],
      "platform_distribution": [
        {"platform": "amazon", "count": 8932, "percentage": 57.1},
        {"platform": "tiktok", "count": 6708, "percentage": 42.9}
      ]
    },
    "top_categories": [
      {"category": "T-Shirt", "count": 3456, "trend": "+5%"},
      {"category": "Hoodie", "count": 2134, "trend": "+3%"}
    ],
    "price_analysis": {
      "avg_price": 45.67,
      "median_price": 39.99,
      "min_price": 9.99,
      "max_price": 299.99
    }
  }
}
```

#### 获取热门产品

```http
GET /api/v1/analytics/trending
```

**查询参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| period | string | 否 | 时间周期: `1d`, `7d`, `30d`, `90d` |
| platform | string | 否 | 平台筛选 |
| metric | string | 否 | 排序指标: `sales_rank`, `rating`, `review_count` |

**响应示例**：
```json
{
  "success": true,
  "data": {
    "trending_products": [
      {
        "id": "prod_12345",
        "title": "Best Selling Hoodie 2025",
        "platform": "amazon",
        "price": 59.99,
        "rating": 4.8,
        "review_count": 2341,
        "sales_rank": 3,
        "trend_score": 95,
        "trend_direction": "up",
        "growth_rate": "+15%"
      }
    ],
    "trending_categories": [
      {"category": "T-Shirt", "growth": "+12%", "new_products": 45}
    ]
  }
}
```

#### 价格分析

```http
GET /api/v1/analytics/price-analysis
```

**查询参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| category | string | 否 | 产品分类 |
| platform | string | 否 | 平台 |
| period | string | 否 | 分析周期: `7d`, `30d`, `90d` |

**响应示例**：
```json
{
  "success": true,
  "data": {
    "price_statistics": {
      "count": 1234,
      "mean": 45.67,
      "median": 39.99,
      "std_dev": 18.23,
      "min": 9.99,
      "max": 299.99,
      "percentiles": {
        "25": 29.99,
        "50": 39.99,
        "75": 54.99,
        "90": 79.99,
        "95": 99.99
      }
    },
    "price_distribution": [
      {"range": "0-20", "count": 123, "percentage": 10.0},
      {"range": "20-40", "count": 456, "percentage": 37.0}
    ],
    "price_trends": [
      {"date": "2025-11-14", "avg_price": 45.67},
      {"date": "2025-11-13", "avg_price": 45.12}
    ]
  }
}
```

### 抓取任务接口

#### 启动抓取任务

```http
POST /api/v1/scraping/tasks
```

**请求体**：
```json
{
  "platform": "amazon",
  "categories": ["T-Shirt", "Hoodie"],
  "keywords": ["print", "graphic"],
  "options": {
    "max_products": 1000,
    "priority": "high",
    "schedule_time": "2025-11-14T12:00:00Z"
  }
}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "task_id": "task_98765",
    "status": "pending",
    "estimated_completion": "2025-11-14T12:15:00Z",
    "queue_position": 1,
    "estimated_products": 800
  }
}
```

#### 获取任务状态

```http
GET /api/v1/scraping/tasks/{task_id}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "task": {
      "task_id": "task_98765",
      "platform": "amazon",
      "status": "running",
      "progress": 65,
      "products_found": 520,
      "products_processed": 338,
      "start_time": "2025-11-14T12:00:00Z",
      "estimated_completion": "2025-11-14T12:15:00Z",
      "errors": [],
      "warnings": []
    }
  }
}
```

#### 列出任务

```http
GET /api/v1/scraping/tasks
```

**查询参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| status | string | 否 | 状态筛选: `pending`, `running`, `completed`, `failed` |
| platform | string | 否 | 平台筛选 |
| limit | integer | 否 | 返回数量 |
| offset | integer | 否 | 偏移量 |

### 数据导出接口

#### 导出数据

```http
POST /api/v1/export
```

**请求体**：
```json
{
  "format": "json",  // "json", "csv", "excel", "xml"
  "filters": {
    "platform": "amazon",
    "category": "T-Shirt",
    "created_after": "2025-11-01T00:00:00Z"
  },
  "fields": [
    "id", "title", "price", "rating", "review_count"
  ],
  "options": {
    "include_images": false,
    "compress": true
  }
}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "export_id": "exp_abcdef",
    "status": "processing",
    "download_url": null,
    "estimated_completion": "2025-11-14T12:05:00Z",
    "file_size": "15.2MB",
    "record_count": 12345
  }
}
```

#### 获取导出状态

```http
GET /api/v1/export/{export_id}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "export": {
      "export_id": "exp_abcdef",
      "status": "completed",
      "download_url": "https://api.scraper-system.com/v1/exports/exp_abcdef/download",
      "expires_at": "2025-11-21T12:00:00Z",
      "file_size": "15.2MB",
      "record_count": 12345,
      "created_at": "2025-11-14T12:00:00Z",
      "completed_at": "2025-11-14T12:04:23Z"
    }
  }
}
```

#### 下载导出文件

```http
GET /api/v1/exports/{export_id}/download
```

**响应**：直接返回文件流

### 系统管理接口

#### 获取系统状态

```http
GET /api/v1/system/status
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": "7d 12h 34m",
    "components": {
      "database": {"status": "healthy", "response_time": "5ms"},
      "scraper": {"status": "healthy", "active_tasks": 2},
      "api": {"status": "healthy", "response_time": "12ms"}
    },
    "resources": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "disk_usage": 23.1,
      "network_io": {
        "bytes_sent": 1024000,
        "bytes_received": 2048000
      }
    },
    "recent_errors": []
  }
}
```

#### 获取配置

```http
GET /api/v1/system/config
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "config": {
      "scraping": {
        "amazon": {
          "enabled": true,
          "max_concurrent": 3,
          "request_delay": 1.0
        },
        "tiktok": {
          "enabled": true,
          "max_concurrent": 2,
          "request_delay": 2.0
        }
      },
      "database": {
        "backup_enabled": true,
        "backup_interval": "24h"
      },
      "monitoring": {
        "log_level": "INFO",
        "performance_tracking": true
      }
    }
  }
}
```

#### 更新配置

```http
PUT /api/v1/system/config
```

**请求体**：
```json
{
  "scraping": {
    "amazon": {
      "max_concurrent": 5,
      "request_delay": 0.5
    }
  }
}
```

## 命令行接口

### 基本命令

#### 查看帮助

```bash
# 主帮助
python main.py --help

# 子命令帮助
python main.py scrape --help
python main.py config --help
python main.py status --help
```

### 抓取相关命令

#### 启动抓取

```bash
# 抓取Amazon数据
python main.py scrape --platform amazon

# 抓取TikTok数据
python main.py scrape --platform tiktok

# 同时抓取两个平台
python main.py scrape --platform all

# 自定义参数
python main.py scrape --platform amazon --category "T-Shirt" --keywords "print,graphic" --max-products 100

# 异步执行
python main.py scrape --platform all --async --output-file results.json
```

#### 抓取选项

| 选项 | 描述 | 示例 |
|------|------|------|
| `--platform` | 指定平台 | `amazon`, `tiktok`, `all` |
| `--category` | 产品分类 | `"T-Shirt,Hoodie"` |
| `--keywords` | 搜索关键词 | `"print,graphic"` |
| `--max-products` | 最大产品数 | `1000` |
| `--async` | 异步执行 | - |
| `--output-file` | 输出文件 | `results.json` |
| `--timeout` | 超时时间 | `300` |

### 状态监控命令

#### 查看系统状态

```bash
# 基本状态
python main.py status

# 详细状态
python main.py status --verbose

# 特定组件状态
python main.py status --component database
python main.py status --component scraper
python main.py status --component api
```

#### 实时监控

```bash
# 实时日志
python main.py monitor --log

# 性能监控
python main.py monitor --performance --interval 10

# 资源监控
python main.py monitor --resources
```

### 数据查询命令

#### 产品查询

```bash
# 基本查询
python main.py query --platform amazon --category "T-Shirt"

# 价格范围查询
python main.py query --price-min 20 --price-max 100

# 高级查询
python main.py query --brand "Nike" --rating-min 4.0 --sort-by price --order asc

# 输出格式
python main.py query --format json --output products.json
```

#### 统计查询

```bash
# 基础统计
python main.py stats --platform amazon

# 分类统计
python main.py stats --by-category --period 30d

# 价格统计
python main.py stats --price-analysis --platform all

# 趋势分析
python main.py stats --trends --period 7d --output trends.json
```

### 配置管理命令

#### 查看配置

```bash
# 查看所有配置
python main.py config show

# 查看特定模块
python main.py config show scraping.amazon

# 查看特定参数
python main.py config get scraping.amazon.max_concurrent
```

#### 修改配置

```bash
# 设置单个参数
python main.py config set scraping.amazon.max_concurrent 5

# 批量设置
python main.py config set-batch config/quick_settings.yaml

# 重置配置
python main.py config reset --module scraping.amazon
```

### 数据库管理命令

#### 数据库操作

```bash
# 初始化数据库
python main.py db init

# 备份数据库
python main.py db backup --path /backup/scraping_$(date +%Y%m%d).db

# 恢复数据库
python main.py db restore --path /backup/scraping_20251114.db

# 清理数据
python main.py db cleanup --older-than 30d

# 数据库优化
python main.py db optimize
```

#### 数据导出

```bash
# 导出JSON
python main.py export --format json --output products.json

# 导出CSV
python main.py export --format csv --output products.csv --platform amazon

# 自定义字段
python main.py export --fields "id,title,price,rating" --output custom_export.xlsx
```

## Python SDK

### 安装SDK

```bash
pip install tiktok-amazon-scraper-sdk
```

### 基础使用

#### 初始化客户端

```python
from scraper_sdk import ScraperClient

# 初始化客户端
client = ScraperClient(
    base_url="http://localhost:8000/api/v1",
    api_key="your-api-key"
)
```

#### 产品查询

```python
# 获取产品列表
products = client.products.list(
    platform="amazon",
    category="T-Shirt",
    limit=50,
    sort="price"
)

for product in products:
    print(f"{product.title}: ${product.price}")

# 获取单个产品
product = client.products.get("prod_12345")
print(f"Product: {product.title}")

# 搜索产品
search_results = client.products.search(
    q="graphic tee",
    platform="amazon",
    sort_by="price_low",
    limit=20
)
```

#### 数据分析

```python
# 获取概览统计
overview = client.analytics.overview()
print(f"Total products: {overview.total_products}")

# 获取趋势数据
trending = client.analytics.trending(
    period="7d",
    platform="amazon"
)

# 价格分析
price_analysis = client.analytics.price_analysis(
    category="T-Shirt",
    period="30d"
)
```

#### 抓取任务管理

```python
# 启动抓取任务
task = client.scraping.start_task(
    platform="amazon",
    categories=["T-Shirt", "Hoodie"],
    keywords=["print", "graphic"],
    max_products=1000
)

print(f"Task ID: {task.task_id}")

# 轮询任务状态
import time
while task.status in ["pending", "running"]:
    task = client.scraping.get_task(task.task_id)
    print(f"Progress: {task.progress}%")
    time.sleep(5)

print(f"Task completed. Found {task.products_found} products")
```

### 高级功能

#### 批量操作

```python
from scraper_sdk import BatchClient

# 批量查询
batch_client = BatchClient(client)

# 批量产品查询
product_queries = [
    {"platform": "amazon", "category": "T-Shirt"},
    {"platform": "amazon", "category": "Hoodie"},
    {"platform": "tiktok", "category": "服装"}
]

results = batch_client.products.batch_query(product_queries)
for result in results:
    print(f"Query {result.query}: {len(result.products)} products")
```

#### 异步操作

```python
import asyncio
from scraper_sdk import AsyncScraperClient

async def async_example():
    client = AsyncScraperClient(
        base_url="http://localhost:8000/api/v1",
        api_key="your-api-key"
    )
    
    # 异步查询多个平台
    tasks = [
        client.products.list(platform="amazon", limit=100),
        client.products.list(platform="tiktok", limit=100)
    ]
    
    results = await asyncio.gather(*tasks)
    amazon_products, tiktok_products = results
    
    print(f"Amazon: {len(amazon_products)} products")
    print(f"TikTok: {len(tiktok_products)} products")

# 运行异步函数
asyncio.run(async_example())
```

#### 流式数据处理

```python
from scraper_sdk import StreamingClient

def process_products():
    client = StreamingClient(
        base_url="http://localhost:8000/api/v1",
        api_key="your-api-key"
    )
    
    # 流式处理大量数据
    count = 0
    for product in client.products.stream(platform="amazon"):
        # 实时处理每个产品
        process_product(product)
        count += 1
        
        if count % 1000 == 0:
            print(f"Processed {count} products")
    
    print(f"Total processed: {count} products")

process_products()
```

## 数据模型

### 产品模型 (Product)

```python
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Product:
    """产品数据模型"""
    id: str
    platform: str  # 'amazon' or 'tiktok'
    product_id: str  # 平台产品ID
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    category: Optional[str] = None
    subcategory: Optional[str] = None
    rating: Optional[float] = None
    review_count: int = 0
    sales_rank: Optional[int] = None
    availability: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    specifications: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_scraped: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """从字典创建实例"""
        return cls(**data)
```

### 任务模型 (Task)

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScrapingTask:
    """抓取任务模型"""
    task_id: str
    platform: str
    status: TaskStatus
    categories: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    options: Optional[dict] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: int = 0
    products_found: int = 0
    products_processed: int = 0
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    
    @property
    def is_completed(self) -> bool:
        """检查任务是否完成"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    @property
    def duration(self) -> Optional[int]:
        """获取任务执行时长（秒）"""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return None
```

### 分析模型 (Analytics)

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class PlatformStats:
    """平台统计"""
    platform: str
    total_products: int
    avg_price: float
    top_categories: List[str]
    growth_rate: Optional[float] = None

@dataclass
class PriceStats:
    """价格统计"""
    count: int
    mean: float
    median: float
    std_dev: float
    min_price: float
    max_price: float
    percentiles: Dict[str, float]

@dataclass
class TrendData:
    """趋势数据"""
    date: datetime
    value: float
    platform: Optional[str] = None
    category: Optional[str] = None

@dataclass
class AnalyticsOverview:
    """分析概览"""
    total_products: int
    amazon_products: int
    tiktok_products: int
    today_new_products: int
    categories_count: int
    brands_count: int
    platform_stats: List[PlatformStats]
    price_stats: PriceStats
    top_categories: List[Dict]
    recent_trends: List[TrendData]
```

## 错误处理

### 错误码定义

| 错误码 | HTTP状态 | 描述 |
|--------|----------|------|
| `VALIDATION_ERROR` | 400 | 请求参数验证失败 |
| `AUTHENTICATION_ERROR` | 401 | 认证失败 |
| `AUTHORIZATION_ERROR` | 403 | 权限不足 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |
| `TIMEOUT_ERROR` | 504 | 请求超时 |

### 异常处理示例

#### Python SDK异常处理

```python
from scraper_sdk import ScraperClient, APIError, ValidationError, RateLimitError

client = ScraperClient(base_url="http://localhost:8000/api/v1", api_key="your-key")

try:
    products = client.products.list(platform="invalid_platform")
except ValidationError as e:
    print(f"参数验证错误: {e.message}")
    print(f"错误详情: {e.details}")
except RateLimitError as e:
    print(f"频率限制，等待 {e.retry_after} 秒")
    time.sleep(e.retry_after)
    # 重试请求
    products = client.products.list(platform="amazon")
except APIError as e:
    print(f"API错误: {e.code} - {e.message}")
    # 记录错误日志
    logger.error(f"API调用失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

#### REST API错误处理

```python
import requests
from requests.exceptions import RequestException

def api_request(url, headers=None, timeout=30):
    """API请求封装"""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise APIError("REQUEST_TIMEOUT", "请求超时")
    except requests.exceptions.ConnectionError:
        raise APIError("CONNECTION_ERROR", "网络连接失败")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            raise RateLimitError("频率限制")
        elif e.response.status_code == 401:
            raise APIError("AUTHENTICATION_ERROR", "认证失败")
        else:
            raise APIError("HTTP_ERROR", f"HTTP错误: {e.response.status_code}")
    except RequestException as e:
        raise APIError("REQUEST_ERROR", f"请求错误: {e}")
```

### 重试机制

#### 自动重试

```python
from scraper_sdk import RetryConfig, ScraperClient

# 配置重试策略
retry_config = RetryConfig(
    max_retries=3,
    backoff_factor=2.0,
    max_retry_delay=60,
    retryable_status_codes=[429, 500, 502, 503, 504]
)

client = ScraperClient(
    base_url="http://localhost:8000/api/v1",
    api_key="your-key",
    retry_config=retry_config
)

# 启用重试的请求
products = client.products.list(platform="amazon")  # 自动重试失败请求
```

#### 手动重试

```python
import time
from scraper_sdk import RateLimitError

def retry_with_backoff(func, max_retries=3, base_delay=1):
    """指数退避重试"""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"频率限制，等待 {delay} 秒后重试...")
            time.sleep(delay)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(base_delay)

# 使用重试函数
products = retry_with_backoff(
    lambda: client.products.list(platform="amazon"),
    max_retries=3
)
```

## 认证授权

### API Key认证

```python
# 通过header传递
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}

# 通过参数传递
client = ScraperClient(
    base_url="http://localhost:8000/api/v1",
    api_key="your-api-key"
)
```

### OAuth认证

```python
from scraper_sdk import OAuthClient

# OAuth流程
oauth_client = OAuthClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="http://localhost:8000/callback"
)

# 获取授权URL
auth_url = oauth_client.get_authorization_url(
    scope="read write",
    state="random-state-string"
)

# 处理回调
def handle_oauth_callback(code, state):
    tokens = oauth_client.exchange_code(code)
    access_token = tokens["access_token"]
    
    # 使用访问令牌初始化客户端
    client = ScraperClient(
        base_url="http://localhost:8000/api/v1",
        access_token=access_token
    )
    
    return client
```

### 权限管理

#### 权限级别

| 权限 | 描述 | 允许的操作 |
|------|------|-----------|
| `read` | 只读权限 | 查询产品、统计数据 |
| `write` | 读写权限 | 启动抓取任务、导出数据 |
| `admin` | 管理权限 | 修改配置、系统管理 |
| `billing` | 计费权限 | 查看使用统计、管理订阅 |

#### 权限验证

```python
# 检查权限
def check_permission(client, required_permission):
    user_permissions = client.auth.get_permissions()
    if required_permission not in user_permissions:
        raise PermissionError(f"需要 {required_permission} 权限")

# 使用权限检查
try:
    check_permission(client, "write")
    task = client.scraping.start_task(platform="amazon")
except PermissionError as e:
    print(f"权限不足: {e}")
```

## 限流策略

### 限流规则

| 用户类型 | 每分钟请求数 | 每小时请求数 | 并发连接数 |
|----------|-------------|-------------|-----------|
| 免费用户 | 60 | 1000 | 3 |
| 付费用户 | 300 | 10000 | 10 |
| 企业用户 | 1000 | 50000 | 50 |

### 限流头信息

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
X-RateLimit-Retry-After: 45
```

### 限流处理

```python
from scraper_sdk import RateLimitError

def handle_rate_limit(response):
    """处理限流响应"""
    if response.status_code == 429:
        retry_after = int(response.headers.get('X-RateLimit-Retry-After', 60))
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        
        raise RateLimitError(
            message="请求频率超限",
            retry_after=retry_after,
            remaining=remaining,
            reset_time=datetime.fromtimestamp(reset_time)
        )

# 使用限流处理
try:
    result = api_request("http://localhost:8000/api/v1/products")
except RateLimitError as e:
    print(f"限流重试，等待 {e.retry_after} 秒")
    time.sleep(e.retry_after)
    result = api_request("http://localhost:8000/api/v1/products")
```

## SDK示例

### 完整示例：电商竞品分析

```python
import asyncio
from datetime import datetime, timedelta
from scraper_sdk import AsyncScraperClient
import pandas as pd
import matplotlib.pyplot as plt

class CompetitorAnalyzer:
    """竞品分析器"""
    
    def __init__(self, api_key: str):
        self.client = AsyncScraperClient(
            base_url="http://localhost:8000/api/v1",
            api_key=api_key
        )
    
    async def analyze_market_trends(self, category: str = "T-Shirt"):
        """分析市场趋势"""
        print(f"分析 {category} 类别的市场趋势...")
        
        # 并行获取数据
        tasks = [
            self.client.products.list(
                platform="amazon",
                category=category,
                limit=1000,
                sort="sales_rank"
            ),
            self.client.products.list(
                platform="tiktok",
                category=category,
                limit=1000,
                sort="rating"
            )
        ]
        
        amazon_products, tiktok_products = await asyncio.gather(*tasks)
        
        # 数据分析
        analysis = self._analyze_products(amazon_products, tiktok_products, category)
        
        return analysis
    
    def _analyze_products(self, amazon_products, tiktok_products, category):
        """分析产品数据"""
        analysis = {
            "category": category,
            "timestamp": datetime.now(),
            "amazon": {
                "count": len(amazon_products),
                "avg_price": sum(p.price for p in amazon_products if p.price) / len(amazon_products) if amazon_products else 0,
                "top_brands": self._get_top_brands(amazon_products, 5),
                "price_range": self._get_price_range(amazon_products)
            },
            "tiktok": {
                "count": len(tiktok_products),
                "avg_rating": sum(p.rating for p in tiktok_products if p.rating) / len([p for p in tiktok_products if p.rating]) if tiktok_products else 0,
                "top_brands": self._get_top_brands(tiktok_products, 5),
                "engagement": self._calculate_engagement(tiktok_products)
            },
            "comparison": self._compare_platforms(amazon_products, tiktok_products)
        }
        
        return analysis
    
    def _get_top_brands(self, products, limit=5):
        """获取热门品牌"""
        brand_counts = {}
        for product in products:
            if product.brand:
                brand_counts[product.brand] = brand_counts.get(product.brand, 0) + 1
        
        return sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def _get_price_range(self, products):
        """获取价格范围"""
        prices = [p.price for p in products if p.price]
        if prices:
            return {
                "min": min(prices),
                "max": max(prices),
                "median": sorted(prices)[len(prices)//2]
            }
        return None
    
    def _calculate_engagement(self, products):
        """计算参与度指标"""
        ratings = [p.rating for p in products if p.rating]
        review_counts = [p.review_count for p in products]
        
        return {
            "avg_rating": sum(ratings) / len(ratings) if ratings else 0,
            "total_reviews": sum(review_counts),
            "engagement_score": sum(r * rc for r, rc in zip(ratings, review_counts)) / len(products) if products else 0
        }
    
    def _compare_platforms(self, amazon_products, tiktok_products):
        """平台对比分析"""
        return {
            "price_difference": self._calculate_price_diff(amazon_products, tiktok_products),
            "quality_comparison": self._compare_quality(amazon_products, tiktok_products),
            "market_overlap": self._calculate_overlap(amazon_products, tiktok_products)
        }
    
    def _calculate_price_diff(self, amazon_products, tiktok_products):
        """计算价格差异"""
        amazon_prices = [p.price for p in amazon_products if p.price]
        tiktok_prices = [p.price for p in tiktok_products if p.price]
        
        if amazon_prices and tiktok_prices:
            avg_amazon = sum(amazon_prices) / len(amazon_prices)
            avg_tiktok = sum(tiktok_prices) / len(tiktok_prices)
            
            return {
                "amazon_avg": avg_amazon,
                "tiktok_avg": avg_tiktok,
                "difference_percent": ((avg_tiktok - avg_amazon) / avg_amazon) * 100
            }
        return None
    
    def _compare_quality(self, amazon_products, tiktok_products):
        """质量对比"""
        amazon_ratings = [p.rating for p in amazon_products if p.rating]
        tiktok_ratings = [p.rating for p in tiktok_products if p.rating]
        
        return {
            "amazon_avg_rating": sum(amazon_ratings) / len(amazon_ratings) if amazon_ratings else 0,
            "tiktok_avg_rating": sum(tiktok_ratings) / len(tiktok_ratings) if tiktok_ratings else 0
        }
    
    def _calculate_overlap(self, amazon_products, tiktok_products):
        """计算市场重叠度"""
        # 基于品牌和价格范围的简单重叠度计算
        amazon_brands = set(p.brand for p in amazon_products if p.brand)
        tiktok_brands = set(p.brand for p in tiktok_products if p.brand)
        
        common_brands = amazon_brands & tiktok_brands
        total_brands = amazon_brands | tiktok_brands
        
        return {
            "common_brands": len(common_brands),
            "total_brands": len(total_brands),
            "overlap_percentage": (len(common_brands) / len(total_brands)) * 100 if total_brands else 0
        }
    
    async def generate_report(self, analysis):
        """生成分析报告"""
        report = f"""
# {analysis['category']} 竞品分析报告

## 执行时间
{analysis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

## 平台对比

### Amazon
- 产品数量: {analysis['amazon']['count']}
- 平均价格: ${analysis['amazon']['avg_price']:.2f}
- 价格范围: ${analysis['amazon']['price_range']['min']:.2f} - ${analysis['amazon']['price_range']['max']:.2f}
- 热门品牌: {', '.join([f"{brand}({count})" for brand, count in analysis['amazon']['top_brands'][:3]])}

### TikTok
- 产品数量: {analysis['tiktok']['count']}
- 平均评分: {analysis['tiktok']['avg_rating']:.2f}
- 参与度评分: {analysis['tiktok']['engagement']['engagement_score']:.2f}
- 热门品牌: {', '.join([f"{brand}({count})" for brand, count in analysis['tiktok']['top_brands'][:3]])}

## 市场竞争分析

### 价格对比
{f"Amazon平均价格比TikTok低 {abs(analysis['comparison']['price_difference']['difference_percent']):.1f}%" if analysis['comparison']['price_difference'] else "价格数据不足"}

### 质量对比
- Amazon平均评分: {analysis['comparison']['quality_comparison']['amazon_avg_rating']:.2f}
- TikTok平均评分: {analysis['comparison']['quality_comparison']['tiktok_avg_rating']:.2f}

### 品牌重叠度
- 共同品牌数量: {analysis['comparison']['market_overlap']['common_brands']}
- 总品牌数量: {analysis['comparison']['market_overlap']['total_brands']}
- 重叠率: {analysis['comparison']['market_overlap']['overlap_percentage']:.1f}%

## 建议
1. 关注价格敏感的市场机会
2. 重点关注高评分产品特征
3. 考虑品牌合作策略
4. 监控热门产品趋势
"""
        return report
    
    def export_to_excel(self, analysis, filename="competitor_analysis.xlsx"):
        """导出分析结果到Excel"""
        with pd.ExcelWriter(filename) as writer:
            # Amazon数据
            amazon_data = []
            for product in analysis.get('amazon_products', []):
                amazon_data.append({
                    'title': product.title,
                    'brand': product.brand,
                    'price': product.price,
                    'rating': product.rating,
                    'review_count': product.review_count
                })
            
            if amazon_data:
                pd.DataFrame(amazon_data).to_excel(writer, sheet_name='Amazon Products', index=False)
            
            # TikTok数据
            tiktok_data = []
            for product in analysis.get('tiktok_products', []):
                tiktok_data.append({
                    'title': product.title,
                    'brand': product.brand,
                    'rating': product.rating,
                    'review_count': product.review_count,
                    'engagement_score': (product.rating or 0) * product.review_count
                })
            
            if tiktok_data:
                pd.DataFrame(tiktok_data).to_excel(writer, sheet_name='TikTok Products', index=False)
            
            # 分析摘要
            summary_data = [
                ['Amazon产品数量', analysis['amazon']['count']],
                ['Amazon平均价格', f"${analysis['amazon']['avg_price']:.2f}"],
                ['TikTok产品数量', analysis['tiktok']['count']],
                ['TikTok平均评分', f"{analysis['tiktok']['avg_rating']:.2f}"],
                ['品牌重叠率', f"{analysis['comparison']['market_overlap']['overlap_percentage']:.1f}%"]
            ]
            
            pd.DataFrame(summary_data, columns=['指标', '值']).to_excel(
                writer, sheet_name='Analysis Summary', index=False
            )

# 使用示例
async def main():
    analyzer = CompetitorAnalyzer(api_key="your-api-key")
    
    # 分析市场趋势
    analysis = await analyzer.analyze_market_trends("T-Shirt")
    
    # 生成报告
    report = await analyzer.generate_report(analysis)
    print(report)
    
    # 导出数据
    analyzer.export_to_excel(analysis, "t-shirt_analysis.xlsx")
    
    # 保存报告
    with open("competitor_report.md", "w", encoding="utf-8") as f:
        f.write(report)

# 运行示例
if __name__ == "__main__":
    asyncio.run(main())
```

## 最佳实践

### 性能优化

#### 1. 使用批量请求

```python
# 错误做法：单次请求
for product_id in product_ids:
    product = client.products.get(product_id)  # 100个请求

# 正确做法：批量请求
products = client.products.batch_get(product_ids)  # 1个请求
```

#### 2. 使用筛选条件

```python
# 错误做法：获取所有数据后过滤
all_products = client.products.list(limit=10000)
filtered_products = [p for p in all_products if p.price > 50]

# 正确做法：服务端筛选
filtered_products = client.products.list(
    price_min=50,
    limit=1000
)
```

#### 3. 使用流式处理

```python
# 处理大量数据时使用流式处理
def process_large_dataset():
    count = 0
    for product in client.products.stream(platform="amazon"):
        process_product(product)
        count += 1
        
        if count % 1000 == 0:
            print(f"已处理 {count} 个产品")

# 而不是一次性获取
# products = client.products.list(limit=10000)  # 可能导致内存问题
```

### 错误处理

#### 1. 使用适当的异常类型

```python
from scraper_sdk import (
    ValidationError, RateLimitError, 
    AuthenticationError, APIError
)

try:
    result = client.products.list(invalid_param="value")
except ValidationError as e:
    # 处理参数验证错误
    logger.warning(f"参数验证失败: {e.details}")
except RateLimitError as e:
    # 处理频率限制
    wait_time = e.retry_after
    logger.info(f"频率限制，等待 {wait_time} 秒")
    time.sleep(wait_time)
except AuthenticationError as e:
    # 处理认证错误
    logger.error("认证失败，请检查API密钥")
    raise
except APIError as e:
    # 处理其他API错误
    logger.error(f"API错误 {e.code}: {e.message}")
```

#### 2. 实现指数退避重试

```python
import random
import asyncio

async def retry_with_jitter(func, max_retries=3):
    """带随机抖动的重试机制"""
    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            # 指数退避 + 随机抖动
            base_delay = 2 ** attempt
            jitter = random.uniform(0, 1)
            delay = base_delay + jitter
            
            logger.info(f"重试 {attempt + 1}/{max_retries}，等待 {delay:.2f} 秒")
            await asyncio.sleep(delay)
```

### 数据缓存

#### 1. 本地缓存

```python
from functools import lru_cache
import time

class CachedScraperClient:
    def __init__(self, client):
        self.client = client
        self.cache_ttl = 300  # 5分钟缓存
    
    @lru_cache(maxsize=1000)
    def get_product(self, product_id, cache_key=None):
        """缓存产品查询结果"""
        return self.client.products.get(product_id)
    
    def clear_cache(self):
        """清除缓存"""
        self.get_product.cache_clear()

# 使用缓存客户端
cached_client = CachedScraperClient(client)
```

#### 2. 结果缓存

```python
import hashlib
import json

def cache_result(func):
    """简单的结果缓存装饰器"""
    cache = {}
    
    def wrapper(*args, **kwargs):
        # 生成缓存键
        cache_key = hashlib.md5(
            json.dumps((args, kwargs), sort_keys=True).encode()
        ).hexdigest()
        
        if cache_key in cache:
            result, timestamp = cache[cache_key]
            if time.time() - timestamp < 300:  # 5分钟TTL
                return result
        
        # 执行函数并缓存结果
        result = func(*args, **kwargs)
        cache[cache_key] = (result, time.time())
        return result
    
    return wrapper

# 使用缓存装饰器
@cache_result
def get_cached_products(platform, category):
    return client.products.list(platform=platform, category=category)
```

### 并发控制

#### 1. 限制并发数

```python
import asyncio
from asyncio import Semaphore

async def concurrent_scraping(product_ids, max_concurrent=10):
    """限制并发数的批量抓取"""
    semaphore = Semaphore(max_concurrent)
    
    async def scrape_single(product_id):
        async with semaphore:
            try:
                return await client.products.get(product_id)
            except Exception as e:
                logger.error(f"抓取产品 {product_id} 失败: {e}")
                return None
    
    # 创建任务
    tasks = [scrape_single(pid) for pid in product_ids]
    
    # 限制并发执行
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 过滤有效结果
    valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
    
    return valid_results
```

#### 2. 异步处理

```python
async def async_data_processing():
    """异步数据处理流程"""
    # 并行获取不同平台数据
    tasks = [
        client.products.list(platform="amazon", limit=500),
        client.products.list(platform="tiktok", limit=500),
        client.analytics.trending(period="7d")
    ]
    
    amazon_products, tiktok_products, trends = await asyncio.gather(*tasks)
    
    # 并行处理数据
    processing_tasks = [
        process_amazon_data(amazon_products),
        process_tiktok_data(tiktok_products),
        analyze_trends(trends)
    ]
    
    results = await asyncio.gather(*processing_tasks)
    
    return results
```

### 监控和日志

#### 1. 性能监控

```python
import time
import functools
from contextlib import contextmanager

@contextmanager
def measure_time(operation_name):
    """性能监控上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"{operation_name} 耗时: {duration:.2f} 秒")

# 使用性能监控
def expensive_operation():
    with measure_time("expensive_operation"):
        # 耗时的操作
        products = client.products.list(limit=1000)

def monitor_api_calls(func):
    """API调用监控装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            logger.info(f"API调用成功: {func.__name__}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"API调用失败: {func.__name__}, 耗时: {duration:.2f}s, 错误: {e}")
            raise
        finally:
            pass
    return wrapper

# 应用监控
client.products.list = monitor_api_calls(client.products.list)
```

#### 2. 详细日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('scraper')

def log_api_usage(endpoint, params, result_count):
    """记录API使用情况"""
    logger.info(
        f"API调用: {endpoint} | 参数: {params} | 结果数量: {result_count}"
    )

def log_error_with_context(error, context):
    """记录带上下文的错误"""
    logger.error(
        f"错误: {error} | 上下文: {context}",
        exc_info=True
    )

# 在API调用中使用
try:
    products = client.products.list(platform="amazon")
    log_api_usage("products.list", {"platform": "amazon"}, len(products))
except Exception as e:
    log_error_with_context(e, {"platform": "amazon", "operation": "list"})
```

---

## 总结

本文档全面介绍了TikTok & Amazon服装数据系统的API接口：

- **REST API**：提供完整的HTTP接口
- **CLI接口**：便于脚本和自动化
- **Python SDK**：程序化访问和集成
- **数据模型**：标准化的数据结构
- **错误处理**：完善的异常处理机制
- **最佳实践**：性能优化和使用建议

通过本API文档，您可以：

1. 集成系统到现有应用
2. 构建自定义的数据分析工具
3. 自动化数据处理流程
4. 开发实时监控应用

如需更多帮助，请参考[故障排除指南](troubleshooting.md)或联系技术支持团队。