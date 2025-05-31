# 🧠 模块化记忆管理系统指南

## 概述

新的模块化记忆管理系统将原本分散在各个文件中的记忆功能集中到专门的模块中，提供了更好的维护性、扩展性和功能性。

## 系统架构

### 核心模块

1. **`memory_manager.py`** - 核心记忆管理模块
   - `MemoryManager` - 主要的记忆管理类
   - `InMemoryStore` - 内存存储后端
   - `FileBasedMemoryStore` - 文件存储后端
   - `MemoryStats` - 记忆统计数据类

2. **`memory_tools.py`** - 记忆相关工具模块
   - `MemoryTools` - 记忆工具集合类
   - 各种记忆管理工具函数

3. **`memory_demo.py`** - 演示脚本
   - 展示新记忆系统的各种功能

## 主要特性

### ✅ 集中化管理
- 所有记忆相关功能集中在专门模块中
- 统一的接口和API设计
- 易于维护和扩展

### ✅ 多种存储后端
- **内存存储** (`InMemoryStore`) - 快速，适合临时使用
- **文件存储** (`FileBasedMemoryStore`) - 持久化，适合长期使用

### ✅ 高级统计分析
- 消息数量统计
- Token 使用量分析
- 内存占用监控
- 时间戳跟踪

### ✅ 会话管理
- 多会话隔离
- 会话清理和优化
- 会话导出/导入
- 批量操作支持

### ✅ 工具集成
- 丰富的记忆管理工具
- 与 LangChain 工具系统无缝集成
- 支持 Agent 直接调用

## 使用方法

### 基本使用

```python
from memory_manager import create_memory_manager

# 创建内存存储的记忆管理器
memory_manager = create_memory_manager(store_type="memory")

# 创建文件存储的记忆管理器
file_memory_manager = create_memory_manager(
    store_type="file",
    storage_dir="my_memory_storage"
)

# 获取会话历史
session_history = memory_manager.get_session_history("my_session")

# 获取记忆统计
stats = memory_manager.get_memory_stats("my_session")
print(f"消息数量: {stats.message_count}")
print(f"Token 数量: {stats.total_tokens}")
print(f"内存大小: {stats.memory_size_bytes} bytes")
```

### 与 Agent 集成

```python
from memory_manager import create_memory_manager
from memory_tools import create_basic_memory_info_tool

class MyAgent:
    def __init__(self):
        # 创建记忆管理器
        self.memory_manager = create_memory_manager(store_type="file")
        
        # 创建带记忆的 Agent
        self.agent_with_chat_history = self.memory_manager.create_runnable_with_history(
            self.agent_executor
        )
        
        # 添加记忆工具
        memory_tool = create_basic_memory_info_tool(self.memory_manager)
        self.tools.append(memory_tool)
```

### 记忆工具使用

```python
from memory_tools import create_memory_tools

# 创建完整的记忆工具集
memory_tools = create_memory_tools(memory_manager)

# 工具包括：
# - get_memory_stats: 获取记忆统计
# - get_all_sessions: 获取所有会话
# - clear_session: 清除会话
# - export_session: 导出会话
# - import_session: 导入会话
# - cleanup_old_sessions: 清理旧会话
# - get_memory_summary: 获取记忆摘要
# - trim_session_messages: 修剪会话消息
```

## API 参考

### MemoryManager

#### 初始化参数
- `store_type`: 存储类型 ("memory" 或 "file")
- `storage_dir`: 文件存储目录 (仅文件存储)
- `max_messages_per_session`: 每个会话最大消息数
- `auto_save`: 是否自动保存 (仅文件存储)

#### 主要方法
- `get_session_history(session_id)`: 获取会话历史
- `clear_session(session_id)`: 清除会话
- `get_memory_stats(session_id)`: 获取记忆统计
- `export_session(session_id, format)`: 导出会话
- `import_session(session_id, data, format)`: 导入会话
- `get_memory_summary()`: 获取总体记忆摘要

### MemoryStats

