# 集成测试系统

本目录包含了电商数据抓取和分析系统的完整集成测试套件。

## 🧪 测试模块

### 1. 主要集成测试 (`integration_tests.py`)
- 完整工作流程测试
- 组件集成测试  
- 数据一致性测试
- 性能指标测试

### 2. 数据流测试 (`test_data_flow.py`)
- 端到端数据流程验证
- 数据清洗和转换规则测试
- 数据完整性检查
- 数据流性能测试

### 3. 错误处理测试 (`test_error_handling.py`)
- 网络错误处理
- 数据库错误恢复
- 数据验证错误处理
- 重试机制测试

### 4. 用户界面测试 (`test_user_interface.py`)
- React组件渲染测试
- 用户交互功能测试
- 数据可视化测试
- 响应式设计测试

### 5. 测试运行器 (`run_integration_tests.py`)
- 自动执行所有测试
- 生成综合测试报告
- 环境检查和设置

## 🚀 快速开始

### 运行所有测试
```bash
# 进入项目根目录
cd /workspace

# 运行完整测试套件
python tests/run_integration_tests.py
```

### 运行特定测试
```bash
# 运行主要集成测试
python tests/integration_tests.py

# 运行数据流测试
python tests/test_data_flow.py

# 运行错误处理测试
python tests/test_error_handling.py

# 运行UI测试
python tests/test_user_interface.py
```

## 📋 测试覆盖范围

### 数据流程测试
- ✅ 数据抓取 → 清洗 → 存储 → 展示
- ✅ 多平台数据整合（Amazon + TikTok）
- ✅ 数据去重和一致性检查
- ✅ 批量数据处理性能

### 组件集成测试
- ✅ `amazon_scraper.py` + `database.py`
- ✅ `tiktok_scraper.py` + `data_cleaner.py`
- ✅ `main.py` + 数据库 + 可视化界面
- ✅ 所有模块协同工作

### 错误处理测试
- ✅ 网络连接异常处理
- ✅ 数据库锁和约束错误
- ✅ 数据验证失败处理
- ✅ 系统资源不足恢复

### 用户体验测试
- ✅ 完整用户操作流程
- ✅ 数据筛选和搜索功能
- ✅ 报表生成和导出
- ✅ 响应式界面适配

## 🎯 验证标准

- **功能可用性**: 100%
- **数据完整性**: > 99%
- **错误处理覆盖**: > 90%
- **用户体验**: 流畅

## 📊 测试报告

测试完成后会生成以下报告：

1. **控制台输出**: 实时测试进度和结果
2. `tests/logs/integration_test.log`: 详细日志
3. `tests/reports/integration_test_summary.json`: 结构化测试摘要
4. `tests/integration_report.md`: 详细测试报告

## 🔧 配置选项

编辑 `tests/test_config.py` 来自定义测试行为：

```python
# 调整测试数据大小
TEST_ENVIRONMENT['test_data_size'] = 'large'

# 更改超时设置
SCRAPER_CONFIG['amazon']['timeout_seconds'] = 30

# 调整并发数
PERFORMANCE_CONFIG['concurrent_operations'] = 10
```

## ⚠️ 注意事项

1. **测试环境**: 测试使用独立的临时数据库，不会影响生产数据
2. **网络依赖**: 某些测试可能需要网络连接（可通过mock禁用）
3. **资源清理**: 测试完成后会自动清理临时文件
4. **日志**: 确保 `tests/logs` 目录有写入权限

## 🐛 故障排除

### 常见问题

**问题**: 模块导入错误
```bash
解决方案: 确保在项目根目录运行测试
cd /workspace && python tests/run_integration_tests.py
```

**问题**: 权限错误
```bash
解决方案: 给予测试目录写权限
chmod -R 755 tests/
```

**问题**: 测试超时
```bash
解决方案: 在test_config.py中调整timeout设置
SCRAPER_CONFIG['amazon']['timeout_seconds'] = 60
```

## 📞 支持

如遇到问题，请检查：
1. 测试日志: `tests/logs/integration_test.log`
2. 错误信息: 控制台输出
3. 项目结构: 确保所有必要文件存在

---

**最后更新**: 2025-11-14  
**维护者**: Claude AI Assistant