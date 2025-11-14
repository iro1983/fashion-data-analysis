# TikTok & Amazon 时尚数据抓取系统 - 快速开始指南

## 🚀 快速部署

### 第一步：准备环境

```bash
# 1. 克隆项目到本地
git clone <your-repository-url>
cd fashion-scraper

# 2. 进入部署目录
cd deployment

# 3. 复制环境配置
cp .env.example .env

# 4. 编辑环境变量（填入你的API密钥）
vim .env
```

### 第二步：配置必需的服务

#### AWS 配置
```bash
# 安装AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && ./aws/install

# 配置AWS凭证
aws configure
```

#### Vercel 配置
```bash
# 安装Vercel CLI
npm install -g vercel

# 登录Vercel
vercel login
```

### 第三步：执行部署

```bash
# 开发环境部署
./setup.sh dev deploy

# 生产环境部署  
./setup.sh prod deploy
```

## 📁 部署文件清单

```
deployment/
├── 📖 README.md                    # 完整部署指南 (563行)
├── 📖 DEPLOYMENT_SUMMARY.md        # 部署方案总结
├── ⚙️  setup.sh                    # 一键部署脚本
├── 🌐  vercel.json                 # Vercel配置
├── 🌐  vercel-api.js               # API路由
├── 🐳  Dockerfile                  # Docker配置
├── 🐳  docker-compose.yml          # 容器编排
├── 🔧  .env.example                # 环境配置模板
└── 🔄 .github/workflows/
    └── daily-scrape.yml            # 自动化工作流

cloud-function/
├── ☁️  lambda_scraper.py           # AWS Lambda函数
└── ☁️  cloudformation-template.yaml # 云基础设施
```

## 🎯 核心功能

| 功能 | 技术实现 | 部署状态 |
|------|----------|----------|
| 前端可视化 | React + Vercel | ✅ 已配置 |
| 数据抓取 | Python + AWS Lambda | ✅ 已配置 |
| 自动化调度 | GitHub Actions | ✅ 已配置 |
| 数据库 | SQLite/Supabase | ✅ 已配置 |
| 监控告警 | CloudWatch + Slack | ✅ 已配置 |
| 容器化 | Docker + Compose | ✅ 已配置 |

## 💰 成本估算

### 免费使用（月度）
- **Vercel**: 100GB带宽免费
- **GitHub Actions**: 2000分钟/月免费  
- **AWS Lambda**: 100万请求免费
- **总计**: $0/月

### 生产环境（月度）
- **Supabase数据库**: $25/月
- **Vercel Pro**: $20/月
- **AWS服务**: $5-10/月
- **总计**: $50-55/月

## 🔧 常用命令

### 开发环境
```bash
# 本地开发
docker-compose up postgres redis jupyter

# 前端开发
cd fashion-dashboard && npm run dev

# 数据抓取测试
cd code && python main.py --mode test

# 查看日志
docker-compose logs -f scraper
```

### 生产部署
```bash
# 一键部署
./setup.sh prod deploy

# 查看部署状态
vercel ls

# 测试API
curl https://your-api.vercel.app/api/v1/health

# 手动触发抓取
curl -X POST https://your-api.vercel.app/api/v1/trigger \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["amazon", "tiktok"]}'
```

## 📊 监控面板

部署完成后，可访问：

- **前端仪表板**: `https://your-app.vercel.app`
- **API健康检查**: `https://your-api.vercel.app/api/v1/health`
- **Grafana监控**: `http://localhost:3001` (如启用监控)
- **Jupyter Notebook**: `http://localhost:8888` (开发环境)

## 🛠️ 故障排除

### 常见问题

1. **部署失败**
   ```bash
   # 检查环境变量
   cat .env
   
   # 查看详细错误日志
   ./setup.sh dev test
   ```

2. **数据抓取失败**
   ```bash
   # 检查Lambda日志
   aws logs tail /aws/lambda/fashion-scraper-dev --follow
   
   # 手动测试抓取
   python code/main.py --platform amazon --mode test
   ```

3. **前端无法访问**
   ```bash
   # 检查Vercel部署状态
   vercel ls --prod
   
   # 重新部署
   vercel --prod
   ```

### 重置环境
```bash
# 清理开发环境
./setup.sh dev cleanup

# 重新部署
./setup.sh dev deploy
```

## 📞 获取帮助

- **详细文档**: 查看 `deployment/README.md`
- **技术问题**: GitHub Issues
- **紧急支持**: 检查 `deployment/DEPLOYMENT_SUMMARY.md`

---

**🎉 部署完成！开始你的时尚数据分析之旅！**

---
*快速开始指南 v1.0 | 2025-11-14*