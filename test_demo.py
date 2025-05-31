"""
Simple test script to verify the demo functionality
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from modern_langchain_demo import ModernMemoryAgent
        print("✅ modern_langchain_demo imported successfully")
        
        from langchain_openai import ChatOpenAI
        print("✅ langchain_openai imported successfully")
        
        from langchain_core.tools import tool
        print("✅ langchain_core.tools imported successfully")
        
        from langchain.agents import create_tool_calling_agent, AgentExecutor
        print("✅ langchain.agents imported successfully")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_env_file():
    """Test if .env file exists and has required keys"""
    print("\n🔧 Testing environment configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("💡 Create a .env file with:")
        print("OPENAI_API_KEY=sk-or-v1-your-openrouter-key")
        print("OPENAI_API_BASE=https://openrouter.ai/api/v1")
        return False
    
    print("✅ .env file found")
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OPENAI_API_KEY is set")
        if api_key.startswith("sk-or-v1"):
            print("✅ Using OpenRouter API key")
        elif api_key.startswith("sk-"):
            print("✅ Using OpenAI API key")
        else:
            print("⚠️  API key format not recognized")
    else:
        print("❌ OPENAI_API_KEY not set")
        return False
    
    api_base = os.getenv("OPENAI_API_BASE")
    if api_base:
        print(f"✅ OPENAI_API_BASE is set: {api_base}")
    else:
        print("ℹ️  OPENAI_API_BASE not set (will use default)")
    
    return True

def test_agent_initialization():
    """Test if the agent can be initialized"""
    print("\n🤖 Testing agent initialization...")
    
    try:
        from modern_langchain_demo import ModernMemoryAgent
        agent = ModernMemoryAgent()
        
        if agent.api_available:
            print("✅ Agent initialized successfully")
            print(f"✅ Tools available: {len(agent.tools)}")
            return True
        else:
            print("❌ Agent initialization failed - API not available")
            return False
            
    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧠 LangChain Agent Demo - Test Suite")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please run: pip install -r requirements.txt")
        return
    
    # Test environment
    if not test_env_file():
        print("\n❌ Environment tests failed. Please check your .env file.")
        return
    
    # Test agent initialization
    if not test_agent_initialization():
        print("\n❌ Agent initialization failed. Please check your API configuration.")
        return
    
    print("\n🎉 All tests passed!")
    print("\n🚀 You can now run the demo:")
    print("   python modern_langchain_demo.py")
    print("\n💡 Or try the Streamlit interface:")
    print("   streamlit run streamlit_demo.py")

if __name__ == "__main__":
    main() 