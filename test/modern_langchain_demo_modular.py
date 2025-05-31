"""
Modern LangChain Agent with Modular Tools Demo

Using the latest LangChain 0.3.x with the new modular tool system.
Features:
- Modern LangChain 0.3.x architecture
- Modular tool system for better organization
- Memory management with conversation history
- Interactive tools with category-based filtering
- OpenRouter API support
- User approval system for sensitive operations
"""

import os
import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Import the new modular tools system
from tools import ToolRegistry, get_available_tools, get_tool_info, ToolCategory
from memory_manager import MemoryManager, create_memory_manager

# Load environment variables
load_dotenv()

class ModularMemoryAgent:
    def __init__(self, 
                 enabled_categories=None, 
                 enabled_tools=None, 
                 enable_user_approval=False,
                 approval_handler=None):
        """Initialize the modern LangChain agent with modular tools"""
        
        # Load API configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
        
        if not self.api_key:
            print("❌ Please set your OPENAI_API_KEY environment variable.")
            print("You can create a .env file with: OPENAI_API_KEY=your_key_here")
            self.api_available = False
            return
        
        print(f"🔗 Using API: {self.api_base}")
        self.api_available = True
        
        # Initialize the LLM with OpenRouter configuration
        self.llm = ChatOpenAI(
            model="qwen/qwen3-32b:free",
            temperature=0.7,
            api_key=self.api_key,
            base_url=self.api_base,
            default_headers={
                "HTTP-Referer": "https://github.com/langchain-ai/langchain",
                "X-Title": "Modern LangChain Agent Demo"
            }
        )
        
        # Setup memory using the memory manager
        self.memory_manager = create_memory_manager(store_type="memory")
        
        # Setup modular tools system
        self.enabled_categories = enabled_categories or ['utility', 'information', 'productivity', 'memory']
        self.enabled_tools = enabled_tools
        self.enable_user_approval = enable_user_approval
        self.approval_handler = approval_handler
        
        # Create tool registry
        self.tool_registry = ToolRegistry(
            memory_manager=self.memory_manager,
            enable_user_approval=self.enable_user_approval,
            enabled_categories=self.enabled_categories,
            enabled_tools=self.enabled_tools,
            approval_handler=self.approval_handler
        )
        
        # Get tools from registry
        self.tools = self.tool_registry.get_tools()
        
        # Setup prompt template
        self.prompt = self._create_prompt_template()
        
        # Create the agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
        
        # Create runnable with chat history
        self.agent_with_chat_history = self.memory_manager.create_runnable_with_history(
            self.agent_executor
        )
        
        print("✅ Modern LangChain agent with modular tools initialized successfully!")
        print(f"🔧 Loaded {len(self.tools)} tools from {len(self.enabled_categories)} categories")
    
    def _create_prompt_template(self):
        """Create the prompt template with tool information"""
        # Get tool information for the prompt
        tool_info = self.tool_registry.get_tool_info()
        
        tools_text = "Available tool categories:\n"
        for category, info in tool_info.items():
            tools_text += f"- {info['name']}: {info['count']} tools\n"
            for tool_name, tool_config in list(info['tools'].items())[:3]:  # Show first 3 tools
                tools_text += f"  • {tool_name}: {tool_config['description']}\n"
            if info['count'] > 3:
                tools_text += f"  ... and {info['count'] - 3} more tools\n"
        
        approval_note = ""
        if self.enable_user_approval:
            approval_note = "\nNote: Some tools require user approval for security."
        
        return ChatPromptTemplate.from_messages([
            ("system", f"""You are a helpful AI assistant with memory and access to modular tools. 
            You can remember our conversation and use tools to help answer questions.
            
            {tools_text}
            {approval_note}
            
            Always be helpful and use your memory of our conversation when relevant. 
            When appropriate, use the available tools to provide better assistance."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{{input}}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    
    def chat(self, message: str, session_id: str = "default") -> str:
        """Send a message to the agent and get a response"""
        if not self.api_available:
            return "API not available. Please check your configuration."
        
        try:
            response = self.agent_with_chat_history.invoke(
                {"input": message},
                config={"configurable": {"session_id": session_id}},
            )
            return response["output"]
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded tools"""
        return self.tool_registry.get_statistics()
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about available tools"""
        return self.tool_registry.get_tool_info()
    
    def clear_memory(self, session_id: str = "default") -> str:
        """Clear conversation memory"""
        self.memory_manager.clear_session(session_id)
        return "Memory cleared!"
    
    def show_memory(self, session_id: str = "default") -> str:
        """Show conversation memory"""
        session_history = self.memory_manager.get_session_history(session_id)
        stats = self.memory_manager.get_memory_stats(session_id)
        
        if not session_history.messages:
            return "No conversation history yet."
        
        result = f"Conversation History (Session: {session_id}):\n"
        result += f"📊 Stats: {stats.message_count} messages, {stats.total_tokens} tokens, {stats.memory_size_bytes} bytes\n\n"
        
        for i, msg in enumerate(session_history.messages[-10:], 1):  # Show last 10 messages
            if isinstance(msg, HumanMessage):
                role = "You"
            elif isinstance(msg, AIMessage):
                role = "AI"
            else:
                role = "System"
            
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            result += f"{i}. {role}: {content}\n"
        
        return result


def run_modular_demo():
    """Run demo with the new modular tool system"""
    
    print("🧠 Modern LangChain Agent - Modular Tools Demo")
    print("=" * 60)
    print("💡 Testing the new modular tool system!")
    print()
    
    # Define approval handler for demonstration
    def approval_handler(description: str, action):
        print(f"\n🔍 Approval Request: {description}")
        user_input = input("Approve this action? (y/n): ").lower().strip()
        if user_input in ['y', 'yes']:
            print("✅ Approved - executing action...")
            return action()
        else:
            print("❌ Denied - action cancelled")
            return "Action was denied by user"
    
    # Predefined conversation options
    conversation_options = [
        "Hi, my name is Alice and I'm a developer",
        "What time is it?",
        "Calculate 15 * 23", 
        "Take a note: Meeting with team tomorrow at 3 PM",
        "What's my name and what note did I just save?",
        "How many messages do we have in our conversation?",
        "Analyze this text: The quick brown fox jumps over the lazy dog",
        "What do you know about me so far?",
        "Show me my saved notes",
        "What's the weather like in Tokyo?"
    ]
    
    # Initialize agent with specific tool categories
    print("🔧 Initializing agent with modular tools...")
    agent = ModularMemoryAgent(
        enabled_categories=['utility', 'information', 'productivity', 'memory'],
        enable_user_approval=True,
        approval_handler=approval_handler
    )
    
    if not agent.api_available:
        print("\n⚠️  Agent initialization failed. Please check your API configuration.")
        return
    
    # Show tool statistics
    stats = agent.get_tool_statistics()
    print(f"\n📊 Tool Statistics:")
    print(f"  • Total tools: {stats['total_tools']}")
    print(f"  • Enabled tools: {stats['enabled_tools']}")
    print(f"  • Modules loaded: {stats['modules_loaded']}")
    print(f"  • Categories: {', '.join(stats['categories'].keys())}")
    
    session_id = "modular_demo"
    
    while True:
        print("\n" + "="*60)
        print("📋 Conversation Options:")
        for i, option in enumerate(conversation_options, 1):
            print(f"{i:2d}. {option}")
        
        print("\n🔧 Commands:")
        print("11. Show tool information")
        print("12. Show memory")
        print("13. Clear memory")
        print("14. Custom question")
        print("15. Tool statistics")
        print("99. Auto-run first 5 questions")
        print(" 0. Exit")
        
        try:
            choice = input("\n👆 Enter number: ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "11":
                print("\n🔧 Tool Information:")
                tool_info = agent.get_tool_info()
                for category, info in tool_info.items():
                    print(f"\n📂 {info['name']} ({info['count']} tools):")
                    for tool_name, tool_config in info['tools'].items():
                        approval_str = "🔒" if tool_config['requires_approval'] else "✅"
                        print(f"  {approval_str} {tool_name}: {tool_config['description']}")
                continue
            elif choice == "12":
                print("\n🧠 Memory Information:")
                print(agent.show_memory(session_id))
                continue
            elif choice == "13":
                print(agent.clear_memory(session_id))
                continue
            elif choice == "14":
                custom_input = input("Enter your question: ")
                if custom_input.strip():
                    message = custom_input
                else:
                    continue
            elif choice == "15":
                print("\n📊 Tool Statistics:")
                stats = agent.get_tool_statistics()
                for key, value in stats.items():
                    print(f"  • {key}: {value}")
                continue
            elif choice == "99":
                print("\n🚀 Auto-running first 5 questions...")
                for i, question in enumerate(conversation_options[:5], 1):
                    print(f"\n{'='*60}")
                    print(f"Question {i}: {question}")
                    print(f"{'='*60}")
                    response = agent.chat(question, session_id)
                    print(f"🤖 Response: {response}")
                    input("\nPress Enter to continue...")
                continue
            elif choice.isdigit() and 1 <= int(choice) <= len(conversation_options):
                message = conversation_options[int(choice) - 1]
            else:
                print("❌ Invalid choice. Please try again.")
                continue
            
            print(f"\n{'='*60}")
            print(f"You: {message}")
            print(f"{'='*60}")
            
            # Get response from agent
            response = agent.chat(message, session_id)
            print(f"🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def demonstrate_tool_categories():
    """Demonstrate different tool category configurations"""
    print("\n🎯 Tool Categories Demonstration")
    print("=" * 60)
    
    category_configs = [
        {
            "name": "Basic Assistant",
            "categories": ['utility', 'information'],
            "description": "Simple assistant with basic tools"
        },
        {
            "name": "Research Assistant", 
            "categories": ['utility', 'information', 'communication'],
            "description": "Assistant with search capabilities"
        },
        {
            "name": "Productivity Assistant",
            "categories": ['utility', 'productivity', 'memory'],
            "description": "Assistant for productivity tasks"
        },
        {
            "name": "Full-Featured Assistant",
            "categories": ['utility', 'information', 'productivity', 'memory', 'communication'],
            "description": "Assistant with all available tools"
        }
    ]
    
    for config in category_configs:
        print(f"\n📋 {config['name']}")
        print(f"📝 {config['description']}")
        
        try:
            agent = ModularMemoryAgent(
                enabled_categories=config['categories'],
                enable_user_approval=False
            )
            
            if agent.api_available:
                stats = agent.get_tool_statistics()
                print(f"🔧 Tools loaded: {stats['enabled_tools']}")
                print(f"📂 Categories: {', '.join(stats['categories'].keys())}")
            else:
                print("⚠️ API not available")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    """Main demo function"""
    print("🚀 Modern LangChain Agent with Modular Tools")
    print("=" * 60)
    print()
    
    # Show available tool information
    print("📊 Available Tools Overview:")
    try:
        tool_info = get_tool_info()
        total_tools = sum(info['count'] for info in tool_info.values())
        print(f"🔧 Total available tools: {total_tools}")
        print(f"📂 Available categories: {len(tool_info)}")
        
        for category, info in tool_info.items():
            print(f"  • {info['name']}: {info['count']} tools")
    except Exception as e:
        print(f"❌ Error loading tool info: {str(e)}")
    
    print("\n" + "="*60)
    print("Choose demonstration:")
    print("1. Interactive Demo with Modular Tools")
    print("2. Tool Categories Demonstration")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_modular_demo()
    elif choice == "2":
        demonstrate_tool_categories()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main() 