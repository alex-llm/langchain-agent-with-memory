# 🔧 工具系统模块化指南

## 📋 概述

本指南介绍了新的模块化工具系统的设计、实现和使用方法。新系统提供了更好的组织结构、可维护性和可扩展性。

## 🎯 设计目标

- **模块化**: 将工具按功能分类到不同模块
- **可配置**: 支持灵活的工具选择和配置
- **可扩展**: 易于添加新工具和新类别
- **安全性**: 内置权限管理和审批系统
- **标准化**: 统一的工具接口和配置格式

## 🏗️ 系统架构

```
tools/
├── __init__.py          # 模块公共接口
├── registry.py          # 工具注册系统
├── basic_tools.py       # 基础工具模块
├── advanced_tools.py    # 高级工具模块
├── memory_tools_module.py # 内存管理工具模块
└── mcp_tools.py         # MCP工具模块
```

### 核心组件

1. **ToolRegistry**: 中央工具注册器
2. **BaseToolModule**: 工具模块基类
3. **ToolConfig**: 工具配置数据类
4. **ToolCategory**: 工具类别枚举

## 📂 工具分类

| 类别 | 描述 | 示例工具 |
|------|------|----------|
| `UTILITY` | 基础实用工具 | 计算器、文本分析 |
| `INFORMATION` | 信息获取工具 | 时间、天气、随机事实 |
| `PRODUCTIVITY` | 生产力工具 | 笔记管理 |
| `COMMUNICATION` | 通信工具 | 网络搜索 |
| `MEMORY` | 内存管理工具 | 会话管理、数据导出 |
| `SYSTEM` | 系统工具 | 文件操作 |
| `ENTERTAINMENT` | 娱乐工具 | 随机事实 |
| `MCP` | MCP协议工具 | 外部服务集成 |
| `CUSTOM` | 自定义工具 | 用户定义工具 |

## 🚀 快速开始

### 基础使用

```python
from tools import get_available_tools, ToolRegistry

# 获取所有工具
all_tools = get_available_tools()

# 按类别获取工具
basic_tools = get_available_tools(categories=['utility', 'information'])

# 获取特定工具
specific_tools = get_available_tools(
    enabled_tools=['calculator', 'get_current_time']
)
```

### 高级配置

```python
from tools import ToolRegistry, ToolCategory
from memory_manager import create_memory_manager

# 创建内存管理器
memory_manager = create_memory_manager()

# 创建工具注册器
registry = ToolRegistry(
    memory_manager=memory_manager,
    enable_user_approval=True,
    enabled_categories=[ToolCategory.UTILITY, ToolCategory.MEMORY],
    approval_handler=my_approval_handler
)

# 获取配置的工具
tools = registry.get_tools()
```

## 🔄 迁移指南

### 从现有代码迁移

#### 1. 替换工具创建代码

**旧方式** (`modern_langchain_demo.py`):
```python
def _create_tools(self):
    @tool
    def calculator(expression: str) -> str:
        # 工具实现
    
    @tool
    def get_current_time() -> str:
        # 工具实现
    
    return [calculator, get_current_time, memory_info]
```

**新方式**:
```python
from tools import ToolRegistry

def _create_tools(self):
    registry = ToolRegistry(
        memory_manager=self.memory_manager,
        enabled_categories=['utility', 'information', 'memory']
    )
    return registry.get_tools()
```

#### 2. 更新工具导入

**旧方式**:
```python
from memory_tools import create_basic_memory_info_tool
```

**新方式**:
```python
from tools import ToolRegistry
# 内存工具会自动包含在注册器中
```

#### 3. 配置审批系统

**旧方式**:
```python
def calculator(expression: str) -> str:
    if self.enable_user_approval:
        return self._request_approval(f"Calculate: {expression}", lambda: self._safe_calculate(expression))
    return self._safe_calculate(expression)
```

**新方式**:
```python
# 审批系统内置在工具模块中
registry = ToolRegistry(
    enable_user_approval=True,
    approval_handler=self.approval_handler
)
```

### Streamlit应用迁移

**旧方式** (`streamlit_demo.py`):
```python
def _create_tools(self):
    all_tools = {
        "calculator": calculator,
        "get_current_time": get_current_time,
        # ... 其他工具
    }
    return [all_tools[tool_name] for tool_name in self.enabled_tools]
```

**新方式**:
```python
from tools import ToolRegistry

def _create_tools(self):
    registry = ToolRegistry(
        memory_manager=self.memory_manager,
        enable_user_approval=self.enable_user_approval,
        enabled_tools=self.enabled_tools,
        approval_handler=self._request_approval if self.enable_user_approval else None
    )
    return registry.get_tools()
```

## 🛠️ 工具开发

### 创建新的工具模块

```python
from typing import Dict, List
from langchain_core.tools import tool
from .registry import BaseToolModule, ToolConfig, ToolCategory

class MyToolsModule(BaseToolModule):
    """自定义工具模块"""
    
    def get_tools(self) -> List:
        return [
            self._create_my_tool()
        ]
    
    def get_tool_configs(self) -> Dict[str, ToolConfig]:
        return {
            "my_tool": ToolConfig(
                name="my_tool",
                category=ToolCategory.CUSTOM,
                description="我的自定义工具",
                requires_approval=False,
                risk_level="low",
                example_usage="使用我的工具",
                parameters={"input": "输入参数"},
                tags=["custom", "example"]
            )
        }
    
    def _create_my_tool(self):
        @tool
        def my_tool(input_data: str) -> str:
            """我的自定义工具"""
            return f"处理结果: {input_data}"
        
        return my_tool
```

