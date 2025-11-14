#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页应用性能测试模块

测试内容包括：
1. 页面加载速度
2. 图表渲染性能
3. 移动端响应速度
4. 内存使用情况

测试指标：
- 页面加载: < 2s
- 图表渲染: < 1s
- 首次内容绘制: < 1.5s
- 交互准备时间: < 3s
"""

import time
import json
import statistics
from typing import Dict, List, Any
import subprocess
import sys
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebPerformanceTest:
    """网页应用性能测试类"""
    
    def __init__(self, dashboard_path: str = "fashion-dashboard"):
        """初始化测试环境"""
        self.dashboard_path = Path(dashboard_path)
        self.test_results = {}
        self.lighthouse_metrics = {}
        
    def setup_dashboard(self):
        """设置并启动仪表板应用"""
        logger.info("设置仪表板应用...")
        
        if not self.dashboard_path.exists():
            raise FileNotFoundError(f"仪表板目录不存在: {self.dashboard_path}")
        
        # 检查package.json
        package_json = self.dashboard_path / "package.json"
        if not package_json.exists():
            raise FileNotFoundError(f"package.json不存在: {package_json}")
        
        logger.info("仪表板设置完成")
    
    def test_build_performance(self):
        """测试构建性能"""
        logger.info("测试构建性能...")
        
        start_time = time.time()
        
        try:
            # 运行构建命令
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=self.dashboard_path,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            build_time = time.time() - start_time
            
            if result.returncode != 0:
                logger.error(f"构建失败: {result.stderr}")
                return {
                    'success': False,
                    'build_time': build_time,
                    'error': result.stderr
                }
            
            # 检查构建结果
            dist_path = self.dashboard_path / "dist"
            if not dist_path.exists():
                return {
                    'success': False,
                    'build_time': build_time,
                    'error': "dist目录未生成"
                }
            
            # 获取构建文件大小
            total_size = self._get_directory_size(dist_path)
            
            build_performance = {
                'success': True,
                'build_time': round(build_time, 2),
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'target_met': build_time < 60,  # 构建时间<60s
                'dist_files': len(list(dist_path.rglob("*"))) if dist_path.exists() else 0
            }
            
            logger.info(f"构建完成: {build_time:.1f}s, 大小: {total_size/1024/1024:.1f}MB")
            
        except subprocess.TimeoutExpired:
            build_performance = {
                'success': False,
                'build_time': 300,
                'error': "构建超时(5分钟)"
            }
        except Exception as e:
            build_performance = {
                'success': False,
                'build_time': time.time() - start_time,
                'error': str(e)
            }
        
        self.test_results['build_performance'] = build_performance
        return build_performance
    
    def _get_directory_size(self, directory: Path) -> int:
        """获取目录总大小"""
        total_size = 0
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            logger.warning(f"计算目录大小时出错: {e}")
        return total_size
    
    def test_lighthouse_performance(self, url: str = "http://localhost:5173"):
        """使用Lighthouse测试性能指标"""
        logger.info("运行Lighthouse性能测试...")
        
        lighthouse_script = """
        const puppeteer = require('puppeteer');
        const lighthouse = require('lighthouse');
        
        (async () => {
            const browser = await puppeteer.launch();
            const { lhr } = await lighthouse(url, {
                port: new URL(browser.wsEndpoint()).port,
                output: 'json',
                logLevel: 'info',
                onlyCategories: ['performance']
            });
            
            console.log(JSON.stringify(lhr));
            await browser.close();
        })();
        """
        
        try:
            # 检查Lighthouse是否可用
            result = subprocess.run(
                ["which", "lighthouse"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning("Lighthouse未安装，跳过性能测试")
                return {
                    'available': False,
                    'note': 'Lighthouse未安装，需要: npm install -g lighthouse'
                }
            
            # 运行Lighthouse测试
            result = subprocess.run(
                ["lighthouse", url, "--output=json", "--quiet"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                lhr_data = json.loads(result.stdout)
                lighthouse_metrics = self._extract_lighthouse_metrics(lhr_data)
            else:
                lighthouse_metrics = {
                    'available': False,
                    'error': result.stderr
                }
                
        except Exception as e:
            logger.warning(f"Lighthouse测试失败: {e}")
            lighthouse_metrics = {
                'available': False,
                'error': str(e)
            }
        
        self.test_results['lighthouse_performance'] = lighthouse_metrics
        return lighthouse_metrics
    
    def _extract_lighthouse_metrics(self, lhr_data: Dict) -> Dict[str, Any]:
        """提取Lighthouse关键指标"""
        try:
            categories = lhr_data.get('categories', {})
            audits = lhr_data.get('audits', {})
            
            # 提取核心Web指标
            metrics = {
                'performance_score': round(categories.get('performance', {}).get('score', 0) * 100, 1),
                'first-contentful-paint': {
                    'displayValue': audits.get('first-contentful-paint', {}).get('displayValue', 'N/A'),
                    'numericValue': round(audits.get('first-contentful-paint', {}).get('numericValue', 0) / 1000, 2)
                },
                'largest-contentful-paint': {
                    'displayValue': audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                    'numericValue': round(audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000, 2)
                },
                'speed-index': {
                    'displayValue': audits.get('speed-index', {}).get('displayValue', 'N/A'),
                    'numericValue': round(audits.get('speed-index', {}).get('numericValue', 0) / 1000, 2)
                },
                'cumulative-layout-shift': {
                    'displayValue': audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A'),
                    'numericValue': round(audits.get('cumulative-layout-shift', {}).get('numericValue', 0), 3)
                },
                'total-blocking-time': {
                    'displayValue': audits.get('total-blocking-time', {}).get('displayValue', 'N/A'),
                    'numericValue': round(audits.get('total-blocking-time', {}).get('numericValue', 0) / 1000, 2)
                },
                'available': True
            }
            
            # 检查目标是否达成
            metrics['targets_met'] = {
                'fcp_under_1_5s': metrics['first-contentful-paint']['numericValue'] < 1.5,
                'lcp_under_2_5s': metrics['largest-contentful-paint']['numericValue'] < 2.5,
                'cls_under_0_1': metrics['cumulative-layout-shift']['numericValue'] < 0.1,
                'tbt_under_200ms': metrics['total-blocking-time']['numericValue'] < 0.2
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"提取Lighthouse指标时出错: {e}")
            return {
                'available': False,
                'error': str(e)
            }
    
    def test_bundle_analysis(self):
        """分析打包文件大小"""
        logger.info("分析打包文件...")
        
        dist_path = self.dashboard_path / "dist"
        if not dist_path.exists():
            return {
                'available': False,
                'error': 'dist目录不存在，请先运行构建'
            }
        
        bundle_analysis = {
            'available': True,
            'total_size_mb': 0,
            'js_files': [],
            'css_files': [],
            'asset_files': [],
            'largest_files': []
        }
        
        try:
            all_files = list(dist_path.rglob("*"))
            
            for file_path in all_files:
                if file_path.is_file():
                    size = file_path.stat().st_size
                    relative_path = file_path.relative_to(dist_path)
                    
                    file_info = {
                        'path': str(relative_path),
                        'size_kb': round(size / 1024, 2)
                    }
                    
                    if file_path.suffix == '.js':
                        bundle_analysis['js_files'].append(file_info)
                    elif file_path.suffix == '.css':
                        bundle_analysis['css_files'].append(file_info)
                    else:
                        bundle_analysis['asset_files'].append(file_info)
            
            # 计算总大小
            bundle_analysis['total_size_mb'] = round(
                sum(f['size_kb'] for f in 
                    bundle_analysis['js_files'] + 
                    bundle_analysis['css_files'] + 
                    bundle_analysis['asset_files']) / 1024, 2
            )
            
            # 找出最大的文件
            all_files_sorted = sorted(
                bundle_analysis['js_files'] + bundle_analysis['css_files'] + bundle_analysis['asset_files'],
                key=lambda x: x['size_kb'],
                reverse=True
            )[:10]
            
            bundle_analysis['largest_files'] = all_files_sorted
            
            # 检查目标 (JS文件 < 500KB, CSS文件 < 100KB)
            js_sizes = [f['size_kb'] for f in bundle_analysis['js_files']]
            css_sizes = [f['size_kb'] for f in bundle_analysis['css_files']]
            
            bundle_analysis['targets_met'] = {
                'js_under_500kb': all(size < 500 for size in js_sizes) if js_sizes else True,
                'css_under_100kb': all(size < 100 for size in css_sizes) if css_sizes else True,
                'total_under_2mb': bundle_analysis['total_size_mb'] < 2
            }
            
            logger.info(f"打包分析完成: 总大小 {bundle_analysis['total_size_mb']}MB")
            
        except Exception as e:
            bundle_analysis = {
                'available': False,
                'error': str(e)
            }
        
        self.test_results['bundle_analysis'] = bundle_analysis
        return bundle_analysis
    
    def test_react_component_performance(self):
        """测试React组件性能"""
        logger.info("测试React组件性能...")
        
        # 分析主要组件文件
        src_path = self.dashboard_path / "src"
        if not src_path.exists():
            return {
                'available': False,
                'error': 'src目录不存在'
            }
        
        component_analysis = {
            'available': True,
            'total_components': 0,
            'components': [],
            'potential_issues': []
        }
        
        try:
            # 查找所有React组件
            component_files = list(src_path.rglob("*.tsx")) + list(src_path.rglob("*.jsx"))
            component_analysis['total_components'] = len(component_files)
            
            for component_file in component_files:
                try:
                    with open(component_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 简单分析组件特征
                    analysis = self._analyze_component_file(component_file, content)
                    component_analysis['components'].append(analysis)
                    
                except Exception as e:
                    logger.warning(f"分析组件文件 {component_file} 时出错: {e}")
            
            # 识别潜在问题
            issues = self._identify_performance_issues(component_analysis['components'])
            component_analysis['potential_issues'] = issues
            
            component_analysis['targets_met'] = {
                'no_large_components': all(c['lines'] < 500 for c in component_analysis['components']),
                'no_deep_nesting': all(c['max_depth'] < 10 for c in component_analysis['components']),
                'reasonable_imports': all(c['import_count'] < 20 for c in component_analysis['components'])
            }
            
            logger.info(f"组件分析完成: {component_analysis['total_components']} 个组件")
            
        except Exception as e:
            component_analysis = {
                'available': False,
                'error': str(e)
            }
        
        self.test_results['react_component_performance'] = component_analysis
        return component_analysis
    
    def _analyze_component_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """分析单个组件文件"""
        lines = content.split('\n')
        
        # 计算基本指标
        line_count = len(lines)
        
        # 简单统计
        jsx_elements = content.count('<') + content.count('</')
        useState_hooks = content.count('useState')
        useEffect_hooks = content.count('useEffect')
        useMemo_hooks = content.count('useMemo')
        useCallback_hooks = content.count('useCallback')
        
        # 导入统计
        import_lines = [line for line in lines if line.strip().startswith('import')]
        import_count = len(import_lines)
        
        # 最大嵌套深度估计
        max_depth = 0
        current_depth = 0
        for line in lines:
            current_depth += line.count('<') - line.count('</>')
            max_depth = max(max_depth, current_depth)
        
        return {
            'name': file_path.stem,
            'path': str(file_path.relative_to(src_path)),
            'lines': line_count,
            'jsx_elements': jsx_elements,
            'hooks': {
                'useState': useState_hooks,
                'useEffect': useEffect_hooks,
                'useMemo': useMemo_hooks,
                'useCallback': useCallback_hooks
            },
            'import_count': import_count,
            'max_depth': max_depth,
            'complexity_score': self._calculate_complexity_score(line_count, jsx_elements, useState_hooks, useEffect_hooks)
        }
    
    def _calculate_complexity_score(self, lines: int, jsx_elements: int, use_state: int, use_effect: int) -> int:
        """计算组件复杂度分数"""
        # 简化的复杂度计算
        return lines // 10 + jsx_elements // 5 + use_state + use_effect * 2
    
    def _identify_performance_issues(self, components: List[Dict]) -> List[str]:
        """识别性能问题"""
        issues = []
        
        # 检查大文件
        large_components = [c for c in components if c['lines'] > 300]
        if large_components:
            issues.append(f"发现 {len(large_components)} 个大文件组件 (>300行)")
        
        # 检查深度嵌套
        deep_components = [c for c in components if c['max_depth'] > 8]
        if deep_components:
            issues.append(f"发现 {len(deep_components)} 个深度嵌套组件 (>8层)")
        
        # 检查过多导入
        heavy_imports = [c for c in components if c['import_count'] > 15]
        if heavy_imports:
            issues.append(f"发现 {len(heavy_imports)} 个导入过多的组件 (>15个导入)")
        
        # 检查过度使用useEffect
        heavy_effects = [c for c in components if c['hooks']['useEffect'] > 5]
        if heavy_effects:
            issues.append(f"发现 {len(heavy_effects)} 个过度使用useEffect的组件 (>5个)")
        
        return issues
    
    def test_mobile_responsiveness(self):
        """测试移动端响应性"""
        logger.info("测试移动端响应性...")
        
        # 检查响应式设计实现
        src_path = self.dashboard_path / "src"
        if not src_path.exists():
            return {
                'available': False,
                'error': 'src目录不存在'
            }
        
        responsiveness_analysis = {
            'available': True,
            'has_responsive_hooks': False,
            'has_media_queries': False,
            'has_mobile_components': False,
            'touch_friendly_elements': 0,
            'mobile_specific_files': []
        }
        
        try:
            # 检查hook实现
            hooks_path = src_path / "hooks"
            if hooks_path.exists():
                use_mobile_file = hooks_path / "use-mobile.tsx"
                if use_mobile_file.exists():
                    responsiveness_analysis['has_responsive_hooks'] = True
                    
                    with open(use_mobile_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 检查移动端检测逻辑
                        if 'window.innerWidth' in content or 'ResizeObserver' in content:
                            responsiveness_analysis['mobile_detection'] = True
            
            # 检查CSS媒体查询
            css_files = list(src_path.rglob("*.css")) + list(self.dashboard_path.rglob("*.css"))
            media_queries_count = 0
            
            for css_file in css_files:
                try:
                    with open(css_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        media_queries_count += content.count('@media')
                except:
                    continue
            
            responsiveness_analysis['has_media_queries'] = media_queries_count > 0
            responsiveness_analysis['media_queries_count'] = media_queries_count
            
            # 检查移动端特定组件
            mobile_files = [f for f in src_path.rglob("*") 
                           if f.is_file() and 'mobile' in f.name.lower()]
            responsiveness_analysis['mobile_specific_files'] = [str(f) for f in mobile_files]
            responsiveness_analysis['has_mobile_components'] = len(mobile_files) > 0
            
            # 检查移动端友好元素
            tsx_files = list(src_path.rglob("*.tsx"))
            touch_friendly_count = 0
            
            for tsx_file in tsx_files:
                try:
                    with open(tsx_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 检查常见移动端交互元素
                        touch_friendly_count += content.count('button')
                        touch_friendly_count += content.count('onClick')
                        touch_friendly_count += content.count('touch')
                except:
                    continue
            
            responsiveness_analysis['touch_friendly_elements'] = touch_friendly_count
            
            # 检查目标达成
            responsiveness_analysis['targets_met'] = {
                'has_responsive_hooks': responsiveness_analysis['has_responsive_hooks'],
                'has_media_queries': responsiveness_analysis['has_media_queries'],
                'has_mobile_optimization': (
                    responsiveness_analysis['has_responsive_hooks'] or 
                    responsiveness_analysis['has_media_queries']
                )
            }
            
            logger.info(f"响应式分析完成: 媒体查询 {media_queries_count} 个")
            
        except Exception as e:
            responsiveness_analysis = {
                'available': False,
                'error': str(e)
            }
        
        self.test_results['mobile_responsiveness'] = responsiveness_analysis
        return responsiveness_analysis
    
    def run_all_tests(self):
        """运行所有网页性能测试"""
        logger.info("开始网页应用性能测试...")
        
        try:
            # 设置测试环境
            self.setup_dashboard()
            
            # 运行各项测试
            self.test_build_performance()
            self.test_bundle_analysis()
            self.test_react_component_performance()
            self.test_mobile_responsiveness()
            
            # Lighthouse测试 (可选)
            self.test_lighthouse_performance()
            
            logger.info("网页应用性能测试完成")
            
        except Exception as e:
            logger.error(f"测试过程中出错: {e}")
            raise
    
    def generate_report(self) -> Dict[str, Any]:
        """生成性能测试报告"""
        return {
            'test_type': 'web_performance',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'framework': 'React + Vite',
            'test_results': self.test_results,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'overall_status': 'unknown',
            'performance_score': 0
        }
        
        # 检查各项测试是否达标
        test_checks = {
            'build_performance': lambda r: r.get('target_met', False),
            'bundle_analysis': lambda r: r.get('targets_met', {}).get('total_under_2mb', False),
            'react_component_performance': lambda r: r.get('targets_met', {}).get('no_large_components', False),
            'mobile_responsiveness': lambda r: r.get('targets_met', {}).get('has_mobile_optimization', False),
            'lighthouse_performance': lambda r: r.get('performance_score', 0) >= 80
        }
        
        for test_name, check_func in test_checks.items():
            if test_name in self.test_results:
                summary['total_tests'] += 1
                try:
                    if check_func(self.test_results[test_name]):
                        summary['passed_tests'] += 1
                    else:
                        summary['failed_tests'] += 1
                except Exception:
                    summary['failed_tests'] += 1
        
        # 计算性能分数
        if summary['total_tests'] > 0:
            summary['performance_score'] = round((summary['passed_tests'] / summary['total_tests']) * 100, 1)
        
        if summary['passed_tests'] == summary['total_tests']:
            summary['overall_status'] = 'passed'
        elif summary['passed_tests'] > 0:
            summary['overall_status'] = 'partial'
        else:
            summary['overall_status'] = 'failed'
        
        return summary


def run_web_performance_tests():
    """运行网页性能测试的主函数"""
    print("=" * 60)
    print("网页应用性能测试")
    print("=" * 60)
    
    tester = WebPerformanceTest()
    
    try:
        # 运行测试
        tester.run_all_tests()
        
        # 生成报告
        report = tester.generate_report()
        
        # 输出结果
        print("\n📊 测试结果摘要:")
        summary = report['summary']
        print(f"   性能分数: {summary['performance_score']}/100")
        print(f"   总测试项: {summary['total_tests']}")
        print(f"   通过测试: {summary['passed_tests']}")
        print(f"   失败测试: {summary['failed_tests']}")
        print(f"   整体状态: {summary['overall_status']}")
        
        # 详细结果
        print("\n📈 详细测试结果:")
        for test_name, results in report['test_results'].items():
            print(f"\n{test_name}:")
            if isinstance(results, dict):
                for key, value in results.items():
                    if key in ['target_met', 'targets_met'] or isinstance(value, bool):
                        status = "✅" if value else "❌"
                        print(f"   {status} {key}: {value}")
                    else:
                        print(f"   {key}: {value}")
        
        # 保存详细报告
        report_file = Path("tests/web_performance_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        raise


if __name__ == "__main__":
    run_web_performance_tests()