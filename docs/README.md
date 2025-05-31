# 🧠 Advanced LangChain Agent with Memory Demo

A comprehensive demonstration of LangChain agents with memory using **LangChain 0.3.x**. This project showcases how to build conversational AI agents with advanced features including streaming responses, reasoning visualization, and extensive configuration options.

## 🌟 Key Features

### Core Features
- **Latest LangChain 0.3.x**: Uses modern LangChain patterns and APIs
- **Number-Based Interaction**: Just enter numbers to try conversation flows!
- **OpenRouter Support**: Compatible with OpenRouter API for multiple model access
- **Memory Management**: Persistent conversation history with multiple memory types
- **Interactive Tools**: Calculator, time checker, file operations, web search, and more

### 🆕 Advanced Features
- **🌊 Streaming Responses**: Real-time text generation with typewriter effect
- **🧠 Agent Reasoning Display**: Visualize AI thinking process and tool usage
- **🤖 Multiple Agent Types**: Tool Calling, ReAct, and Structured Chat agents
- **🛡️ User Approval System**: Manual confirmation for sensitive operations
- **🔌 MCP Support**: Model Context Protocol for external service integration
- **📋 Agent Presets**: Pre-configured agents for different use cases
- **💾 Configuration Management**: Export/import agent configurations

### Interface Options
- **Number Selection Demo**: Quick testing with pre-defined options
- **Traditional Chat**: Natural conversation flow
- **Advanced Streamlit Web App**: Full-featured web interface with streaming

## 🆕 What's New in This Version

### Streaming & Reasoning
- **Real-time Streaming**: See AI responses as they're generated
- **Thinking Process**: Watch the agent's step-by-step reasoning
- **Tool Call Visualization**: Monitor tool execution in real-time
- **Debug Mode**: Full transparency into agent decision-making

### Agent Configuration
- **Multiple Agent Types**: Choose between different reasoning approaches
- **Custom System Prompts**: Fully customize agent behavior
- **Security Controls**: User approval for sensitive operations
- **Preset Configurations**: Quick setup for common use cases

### MCP Integration
- **External Services**: Connect to Model Context Protocol servers
- **Dynamic Tools**: Add tools from external sources
- **Extensible Architecture**: Easy integration with custom services

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key or OpenRouter API key

### Installation

1. **Clone or download this repository**

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**:
   
   **Option A: OpenRouter (Recommended)**
   ```bash
   # Create a .env file
   OPENAI_API_KEY=sk-or-v1-your-openrouter-key
   OPENAI_API_BASE=https://openrouter.ai/api/v1
   ```
   
   **Option B: OpenAI Direct**
   ```bash
   # Create a .env file
   OPENAI_API_KEY=sk-your-openai-key-here
   ```

### Running the Demo

#### 🎯 Main Demo (Classic)
```bash
python modern_langchain_demo.py
```

This gives you two options:
1. **💡 Number Selection Demo** - Just enter numbers to try conversation flows!
2. **💬 Traditional Chat Demo** - Type questions directly

#### 🌐 Advanced Streamlit Web Interface (Recommended)
```bash
streamlit run streamlit_demo.py
```

**Features:**
- 🌊 **Streaming responses** with real-time generation
- 🧠 **Agent reasoning display** showing thinking process
- 🤖 **Multiple agent types** (Tool Calling, ReAct, Structured Chat)
- 🔧 **Advanced tool configuration** with approval system
- 🔌 **MCP server integration** for external services
- 📋 **Agent presets** for quick setup

## 🎛️ Advanced Configuration

### Agent Types

#### 🔧 Tool Calling Agent
- **Best for**: Most use cases, reliable tool usage
- **Features**: Direct tool invocation, efficient execution
- **Streaming**: ✅ Supported

#### 🤔 ReAct Agent
- **Best for**: Complex reasoning tasks, debugging
- **Features**: Step-by-step thinking, visible reasoning process
- **Streaming**: ✅ Supported with full reasoning display

