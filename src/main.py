#!/usr/bin/env python3
"""
LangChain Agent with Memory - 主入口文件

这是项目的主入口文件，提供统一的访问点来运行项目的各种功能。

功能包括：
- 命令行交互演示
- Web界面启动
- 工具系统演示
- 内存系统演示
- 系统测试
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def show_banner():
    """显示项目横幅"""
    print("=" * 60)
    print("🧠 LangChain Agent with Memory")
    print("=" * 60)
    print("一个基于 LangChain 0.3.x 的现代化智能代理系统")
    print("具有完整的记忆管理和模块化工具架构")
    print("=" * 60)

def show_menu():
    """显示主菜单"""
    print("\n📋 可用功能:")
    print("1. 🎮 运行命令行演示 (数字选择模式)")
    print("2. 🌐 启动 Web 界面 (Streamlit)")
    print("3. 🔧 工具系统演示")
    print("4. 🧠 内存系统演示")
    print("5. 🧪 运行系统测试")
    print("6. 🔍 环境检查")
    print("7. 📚 查看文档")
    print("8. 📊 项目状态概览")
    print("0. 退出")

def run_command_demo():
    """运行命令行演示"""
    print("\n🎮 启动命令行演示...")
    print("=" * 40)
    try:
        subprocess.run([sys.executable, "test/modern_langchain_demo.py"], cwd=project_root)
    except Exception as e:
        print(f"❌ 运行演示失败: {e}")

def start_web_interface():
    """启动 Web 界面"""
    print("\n🌐 启动 Streamlit Web 界面...")
    print("=" * 40)
    print("💡 提示: Web 界面将在浏览器中打开")
    print("   如果没有自动打开，请访问: http://localhost:8501")
    try:
        subprocess.run(["streamlit", "run", "test/streamlit_demo.py"], cwd=project_root)
    except FileNotFoundError:
        print("❌ Streamlit 未安装。请运行: pip install streamlit")
    except Exception as e:
        print(f"❌ 启动 Web 界面失败: {e}")

def run_tools_demo():
    """运行工具系统演示"""
    print("\n🔧 启动工具系统演示...")
    print("=" * 40)
    try:
        subprocess.run([sys.executable, "test/tools_example.py"], cwd=project_root)
    except Exception as e:
        print(f"❌ 运行工具演示失败: {e}")

def run_memory_demo():
    """运行内存系统演示"""
    print("\n🧠 启动内存系统演示...")
    print("=" * 40)
    try:
        subprocess.run([sys.executable, "test/memory_example.py"], cwd=project_root)
    except Exception as e:
        print(f"❌ 运行内存演示失败: {e}")

def run_system_tests():
    """运行系统测试"""
    print("\n🧪 运行系统测试...")
    print("=" * 40)
    
    tests = [
        ("环境检查", "test/test_env.py"),
        ("内存系统测试", "test/test_memory_system.py"),
        ("基础功能测试", "test/test_demo.py")
    ]
    
    for test_name, test_file in tests:
        print(f"\n🔍 运行 {test_name}...")
        try:
            result = subprocess.run([sys.executable, test_file], 
                                 cwd=project_root, 
                                 capture_output=True, 
                                 text=True)
            if result.returncode == 0:
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败: {result.stderr}")
        except Exception as e:
            print(f"❌ 运行 {test_name} 时出错: {e}")

def check_environment():
    """检查环境配置"""
    print("\n🔍 环境检查...")
    print("=" * 40)
    try:
        subprocess.run([sys.executable, "test/test_env.py"], cwd=project_root)
    except Exception as e:
        print(f"❌ 环境检查失败: {e}")

def show_documentation():
    """显示文档信息"""
    print("\n📚 项目文档信息")
    print("=" * 40)
    
    docs = [
        ("项目概览", "README.md"),
        ("完整文档", "docs/README.md"),
        ("文档索引", "docs/INDEX.md"),
        ("工具系统指南", "docs/TOOLS_MODULARIZATION_GUIDE.md"),
        ("内存系统指南", "docs/MEMORY_SYSTEM_GUIDE.md"),
        ("测试和示例", "test/README.md")
    ]
    
    print("📋 可用文档:")
    for i, (name, path) in enumerate(docs, 1):
        file_path = project_root / path
        if file_path.exists():
            print(f"  {i}. {name} - {path}")
        else:
            print(f"  {i}. {name} - {path} (文件不存在)")
    
    print("\n💡 使用方式:")
    print("  cat docs/README.md      # 查看完整文档")
    print("  cat docs/INDEX.md       # 查看文档索引")
    print("  cat test/README.md      # 查看测试说明")

def show_project_overview():
    """显示项目状态概览"""
    print("\n📊 项目状态概览")
    print("=" * 40)
    
    # 检查关键目录和文件
    key_items = [
        ("🔧 工具模块", "tools/"),
        ("🧠 内存模块", "memory/"),
        ("📚 文档目录", "docs/"),
        ("🧪 测试目录", "test/"),
        ("📦 源代码目录", "src/"),
        ("📄 项目配置", "requirements.txt"),
        ("🔑 环境配置", ".env")
    ]
    
    print("📁 项目结构检查:")
    for name, path in key_items:
        file_path = project_root / path
        status = "✅ 存在" if file_path.exists() else "❌ 缺失"
        print(f"  {name}: {status}")
    
    # 统计文件数量
    try:
        docs_count = len(list((project_root / "docs").glob("*.md"))) if (project_root / "docs").exists() else 0
        test_count = len(list((project_root / "test").glob("*.py"))) if (project_root / "test").exists() else 0
        tools_count = len(list((project_root / "tools").glob("*.py"))) if (project_root / "tools").exists() else 0
        memory_count = len(list((project_root / "memory").glob("*.py"))) if (project_root / "memory").exists() else 0
        
        print(f"\n📈 文件统计:")
        print(f"  📚 文档文件: {docs_count} 个")
        print(f"  🧪 测试文件: {test_count} 个")
        print(f"  🔧 工具文件: {tools_count} 个")
        print(f"  🧠 内存文件: {memory_count} 个")
        
    except Exception as e:
        print(f"  ⚠️ 统计文件时出错: {e}")

def run_quick_start():
    """快速开始模式"""
    print("\n🚀 快速开始模式")
    print("=" * 40)
    print("正在检查环境并启动演示...")
    
    # 1. 环境检查
    print("\n1️⃣ 检查环境...")
    try:
        result = subprocess.run([sys.executable, "test/test_env.py"], 
                              cwd=project_root, 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            print("✅ 环境检查通过")
        else:
            print("⚠️ 环境检查有警告，但继续运行")
    except Exception as e:
        print(f"❌ 环境检查失败: {e}")
        return
    
    # 2. 选择启动方式
    print("\n2️⃣ 选择启动方式:")
    print("1. 🎮 命令行演示 (快速)")
    print("2. 🌐 Web 界面 (推荐)")
    
    choice = input("\n请选择 (1-2): ").strip()
    
    if choice == "1":
        run_command_demo()
    elif choice == "2":
        start_web_interface()
    else:
        print("❌ 无效选择")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LangChain Agent with Memory 主入口")
    parser.add_argument("--quick-start", "-q", action="store_true", 
                       help="快速开始模式")
    parser.add_argument("--web", "-w", action="store_true", 
                       help="直接启动 Web 界面")
    parser.add_argument("--demo", "-d", action="store_true", 
                       help="直接运行命令行演示")
    parser.add_argument("--test", "-t", action="store_true", 
                       help="运行系统测试")
    
    args = parser.parse_args()
    
    show_banner()
    
    # 命令行参数处理
    if args.quick_start:
        run_quick_start()
        return
    elif args.web:
        start_web_interface()
        return
    elif args.demo:
        run_command_demo()
        return
    elif args.test:
        run_system_tests()
        return
    
    # 交互式菜单
    while True:
        show_menu()
        
        try:
            choice = input("\n请选择功能 (0-8): ").strip()
            
            if choice == "0":
                print("\n👋 再见！")
                break
            elif choice == "1":
                run_command_demo()
            elif choice == "2":
                start_web_interface()
            elif choice == "3":
                run_tools_demo()
            elif choice == "4":
                run_memory_demo()
            elif choice == "5":
                run_system_tests()
            elif choice == "6":
                check_environment()
            elif choice == "7":
                show_documentation()
            elif choice == "8":
                show_project_overview()
            else:
                print("❌ 无效选择，请输入 0-8 之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
        
        input("\n按 Enter 继续...")

if __name__ == "__main__":
    main() 