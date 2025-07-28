#!/usr/bin/env python3
"""
编译 macOS 桌面应用
将 build_desktop_app.py 编译成 wff.app
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller 安装完成")
    
    # 检查 PyQt6
    try:
        import PyQt6
        print("✅ PyQt6 已安装")
    except ImportError:
        print("❌ PyQt6 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6"], check=True)
        print("✅ PyQt6 安装完成")

def create_spec_file():
    """创建 PyInstaller spec 文件"""
    print("📝 创建 spec 文件...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['build_desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/wff_agent', 'wff_agent'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'wff_agent.agent_client',
        'wff_agent.agent_factory',
        'wff_agent.stock_agents',
        'wff_agent.stock_analysis_workflow',
        'wff_agent.prompts',
        'wff_agent.utils',
        'wff_agent.datasource',
        'wff_agent.agents',
        'wff_agent.workflows',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'asyncio',
        'logging',
        'typing',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='wff',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='wff',
)

app = BUNDLE(
    coll,
    name='wff.app',
    icon=None,
    bundle_identifier='com.wff.investmentanalysis',
    info_plist={
        'CFBundleName': 'WFF Stock Analysis',
        'CFBundleDisplayName': 'WFF 投资分析',
        'CFBundleIdentifier': 'com.wff.investmentanalysis',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
        'NSRequiresAquaSystemAppearance': False,
    },
)
'''
    
    with open('wff.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ spec 文件创建完成")

def build_app():
    """构建应用"""
    print("🔨 开始构建应用...")
    
    # 使用 PyInstaller 构建
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "wff.spec"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=True)
    
    if result.returncode == 0:
        print("✅ 应用构建成功")
    else:
        print("❌ 应用构建失败")
        sys.exit(1)

def verify_app():
    """验证应用"""
    print("🔍 验证应用...")
    
    app_path = Path("dist/wff.app")
    if app_path.exists():
        print(f"✅ 应用已创建: {app_path}")
        
        # 检查应用大小
        app_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
        print(f"📦 应用大小: {app_size / (1024*1024):.1f} MB")
        
        # 检查应用结构
        print("📁 应用结构:")
        for item in app_path.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(app_path)
                print(f"   {rel_path}")
        
        return True
    else:
        print("❌ 应用创建失败")
        return False

def create_installer():
    """创建安装包"""
    print("📦 创建安装包...")
    
    # 创建 DMG 安装包
    dmg_cmd = [
        "hdiutil", "create", "-volname", "WFF Investment Analysis",
        "-srcfolder", "dist/wff.app",
        "-ov", "-format", "UDZO",
        "dist/WFF_Investment_Analysis.dmg"
    ]
    
    try:
        subprocess.run(dmg_cmd, check=True)
        print("✅ DMG 安装包创建成功")
    except subprocess.CalledProcessError:
        print("⚠️  DMG 创建失败，但应用已构建完成")
    except FileNotFoundError:
        print("⚠️  hdiutil 命令不可用，跳过 DMG 创建")

def cleanup():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    
    # 删除 spec 文件
    if os.path.exists('wff.spec'):
        os.remove('wff.spec')
        print("✅ 删除 spec 文件")
    
    # 删除 build 目录
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("✅ 删除 build 目录")
    
    # 删除 __pycache__ 目录
    for pycache in Path('.').rglob('__pycache__'):
        shutil.rmtree(pycache)
    print("✅ 删除 __pycache__ 目录")

def main():
    """主函数"""
    print("🚀 开始编译 macOS 应用...")
    print("=" * 50)
    
    try:
        # 检查依赖
        check_dependencies()
        
        # 创建 spec 文件
        create_spec_file()
        
        # 构建应用
        build_app()
        
        # 验证应用
        if verify_app():
            # 创建安装包
            create_installer()
            
            print("\n🎉 编译完成！")
            print("=" * 50)
            print("📱 应用位置: dist/wff.app")
            print("📦 安装包: dist/WFF_Investment_Analysis.dmg")
            print("💡 双击 wff.app 即可运行应用")
            
        else:
            print("❌ 应用验证失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 用户中断编译")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 编译失败: {e}")
        sys.exit(1)
    finally:
        # 清理临时文件
        cleanup()

if __name__ == "__main__":
    main() 