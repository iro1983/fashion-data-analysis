# 🚀 GitHub部署指南

> 一步到位，将时尚数据分析系统部署到GitHub并开启自动化

## 📋 部署前准备

### 1. 账户准备
- [ ] GitHub账户 (免费)
- [ ] Git安装
- [ ] 代码编辑器 (VS Code推荐)

### 2. 可选服务账户 (生产环境推荐)
- [ ] [Vercel账户](https://vercel.com) (免费) - 前端部署
- [ ] [Supabase账户](https://supabase.com) (免费) - 云数据库  
- [ ] [TikHub API](https://tikhub.io) - TikTok数据API
- [ ] [Amazon SP-API](https://developer.amazon.com/amazon-sp-api) - Amazon数据API

## 🛠️ 快速部署 (5分钟)

### 步骤1: 运行自动部署脚本

```bash
# 在项目根目录运行
bash setup_github.sh
```

这个脚本会自动：
- ✅ 初始化Git仓库
- ✅ 配置.gitignore
- ✅ 添加所有必要文件
- ✅ 创建初始提交
- ✅ 提供推送指导

### 步骤2: 创建GitHub仓库

1. 访问 [GitHub New Repository](https://github.com/new)
2. 仓库名：`fashion-trend-analyzer`
3. 设为 **Public** 或 **Private**
4. **不勾选** `Add a README file`
5. **不选择** .gitignore 和 license
6. 点击 `Create repository`

### 步骤3: 推送代码

```bash
# 添加远程仓库 (替换为你的实际URL)
git remote add origin https://github.com/你的用户名/fashion-trend-analyzer.git

# 推送代码
git branch -M main
git push -u origin main
```

**🎉 恭喜！您的项目已成功部署到GitHub！**

## ⚙️ 配置环境变量

### GitHub Secrets (推荐用于生产环境)

在GitHub仓库 → `Settings` → `Secrets and variables` → `Actions` 中添加：

#### 必需Secrets：
```
AMAZON_ACCESS_KEY=你的Amazon访问密钥
AMAZON_SECRET_KEY=你的Amazon密钥  
TIKHUB_API_KEY=你的TikHub密钥
SUPABASE_URL=你的Supabase项目URL
SUPABASE_ANON_KEY=你的Supabase匿名密钥
```

#### 可选Secrets：
```
VERCEL_TOKEN=你的Vercel令牌
AWS_ACCESS_KEY_ID=你的AWS密钥ID
AWS_SECRET_ACCESS_KEY=你的AWS密钥
DOCKERHUB_USERNAME=你的Docker用户名
DOCKERHUB_TOKEN=你的Docker令牌
```

### 仓库变量 (用于测试环境)

在相同页面添加变量：
```
ENVIRONMENT=development
DATABASE_PATH=data/fashion_data.db
LOG_LEVEL=INFO
```

## 🔄 自动化功能

### GitHub Actions (自动开启)

推送代码后，GitHub Actions将自动：

1. **🏗️ 持续集成**
   - 代码风格检查 (Black, Flake8, isort)
   - 单元测试和集成测试
   - 数据完整性验证

2. **📊 定时数据抓取**
   - 每天凌晨2点自动抓取
   - 数据清洗和质量检查
   - 生成统计报告

3. **🚀 自动部署**
   - 前端部署到Vercel
   - 后端部署到AWS Lambda  
   - 容器镜像推送到Docker Hub

### 手动触发

在GitHub Actions页面可以手动触发：
- 数据抓取任务
- 完整系统测试
- 部署流程

## 🌐 访问系统

### 1. 本地访问
```bash
# 启动数据抓取
cd code
python main.py scrape --platform amazon --category "T-Shirt"

# 启动可视化界面
cd fashion-dashboard  
python -m http.server 9000

# 访问 http://localhost:9000
```

### 2. 云端访问 (部署后)
- **前端**: https://你的用户名.vercel.app
- **API**: https://你的用户名.supabase.co (配置后)
- **监控**: GitHub仓库的Actions页面

## 📈 监控和维护

### GitHub监控面板
- 仓库首页 → `Insights` → `Traffic`
- Actions → `Deployments` 查看部署状态
- Issues → 查看系统问题

### 自动化报告
每次CI/CD完成后会生成：
- ✅ 测试覆盖率报告
- 📊 数据抓取统计
- 🚀 部署状态报告
- ⚡ 性能基准测试

### 日志查看
```bash
# 查看抓取日志
tail -f code/logs/scraper.log

# 查看部署日志  
github.com/你的用户名/fashion-trend-analyzer/actions

# 查看应用日志
# 访问仪表板 → 设置 → 日志
```

## 🔧 故障排除

### 常见问题

#### 1. CI/CD失败
```
❌ 错误: API密钥未配置
✅ 解决: 在GitHub Secrets中添加必需的API密钥
```

#### 2. 数据抓取失败
```
❌ 错误: 403 Forbidden  
✅ 解决: 检查Amazon SP-API权限或TikHub API限额
```

#### 3. 部署失败
```
❌ 错误: 环境变量未设置
✅ 解决: 在仓库设置中添加所需的环境变量
```

#### 4. 前端无法访问
```
❌ 错误: 404 Not Found
✅ 解决: 检查Vercel部署日志，确认域名配置
```

### 获取帮助

1. **📚 文档中心**
   - 查看 `docs/` 目录中的详细文档
   - 运行 `python code/main.py --help` 查看命令帮助

2. **🐛 问题报告**
   - 在GitHub仓库创建Issue
   - 包含错误信息和日志文件

3. **💬 社区支持**
   - GitHub Discussions
   - 官方文档和FAQ

## 🎯 性能优化

### 免费层优化
- GitHub Actions: 2000分钟/月
- Vercel: 100GB带宽/月  
- Supabase: 500MB数据库/月
- AWS Lambda: 1M请求/月

### 成本控制
```bash
# 监控使用量
python code/main.py usage-stats

# 设置配额提醒
# 在GitHub Actions中添加用量检查
```

## 🔒 安全最佳实践

### API密钥管理
- ✅ 始终使用GitHub Secrets存储
- ✅ 定期轮换API密钥
- ✅ 监控API使用量
- ✅ 启用2FA验证

### 数据合规
- ✅ 遵守GDPR/CCPA规定
- ✅ 尊重robots.txt规则
- ✅ 合理的请求频率
- ✅ 数据加密存储

## 🎉 完成部署！

现在您的时尚数据分析系统已经：
- 🚀 部署到GitHub
- 🤖 自动化CI/CD
- 📊 定时数据抓取
- 🌐 云端可访问
- 📈 性能监控

**开始使用**：
1. 访问您的GitHub仓库
2. 查看Actions页面确认部署状态
3. 运行测试: `python code/main.py scrape --platform amazon`
4. 访问仪表板: http://localhost:9000

**🌟 记得给项目点个Star！**