#### 💬 Structured Chat Agent
- **Best for**: Conversational interfaces, chat applications
- **Features**: Structured responses, conversation flow
- **Streaming**: ✅ Supported

### Agent Presets

#### 🤖 General Assistant
- **Tools**: Calculator, Time, Notes, Text Analyzer
- **Security**: Standard mode
- **Best for**: General purpose assistance

#### 🔬 Research Agent
- **Tools**: Web Search, Text Analyzer, Notes
- **Security**: User approval required
- **Features**: Step-by-step reasoning display
- **Best for**: Research and analysis tasks

#### 🛡️ Safe Assistant
- **Tools**: Basic tools only
- **Security**: User approval for all actions
- **Best for**: Secure environments

#### ⚙️ System Admin
- **Tools**: File Operations, Calculator, Text Analyzer
- **Security**: User approval required
- **Best for**: System administration tasks

#### 🐛 Debug Agent
- **Tools**: Calculator, Text Analyzer, Time
- **Features**: Full reasoning visibility
- **Best for**: Understanding agent behavior

### Streaming Features

#### 🌊 Real-time Streaming
- **Character-by-character**: See text as it's generated
- **Typewriter effect**: Smooth text appearance
- **Configurable**: Can be enabled/disabled
- **Fallback**: Simulated streaming for non-streaming models

#### 🧠 Reasoning Display
- **Thinking Steps**: See LLM reasoning process
- **Tool Calls**: Monitor tool execution
- **Decision Process**: Understand agent choices
- **Error Handling**: Clear error visualization

### Security Features

#### 🛡️ User Approval System
- **Sensitive Operations**: Manual confirmation required
- **Real-time Approval**: Approve/deny actions as they occur
- **Action Tracking**: Full audit trail
- **Configurable**: Per-tool approval settings

#### 🔒 Safe Tool Execution
- **Input Validation**: Secure parameter checking
- **Sandboxed Operations**: Isolated execution environment
- **Error Recovery**: Graceful failure handling

## 🆕 Enhanced Approval System (v2.0)

### 🎯 Key Improvements

The approval system has been significantly enhanced with a modern, user-friendly interface:

#### ✅ **Enhanced Button Interface**
- **Green Approve Button**: Click to approve and execute operations
- **Red Deny Button**: Click to reject operations
- **Visual Effects**: Gradient colors, hover animations, and shadow effects
- **Responsive Design**: Works on all screen sizes

#### 📊 **Real-time Statistics Panel**
- **Pending**: Shows current pending approvals count
- **Approved**: Displays approved operations count  
- **Denied**: Shows rejected operations count

#### 🚀 **Batch Operations**
- **Approve All**: One-click approval for all pending operations
- **Deny All**: One-click rejection for all pending operations
- **Clear Processed**: Clean up completed approval records

#### 🔍 **Smart Risk Assessment**
Automatic operation analysis with risk level indicators:

- 🟢 **Low Risk**: Mathematical calculations (usually safe)
- 🟡 **Medium Risk**: File operations, web searches (use caution)
- 🟠 **High Risk**: External service calls (careful review needed)
- ⚪ **Unknown Risk**: Unrecognized operation types

#### 💫 **Improved User Experience**
- **Card Layout**: Each approval has its own styled card
- **Color Coding**: Different colors for different states
- **Interactive Help**: Tooltips and guidance for each button
- **Processing History**: Collapsible view of completed approvals

### 🚀 How to Use the Approval System

1. **Enable User Approval** in Agent Configuration
2. **Review Operations** in the "⏳ Pending Approvals" section
3. **Check Risk Level** shown for each operation
4. **Click Approve/Deny** buttons to make decisions
5. **Use Batch Operations** for multiple similar requests
6. **View History** in the expandable processed operations section

### 🧪 Testing the Approval System

Run the approval test demo:
```bash
streamlit run test_approval_demo.py
```

This provides a dedicated interface to test all approval features including:
- Adding different types of test operations
- Testing batch approval functions
- Verifying risk level detection
- Checking approval history functionality

