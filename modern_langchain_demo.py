"""
Modern LangChain Agent with Memory Demo

Using the latest LangChain 0.3.x with proper modern patterns and OpenRouter support.
Features:
- Modern LangChain 0.3.x architecture
- Memory management with conversation history
- Interactive tools (calculator, time, memory info)
- Number-based conversation flow selection
- OpenRouter API support
"""

import os
import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Import the new memory manager and tools
from memory_manager import MemoryManager, create_memory_manager
from memory_tools import create_basic_memory_info_tool

# Load environment variables
load_dotenv()

class ModernMemoryAgent:
    def __init__(self):
        """Initialize the modern LangChain agent with OpenRouter support"""
        
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
        
        # Setup memory using the new memory manager first
        self.memory_manager = create_memory_manager(store_type="memory")
        
        # Setup tools (now that memory_manager is available)
        self.tools = self._create_tools()
        
        # Setup prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant with memory and access to tools. 
            You can remember our conversation and use tools to help answer questions.
            
            Available tools:
            - calculator: Perform mathematical calculations
            - get_current_time: Get the current date and time
            - memory_info: Get information about conversation memory
            
            Always be helpful and use your memory of our conversation when relevant."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
        
        # Create runnable with chat history
        self.agent_with_chat_history = self.memory_manager.create_runnable_with_history(
            self.agent_executor
        )
        
        print("✅ Modern LangChain agent initialized successfully!")
    
    def _create_tools(self):
        """Create tools for the agent"""
        
        @tool
        def calculator(expression: str) -> str:
            """Calculate mathematical expressions. Input should be a valid mathematical expression."""
            try:
                # Basic safety check
                allowed_chars = set('0123456789+-*/.() ')
                if all(c in allowed_chars for c in expression):
                    result = eval(expression)
                    return f"Calculation result: {result}"
                else:
                    return "Error: Only basic mathematical operations are allowed"
            except Exception as e:
                return f"Calculation error: {str(e)}"
        
        @tool
        def get_current_time() -> str:
            """Get the current date and time."""
            return f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Create memory info tool using the memory manager
        memory_info = create_basic_memory_info_tool(self.memory_manager)
        
        return [calculator, get_current_time, memory_info]
    
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

def run_numbered_demo():
    """Run demo with numbered conversation options"""
    
    print("🧠 Modern LangChain Agent - Number Selection Demo")
    print("=" * 60)
    print("💡 Just enter a number to try the conversation flow!")
    print()
    
    # Predefined conversation options
    conversation_options = [
        "Hi, my name is John and I'm 25 years old",
        "What time is it?",
        "Calculate 15 * 23", 
        "What's my name and age?",
        "What was the result of my calculation?",
        "How many messages do we have?",
        "Calculate 100 / 4",
        "What do you know about me?",
        "What's today's date?",
        "Remember: I like programming"
    ]
    
    # Initialize agent
    agent = ModernMemoryAgent()
    
    if not agent.api_available:
        print("\n⚠️  Agent initialization failed. Please check your API configuration.")
        return
    
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
    """Run the traditional interactive demo"""
    
    print("🧠 Modern LangChain Agent - Traditional Demo")
    print("=" * 60)
    print("Type your questions directly or use commands:")
    print("- 'show memory' to see conversation history")
    print("- 'clear' to clear memory")
    print("- 'quit' to exit")
    print("=" * 60)
    
    # Create agent
    agent = ModernMemoryAgent()
    
    if not agent.api_available:
        print("\n⚠️  Agent initialization failed. Please check your API configuration.")
        return
    
    # Suggested conversation flow
    print("\n💡 Try this conversation flow:")
    print("1. 'Hi, my name is John and I'm 25 years old'")
    print("2. 'What time is it?'")
    print("3. 'Calculate 15 * 23'")
    print("4. 'What's my name and age?'")
    print("5. 'What was the result of my calculation?'")
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
    
    print("🧠 Modern LangChain Agent Demo")
    print("=" * 50)
    print("Choose your demo mode:")
    print("1. 💡 Number Selection Demo (Recommended)")
    print("2. 💬 Traditional Chat Demo")
    print("0. Exit")
    print("-" * 50)
    
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