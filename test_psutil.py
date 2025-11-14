#!/usr/bin/env python3
# 简单的psutil测试脚本

try:
    import psutil
    import os
    
    print(f"psutil导入成功！版本: {psutil.__version__}")
    
    # 获取当前进程信息
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"当前进程内存使用: {memory_mb:.2f} MB")
    
except ImportError as e:
    print(f"psutil导入失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")