### 添加到注册器

```python
# 在 registry.py 的 _initialize_modules 方法中添加
from .my_tools import MyToolsModule

modules = [
    ("basic", BasicToolsModule),
    ("advanced", AdvancedToolsModule),
    ("memory", MemoryToolsModule),
    ("mcp", MCPToolsModule),
    ("my_module", MyToolsModule),  # 添加新模块
]
```

## 🔐 安全和权限

### 风险级别

- **low**: 无风险操作（获取时间、文本分析）
- **medium**: 中等风险操作（计算、网络搜索）
- **high**: 高风险操作（文件操作、数据导入）

### 审批系统

```python
def approval_handler(description: str, action):
    """审批处理器示例"""
    # 显示审批请求给用户
    user_approved = show_approval_dialog(description)
    
    if user_approved:
        return action()
    else:
        return "操作被用户拒绝"

registry = ToolRegistry(
    enable_user_approval=True,
    approval_handler=approval_handler
)
```

## 🔌 MCP集成

### 配置MCP服务器

```python
mcp_servers = [
    {
        "name": "file_server",
        "enabled": True,
        "url": "mcp://localhost:8001",
        "description": "文件操作服务器",
        "tools": [
            {
                "name": "read_file",
                "description": "读取文件",
                "requires_approval": True,
                "parameters": {"path": "文件路径"}
            }
        ]
    }
]

registry = ToolRegistry(mcp_servers=mcp_servers)
```

## 📊 工具信息和统计

### 获取工具信息

```python
from tools import get_tool_info

# 获取所有工具信息
tool_info = get_tool_info()

for category, info in tool_info.items():
    print(f"{info['name']}: {info['count']} 个工具")
    for tool_name, config in info['tools'].items():
        print(f"  - {tool_name}: {config['description']}")
```

### 注册器统计

```python
registry = ToolRegistry()
stats = registry.get_statistics()

print(f"总工具数: {stats['total_tools']}")
print(f"已启用: {stats['enabled_tools']}")
print(f"已加载模块: {stats['modules_loaded']}")
```

## 🧪 测试

### 运行示例

```bash
python tools_example.py
```

### 测试工具功能

```python
from tools import ToolRegistry

# 创建测试注册器
registry = ToolRegistry(
    enabled_categories=['utility'],
    enable_user_approval=False
)

# 获取计算器工具
tools = registry.get_tools()
calculator = next(tool for tool in tools if tool.name == 'calculator')

# 测试计算器
result = calculator.invoke({"expression": "2 + 2"})
print(result)  # 应该输出: "Calculation result: 4"
```

## 📈 性能优化

### 延迟加载

工具模块支持延迟加载，只有在实际使用时才初始化：

```python
# 模块只在需要时才加载
registry = ToolRegistry(enabled_categories=['utility'])
tools = registry.get_tools()  # 这时才加载 utility 工具
```

### 缓存机制

工具配置会被缓存以提高性能：

```python
# 第一次调用会初始化
tools1 = registry.get_tools()

# 后续调用使用缓存
tools2 = registry.get_tools()  # 更快
```

## 🔧 调试和故障排除

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.INFO)

# 工具注册器会输出详细的加载信息
registry = ToolRegistry()
```

### 常见问题

1. **工具未找到**: 检查类别配置和工具名称
2. **审批不工作**: 确保设置了 `approval_handler`
3. **MCP工具无法加载**: 检查MCP服务器配置格式
4. **内存工具缺失**: 确保传递了 `memory_manager`

## 🚀 最佳实践

1. **使用类别过滤**: 只加载需要的工具类别
2. **配置审批**: 为高风险工具启用审批
3. **模块化开发**: 将相关工具放在同一模块
4. **标准化配置**: 使用 ToolConfig 提供完整的元数据
5. **测试覆盖**: 为自定义工具编写测试

## 📝 更新日志

### v1.0.0 (当前版本)
- ✅ 初始模块化系统实现
- ✅ 基础工具模块 (计算器、时间、文本分析、笔记)
- ✅ 高级工具模块 (网络搜索、文件操作、天气、随机事实)
- ✅ 内存管理工具模块
- ✅ MCP工具模块
- ✅ 中央注册系统
- ✅ 权限和审批系统
- ✅ 配置和元数据管理

### 计划功能
- 🔄 动态工具热加载
- 🔄 工具性能监控
- 🔄 工具使用统计
- 🔄 自动化测试框架
- 🔄 工具文档生成

## 🤝 贡献指南

欢迎贡献新的工具模块！请遵循以下步骤：

1. 继承 `BaseToolModule` 类
2. 实现 `get_tools()` 和 `get_tool_configs()` 方法
3. 添加适当的工具配置和元数据
4. 编写测试用例
5. 更新文档

## 📞 支持

如有问题或建议，请：
1. 查看示例代码 (`tools_example.py`)
2. 检查现有工具实现
3. 参考本指南的故障排除部分 