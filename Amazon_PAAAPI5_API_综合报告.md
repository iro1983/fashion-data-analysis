# Amazon Product Advertising API 5.0 综合分析报告

## 概述

Amazon Product Advertising API 5.0 是一个免费的Web服务，为开发者提供访问Amazon商品数据和电子商务功能的能力。该API设计用于构建电子商务店面或帮助他人构建此类店面的应用程序。

**官方文档地址：** https://webservices.amazon.com/paapi5/documentation/

## 一、API使用限制详解

### 1.1 初始限制（使用前30天）
- **TPS（每秒事务数）**: 1 TPS
- **TPD（每日事务数）**: 8,640 TPD

### 1.2 基于收入的扩展系统
- **TPD扩展**: 每产生$0.05的已发货商品收入，可获得1 TPD
- **TPS扩展**: 每产生$4,320的已发货商品收入，可获得1 TPS（最高10 TPS）
- **收入计算**: 基于前30天期间的收入，自动每日更新

### 1.3 重要概念定义
- **TPS（Transactions Per Second）**: 每秒最大API调用数，每个API调用无论请求多少商品都计为1个事务
- **TPD（Transactions Per Day）**: 每日最大API调用数，即使TPS限制允许，当日额度用完也会限流
- **Primary Account**: 用于创建Associates账户和生成PA API凭据的Amazon用户名/密码
- **Shipped Revenue**: 通过PA API生成链接点击产生的已发货商品总销售额

### 1.4 访问撤销与恢复规则
- **撤销条件**: 连续30天无合格推荐销售额
- **恢复时间**: 推荐销售额发货后2天内恢复访问

### 1.5 错误处理
- 超过使用限制或访问被撤销时返回429 TooManyRequests错误

## 二、API申请条件详解

### 2.1 必要前提条件
- **Amazon Associates账户**: 必须拥有已被审核并最终接受的Amazon Associates账户
- **合格销售额**: 必须是已推荐合格销售额并被接受加入计划的关联者
- **Primary Account Owner**: 只有Amazon Associate账户的主要账户所有者可以注册Product Advertising API

### 2.2 注册流程
1. **Tools → Product Advertising API → Join**
2. 注册后可在"Download credentials"页面获取Access Key和Secret Key
3. 每个账户最多允许两个访问密钥对

### 2.3 账户管理要求
- 必须在所有请求中包含Partner标签
- 确保Associate和API账户使用相同的Amazon账户
- 使用主要账户进行请求
- 建议使用PA API链接而不进行编辑

### 2.4 支持的市场
- 可以在已完全接受Associate状态的Amazon marketplace上宣传产品

## 三、支持的数据字段详解

### 3.1 核心Operations（操作）
Product Advertising API 5.0提供四种主要操作：
- **GetBrowseNodes**: 获取浏览节点信息
- **GetItems**: 获取商品详细信息
- **GetVariations**: 获取商品变体信息
- **SearchItems**: 搜索商品

### 3.2 主要Resources（资源）

#### 3.2.1 ItemInfo（商品信息）
包含11个子资源的综合商品属性集合：

**ByLineInfo（品牌信息）**
- Brand（品牌）
- Contributors（贡献者）
- Manufacturer（制造商）

**Classifications（分类）**
- Binding（装订类型）
- ProductGroup（产品组）

**ContentInfo（内容信息）**
- Edition（版本）
- Languages（语言）
- PagesCount（页数）
- PublicationDate（出版日期）

**ContentRating（内容评级）**
- AudienceRating（受众评级）

**ExternalIds（外部ID）**
- EANs（欧洲商品编号）
- ISBNs（国际标准书号）
- UPCs（通用产品代码）

**Features（特色功能）**
- 产品关键功能数组

**ManufactureInfo（制造信息）**
- ItemPartNumber（零件号）
- Model（型号）
- Warranty（保修）