## 💡 Number Selection Demo

The classic feature! Just run the demo and enter numbers:

```
📋 Conversation Options:
 1. Hi, my name is John and I'm 25 years old
 2. What time is it?
 3. Calculate 15 * 23
 4. What's my name and age?
 5. What was the result of my calculation?
 6. How many messages do we have?
 7. Calculate 100 / 4
 8. What do you know about me?
 9. What's today's date?
10. Remember: I like programming

🔧 Commands:
11. Show memory
12. Clear memory
13. Custom question
99. Auto-run first 5 questions
 0. Exit

👆 Enter number: 1
```

## 🎯 Suggested Conversation Flow

Try this sequence to see memory in action:

1. **Enter `1`**: "Hi, my name is John and I'm 25 years old"
2. **Enter `2`**: "What time is it?"
3. **Enter `3`**: "Calculate 15 * 23"
4. **Enter `4`**: "What's my name and age?"
5. **Enter `5`**: "What was the result of my calculation?"

Or just **enter `99`** to auto-run all these questions!

## 🛠️ Available Tools

### Standard Tools

#### 🧮 Calculator
- **Purpose**: Perform mathematical calculations
- **Security**: Requires approval in secure mode
- **Usage**: "Calculate 15 * 23"
- **Safety**: Only allows basic mathematical operations

#### 🕐 Time Checker
- **Purpose**: Get current date and time
- **Security**: No approval required
- **Usage**: "What time is it?"

#### 📝 Note Taker
- **Purpose**: Save and retrieve notes
- **Security**: No approval required
- **Usage**: "Take a note: Buy groceries"

#### 📊 Text Analyzer
- **Purpose**: Analyze text statistics
- **Security**: No approval required
- **Usage**: "Analyze this text: Hello world"

### Advanced Tools

#### 📁 File Operations
- **Purpose**: Read, write, and list files (simulated)
- **Security**: Requires approval
- **Usage**: "Read file: data.txt"
- **Note**: Simulated for demo purposes

#### 🔍 Web Search
- **Purpose**: Search the web for information (simulated)
- **Security**: Requires approval
- **Usage**: "Search for: latest AI news"
- **Note**: Simulated for demo purposes

#### 🌤️ Weather Info
- **Purpose**: Get weather information (simulated)
- **Security**: No approval required
- **Usage**: "What's the weather in Tokyo?"

#### 🎲 Random Fact
- **Purpose**: Get interesting random facts
- **Security**: No approval required
- **Usage**: "Tell me a random fact"

### MCP Tools

#### 🔌 External Services
- **Purpose**: Connect to Model Context Protocol servers
- **Configuration**: JSON-based tool definitions
- **Security**: Configurable approval requirements
- **Usage**: Depends on configured MCP server

## 🔧 Configuration

### OpenRouter Configuration

The demo supports OpenRouter for access to multiple models:

```bash
# .env file
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
OPENAI_API_BASE=https://openrouter.ai/api/v1
```

### Streaming Configuration

```bash
# Enable streaming responses
ENABLE_STREAMING=true

# Show agent reasoning process
SHOW_REASONING=true
```

### MCP Server Configuration

Example MCP server configuration:

```json
{
  "name": "my-service",
  "url": "http://localhost:3000",
  "description": "Custom service integration",
  "enabled": true,
  "tools": [
    {
      "name": "search",
      "description": "Search for information"
    },
    {
      "name": "analyze",
      "description": "Analyze data"
    }
  ]
}
```

### Memory Management

- **Command 11**: Show conversation history
- **Command 12**: Clear memory and start fresh
- **Command 13**: Enter custom questions
- **Command 99**: Auto-run the suggested conversation flow

## 📁 Project Structure

