"""
示例：使用模块化工具系统

这个文件展示了如何使用新的模块化工具系统来创建和管理LangChain代理的工具。
"""

import sys
import os
# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 导入模块化工具系统
from tools import ToolRegistry, get_available_tools, get_tool_info, ToolCategory
from memory_manager import create_memory_manager

# 加载环境变量
load_dotenv()


def example_basic_usage():
    """示例：基础使用方法"""
    print("=" * 60)
    print("🔧 示例 1: 基础工具使用")
    print("=" * 60)
    
    # 获取所有可用工具
    all_tools = get_available_tools()
    print(f"📊 总共可用工具: {len(all_tools)}")
    
    # 按类别获取工具
    basic_tools = get_available_tools(categories=['utility', 'information'])
    print(f"📊 基础工具: {len(basic_tools)}")
    
    # 获取特定工具
    specific_tools = get_available_tools(enabled_tools=['calculator', 'get_current_time', 'text_analyzer'])
    print(f"📊 指定工具: {len(specific_tools)}")
    
    print("\n✅ 基础使用示例完成\n")


def example_with_memory():
    """示例：与内存管理器结合使用"""
    print("=" * 60)
    print("🧠 示例 2: 结合内存管理器")
    print("=" * 60)
    
    # 创建内存管理器
    memory_manager = create_memory_manager(store_type="memory")
    
    # 创建工具注册器，包含内存工具
    registry = ToolRegistry(
        memory_manager=memory_manager,
        enabled_categories=['utility', 'information', 'memory', 'productivity']
    )
    
    tools = registry.get_tools()
    print(f"📊 包含内存工具的总数: {len(tools)}")
    
    # 显示工具统计
    stats = registry.get_statistics()
    print(f"📈 工具统计: {stats}")
    
    print("\n✅ 内存管理器结合示例完成\n")


def example_with_approval_system():
    """示例：启用用户审批系统"""
    print("=" * 60)
    print("🛡️ 示例 3: 用户审批系统")
    print("=" * 60)
    
    def approval_handler(description: str, action):
        """模拟审批处理器"""
        print(f"🔍 审批请求: {description}")
        # 在实际应用中，这里会显示UI并等待用户确认
        # 这里我们自动批准演示用
        print("✅ 自动批准 (演示模式)")
        return action()
    
    registry = ToolRegistry(
        enable_user_approval=True,
        approval_handler=approval_handler,
        enabled_categories=['utility', 'system']  # 包含需要审批的工具
    )
    
    tools = registry.get_tools()
    
    # 显示需要审批的工具
    configs = registry.get_tool_configs()
    approval_tools = [name for name, config in configs.items() if config.requires_approval]
    print(f"🔒 需要审批的工具: {approval_tools}")
    
    print("\n✅ 审批系统示例完成\n")


def example_mcp_integration():
    """示例：MCP工具集成"""
    print("=" * 60)
    print("🔌 示例 4: MCP工具集成")
    print("=" * 60)
    
    # MCP服务器配置示例
    mcp_servers = [
        {
            "name": "test_server",
            "enabled": True,
            "url": "mcp://localhost:8001",
            "description": "测试MCP服务器",
            "tools": [
                {
                    "name": "search_tool",
                    "description": "MCP搜索工具",
                    "requires_approval": False,
                    "parameters": {"query": "搜索查询"}
                },
                {
                    "name": "file_tool",
                    "description": "MCP文件工具",
                    "requires_approval": True,
                    "parameters": {"path": "文件路径"}
                }
            ]
        }
    ]
    
    registry = ToolRegistry(
        mcp_servers=mcp_servers,
        enabled_categories=['mcp', 'utility']
    )
    
    tools = registry.get_tools()
    mcp_tools = [tool for tool in tools if tool.name.startswith('mcp_')]
    print(f"🔌 MCP工具数量: {len(mcp_tools)}")
    
    # 显示MCP工具信息
    for tool in mcp_tools:
        print(f"  • {tool.name}: {tool.description}")
    
    print("\n✅ MCP集成示例完成\n")


