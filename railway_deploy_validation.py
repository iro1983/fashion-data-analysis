#!/usr/bin/env python3
"""
Railway部署配置验证脚本
检查所有配置文件是否正确和一致
"""

import os
import json
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description} 存在: {file_path}")
        return True
    else:
        print(f"❌ {description} 不存在: {file_path}")
        return False

def validate_procfile():
    """验证Procfile"""
    print("\n🔍 检查 Procfile...")
    if not check_file_exists("Procfile", "Procfile"):
        return False
    
    with open("Procfile", "r") as f:
        content = f.read().strip()
        print(f"   内容: {content}")
        
        # 检查是否包含正确的启动命令
        if "python -m uvicorn app.main:app" in content:
            print("✅ Procfile 启动命令正确")
            return True
        else:
            print("❌ Procfile 启动命令不正确")
            return False

def validate_railway_json():
    """验证railway.json"""
    print("\n🔍 检查 railway.json...")
    if not check_file_exists("railway.json", "railway.json"):
        return False
    
    try:
        with open("railway.json", "r") as f:
            config = json.load(f)
        
        start_cmd = config.get("deploy", {}).get("startCommand", "")
        print(f"   startCommand: {start_cmd}")
        
        if "python -m uvicorn app.main:app" in start_cmd:
            print("✅ railway.json 启动命令正确")
            return True
        else:
            print("❌ railway.json 启动命令不正确")
            return False
    except json.JSONDecodeError as e:
        print(f"❌ railway.json 格式错误: {e}")
        return False

def validate_nixpacks_toml():
    """验证nixpacks.toml"""
    print("\n🔍 检查 nixpacks.toml...")
    if not check_file_exists("nixpacks.toml", "nixpacks.toml"):
        return False
    
    with open("nixpacks.toml", "r") as f:
        content = f.read()
        
        # 检查关键配置
        checks = [
            ("python3", "Python3 指定"),
            ("uvicorn", "Uvicorn 启动"),
            ("app.main:app", "应用入口")
        ]
        
        all_passed = True
        for check_item, description in checks:
            if check_item in content:
                print(f"✅ {description} 正确")
            else:
                print(f"❌ {description} 缺失")
                all_passed = False
        
        return all_passed

def validate_requirements():
    """验证requirements.txt"""
    print("\n🔍 检查 requirements.txt...")
    if not check_file_exists("requirements.txt", "requirements.txt"):
        return False
    
    with open("requirements.txt", "r") as f:
        lines = f.readlines()
    
    required_packages = ["fastapi", "uvicorn"]
    all_passed = True
    
    for package in required_packages:
        if any(package in line for line in lines):
            print(f"✅ {package} 依赖存在")
        else:
            print(f"❌ {package} 依赖缺失")
            all_passed = False
    
    return all_passed

def validate_main_app():
    """验证app/main.py"""
    print("\n🔍 检查 app/main.py...")
    if not check_file_exists("app/main.py", "主应用文件"):
        return False
    
    # 简单检查应用是否存在
    with open("app/main.py", "r") as f:
        content = f.read()
        
        if "FastAPI" in content and "uvicorn.run" in content:
            print("✅ 主应用结构正确")
            return True
        else:
            print("❌ 主应用结构有问题")
            return False

def main():
    """主验证函数"""
    print("🚀 Railway部署配置验证开始...")
    print("=" * 50)
    
    # 检查所有配置文件
    checks = [
        ("Procfile", validate_procfile),
        ("railway.json", validate_railway_json),
        ("nixpacks.toml", validate_nixpacks_toml),
        ("requirements.txt", validate_requirements),
        ("app/main.py", validate_main_app)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 检查 {name} 时出错: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 验证结果汇总:")
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有检查通过！配置正确，可以部署到Railway")
        print("\n📋 部署步骤:")
        print("1. 进入 Railway Dashboard")
        print("2. 选择你的项目")
        print("3. 进入 Settings > Deploy")
        print("4. 设置 Start Command: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT")
        print("5. 点击 Deploy Now")
        return True
    else:
        print("❌ 配置有问题，请检查失败的检查项")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)