#!/usr/bin/env python3
"""
记忆模块使用示例

展示新的模块化记忆系统的使用方法，包括：
- 新的推荐导入方式
- 向后兼容的导入方式
- 基本功能演示
"""

import sys
import os
# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def example_new_modular_way():
    """使用新的模块化方式"""
    print("🆕 新的模块化方式:")
    print("-" * 30)
    
    # 新的推荐导入方式
    from memory import MemoryManager, create_memory_manager
    from memory import MemoryTools, create_memory_tools
    
    # 创建内存管理器
    memory_manager = create_memory_manager(store_type="memory")
    print(f"✅ 创建内存管理器: {type(memory_manager).__name__}")
    
    # 创建内存工具
    memory_tools = MemoryTools(memory_manager)
    tools = memory_tools.get_tools()
    print(f"✅ 创建内存工具: {len(tools)} 个工具")
    
    # 基本操作
    stats = memory_manager.get_memory_stats("demo_session")
    print(f"✅ 获取会话统计: {stats.message_count} 条消息")
    
    return memory_manager, tools

def example_backward_compatible_way():
    """使用向后兼容的方式"""
    print("\n🔄 向后兼容方式:")
    print("-" * 30)
    
    # 旧的导入方式（仍然有效）
    from memory_manager import MemoryManager, create_memory_manager
    from memory_tools import MemoryTools, create_memory_tools
    
    # 创建组件（与之前完全相同）
    memory_manager = create_memory_manager(store_type="memory")
    tools = create_memory_tools(memory_manager)
    
    print(f"✅ 向后兼容创建成功: {len(tools)} 个工具")
    
    return memory_manager, tools

def example_mixed_usage():
    """展示混合使用方式"""
    print("\n🔀 混合使用方式:")
    print("-" * 30)
    
    # 使用新方式创建管理器
    from memory import create_memory_manager
    mm = create_memory_manager()
    
    # 使用旧方式创建工具
    from memory_tools import MemoryTools
    tools = MemoryTools(mm)
    
    print("✅ 新旧方式混合使用成功")
    
    return mm, tools.get_tools()

def demonstrate_functionality(memory_manager, tools):
    """演示基本功能"""
    print("\n🔧 功能演示:")
    print("-" * 30)
    
    # 添加一些测试消息
    from langchain_core.messages import HumanMessage, AIMessage
    
    history = memory_manager.get_session_history("demo")
    history.add_message(HumanMessage(content="Hello, this is a test message"))
    history.add_message(AIMessage(content="Hi! I received your test message."))
    
    # 获取统计信息
    stats = memory_manager.get_memory_stats("demo")
    print(f"📊 会话统计:")
    print(f"  • 消息数量: {stats.message_count}")
    print(f"  • 内存大小: {stats.memory_size_bytes} 字节")
    
    # 获取所有会话
    sessions = memory_manager.get_all_sessions()
    print(f"📋 总会话数: {len(sessions)}")
    
    # 展示可用工具
    print(f"🔧 可用工具:")
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool.name}: {tool.description}")

def main():
    """主函数"""
    print("🧠 记忆模块使用示例")
    print("=" * 50)
    
    # 演示不同的使用方式
    mm1, tools1 = example_new_modular_way()
    mm2, tools2 = example_backward_compatible_way()
    mm3, tools3 = example_mixed_usage()
    
    # 演示功能
    demonstrate_functionality(mm1, tools1)
    
    print("\n" + "=" * 50)
    print("✅ 所有示例运行成功！")
    print("\n💡 建议:")
    print("  • 新项目使用: from memory import ...")
    print("  • 现有项目可继续使用旧的导入方式")
    print("  • 逐步迁移到新的模块化方式")

if __name__ == "__main__":
    main() 