def example_custom_configuration():
    """示例：自定义配置"""
    print("=" * 60)
    print("⚙️ 示例 5: 自定义配置")
    print("=" * 60)
    
    # 创建具有自定义配置的工具注册器
    registry = ToolRegistry(
        enabled_categories=[ToolCategory.UTILITY, ToolCategory.INFORMATION],
        enabled_tools=['calculator', 'get_current_time', 'text_analyzer', 'weather_info'],
        enable_user_approval=False
    )
    
    # 获取工具信息
    tool_info = registry.get_tool_info()
    
    print("📋 按类别组织的工具信息:")
    for category, info in tool_info.items():
        print(f"\n📂 {info['name']} ({info['count']} 个工具):")
        for tool_name, tool_config in info['tools'].items():
            print(f"  • {tool_name}: {tool_config['description']}")
            print(f"    风险级别: {tool_config['risk_level']}, 需要审批: {tool_config['requires_approval']}")
    
    print("\n✅ 自定义配置示例完成\n")


def example_agent_integration():
    """示例：与LangChain代理集成"""
    print("=" * 60)
    print("🤖 示例 6: LangChain代理集成")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 未设置OPENAI_API_KEY，跳过代理集成示例")
        return
    
    try:
        # 创建内存管理器
        memory_manager = create_memory_manager(store_type="memory")
        
        # 创建工具注册器
        registry = ToolRegistry(
            memory_manager=memory_manager,
            enabled_categories=['utility', 'information', 'productivity'],
            enable_user_approval=False
        )
        
        # 获取工具
        tools = registry.get_tools()
        
        # 创建LLM
        llm = ChatOpenAI(
            model="deepseek/deepseek-chat-v3-0324",
            temperature=0.7,
            api_key=api_key,
            base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
        )
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个有用的AI助手，可以使用各种工具来帮助回答问题。
            
            可用工具类别:
            - 实用工具: 计算器、文本分析等
            - 信息工具: 时间、天气等
            - 生产力工具: 笔记管理等
            
            请根据需要使用这些工具来提供最佳帮助。"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建代理
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        print(f"🤖 代理创建成功，包含 {len(tools)} 个工具")
        
        # 测试代理
        test_input = "当前时间是什么？然后帮我计算 25 * 36"
        print(f"\n📝 测试输入: {test_input}")
        
        try:
            response = agent_executor.invoke({"input": test_input})
            print(f"🤖 代理响应: {response['output']}")
        except Exception as e:
            print(f"⚠️ 代理执行错误: {str(e)}")
        
    except Exception as e:
        print(f"❌ 代理集成示例失败: {str(e)}")
    
    print("\n✅ 代理集成示例完成\n")


def show_tool_overview():
    """显示工具系统概览"""
    print("=" * 60)
    print("📊 工具系统概览")
    print("=" * 60)
    
    # 获取工具信息
    tool_info = get_tool_info()
    
    total_tools = sum(info['count'] for info in tool_info.values())
    print(f"🔧 总工具数量: {total_tools}")
    print(f"📂 工具类别数量: {len(tool_info)}")
    
    print("\n📋 各类别工具详情:")
    for category, info in tool_info.items():
        print(f"\n🗂️ {info['name']} ({info['count']} 个工具)")
        
        for tool_name, tool_config in info['tools'].items():
            approval_str = "🔒需要审批" if tool_config['requires_approval'] else "✅无需审批"
            risk_color = "🔴" if tool_config['risk_level'] == 'high' else "🟡" if tool_config['risk_level'] == 'medium' else "🟢"
            
            print(f"  • {tool_name}")
            print(f"    📝 {tool_config['description']}")
            print(f"    {approval_str} | {risk_color} {tool_config['risk_level']} | 标签: {', '.join(tool_config['tags'])}")
            if tool_config['example_usage']:
                print(f"    💡 示例: {tool_config['example_usage']}")


def main():
    """运行所有示例"""
    print("🚀 模块化工具系统示例演示")
    print("=" * 60)
    
    # 显示工具概览
    show_tool_overview()
    
    # 运行示例
    example_basic_usage()
    example_with_memory()
    example_with_approval_system()
    example_mcp_integration()
    example_custom_configuration()
    example_agent_integration()
    
    print("🎉 所有示例演示完成！")
    print("\n💡 使用建议:")
    print("- 使用 ToolRegistry 类来管理工具")
    print("- 通过类别过滤来选择需要的工具")
    print("- 启用审批系统来提高安全性")
    print("- 集成MCP服务器来扩展功能")
    print("- 结合内存管理器实现持久化对话")


if __name__ == "__main__":
    main() 