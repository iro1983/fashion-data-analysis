# Railway 部署时尚数据分析系统

## 部署步骤

### 第一步：创建新项目
1. 访问 https://railway.app/dashboard
2. 点击 "New Project" 按钮
3. 选择 "Deploy from GitHub repo"
4. 找到并选择您的仓库：**iro1983/fashion-data-analysis**

### 第二步：配置项目设置
1. Railway会自动识别这是一个Python项目
2. 检查配置文件：
   - **启动命令**: `uvicorn code.main:app --host 0.0.0.0 --port $PORT`
   - **环境**: Python 3.9+
   - **工作目录**: `/workspace`

### 第三步：配置环境变量
在Railway项目设置中添加以下环境变量：

```
TIKHUB_API_KEY=your_tikhub_api_key_here
AMAZON_ACCESS_KEY=your_amazon_access_key_here
AMAZON_SECRET_KEY=your_amazon_secret_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
DEBUG=false
SECRET_KEY=your_random_secret_key_here
```

### 第四步：部署设置
1. Railway会自动构建Docker镜像
2. 部署过程大约需要3-5分钟
3. 完成后会提供一个公共URL

### 第五步：数据库配置
1. Railway会自动创建PostgreSQL数据库
2. 可以选择连接到SQLite或迁移到PostgreSQL
3. 建议使用PostgreSQL以获得更好的性能

## 预期的部署结果
✅ 后端API服务运行在 https://your-app-name.railway.app
✅ 前端React应用访问同一URL
✅ 数据库连接正常
✅ 定时数据抓取功能运行

## 部署后测试
部署完成后，请告诉我结果，我将进一步指导您测试所有功能。