#### 属性
- `session_id`: 会话ID
- `message_count`: 消息数量
- `total_tokens`: 总Token数
- `first_message_time`: 首次消息时间
- `last_message_time`: 最后消息时间
- `memory_size_bytes`: 内存大小（字节）

## 迁移指南

### 从旧系统迁移

#### 1. 更新导入
```python
# 旧方式
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 新方式
from memory_manager import create_memory_manager
from memory_tools import create_basic_memory_info_tool
# 注意：不再需要导入 ChatMessageHistory，使用内置的 SimpleChatMessageHistory
```

#### 2. 更新初始化
```python
# 旧方式
self.store = {}
self.agent_with_chat_history = RunnableWithMessageHistory(
    self.agent_executor,
    self._get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# 新方式
self.memory_manager = create_memory_manager(store_type="memory")
self.agent_with_chat_history = self.memory_manager.create_runnable_with_history(
    self.agent_executor
)
```

#### 3. 更新记忆操作
```python
# 旧方式
def clear_memory(self, session_id="default"):
    if session_id in self.store:
        self.store[session_id] = ChatMessageHistory()

# 新方式
def clear_memory(self, session_id="default"):
    self.memory_manager.clear_session(session_id)
```

## 配置选项

### 内存存储配置
```python
memory_manager = create_memory_manager(
    store_type="memory",
    max_messages_per_session=1000
)
```

### 文件存储配置
```python
file_memory_manager = create_memory_manager(
    store_type="file",
    storage_dir="custom_memory_dir",
    max_messages_per_session=2000,
    auto_save=True
)
```

## 最佳实践

### 1. 选择合适的存储类型
- **内存存储**: 适合临时会话、测试环境
- **文件存储**: 适合生产环境、需要持久化的场景

### 2. 定期清理
```python
# 清理30天前的旧会话
cleaned_count = memory_manager.cleanup_old_sessions(days_old=30)
```

### 3. 监控内存使用
```python
# 获取内存使用摘要
summary = memory_manager.get_memory_summary()
print(f"总内存使用: {summary['total_memory_bytes']} bytes")
```

### 4. 限制会话大小
```python
# 限制会话最大消息数
memory_manager.trim_session_messages("session_id", max_messages=100)
```

## 故障排除

### 常见问题

#### 1. 文件权限错误
确保应用有权限写入指定的存储目录。

#### 2. 内存使用过高
- 使用文件存储而非内存存储
- 定期清理旧会话
- 限制会话消息数量

#### 3. 导入/导出失败
- 检查数据格式是否正确
- 确保有足够的磁盘空间

## 示例代码

### 完整的 Agent 示例
```python
from memory_manager import create_memory_manager
from memory_tools import create_memory_tools, create_basic_memory_info_tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor

class EnhancedMemoryAgent:
    def __init__(self):
        # 创建记忆管理器
        self.memory_manager = create_memory_manager(
            store_type="file",
            storage_dir="agent_memory"
        )
        
        # 创建 LLM 和基础工具
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        self.tools = self._create_basic_tools()
        
        # 添加记忆工具
        memory_tools = create_memory_tools(self.memory_manager)
        self.tools.extend(memory_tools)
        
        # 创建 Agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)
        
        # 创建带记忆的 Agent
        self.agent_with_chat_history = self.memory_manager.create_runnable_with_history(
            self.agent_executor
        )
    
    def chat(self, message, session_id="default"):
        return self.agent_with_chat_history.invoke(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
        )
```

## 总结

新的模块化记忆管理系统提供了：

1. **更好的组织结构** - 记忆功能集中管理
2. **更强的功能** - 高级统计、导出导入、会话管理
3. **更好的扩展性** - 模块化设计，易于添加新功能
4. **更好的维护性** - 清晰的接口，统一的API
5. **向后兼容** - 可以逐步迁移现有代码

通过使用这个新系统，你可以更好地管理 LangChain Agent 的记忆功能，提高应用的性能和用户体验。 