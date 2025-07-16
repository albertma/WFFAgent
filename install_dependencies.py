#!/usr/bin/env python3
"""
依赖安装脚本
解决 langchain 版本兼容性问题
"""

import subprocess
import sys
import os

def run_command(command):
    """运行命令并显示输出"""
    print(f"执行命令: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ 成功: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {e.stderr}")
        return False

def main():
    print("🔧 开始安装依赖...")
    print("=" * 50)
    
    # 1. 卸载可能冲突的包
    print("\n1. 卸载可能冲突的包...")
    packages_to_remove = [
        "langchain",
        "langchain-core", 
        "langchain-community",
        "langchain-openai"
    ]
    
    for package in packages_to_remove:
        run_command(f"pip uninstall -y {package}")
    
    # 2. 安装指定版本的包
    print("\n2. 安装指定版本的包...")
    packages_to_install = [
        "langchain~=0.3",
        "langchain-core~=0.3",
        "langchain-openai~=0.3",
        "langchain-community~=0.3"
    ]
    
    for package in packages_to_install:
        if not run_command(f"pip install {package}"):
            print(f"⚠️ 警告: {package} 安装失败，尝试继续...")
    
    # 3. 安装其他依赖
    print("\n3. 安装其他依赖...")
    other_packages = [
        "requests",
        "yfinance", 
        "pandas",
        "fastmcp",
        "fastapi",
        "mcp[cli]",
        "langchain-mcp",
        "langchain-groq",
        "openai",
        "gradio~=5.27.0",
        "akshare",
    ]
    
    for package in other_packages:
        if not run_command(f"pip install {package}"):
            print(f"⚠️ 警告: {package} 安装失败")
    
    # 4. 验证安装
    print("\n4. 验证安装...")
    try:
        import langchain
        import langchain_core
        from langchain.agents.openai_tools import create_openai_tools_agent
        print("✅ langchain 导入成功")
    except ImportError as e:
        print(f"❌ langchain 导入失败: {e}")
        return False
    
    print("\n🎉 依赖安装完成！")
    print("=" * 50)
    print("现在可以运行以下命令来测试:")
    print("python simple_stock_dialogue.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 