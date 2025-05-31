"""
Modern LangChain Agent with Memory Demo

Using the latest LangChain 0.3.x with modular tools system and OpenRouter support.
Features:
- Modern LangChain 0.3.x architecture
- Modular tool system for better organization and maintainability
- Memory management with conversation history
- Interactive tools (calculator, time, memory info, text analysis, notes)
- Number-based conversation flow selection
- OpenRouter API support
"""

import os
import sys
import datetime
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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

class ModernMemoryAgent:
    def __init__(self, 
                 enabled_categories=None, 
                 enabled_tools=None, 
                 enable_user_approval=False):
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
            model="deepseek/deepseek-chat-v3-0324",
            temperature=0.7,
            api_key=self.api_key,
            base_url=self.api_base,
            default_headers={
                "HTTP-Referer": "https://github.com/langchain-ai/langchain",
                "X-Title": "Modern LangChain Agent Demo"
            }
        )
        
        # Setup memory using the memory manager first
        self.memory_manager = create_memory_manager(store_type="memory")
        
        # Setup modular tools system
        self.enabled_categories = enabled_categories or ['utility', 'information', 'productivity', 'memory']
        self.enabled_tools = enabled_tools
        self.enable_user_approval = enable_user_approval
        
        # Create tool registry and get tools
        self.tool_registry = ToolRegistry(
            memory_manager=self.memory_manager,
            enable_user_approval=self.enable_user_approval,
            enabled_categories=self.enabled_categories,
            enabled_tools=self.enabled_tools
        )
        
        self.tools = self.tool_registry.get_tools()
        
        # Setup prompt template with dynamic tool information
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
        """Create prompt template with dynamic tool information"""
        # Get tool information for the prompt
        tool_info = self.tool_registry.get_tool_info()
        
        tools_text = "Available tool categories:\n"
        for category, info in tool_info.items():
            tools_text += f"- {info['name']}: {info['count']} tools\n"
            # Show a few example tools from each category
            for tool_name, tool_config in list(info['tools'].items())[:3]:
                tools_text += f"  • {tool_name}: {tool_config['description']}\n"
            if info['count'] > 3:
                tools_text += f"  ... and {info['count'] - 3} more tools\n"
        
        approval_note = ""
        if self.enable_user_approval:
            approval_note = "\nNote: Some tools require user approval for security."
        
        return ChatPromptTemplate.from_messages([
            ("system", f"""You are a helpful AI assistant with memory and access to tools. 
            You can remember our conversation and use tools to help answer questions.
            
            {tools_text}
            {approval_note}
            
            Always be helpful and use your memory of our conversation when relevant."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{{input}}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    
    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create session history - delegated to memory manager"""
        return self.memory_manager.get_session_history(session_id)
    
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
    
    def clear_memory(self, session_id: str = "default") -> str:
        """Clear conversation memory"""
        self.memory_manager.clear_session(session_id)
        return "Memory cleared!"
    
    def show_memory(self, session_id: str = "default") -> str:
        """Show conversation memory"""
        session_history = self._get_session_history(session_id)
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
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded tools"""
        return self.tool_registry.get_statistics()
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about available tools"""
        return self.tool_registry.get_tool_info()

def run_numbered_demo():
    """Run demo with numbered conversation options using modular tools"""
    
    print("🧠 Modern LangChain Agent - Modular Tools Demo")
    print("=" * 60)
    print("💡 Now using the new modular tool system!")
    print()
    
    # Enhanced conversation options to showcase more tools
    conversation_options = [
        "Hi, my name is John and I'm 25 years old",
        "What time is it?",
        "Calculate 15 * 23", 
        "Take a note: Meeting with team tomorrow at 3 PM",
        "What's my name and what note did I just save?",
        "How many messages do we have?",
        "Analyze this text: The quick brown fox jumps over the lazy dog",
        "What do you know about me so far?",
        "Show me my saved notes",
        "Remember: I like programming and AI"
    ]
    
    # Initialize agent with modular tools
    agent = ModernMemoryAgent(
        enabled_categories=['utility', 'information', 'productivity', 'memory'],
        enable_user_approval=False  # Disable for demo simplicity
    )
    
    if not agent.api_available:
        print("\n⚠️  Agent initialization failed. Please check your API configuration.")
        return
    
    # Show tool statistics
    stats = agent.get_tool_statistics()
    print(f"📊 Tool Statistics:")
    print(f"  • Total tools: {stats['total_tools']}")
    print(f"  • Enabled tools: {stats['enabled_tools']}")
    print(f"  • Categories: {', '.join(stats['categories'].keys())}")
    print()
    
    session_id = "numbered_demo"
    
    while True:
        print("\n" + "=" * 60)
        print("📋 Conversation Options:")
        print("-" * 25)
        
        # Show numbered options
        for i, option in enumerate(conversation_options, 1):
            print(f"{i:2d}. {option}")
        
        print("\n🔧 Commands:")
        print("-" * 12)
        print("11. Show memory")
        print("12. Clear memory") 
        print("13. Custom question")
        print("14. Show tool information")
        print("15. Tool statistics")
        print("99. Auto-run first 5 questions")
        print(" 0. Exit")
        
        print("=" * 60)
        
        try:
            choice = input("👆 Enter number: ").strip()
            
            if choice == "0":
                print("👋 Thanks for trying the demo!")
                break
            
            elif choice == "11":
                print("\n📝 Memory Status:")
                print("-" * 20)
                result = agent.show_memory(session_id)
                print(result)
                continue
            
            elif choice == "12":
                result = agent.clear_memory(session_id)
                print(f"\n🧹 {result}")
                continue
            
            elif choice == "13":
                custom_input = input("\n💬 Enter your question: ").strip()
                if custom_input:
                    print(f"\n🤖 Processing: '{custom_input}'")
                    print("-" * 50)
                    response = agent.chat(custom_input, session_id)
                    print(f"✅ Response: {response}")
                continue
            
            elif choice == "14":
                print("\n🔧 Tool Information:")
                print("-" * 20)
                tool_info = agent.get_tool_info()
                for category, info in tool_info.items():
                    print(f"\n📂 {info['name']} ({info['count']} tools):")
                    for tool_name, tool_config in info['tools'].items():
                        approval_str = "🔒" if tool_config['requires_approval'] else "✅"
                        print(f"  {approval_str} {tool_name}: {tool_config['description']}")
                continue
            
            elif choice == "15":
                print("\n📊 Tool Statistics:")
                print("-" * 20)
                stats = agent.get_tool_statistics()
                for key, value in stats.items():
                    if isinstance(value, dict):
                        print(f"• {key}:")
                        for sub_key, sub_value in value.items():
                            print(f"    - {sub_key}: {sub_value}")
                    else:
                        print(f"• {key}: {value}")
                continue
            
            elif choice == "99":
                print("\n🚀 Auto-running first 5 questions...")
                print("=" * 50)
                
                for i in range(5):
                    question = conversation_options[i]
                    print(f"\n{i+1}. 🤖 Processing: '{question}'")
                    print("-" * 40)
                    
                    try:
                        response = agent.chat(question, session_id)
                        print(f"✅ Response: {response}")
                    except Exception as e:
                        print(f"❌ Error: {str(e)}")
                
                print(f"\n📝 Final Memory Status:")
                memory_info = agent.show_memory(session_id)
                print(memory_info)
                continue
            
            # Handle numbered choices
            choice_num = int(choice)
            if 1 <= choice_num <= len(conversation_options):
                selected_question = conversation_options[choice_num - 1]
                
                print(f"\n🤖 Processing Question #{choice_num}:")
                print(f"'{selected_question}'")
                print("-" * 50)
                
                try:
                    response = agent.chat(selected_question, session_id)
                    print(f"✅ Response: {response}")
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(conversation_options)} or use commands.")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def run_traditional_demo():
    """Run the traditional interactive demo with modular tools"""
    
    print("🧠 Modern LangChain Agent - Traditional Demo (Modular Tools)")
    print("=" * 60)
    print("Type your questions directly or use commands:")
    print("- 'show memory' to see conversation history")
    print("- 'show tools' to see available tools")
    print("- 'clear' to clear memory")
    print("- 'quit' to exit")
    print("=" * 60)
    
    # Create agent with modular tools
    agent = ModernMemoryAgent(
        enabled_categories=['utility', 'information', 'productivity', 'memory'],
        enable_user_approval=False
    )
    
    if not agent.api_available:
        print("\n⚠️  Agent initialization failed. Please check your API configuration.")
        return
    
    # Show tool statistics
    stats = agent.get_tool_statistics()
    print(f"\n🔧 Loaded {stats['enabled_tools']} tools from {len(stats['categories'])} categories")
    
    # Enhanced conversation flow suggestions
    print("\n💡 Try this enhanced conversation flow:")
    print("1. 'Hi, my name is John and I'm 25 years old'")
    print("2. 'What time is it?'")
    print("3. 'Calculate 15 * 23'")
    print("4. 'Take a note: Buy groceries tomorrow'")
    print("5. 'Analyze this text: Hello world, how are you?'")
    print("6. 'What's my name and what note did I save?'")
    print()
    
    session_id = "traditional_demo"
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                result = agent.clear_memory(session_id)
                print(f"🤖 Agent: {result}")
                continue
            
            if user_input.lower() in ['show memory', 'memory']:
                result = agent.show_memory(session_id)
                print(f"📝 {result}")
                continue
            
            if user_input.lower() in ['show tools', 'tools']:
                print("🔧 Available Tools:")
                tool_info = agent.get_tool_info()
                for category, info in tool_info.items():
                    print(f"\n📂 {info['name']} ({info['count']} tools):")
                    for tool_name, tool_config in info['tools'].items():
                        approval_str = "🔒" if tool_config['requires_approval'] else "✅"
                        print(f"  {approval_str} {tool_name}: {tool_config['description']}")
                continue
            
            if not user_input:
                continue
            
            print("🤖 Agent: ", end="", flush=True)
            response = agent.chat(user_input, session_id)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            break

def main():
    """Main function with demo mode selection"""
    
    print("🧠 Modern LangChain Agent Demo (Modular Tools System)")
    print("=" * 60)
    
    # Show available tools overview
    try:
        from tools import get_tool_info
        tool_info = get_tool_info()
        total_tools = sum(info['count'] for info in tool_info.values())
        print(f"📊 Available Tools: {total_tools} tools across {len(tool_info)} categories")
        for category, info in tool_info.items():
            print(f"  • {info['name']}: {info['count']} tools")
    except Exception as e:
        print(f"⚠️ Could not load tool information: {str(e)}")
    
    print("\n" + "="*60)
    print("Choose your demo mode:")
    print("1. 💡 Number Selection Demo (Recommended)")
    print("2. 💬 Traditional Chat Demo")
    print("0. Exit")
    print("-" * 60)
    
    while True:
        try:
            choice = input("Enter your choice (0-2): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                run_numbered_demo()
                break
            elif choice == "2":
                run_traditional_demo()
                break
            else:
                print("❌ Invalid choice. Please enter 0, 1, or 2.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 