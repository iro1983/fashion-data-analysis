# 📚 时尚数据分析系统 - 完整分步教学

> 从零开始，手把手教您部署和使用时尚数据分析系统

## 🎯 教学目标

学完本教程后，您将能够：
1. ✅ 成功创建GitHub仓库
2. ✅ 部署完整的时尚数据分析系统
3. ✅ 配置API密钥获取真实数据
4. ✅ 启动和使用可视化仪表板
5. ✅ 理解系统各项功能

---

## 📋 准备工作清单

### 前置要求检查
在开始前，请确认您已完成：

- [ ] **GitHub账户注册** ([github.com](https://github.com) - 免费)
- [ ] **Git工具安装** ([git-scm.com](https://git-scm.com))
- [ ] **Python 3.8+** ([python.org](https://python.org))
- [ ] **网络连接** (下载依赖和API访问)

### 辅助工具 (可选但推荐)
- [ ] **VS Code** (代码编辑器)
- [ ] **Chrome/Edge浏览器** (测试仪表板)
- [ ] **记事本或文本编辑器** (编辑配置文件)

---

## 🏗️ 第一部分：GitHub仓库创建 (15分钟)

### 步骤 1：创建GitHub账户 (如没有)

1. **打开浏览器，访问 GitHub**
   ```
   📍 在地址栏输入: https://github.com
   ```

2. **点击 "Sign up" 注册**
   ```
   🖱️ 点击页面右上角的绿色 "Sign up" 按钮
   ```

3. **填写注册信息**
   ```
   📝 用户名: 选择一个唯一的中文名或英文名
   📧 邮箱: 使用您常用的邮箱地址
   🔒 密码: 设置强密码 (8位以上，包含字母数字)
   ```

4. **验证邮箱**
   ```
   📧 打开您的邮箱，找到GitHub发送的验证邮件
   📧 点击邮件中的 "Verify email address" 链接
   ```

5. **完成账户设置**
   ```
   ✅ 选择您的计划 (个人用户选择 "Free")
   ✅ 选择是否完成详细资料 (可选跳过)
   ```

### 步骤 2：创建GitHub仓库

1. **登录GitHub并进入创建页面**
   ```
   🌐 访问: https://github.com/new
   或者在GitHub首页点击右上角的 "+" → "New repository"
   ```

2. **填写仓库信息**
   ```
   📦 Repository name: fashion-trend-analyzer
   
   📝 Description (可选): 
   时尚数据抓取与可视化分析系统 - 自动化获取TikTok和Amazon服装趋势数据
   
   🔒 Visibility: 
   选择 "Public" (公开仓库，所有人可见)
   或者选择 "Private" (私有仓库，只有您可见)
   
   ❌ 重要提示：
   - 不要勾选 "Add a README file"
   - 不要选择 .gitignore template
   - 不要选择 license
   ```

3. **创建仓库**
   ```
   🖱️ 点击页面底部的绿色 "Create repository" 按钮
   ```

4. **获取仓库URL**
   ```
   创建成功后，页面会显示您的仓库URL，类似：
   https://github.com/您的用户名/fashion-trend-analyzer
   
   请记住这个URL，下一步会用到！
   ```

---

## 💻 第二部分：代码部署 (20分钟)

### 步骤 3：准备本地项目

1. **打开命令行/终端**

   **Windows用户：**
   ```
   按 Win + R 键，输入 cmd 或 powershell，按回车
   ```

   **Mac用户：**
   ```
   按 Cmd + 空格键，输入 "terminal"，按回车
   ```

2. **检查Git是否已安装**
   ```bash
   git --version
   ```
   
   **如果显示版本号 (如 git version 2.30.0)** ✅ 继续下一步
   
   **如果显示 "command not found" 或类似错误：**
   ```
   Windows: 访问 https://git-scm.com/download/win 下载安装
   Mac: 运行 brew install git 或访问 https://git-scm.com/download/mac
   Linux: 运行 sudo apt install git
   ```

3. **检查Python是否已安装**
   ```bash
   python --version
   或
   python3 --version
   ```
   
   **如果显示版本号 (如 Python 3.9.0)** ✅ 继续下一步
   
   **如果版本低于3.8，请升级Python到3.8+**

4. **创建项目目录**
   ```bash
   # 创建项目文件夹
   mkdir fashion-trend-analyzer
   cd fashion-trend-analyzer
   ```

### 步骤 4：下载项目文件

现在您需要将项目文件下载到本地。有两种方法：

#### 方法 A：直接复制文件 (推荐)
如果您已经有权访问项目文件：

1. **复制所有项目文件到您的 `fashion-trend-analyzer` 目录**
   ```
   将之前准备的所有文件复制到项目目录中，包括：
   - README.md
   - .env.example
   - code/ 文件夹
   - fashion-dashboard/ 文件夹
   - deployment/ 文件夹
   - tests/ 文件夹
   - docs/ 文件夹
   - .github/ 文件夹
   - Dockerfile
   - docker-compose.yml
   - LICENSE
   ```

2. **确认文件结构**
   ```bash
   # 检查目录结构
   ls -la
   ```
   
   应该看到类似这样的输出：
   ```
   total 20
   drwxr-xr-x  4 user group  4096 Nov 14 20:00 .
   drwxr-xr-x  3 user group  4096 Nov 14 20:00 ..
   -rw-r--r-- 1 user group 1.2K Nov 14 20:00 README.md
   drwxr-xr-x  1.4K Nov 14 20:00 code/
   drwxr-xr-x  4.5K Nov 14 20:00 fashion-dashboard/
   ...
   ```

#### 方法 B：从空仓库开始 (手动创建)
如果您是从空的GitHub仓库开始：

1. **初始化Git仓库**
   ```bash
   git init
   ```

2. **创建基础文件结构**
   ```bash
   mkdir -p code fashion-dashboard deployment tests docs .github/workflows
   mkdir -p config data logs
   ```

3. **复制提供的项目文件到对应目录**

### 步骤 5：配置Git仓库

1. **设置Git用户信息**
   ```bash
   git config --global user.email "your-email@example.com"
   git config --global user.name "Your Name"
   ```

2. **添加所有文件到Git**
   ```bash
   git add .
   ```

3. **创建初始提交**
   ```bash
   git commit -m "🎉 初始提交: 时尚数据抓取与可视化分析系统"
   ```

4. **连接GitHub仓库**
   ```bash
   # 替换为您实际的GitHub仓库URL
   git remote add origin https://github.com/您的用户名/fashion-trend-analyzer.git
   ```

5. **推送代码到GitHub**
   ```bash
   git branch -M main
   git push -u origin main
   ```

6. **验证上传**
   ```
   刷新您的GitHub仓库页面，应该能看到所有文件已上传
   ```

---

## 🔧 第三部分：配置和测试 (25分钟)

### 步骤 6：安装Python依赖

1. **进入代码目录**
   ```bash
   cd code
   ```

2. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

   **如果遇到权限错误，尝试：**
   ```bash
   pip install --user -r requirements.txt
   ```

   **如果速度太慢，可以使用国内镜像：**
   ```bash
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
   ```

3. **验证安装**
   ```bash
   python main.py --help
   ```

   **应该显示类似：**
   ```
   usage: main.py [-h] {scrape,stats,export,clean,serve} ...
   
   positional arguments:
     {scrape,stats,export,clean,serve}
       scrape               抓取数据
       stats                查看统计信息
       export               导出数据
       clean                清理数据
       serve                启动Web服务
   ```

### 步骤 7：配置环境变量

1. **复制环境配置模板**
   ```bash
   cd ..
   cp .env.example .env
   ```

2. **编辑配置文件**
   ```bash
   # Windows用户
   notepad .env
   
   # Mac/Linux用户
   nano .env
   # 或
   vim .env
   ```

3. **填入配置信息 (暂时使用测试配置)**
   ```
   # 暂时使用测试值，稍后会替换为真实API密钥
   TIKHUB_API_KEY=test_key
   AMAZON_ACCESS_KEY=test_key
   AMAZON_SECRET_KEY=test_key
   DATABASE_PATH=data/fashion_data.db
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

4. **保存文件**
   ```
   Windows: Ctrl + S 保存后关闭记事本
   Mac/Linux: 按 Esc，然后输入 :wq 再按回车
   ```

### 步骤 8：初始化数据库

1. **进入代码目录**
   ```bash
   cd code
   ```

2. **创建数据目录**
   ```bash
   mkdir -p ../data
   ```

3. **初始化数据库**
   ```bash
   python -c "
   from database import Database
   db = Database()
   db.create_tables()
   print('✅ 数据库初始化完成')
   "
   ```

4. **验证数据库文件**
   ```bash
   ls -la ../data/
   ```
   
   **应该看到：** `fashion_data.db` 文件

### 步骤 9：测试数据抓取功能

1. **测试Amazon数据抓取**
   ```bash
   python main.py scrape --platform amazon --category "T-Shirt" --limit 5
   ```
   
   **预期输出：**
   ```
   🛒 开始抓取 Amazon T-Shirt 数据...
   🔍 搜索关键词: T-Shirt
   📊 找到 5 个产品
   ✅ 数据抓取完成
   ```

2. **查看抓取统计**
   ```bash
   python main.py stats
   ```
   
   **预期输出：**
   ```
   📊 数据统计报告
   ================
   📦 总产品数: 5
   🛒 Amazon产品: 5
   📱 TikTok产品: 0
   ✅ 数据库连接正常
   ```

3. **如果遇到错误**
   ```
   常见错误及解决方案：
   ❌ "module not found": 运行 pip install -r requirements.txt
   ❌ "permission denied": 使用 python3 main.py 命令
   ❌ "database error": 检查 data/ 目录是否存在
   ```

---

## 🌐 第四部分：启动可视化界面 (10分钟)

### 步骤 10：启动Web仪表板

1. **进入仪表板目录**
   ```bash
   cd ../fashion-dashboard
   ```

2. **启动本地Web服务器**
   ```bash
   python -m http.server 9000
   ```
   
   **预期输出：**
   ```
   Serving HTTP on 0.0.0.0 port 9000 (http://0.0.0.0:9000/) ...
   ```

3. **打开浏览器测试**
   ```
   🌐 在浏览器中访问: http://localhost:9000
   ```

4. **验证仪表板功能**
   ```
   ✅ 应该看到：
   - 顶部导航栏 (仪表板、产品、价格分析、平台比较、排行榜)
   - 左侧统计卡片 (总产品数、平台分布等)
   - 主要内容区域 (图表和数据展示)
   ```

### 步骤 11：测试交互功能

1. **产品过滤**
   ```
   🖱️ 在产品页面点击不同筛选条件
   ✅ 页面数据应该相应更新
   ```

2. **图表交互**
   ```
   🖱️ 点击图表中的不同数据点
   ✅ 应该显示产品详细信息
   ```

3. **搜索功能**
   ```
   🔍 在搜索框中输入 "Nike"
   ✅ 应该过滤出相关产品
   ```

---

## 🔑 第五部分：配置真实API (20分钟)

### 步骤 12：获取TikTok数据API

1. **访问TikHub API**
   ```
   🌐 浏览器访问: https://tikhub.io
   ```

2. **注册账户**
   ```
   📧 点击 "Sign Up" 注册
   📝 填写信息：邮箱、密码、姓名等
   ✅ 完成邮箱验证
   ```

3. **获取API密钥**
   ```
   🗝️ 登录后进入 Dashboard
   🗝️ 找到 "API Keys" 或 "API Access"
   🗝️ 点击 "Create New API Key"
   🗝️ 复制生成的 API Key
   ```

4. **更新配置文件**
   ```bash
   # 编辑 .env 文件
   nano .env
   ```
   
   **将测试密钥替换为真实密钥：**
   ```
   TIKHUB_API_KEY=您的真实TikHub API密钥
   ```

### 步骤 13：获取Amazon SP-API

1. **访问Amazon SP-API**
   ```
   🌐 浏览器访问: https://developer.amazon.com/amazon-sp-api
   ```

2. **创建开发者账户**
   ```
   📧 使用您的Amazon卖家账户登录
   ✅ 完成开发者注册流程
   ```

3. **创建应用程序**
   ```
   🏗️ 在 Developer Console 中创建新应用
   📋 填写应用信息：
   - 名称: Fashion Trend Analyzer
   - 描述: 时尚趋势数据分析
   - 分类: 数据分析工具
   ```

4. **获取API凭证**
   ```
   🗝️ 在应用详情页面找到：
   - Access Key ID
   - Secret Access Key
   - Marketplace ID (通常是 ATVPDKIKX0DER)
   ```

5. **更新配置文件**
   ```bash
   nano .env
   ```
   
   **添加Amazon配置：**
   ```
   AMAZON_ACCESS_KEY=您的Amazon Access Key
   AMAZON_SECRET_KEY=您的Amazon Secret Key
   AMAZON_REGION=us-east-1
   AMAZON_MARKETPLACE_ID=ATVPDKIKX0DER
   ```

### 步骤 14：测试真实数据

1. **重新启动数据抓取**
   ```bash
   cd code
   python main.py scrape --platform amazon --category "T-Shirt"
   ```

2. **验证数据质量**
   ```bash
   python main.py stats
   ```
   
   **应该看到更真实的Amazon产品数据**

3. **检查TikTok数据**
   ```bash
   python main.py scrape --platform tiktok --category "Printed"
   ```

---

## 🚀 第六部分：自动化和云端部署 (30分钟)

### 步骤 15：配置GitHub Secrets

1. **进入GitHub仓库设置**
   ```
   🌐 在您的GitHub仓库页面点击 "Settings"
   ```

2. **找到Secrets配置**
   ```
   📋 左侧菜单中找到 "Secrets and variables"
   📋 点击 "Actions"
   ```

3. **添加API密钥Secrets**
   ```
   🔒 点击 "New repository secret"
   
   添加以下密钥：
   
   1. 名称: TIKHUB_API_KEY
      值: 您的TikHub API密钥
   
   2. 名称: AMAZON_ACCESS_KEY  
      值: 您的Amazon Access Key
   
   3. 名称: AMAZON_SECRET_KEY
      值: 您的Amazon Secret Key
   
   4. 名称: SUPABASE_URL (可选)
      值: 您的Supabase项目URL
   
   5. 名称: SUPABASE_ANON_KEY (可选)
      值: 您的Supabase匿名密钥
   ```

4. **保存配置**
   ```
   💾 点击 "Add secret" 保存每个密钥
   ```

### 步骤 16：测试GitHub Actions

1. **查看Actions页面**
   ```
   🌐 在GitHub仓库页面点击 "Actions" 标签
   ```

2. **查看工作流状态**
   ```
   ✅ 首次推送后应该自动运行 CI/CD 流程
   📊 可以看到 Workflow runs 列表
   ```

3. **手动触发工作流**
   ```
   🖱️ 点击 "Run workflow" 按钮
   📋 选择分支: main
   🖱️ 点击 "Run workflow"
   ```

4. **监控执行进度**
   ```
   📈 点击正在运行的工作流
   🔍 查看每个步骤的执行状态
   ✅ 应该看到：Lint and Test → Setup Database → Scrape Data 等
   ```

### 步骤 17：部署到Vercel (前端)

1. **注册Vercel账户**
   ```
   🌐 访问 https://vercel.com
   📧 使用GitHub账户登录 (推荐)
   ```

2. **连接GitHub仓库**
   ```
   🔗 点击 "New Project"
   📋 选择 "Import Git Repository"
   ✅ 找到并选择您的 fashion-trend-analyzer 仓库
   ```

3. **配置部署设置**
   ```
   ⚙️ Framework Preset: Other
   📂 Root Directory: fashion-dashboard
   🌐 Build Command: (留空)
   📦 Output Directory: (留空)
   ```

4. **部署**
   ```
   🚀 点击 "Deploy" 按钮
   ⏳ 等待部署完成 (通常2-5分钟)
   🌐 获取您的网站URL: https://your-app.vercel.app
   ```

### 步骤 18：配置定时任务

1. **验证GitHub Actions定时任务**
   ```
   📅 默认配置：每天凌晨2点 (UTC时间) 自动运行
   📊 在Actions页面查看 "Scheduled" 触发的工作流
   ```

2. **手动测试定时任务**
   ```
   🖱️ 进入Actions页面
   📅 点击左侧 "Scheduled workflow"
   🖱️ 选择 "Run workflow"
   ```

---

## 📊 第七部分：系统使用指南 (15分钟)

### 步骤 19：日常使用操作

1. **每日数据更新**
   ```bash
   # 手动更新数据
   cd code
   python main.py scrape --all
   
   # 查看更新统计
   python main.py stats
   ```

2. **查看仪表板**
   ```
   🌐 本地访问: http://localhost:9000
   🌐 云端访问: https://您的vercel域名.vercel.app
   ```

3. **数据分析功能**
   ```
   📊 仪表板页面：查看整体趋势和统计
   🛍️ 产品页面：浏览和筛选具体产品
   💰 价格分析：查看价格趋势和历史数据
   📈 平台比较：对比Amazon vs TikTok数据
   🏆 排行榜：查看销量、评分、价格排名
   ```

4. **数据导出**
   ```bash
   # 导出为JSON格式
   python main.py export --format json --output data/products.json
   
   # 导出为CSV格式
   python main.py export --format csv --output data/products.csv
   ```

### 步骤 20：系统维护

1. **查看系统日志**
   ```bash
   # 查看抓取日志
   tail -f code/logs/scraper.log
   
   # 查看错误日志
   tail -f code/logs/error.log
   ```

2. **数据备份**
   ```bash
   # 备份数据库
   python main.py backup
   
   # 恢复数据库
   python main.py restore --file backup_20231114.db
   ```

3. **性能监控**
   ```bash
   # 查看系统性能
   python main.py performance
   
   # 数据库清理
   python main.py clean --remove-old
   ```

---

## 🔧 第八部分：故障排除指南 (10分钟)

### 常见问题及解决方案

#### 问题1：API密钥配置错误
```
❌ 症状：抓取数据返回空结果或错误
✅ 解决方案：
1. 检查 .env 文件中的密钥是否正确
2. 确认API密钥是否已激活
3. 验证API使用量是否超限
```

#### 问题2：数据库连接失败
```
❌ 症状：程序启动时报数据库错误
✅ 解决方案：
1. 检查 data/ 目录是否存在
2. 确认 SQLite 文件权限
3. 运行数据库初始化命令
```

#### 问题3：Web仪表板无法访问
```
❌ 症状：访问 localhost:9000 显示错误
✅ 解决方案：
1. 确认端口9000未被占用
2. 检查防火墙设置
3. 重启Web服务器
```

#### 问题4：GitHub Actions失败
```
❌ 症状：Actions页面显示红色失败状态
✅ 解决方案：
1. 查看详细错误日志
2. 检查GitHub Secrets配置
3. 验证API密钥权限
```

---

## ✅ 完成检查清单

使用系统前，请确认：

- [ ] GitHub仓库创建成功
- [ ] 代码成功推送到GitHub
- [ ] Python依赖安装完成
- [ ] 数据库初始化成功
- [ ] 环境变量配置正确
- [ ] 测试数据抓取功能正常
- [ ] Web仪表板可以访问
- [ ] TikTok API密钥配置
- [ ] Amazon SP-API配置
- [ ] GitHub Secrets配置完成
- [ ] Vercel部署成功
- [ ] 定时任务正常运行

---

## 🎉 恭喜！

如果您完成了以上所有步骤，现在您拥有：

✅ **完整的时尚数据分析系统**
- 自动化数据抓取 (TikTok + Amazon)
- 智能数据清洗和分析
- 实时可视化仪表板
- 云端部署和定时任务

✅ **持续学习的能力**
- 理解系统架构和运行机制
- 掌握故障排除方法
- 具备扩展功能的基础

### 🔮 下一步学习建议

1. **数据分析深入**：学习如何使用数据进行商业洞察
2. **系统扩展**：添加更多数据源或功能
3. **性能优化**：提升抓取速度和数据准确性
4. **商业应用**：将数据用于实际的商业决策

### 📞 获取帮助

如果在使用过程中遇到任何问题：

1. **📚 查看文档**：详细文档在 `docs/` 目录
2. **🐛 创建Issue**：在GitHub仓库创建问题报告
3. **💬 社区讨论**：参与GitHub Discussions
4. **📧 联系支持**：发送邮件到支持邮箱

---

**🌟 祝您使用愉快！开始探索时尚数据的奥秘吧！**