# Amazon & TikTok 数据抓取系统 - 性能优化方案

## 优化概述

**优化目标**: 提升系统性能，降低资源消耗，改善用户体验  
**预期收益**: 响应速度提升50%，系统吞吐量提升100%  
**优化周期**: 2-4周  
**实施优先级**: 高

---

## 1. 数据库优化

### 1.1 索引优化
```sql
-- 产品表索引优化
CREATE INDEX idx_products_platform_category ON products(platform, category);
CREATE INDEX idx_products_title_fulltext ON products(title);
CREATE INDEX idx_products_price_range ON products(price);
CREATE INDEX idx_products_scraped_at ON products(scraped_at);

-- 任务表索引优化
CREATE INDEX idx_tasks_status_created ON tasks(status, created_at);
CREATE INDEX idx_tasks_platform_status ON tasks(platform, status);

-- 结果表索引优化
CREATE INDEX idx_results_task_platform ON results(task_id, platform);
CREATE INDEX idx_results_timestamp ON results(timestamp);
```

### 1.2 查询优化
```sql
-- 优化前
SELECT * FROM products WHERE platform = 'amazon' ORDER BY scraped_at DESC LIMIT 100;

-- 优化后
SELECT product_id, title, price, category, scraped_at 
FROM products 
WHERE platform = 'amazon' AND scraped_at > datetime('now', '-7 days')
ORDER BY scraped_at DESC LIMIT 100;
```

### 1.3 数据分区策略
```sql
-- 按月份分区产品表
CREATE TABLE products_2025_11 PARTITION OF products
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE products_2025_12 PARTITION OF products
FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');
```

### 1.4 过期数据清理
```sql
-- 清理30天前的任务数据
DELETE FROM tasks WHERE created_at < datetime('now', '-30 days');

-- 归档历史数据到备份表
INSERT INTO products_archive SELECT * FROM products 
WHERE scraped_at < datetime('now', '-90 days');

DELETE FROM products WHERE scraped_at < datetime('now', '-90 days');
```

### 1.5 性能监控SQL
```sql
-- 查询最慢的SQL
SELECT sql, total_time, calls 
FROM sqlite_stat1 
ORDER BY total_time DESC 
LIMIT 10;

-- 数据库大小统计
SELECT 
    name as table_name,
    (SELECT COUNT(*) FROM main.sqlite_master WHERE type='index' AND tbl_name=main.name) as index_count
FROM main.sqlite_master main
WHERE type='table';
```

---

## 2. 应用层优化

### 2.1 缓存策略
```python
# Redis缓存配置
import redis
import json
from functools import wraps

# 缓存装饰器
def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            redis_client.setex(
                cache_key, 
                expire_time, 
                json.dumps(result, default=str)
            )
            return result
        return wrapper
    return decorator

# 产品数据缓存
@cache_result(expire_time=600)
def get_cached_products(platform, category, limit=100):
    # 数据库查询逻辑
    pass
```

### 2.2 连接池优化
```python
# 数据库连接池配置
import sqlite3
from contextlib import contextmanager
import threading

class OptimizedDatabaseManager:
    def __init__(self, db_path, pool_size=10):
        self.db_path = db_path
        self.pool_size = pool_size
        self._local = threading.local()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            # 优化连接设置
            self._local.conn.execute('PRAGMA journal_mode=WAL')
            self._local.conn.execute('PRAGMA cache_size=10000')
            self._local.conn.execute('PRAGMA temp_store=memory')
        
        try:
            yield self._local.conn
        except Exception:
            self._local.conn.rollback()
            raise
```

### 2.3 异步处理优化
```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class OptimizedScraper:
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
    
    async def scrape_concurrent(self, tasks):
        """并发抓取优化"""
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=self.max_concurrent,
                limit_per_host=5
            ),
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            self.session = session
            
            # 使用信号量控制并发数
            async def scrape_with_limit(task):
                async with self.semaphore:
                    return await self.scrape_single(task)
            
            # 并发执行所有任务
            results = await asyncio.gather(*[
                scrape_with_limit(task) for task in tasks
            ], return_exceptions=True)
            
            return results
```

### 2.4 内存使用优化
```python
# 内存优化配置
import gc
import psutil
import threading
from functools import lru_cache

class MemoryOptimizer:
    def __init__(self):
        self.memory_threshold = 80  # 内存使用率阈值
        self.monitor_thread = None
    
    def start_monitoring(self):
        """启动内存监控"""
        if self.monitor_thread is None:
            self.monitor_thread = threading.Thread(target=self._monitor_memory)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def _monitor_memory(self):
        """内存监控线程"""
        while True:
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > self.memory_threshold:
                # 执行垃圾回收
                gc.collect()
                print(f"内存使用率过高 ({memory_percent}%)，已执行垃圾回收")
            
            time.sleep(30)  # 每30秒检查一次
    
    @lru_cache(maxsize=1000)
    def cached_data_processing(self, data_hash):
        """缓存数据处理结果"""
        # 数据处理逻辑
        return processed_data
```

