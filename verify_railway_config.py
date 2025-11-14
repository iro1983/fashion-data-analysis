#!/usr/bin/env python3
"""
Railway部署配置验证脚本
========================
验证所有关键配置文件是否正确配置
"""
import os
import json
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}缺失: {filepath}")
        return False

def check_file_content(filepath, expected_content, description):
    """检查文件内容是否包含期望内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if expected_content in content:
                print(f"✅ {description}: 包含 '{expected_content[:50]}...'")
                return True
            else:
                print(f"❌ {description}: 缺少 '{expected_content[:50]}...'")
                return False
    except Exception as e:
        print(f"❌ {description}: 读取失败 - {e}")
        return False

def main():
    print("🚀 Railway部署配置验证")
    print("=" * 50)
    
    # 检查关键文件
    checks_passed = 0
    total_checks = 0
    
    # 1. 检查Procfile
    total_checks += 1
    if check_file_content("Procfile", "web: python main.py", "Procfile配置"):
        checks_passed += 1
    
    # 2. 检查main.py
    total_checks += 1
    if check_file_content("main.py", "from app.main import app", "主入口文件导入"):
        checks_passed += 1
    
    # 3. 检查railway.json
    total_checks += 1
    if Path("railway.json").exists():
        try:
            with open("railway.json", 'r') as f:
                railway_config = json.load(f)
                if railway_config.get("deploy", {}).get("startCommand") == "python main.py":
                    print("✅ railway.json启动命令配置正确")
                    checks_passed += 1
                else:
                    print(f"❌ railway.json启动命令错误: {railway_config.get('deploy', {}).get('startCommand')}")
        except Exception as e:
            print(f"❌ railway.json解析失败: {e}")
    
    # 4. 检查requirements.txt是否移除了重型依赖
    total_checks += 1
    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
            if "selenium" not in requirements and "opencv" not in requirements:
                print("✅ requirements.txt已移除重型依赖")
                checks_passed += 1
            else:
                print("❌ requirements.txt仍包含重型依赖")
    except Exception as e:
        print(f"❌ requirements.txt读取失败: {e}")
    
    # 5. 检查FastAPI应用
    total_checks += 1
    if check_file_content("app/main.py", "app = FastAPI", "FastAPI应用定义"):
        checks_passed += 1
    
    print("\n" + "=" * 50)
    print(f"验证结果: {checks_passed}/{total_checks} 项检查通过")
    
    if checks_passed == total_checks:
        print("🎉 所有配置验证通过！可以安全部署到Railway")
        return True
    else:
        print("⚠️  发现配置问题，请修复后再部署")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)