```
langchain-agent-with-memory/
├── requirements.txt              # Python dependencies (LangChain 0.3.x)
├── .env                         # Environment variables (API keys)
├── README.md                    # This file
├── VERSION_INFO.md              # Version history and migration notes
├── modern_langchain_demo.py     # 🌟 Classic demo with number selection
├── streamlit_demo.py           # 🚀 Advanced web interface with streaming
├── test_demo.py                # 🧪 Test script to verify setup
└── __pycache__/                # Python cache files
```

## 🎨 Demo Modes

### 1. Number Selection Demo (Classic)
- **Perfect for**: Quick testing and demonstrations
- **Features**: Pre-defined conversation options, just enter numbers
- **Best for**: First-time users and showcasing memory capabilities

### 2. Traditional Chat Demo
- **Perfect for**: Natural conversation flow
- **Features**: Type questions directly, full conversational experience
- **Best for**: Extended conversations and custom interactions

### 3. Advanced Streamlit Web Interface (Recommended)
- **Perfect for**: Full-featured experience with all advanced capabilities
- **Features**: 
  - 🌊 Streaming responses with real-time generation
  - 🧠 Agent reasoning process visualization
  - 🤖 Multiple agent types and configurations
  - 🔧 Advanced tool management
  - 🔌 MCP server integration
  - 🛡️ Security controls and user approval
  - 📋 Agent presets and configuration management
- **Best for**: Exploring all features and advanced use cases

## 🌊 Streaming Experience

### Real-time Features
- **Live Text Generation**: See responses as they're typed
- **Thinking Process**: Watch the agent reason through problems
- **Tool Execution**: Monitor tool calls in real-time
- **Error Handling**: Immediate feedback on issues

### Reasoning Visualization
- **Step-by-Step**: Clear breakdown of agent thinking
- **Tool Decisions**: See why tools are chosen
- **Input/Output**: Full transparency of tool usage
- **Debug Mode**: Complete execution trace

## 🐛 Troubleshooting

### Common Issues

1. **"Please set your OPENAI_API_KEY"**
   - Make sure your API key is set in the `.env` file
   - Verify the API key is valid and has credits

2. **Import errors**
   - Run `pip install -r requirements.txt`
   - Make sure you're using Python 3.8+
   - Ensure you have the latest LangChain 0.3.x versions

3. **"Rate limit exceeded"**
   - You've hit API rate limits
   - Wait a moment and try again
   - Consider using OpenRouter for better rate limits

4. **Streamlit issues**
   - Make sure Streamlit is installed: `pip install streamlit`
   - Try running with: `python -m streamlit run streamlit_demo.py`

5. **Streaming not working**
   - Check if your model supports streaming
   - Try disabling streaming in settings
   - Verify your API configuration

### Performance Tips

- Use **OpenRouter** for access to multiple models and better pricing
- The **Number Selection Demo** is fastest for testing
- Use **Command 99** to quickly test the full conversation flow
- **Command 12** to clear memory if responses become inconsistent
- Enable **streaming** for better user experience
- Use **ReAct agent** with reasoning display for debugging

## 🔒 Security Notes

- Never commit your API keys to version control
- The calculator tool uses `eval()` with basic safety checks
- In production, implement more robust input validation
- OpenRouter provides additional security and monitoring features
- Use **user approval** for sensitive operations
- MCP servers should be properly secured and validated

## 🆕 LangChain 0.3.x Migration Notes

Key improvements from older versions:

1. **Agent Creation**: Uses `create_tool_calling_agent` instead of deprecated methods
2. **Memory Integration**: Uses `RunnableWithMessageHistory` for better memory management
3. **Tool Definition**: Uses `@tool` decorator for simpler tool creation
4. **Prompt Templates**: Uses `ChatPromptTemplate` with `MessagesPlaceholder`
5. **Streaming Support**: Native streaming capabilities with callback handlers
6. **Better Error Handling**: Improved error messages and recovery
7. **Agent Types**: Support for multiple agent architectures
8. **Callback System**: Enhanced monitoring and debugging capabilities

## 🤝 Contributing