---

## 3. 前端优化

### 3.1 懒加载实现
```typescript
// 组件懒加载
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const ProductList = React.lazy(() => import('./pages/ProductList'));

// 路由懒加载
const AppRouter = () => (
  <Suspense fallback={<LoadingSpinner />}>
    <Routes>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/products" element={<ProductList />} />
    </Routes>
  </Suspense>
);

// 图片懒加载
const LazyImage = ({ src, alt, ...props }) => {
  const [loaded, setLoaded] = useState(false);
  const imgRef = useRef();
  
  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setLoaded(true);
        observer.disconnect();
      }
    });
    
    if (imgRef.current) {
      observer.observe(imgRef.current);
    }
    
    return () => observer.disconnect();
  }, []);
  
  return (
    <div ref={imgRef} {...props}>
      {loaded ? (
        <img src={src} alt={alt} loading="lazy" />
      ) : (
        <div className="placeholder">加载中...</div>
      )}
    </div>
  );
};
```

### 3.2 虚拟滚动
```typescript
// 产品列表虚拟滚动
import { FixedSizeList as List } from 'react-window';

const VirtualizedProductList = ({ products }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ProductCard product={products[index]} />
    </div>
  );
  
  return (
    <List
      height={600}
      itemCount={products.length}
      itemSize={120}
      width="100%"
    >
      {Row}
    </List>
  );
};
```

### 3.3 缓存策略
```typescript
// Service Worker缓存
const CACHE_NAME = 'fashion-dashboard-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/api/products'
];

// 安装Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// 缓存优先策略
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // 返回缓存的版本
        return response || fetch(event.request);
      }
    )
  );
});
```

### 3.4 代码分割
```typescript
// 按功能模块分割
const AdminPanel = React.lazy(() => 
  import('./components/AdminPanel').then(module => ({
    default: module.AdminPanel
  }))
);

const Analytics = React.lazy(() => 
  import('./pages/Analytics').then(module => ({
    default: module.Analytics
  }))
);

// 条件加载
const loadComponent = async (componentName: string) => {
  const module = await import(`./components/${componentName}`);
  return module.default;
};
```

---

## 4. 网络层优化

### 4.1 API响应压缩
```python
# Flask响应压缩
from flask import Flask, request, jsonify
from flask_compress import Compress

app = Flask(__name__)
Compress(app)

@app.route('/api/products')
@compress.compressed()
def get_products():
    # API逻辑
    return jsonify(large_dataset)
```

### 4.2 请求合并
```python
# 批量请求处理
class BatchRequestHandler:
    def __init__(self, batch_size=100):
        self.batch_size = batch_size
        self.pending_requests = []
    
    def add_request(self, request_data):
        """添加请求到批次"""
        self.pending_requests.append(request_data)
        
        if len(self.pending_requests) >= self.batch_size:
            return self.process_batch()
        return None
    
    def process_batch(self):
        """批量处理请求"""
        if not self.pending_requests:
            return None
        
        batch = self.pending_requests.copy()
        self.pending_requests.clear()
        
        # 批量处理逻辑
        results = self.execute_batch_requests(batch)
        return results
```

### 4.3 CDN配置
```nginx
# Nginx CDN配置
server {
    listen 80;
    server_name your-domain.com;
    
    # 静态资源CDN
    location /static/ {
        proxy_cache static_cache;
        proxy_cache_valid 200 1y;
        add_header Cache-Control "public, max-age=31536000";
    }
    
    # API响应缓存
    location /api/ {
        proxy_cache api_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_valid 404 1m;
        add_header Cache-Control "public, max-age=300";
    }
}
```

---

## 5. 监控和告警

### 5.1 性能监控
```python
# 性能监控中间件
import time
import functools
from prometheus_client import Counter, Histogram, Gauge

# Prometheus指标
request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_connections = Gauge('database_connections_active', 'Active database connections')

def monitor_performance(func):
    """性能监控装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        request_count.inc()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            request_duration.observe(duration)
    
    return wrapper

@monitor_performance
def expensive_operation():
    # 耗时操作
    pass
```

