# 数据清洗处理模块

一个通用的数据清洗和处理模块，专门用于处理从TikTok和Amazon抓取的产品数据，确保数据符合数据库结构要求。

## 功能特性

### 1. 产品信息标准化
- **产品名称清理**：去除HTML标签，标准化空白字符，移除特殊字符
- **价格格式化**：去除货币符号，统一为小数格式，验证价格范围（0-1000美元）
- **分类标签映射**：自动映射常见产品分类（tshirt/hoodie/sweatshirt/other）
- **URL验证和规范化**：验证URL格式，添加协议，标准化域名大小写

### 2. 数据验证
- **价格范围验证**：确保价格在0-1000美元之间
- **评分范围验证**：确保评分在0-5星之间
- **URL格式验证**：验证产品链接和图片链接的有效性
- **必填字段检查**：验证title、price、category、product_url等必填字段

### 3. 数据增强
- **关键词提取**：从产品标题中提取有意义的关键词
- **产品Slug生成**：生成SEO友好的产品标识符
- **热度分数计算**：基于评分、评论数、价格等计算产品热度
- **数据来源标识**：标记数据来源（amazon/tiktok）

### 4. 去重算法
- **URL去重**：基于产品URL去除完全重复的产品
- **名称相似度去重**：使用模糊字符串匹配识别相似产品（85%相似度阈值）
- **智能合并策略**：优先保留数据更完整的产品记录

## 安装和使用

### 基本使用

```python
from data_cleaner import DataCleaner

# 创建数据清洗器实例
cleaner = DataCleaner()

# 单条数据清洗
raw_data = {
    'title': 'Nike T-Shirt - Black <b>Sale!</b>',
    'price': '$29.99',
    'category': 'T-Shirts & Tanks',
    'rating': 4.5,
    'review_count': '1,234 reviews',
    'product_url': 'https://amazon.com/product/123',
    'source': 'amazon',
    'source_id': 'B08N5WRWNW'
}

# 清洗数据
cleaned_data = cleaner.clean_product_data(raw_data)
print(cleaned_data)
```

### 批量处理

```python
# 批量数据清洗
batch_data = [
    {
        'title': 'Classic Cotton T-Shirt',
        'price': '$29.99',
        'category': 'T-Shirt',
        'product_url': 'https://amazon.com/product/1',
        'source': 'amazon',
        'source_id': 'A1'
    },
    {
        'title': '连帽卫衣 - 灰色',
        'price': '89.99',
        'category': '卫衣',
        'product_url': 'https://tiktok.com/product/2',
        'source': 'tiktok',
        'source_id': 'T2'
    }
]

# 批量清洗
result = cleaner.clean_batch(batch_data)

print(f"处理结果:")
print(f"- 原始数据量: {len(batch_data)}")
print(f"- 清洗后数据量: {len(result['products'])}")
print(f"- 有效数据: {len(result['valid_products'])}")
print(f"- 无效数据: {len(result['invalid_products'])}")
print(f"- 去重移除: {result['quality_report']['summary']['duplicates_removed']}")

# 查看质量报告
quality_report = result['quality_report']
print(f"\n质量报告:")
print(f"- 有效率: {quality_report['summary']['valid_rate']}%")
print(f"- 数据质量分数: {quality_report['summary']['data_quality_score']}")
```

### 数据导出

```python
# 导出清洗后的数据
json_output = cleaner.export_cleaned_data(cleaned_data, 'json')
print(json_output)
```

## 输出格式

清洗后的产品数据包含以下字段：

```json
{
  "title": "清洗后的产品标题",
  "price": 29.99,
  "original_price": 39.99,
  "category": "tshirt",
  "rating": 4.5,
  "review_count": 1234,
  "image_url": "https://example.com/image.jpg",
  "product_url": "https://amazon.com/product/123",
  "brand": "品牌名称",
  "description": "产品描述",
  "colors": ["black", "white", "blue"],
  "sizes": ["S", "M", "L", "XL"],
  "source": "amazon",
  "source_id": "B08N5WRWNW",
  "scraped_at": "2025-11-14T17:30:18.123456",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "slug": "product-slug-name",
  "popularity_score": 85.5,
  "data_quality_score": 100,
  "validation_errors": []
}
```

## 数据质量报告

批量处理后会生成详细的质量报告：

```json
{
  "summary": {
    "total_processed": 100,
    "valid_products": 85,
    "invalid_products": 15,
    "duplicates_removed": 5,
    "valid_rate": 85.0,
    "error_rate": 15.0,
    "data_quality_score": 85.0
  },
  "error_analysis": {
    "total_errors": 20,
    "error_types": {
      "缺少必填字段": 10,
      "URL格式无效": 5,
      "价格超出范围": 3,
      "评分超出范围": 2
    },
    "top_errors": ["缺少必填字段", "URL格式无效"]
  },
  "recommendations": [
    "数据质量良好",
    "建议改进去重算法",
    "最常见的错误是: 缺少必填字段，建议重点改进"
  ]
}
```

## 配置选项

可以通过修改Cleaner类的属性来自定义行为：

```python
cleaner = DataCleaner()

# 修改价格验证范围
cleaner.price_range = (0, 5000)  # 0-5000美元

# 修改评分验证范围
cleaner.rating_range = (1, 10)  # 1-10分

# 自定义分类映射
cleaner.category_mapping = {
    'jacket': ['jacket', '外套', '夹克'],
    'pants': ['pants', '裤子', '长裤']
}
```

## 错误处理

数据清洗器会处理各种异常情况：

- **类型错误**：自动转换数据类型，无法转换的设为默认值
- **格式错误**：使用正则表达式提取有效信息
- **范围错误**：超出范围的数据会被修正或标记为错误
- **缺失数据**：为缺失的必填字段添加错误标记

## 性能特点

- **高效批量处理**：支持同时处理大量数据
- **内存优化**：流式处理，避免内存溢出
- **并行友好**：可以轻松集成到多线程/多进程环境中
- **日志记录**：详细的处理日志，便于调试和监控

## 注意事项

1. **数据备份**：处理前请备份原始数据
2. **配置调整**：根据实际需求调整验证规则和映射关系
3. **性能监控**：大批量处理时建议监控内存使用情况
4. **错误分析**：定期查看质量报告，及时调整处理策略

## 示例场景

### 电商数据分析
```python
# 处理多个平台的电商数据
tiktok_data = [...]  # 从TikTok API获取的数据
amazon_data = [...]   # 从Amazon爬取的数据

# 合并并清洗
all_data = tiktok_data + amazon_data
result = cleaner.clean_batch(all_data)

# 获取高质量产品数据
valid_products = result['valid_products']
```

### 数据仓库预处理
```python
# 作为数据仓库ETL流程的一部分
def preprocess_product_data(raw_batch):
    cleaner = DataCleaner()
    result = cleaner.clean_batch(raw_batch)
    
    # 只保留高质量数据写入仓库
    high_quality_products = [
        p for p in result['products'] 
        if p['data_quality_score'] >= 80
    ]
    
    return high_quality_products
```

## 文件结构

```
code/
├── data_cleaner.py        # 主要的数据清洗模块
├── demo_usage.py          # 使用示例和演示
└── README_DATA_CLEANER.md # 数据清洗器说明文档
```

## 许可证

本模块采用 MIT 许可证，可自由使用和修改。