**ProductInfo（产品信息）**
- Color（颜色）
- IsAdultProduct（成人产品标识）
- ItemDimensions（商品尺寸）
- ReleaseDate（发布日期）
- Size（尺寸）
- UnitCount（单位数量）

**TechnicalInfo（技术信息）**
- Formats（格式）
- EnergyEfficiencyClass（能效等级）

**Title（标题）**
- 产品标题

**TradeInInfo（以旧换新信息）**
- IsEligibleForTradeIn（以旧换新资格）
- Price（价格）

#### 3.2.2 Images（图像资源）
提供三种尺寸的商品图像：
- **Primary（主要图像）**: 搜索结果和详情页显示的主要商品图像
- **Variants（变体图像）**: 所有其他图像

**图像尺寸选项**：
- **Small**: 75像素（_SL75_）
- **Medium**: 160像素（_SL160_）
- **Large**: 500像素（_SL500_）

每个图像尺寸包含：
- URL（图像URL）
- Height（高度）
- Width（宽度）

#### 3.2.3 OffersV2（优惠信息，推荐版本）
提供全面的价格和优惠信息：

**价格字段**：
- Money（金额）
- PricePerUnit（单位价格）
- SavingBasis（节省基准）
- Savings（节省金额）

**可用性信息**：
- IN_STOCK（现货）
- OUT_OF_STOCK（缺货）
- PREORDER（预售）
- 多种状态类型

**条件详情**：
- New（新品）
- Used（二手）
- Refurbished（翻新）
- 子条件和备注

**优惠信息**：
- Lightning Deal（闪电优惠）
- Subscribe & Save（订阅省钱）
- 访问类型、徽章、早期访问时长和时间安排

**商家信息**：
- Merchant ID（商家ID）
- Merchant Name（商家名称）

**其他功能**：
- 忠诚度积分支持（日本市场）
- Buy Box Winner状态
- MAP政策违规指标

#### 3.2.4 其他重要Resources
- **BrowseNodeInfo**: 商品关联的浏览节点信息
- **BrowseNodes**: GetBrowseNodes请求的浏览节点信息
- **ParentASIN**: 商品的父级ASIN
- **SearchRefinements**: 搜索请求的动态搜索优化

### 3.3 地域支持
支持20多个国家和地区，包括：
- 美国、英国、德国、法国、日本、加拿大、澳大利亚等主要市场

### 3.4 特殊功能支持
- **外部标识符搜索**: 支持UPC/EAN/ISBN搜索
- **本地化产品详情**: 多语言和多地域支持
- **Prime资格产品**: Prime产品筛选
- **Prime独家优惠定价**: 特殊定价信息
- **变体处理**: 商品变体和父级关系
- **动态搜索优化**: 智能搜索建议

## 四、技术要求和最佳实践

### 4.1 必备知识
- **JSON格式**: 熟悉JSON数据结构
- **HTTP方法**: 特别是POST方法
- **Web服务**: 理解Web服务概念

### 4.2 最佳编程实践
- 使用PA API链接时不进行修改
- 确保Associate和API账户使用相同的Amazon账户
- 在所有请求中包含Partner标签
- 使用主要账户进行API请求

### 4.3 错误处理和监控
- 监控API使用情况，避免超过限制
- 使用Associates Central的Link Type Performance报告跟踪销售归因
- 妥善处理429 TooManyRequests错误

## 五、支持联系

**联系渠道**: Amazon Associates Customer Service
**申请流程**: Help → Contact Us → Product Advertising API → Comments → Send E-mail
**账户接受审核时间**: 3-4天

## 总结

Amazon Product Advertising API 5.0提供了丰富的商品数据访问能力，支持详细的商品信息、图像、价格和优惠数据。API采用基于收入的扩展模式，鼓励开发者通过实际的销售业绩来提升API使用额度。通过合理的申请流程和技术要求，确保了API服务的质量和可靠性。

---
*报告生成时间: 2025-11-14 17:15:49*
*数据来源: Amazon Product Advertising API 5.0官方文档*