### 5.2 健康检查
```python
# 系统健康检查
class HealthChecker:
    def __init__(self):
        self.checks = [
            self.check_database,
            self.check_redis,
            self.check_memory,
            self.check_disk
        ]
    
    async def check_database(self):
        """数据库健康检查"""
        try:
            with sqlite3.connect('data/scraping.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                return {"status": "healthy", "message": "Database connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    async def check_redis(self):
        """Redis健康检查"""
        try:
            redis_client.ping()
            return {"status": "healthy", "message": "Redis connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    def check_memory(self):
        """内存使用检查"""
        memory = psutil.virtual_memory()
        if memory.percent < 80:
            return {"status": "healthy", "message": f"Memory usage: {memory.percent}%"}
        else:
            return {"status": "warning", "message": f"High memory usage: {memory.percent}%"}
    
    def check_disk(self):
        """磁盘使用检查"""
        disk = psutil.disk_usage('/')
        if disk.percent < 90:
            return {"status": "healthy", "message": f"Disk usage: {disk.percent}%"}
        else:
            return {"status": "unhealthy", "message": f"Low disk space: {disk.percent}%"}
```

---

## 6. 负载均衡

### 6.1 多实例部署
```yaml
# Docker Compose负载均衡
version: '3.8'
services:
  app1:
    image: fashion-scraper:latest
    environment:
      - INSTANCE_ID=1
      - DATABASE_URL=postgresql://user:pass@db:5432/scraper
    ports:
      - "8001:8000"
  
  app2:
    image: fashion-scraper:latest
    environment:
      - INSTANCE_ID=2
      - DATABASE_URL=postgresql://user:pass@db:5432/scraper
    ports:
      - "8002:8000"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app1
      - app2
```

### 6.2 任务队列优化
```python
# Celery任务队列优化
from celery import Celery

app = Celery('scraper', broker='redis://localhost:6379/0')

# 配置优化
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'scraper.tasks.quick_task': {'queue': 'fast'},
        'scraper.tasks.heavy_task': {'queue': 'slow'},
    },
    worker_prefetch_multiplier=1,  # 避免预取过多任务
    task_acks_late=True,  # 任务完成后再确认
    worker_max_tasks_per_child=1000,  # 防止内存泄漏
)

@app.task(bind=True, max_retries=3)
def optimize_scrape_task(self, task_data):
    """优化的抓取任务"""
    try:
        # 任务执行逻辑
        result = perform_scrape(task_data)
        return result
    except Exception as exc:
        # 指数退避重试
        raise self.retry(countdown=2 ** self.request.retries, exc=exc)
```

---

## 7. 实施计划

### 阶段1: 基础设施优化 (Week 1-2)
- [ ] 数据库索引优化
- [ ] 连接池配置
- [ ] 缓存系统部署
- [ ] 监控工具安装

### 阶段2: 应用层优化 (Week 2-3)
- [ ] 代码级性能优化
- [ ] 异步处理增强
- [ ] 内存使用优化
- [ ] 前端性能优化

### 阶段3: 系统集成优化 (Week 3-4)
- [ ] 负载均衡配置
- [ ] CDN部署
- [ ] 完整性能测试
- [ ] 文档更新

### 阶段4: 验证和调优 (Week 4)
- [ ] 性能基准测试
- [ ] 负载测试验证
- [ ] 参数微调
- [ ] 最终验收

---

## 8. 性能基准

### 优化前基准
- 平均响应时间: 2.5秒
- 并发处理能力: 20任务
- 内存使用: 2GB
- CPU使用率: 60%

### 优化目标
- 平均响应时间: < 1.25秒 (50%提升)
- 并发处理能力: 100任务 (400%提升)
- 内存使用: < 1.5GB (25%降低)
- CPU使用率: < 40% (33%降低)

### 预期收益
- **用户体验**: 页面加载更快，操作更流畅
- **系统容量**: 支持更大规模的数据处理
- **资源成本**: 降低服务器资源需求
- **可扩展性**: 为业务增长提供支撑

---

## 9. 风险评估

### 技术风险
- **缓存失效**: 可能导致数据不一致
- **索引冲突**: 复杂的索引可能影响写入性能
- **内存泄漏**: 长期运行可能出现内存问题

### 缓解措施
- **数据一致性检查**: 定期验证缓存数据
- **渐进式索引**: 分步实施索引优化
- **内存监控**: 实时监控内存使用情况

---

## 10. 效果验证

### 监控指标
1. **响应时间**: 持续监控API响应时间
2. **吞吐量**: 监控每秒处理请求数
3. **错误率**: 监控请求错误率
4. **资源使用**: 监控CPU、内存、磁盘使用

### 验收标准
- [ ] 所有性能指标达到目标值
- [ ] 7×24小时稳定性测试通过
- [ ] 用户满意度提升
- [ ] 系统可用性>99.9%

---

**方案制定**: 2025-11-14  
**实施负责人**: 技术团队  
**下次评估**: 2025-12-14