Feel free to:
- Add new conversation options to the number selection demo
- Implement additional tools and MCP integrations
- Improve the streaming and reasoning visualization
- Add support for more LLM providers
- Enhance the user interface and experience
- Contribute new agent presets and configurations

## 📚 Resources

- [LangChain 0.3.x Documentation](https://python.langchain.com/)
- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [LangChain Agent Documentation](https://python.langchain.com/docs/modules/agents/)
- [LangChain Memory Documentation](https://python.langchain.com/docs/modules/memory/)
- [LangChain Streaming Documentation](https://python.langchain.com/docs/modules/model_io/llms/streaming_llm)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## 📄 License

This project is open source and available under the MIT License.

---

**Happy coding! 🚀**

**💡 Pro Tip**: Start with the Advanced Streamlit Interface - run `streamlit run streamlit_demo.py` to experience all the new features including streaming responses and agent reasoning visualization!

# 📚 项目文档目录

本目录包含 LangChain Agent with Memory 项目的所有文档和指南。

## 📋 文档索引

### 🚀 快速开始
- **[README.md](README.md)** - 项目主要说明文档，包含安装和使用指南

### 🛠️ 工具模块化文档
- **[TOOLS_MODULARIZATION_GUIDE.md](TOOLS_MODULARIZATION_GUIDE.md)** - 工具模块化完整指南
- **[TOOLS_MODULARIZATION_SUMMARY.md](TOOLS_MODULARIZATION_SUMMARY.md)** - 工具模块化项目总结
- **[TOOLS_UPDATE.md](TOOLS_UPDATE.md)** - 工具更新日志

### 🧠 记忆系统文档
- **[MEMORY_SYSTEM_GUIDE.md](MEMORY_SYSTEM_GUIDE.md)** - 记忆系统使用指南
- **[MEMORY_MODULARIZATION_SUMMARY.md](MEMORY_MODULARIZATION_SUMMARY.md)** - 记忆模块化总结
- **[MEMORY_MIGRATION_SUMMARY.md](MEMORY_MIGRATION_SUMMARY.md)** - 记忆模块迁移总结

### 🔄 迁移文档
- **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** - 工具模块化迁移总结
- **[README_MIGRATION.md](README_MIGRATION.md)** - 迁移说明文档

### ✅ 审批系统文档
- **[APPROVAL_SYSTEM_GUIDE.md](APPROVAL_SYSTEM_GUIDE.md)** - 审批系统使用指南
- **[APPROVAL_SYSTEM_FIX.md](APPROVAL_SYSTEM_FIX.md)** - 审批系统修复文档
- **[APPROVAL_SYSTEM_FIX_V2.md](APPROVAL_SYSTEM_FIX_V2.md)** - 审批系统修复文档 V2

### 📈 项目改进文档
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - 项目改进建议
- **[VERSION_INFO.md](VERSION_INFO.md)** - 版本信息和更新历史

## 📖 阅读建议

### 新用户
1. 先阅读 [README.md](README.md) 了解项目概况
2. 查看 [TOOLS_MODULARIZATION_GUIDE.md](TOOLS_MODULARIZATION_GUIDE.md) 了解工具系统
3. 阅读 [MEMORY_SYSTEM_GUIDE.md](MEMORY_SYSTEM_GUIDE.md) 了解记忆系统

### 开发者
1. 阅读相关的模块化指南了解系统架构
2. 查看迁移文档了解系统演进历史
3. 参考改进文档了解未来发展方向

### 贡献者
1. 阅读所有相关文档了解项目全貌
2. 查看版本信息了解项目发展历程
3. 参考改进建议了解可以贡献的方向

## 🔄 文档维护

- 所有文档使用 Markdown 格式
- 文档按功能和主题分类组织
- 定期更新文档以反映最新变化
- 新功能开发时同步更新相关文档

## 📞 获取帮助

如果您在阅读文档时遇到问题：
1. 检查是否有相关的FAQ或疑难解答
2. 查看项目的 Issues 页面
3. 参考示例代码和测试文件 