# TikTok & Amazon 时尚数据抓取系统 - 云部署指南

## 📋 目录

1. [系统概述](#系统概述)
2. [技术架构](#技术架构)
3. [部署准备](#部署准备)
4. [快速部署](#快速部署)
5. [详细配置](#详细配置)
6. [监控和维护](#监控和维护)
7. [故障排除](#故障排除)
8. [成本估算](#成本估算)

## 🎯 系统概述

本系统是一个自动化的时尚数据抓取和分析平台，支持：

- **数据抓取**: 自动抓取 TikTok 和 Amazon 的时尚商品数据
- **数据处理**: 数据清洗、去重、质量验证
- **可视化分析**: React 仪表板展示数据趋势和分析结果
- **自动化调度**: 定时任务、错误监控、告警通知

### 核心功能

- ✅ 每日自动数据抓取
- ✅ 实时数据可视化
- ✅ 错误监控和告警
- ✅ 云端数据存储
- ✅ 自动扩缩容
- ✅ 多环境支持

## 🏗️ 技术架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用       │    │   数据抓取服务   │    │   数据存储      │
│                 │    │                 │    │                 │
│ Vercel (React)  │────│ AWS Lambda      │────│ SQLite/Supabase │
│ 仪表板 + 图表    │    │ Python 脚本     │    │ 历史数据存储    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   监控告警      │
                    │                 │
                    │ CloudWatch      │
                    │ Slack/Email     │
                    └─────────────────┘
```

### 组件说明

#### 前端层 (Vercel)
- **技术栈**: React + TypeScript + Vite + Tailwind CSS
- **功能**: 数据可视化、交互式仪表板、响应式设计
- **部署**: Vercel 自动部署，CDN 加速
- **域名**: 支持自定义域名

#### 数据抓取层 (AWS Lambda)
- **技术栈**: Python 3.9 + Boto3 + Requests
- **触发方式**: CloudWatch Events 定时触发
- **并发控制**: 预留并发限制
- **错误处理**: 自动重试、死信队列

#### 数据存储层
- **生产环境**: Supabase (PostgreSQL)
- **开发环境**: SQLite
- **文件存储**: AWS S3
- **备份策略**: 自动备份、生命周期管理

#### 监控层
- **日志**: CloudWatch Logs
- **指标**: CloudWatch Metrics
- **告警**: SNS + Slack/Email
- **可视化**: CloudWatch Dashboard

## 🛠️ 部署准备

### 必需账号和服务

1. **AWS 账号**
   - IAM 用户权限
   - Lambda 执行权限
   - S3 访问权限
   - CloudWatch 权限

2. **Vercel 账号**
   - 项目创建权限
   - 域名配置权限

3. **GitHub 账号**
   - 仓库管理权限
   - Actions 配置权限

4. **第三方API账号**
   - TikTok API 访问权限
   - Amazon Product Advertising API
   - Slack/Email 通知服务

### 环境变量配置

创建以下环境文件：

#### `.env.dev` (开发环境)
```bash
# AWS 配置
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=ap-southeast-1

# Vercel 配置
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_vercel_org_id
VERCEL_PROJECT_ID=your_vercel_project_id

# TikTok API
TIKTOK_USERNAME=your_tiktok_username
TIKTOK_PASSWORD=your_tiktok_password

# Amazon API
AMAZON_ACCESS_KEY=your_amazon_access_key
AMAZON_SECRET_KEY=your_amazon_secret_key
AMAZON_ASSOCIATE_TAG=your_associate_tag

# 通知配置
SLACK_WEBHOOK=your_slack_webhook_url
NOTIFICATION_EMAIL=your_email@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password

# 数据库
DATABASE_URL=sqlite:///data/dev.db

# 前端配置
API_BASE_URL=https://api.example.com
```

#### `.env.prod` (生产环境)
```bash
# 使用相同变量，但值指向生产环境
# 将数据库URL改为Supabase:
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# API URL改为生产域名:
API_BASE_URL=https://your-api-domain.com
```

### AWS IAM 策略

创建以下IAM策略：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:DeleteFunction",
        "lambda:GetFunction",
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:*:*:function:fashion-scraper-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::*-fashion-data",
        "arn:aws:s3:::*-fashion-data/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricAlarm",
        "cloudwatch:DeleteAlarms",
        "cloudwatch:DescribeAlarms"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish",
        "sns:CreateTopic",
        "sns:Subscribe"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## 🚀 快速部署

### 1. 克隆项目并配置

```bash
# 克隆项目
git clone https://github.com/your-username/fashion-scraper.git
cd fashion-scraper

# 配置环境变量
cp .env.dev .env
# 编辑 .env 文件，填入你的配置
```

### 2. 自动化部署

```bash
# 进入部署目录
cd deployment

# 授予脚本执行权限
chmod +x setup.sh

# 部署到开发环境
./setup.sh dev deploy

# 部署到生产环境
./setup.sh prod deploy
```

### 3. 验证部署

部署完成后，访问以下地址验证：

- **前端仪表板**: https://your-app.vercel.app
- **API 端点**: https://your-api-gateway-url/prod/scrape
- **监控面板**: AWS CloudWatch

## ⚙️ 详细配置

### GitHub Actions 配置

1. **设置 Secrets**
   - 进入 GitHub 仓库 Settings > Secrets and variables > Actions
   - 添加以下 secrets:

   ```
   TIKTOK_USERNAME
   TIKTOK_PASSWORD
   AMAZON_ACCESS_KEY
   AMAZON_SECRET_KEY
   AMAZON_ASSOCIATE_TAG
   DATABASE_URL
   VERCEL_TOKEN
   VERCEL_ORG_ID
   VERCEL_PROJECT_ID
   SLACK_WEBHOOK
   NOTIFICATION_EMAIL
   AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY
   S3_BUCKET
   ```

2. **配置分支保护**
   - 设置 main 分支需要 PR 审核
   - 启用状态检查

### Vercel 配置

1. **创建项目**
   - 登录 Vercel Dashboard
   - 点击 "New Project"
   - 选择 GitHub 仓库

2. **环境变量配置**
   - 在项目设置中添加环境变量
   - 确保 `.env` 文件中的变量都已配置

3. **域名配置**
   - 可选：配置自定义域名
   - DNS 记录指向 Vercel

### AWS Lambda 配置

1. **部署函数**
   ```bash
   cd deployment/cloud-function
   
   # 创建部署包
   zip -r function.zip lambda_scraper.py requirements.txt
   
   # 创建函数
   aws lambda create-function \
     --function-name fashion-scraper-dev \
     --runtime python3.9 \
     --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
     --handler lambda_scraper.lambda_handler \
     --zip-file fileb://function.zip \
     --environment Variables="{ENVIRONMENT=dev}"
   ```

2. **设置触发器**
   - 创建 CloudWatch Events 规则
   - 配置定时表达式: `cron(0 2 * * ? *)`

### 数据库配置

#### Supabase 配置

1. **创建项目**
   - 登录 Supabase Dashboard
   - 创建新项目

2. **创建数据表**
   ```sql
   -- 商品表
   CREATE TABLE products (
     id SERIAL PRIMARY KEY,
     platform VARCHAR(20) NOT NULL,
     product_id VARCHAR(100) NOT NULL,
     title TEXT,
     price DECIMAL(10,2),
     currency VARCHAR(3) DEFAULT 'USD',
     category VARCHAR(100),
     image_url TEXT,
     product_url TEXT,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     UNIQUE(platform, product_id)
   );

   -- 抓取日志表
   CREATE TABLE scraping_logs (
     id SERIAL PRIMARY KEY,
     platform VARCHAR(20) NOT NULL,
     status VARCHAR(20) NOT NULL,
     start_time TIMESTAMP NOT NULL,
     end_time TIMESTAMP,
     records_count INTEGER DEFAULT 0,
     error_message TEXT,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- 创建索引
   CREATE INDEX idx_products_platform ON products(platform);
   CREATE INDEX idx_products_category ON products(category);
   CREATE INDEX idx_scraping_logs_start_time ON scraping_logs(start_time);
   ```

#### SQLite 配置（开发环境）

```bash
# 创建数据库目录
mkdir -p data

# 数据库文件会自动创建
# 文件位置: data/scraping.db
```

## 📊 监控和维护

### CloudWatch 监控

1. **Lambda 函数监控**
   - 调用次数
   - 错误率
   - 执行时间
   - 内存使用

2. **自定义指标**
   - 数据抓取成功率
   - 新增商品数量
   - API 调用延迟

### 告警配置

1. **错误告警**
   ```bash
   aws cloudwatch put-metric-alarm \
     --alarm-name "fashion-scraper-errors" \
     --alarm-description "抓取函数错误率过高" \
     --metric-name Errors \
     --namespace AWS/Lambda \
     --statistic Sum \
     --period 300 \
     --threshold 1 \
     --comparison-operator GreaterThanThreshold \
     --evaluation-periods 1 \
     --alarm-actions arn:aws:sns:region:account:notification-topic
   ```

2. **性能告警**
   - 执行时间超过 5 分钟
   - 内存使用超过 80%
   - 错误率超过 10%

### 日志管理

1. **Lambda 日志**
   - 自动保存到 CloudWatch Logs
   - 保留期: 14 天
   - 搜索和过滤

2. **访问日志**
   - Vercel 访问日志
   - API Gateway 日志

### 备份策略

1. **数据库备份**
   - 每日自动备份到 S3
   - 保留期: 30 天
   - 跨区域复制

2. **代码备份**
   - Git 仓库自动备份
   - 标签版本管理

## 🔧 故障排除

### 常见问题

1. **数据抓取失败**
   ```
   症状: Lambda 函数执行失败
   检查项:
   - API 凭据是否有效
   - 网络连接是否正常
   - 限流限制是否触发
   ```

2. **前端部署失败**
   ```
   症状: Vercel 部署失败
   检查项:
   - build 脚本是否正确
   - 环境变量是否配置
   - 依赖包是否冲突
   ```

3. **数据库连接失败**
   ```
   症状: 无法连接数据库
   检查项:
   - 连接字符串是否正确
   - 网络安全组配置
   - 认证凭据是否有效
   ```

### 调试工具

1. **本地测试**
   ```bash
   # 测试数据抓取
   cd code
   python main.py --platform amazon --mode test
   
   # 测试前端构建
   cd fashion-dashboard
   npm run build
   
   # 测试Lambda函数
   cd deployment/cloud-function
   python lambda_scraper.py
   ```

2. **日志查看**
   ```bash
   # 查看Lambda日志
   aws logs tail /aws/lambda/fashion-scraper-dev --follow
   
   # 查看GitHub Actions日志
   # 访问: https://github.com/your-repo/actions
   ```

### 重置和恢复

1. **重置环境**
   ```bash
   # 清理开发环境
   ./setup.sh dev cleanup
   
   # 重新部署
   ./setup.sh dev deploy
   ```

2. **数据恢复**
   ```bash
   # 从S3恢复数据库
   aws s3 cp s3://backup-bucket/database-backup.db ./data/scraping.db
   ```

## 💰 成本估算

### 免费额度

1. **AWS**
   - Lambda: 1,000,000 请求/月免费
   - CloudWatch: 5GB 日志/月免费
   - S3: 5GB 存储/月免费

2. **Vercel**
   - 100GB 带宽/月免费
   - 个人项目免费

3. **GitHub Actions**
   - 2,000 分钟/月免费
   - 公共仓库免费

### 预估成本（生产环境）

| 服务 | 配置 | 月成本 (USD) |
|------|------|-------------|
| AWS Lambda | 512MB, 300s | $2-5 |
| AWS S3 | 50GB + 传输 | $1-2 |
| CloudWatch Logs | 10GB | $0.3 |
| Vercel Pro | 团队协作 | $20 |
| Supabase | 数据库 + 存储 | $25 |
| **总计** | | **$48-52** |

### 成本优化

1. **Lambda 优化**
   - 设置适当的内存分配
   - 使用预留并发
   - 优化代码减少执行时间

2. **存储优化**
   - 设置 S3 生命周期规则
   - 压缩日志文件
   - 定期清理过期数据

3. **监控成本**
   - 设置 CloudWatch 告警
   - 监控Lambda执行时间
   - 优化日志保留期

## 📞 支持和联系

- **项目文档**: `/docs`
- **问题反馈**: GitHub Issues
- **邮件支持**: support@example.com
- **紧急联系**: emergency@example.com

---

**部署指南版本**: v1.0  
**最后更新**: 2025-11-14  
**维护团队**: Claude AI Assistant