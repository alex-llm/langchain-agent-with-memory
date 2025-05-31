# 🧪 测试和示例文件目录

本目录包含项目的所有测试文件、演示脚本和示例代码。

## 📋 文件索引

### 🧪 测试文件
- **[test_env.py](test_env.py)** - 环境测试脚本，验证依赖安装
- **[test_memory_system.py](test_memory_system.py)** - 内存系统综合测试
- **[test_demo.py](test_demo.py)** - 基础功能演示测试
- **[test_approval_demo.py](test_approval_demo.py)** - 审批系统演示测试
- **[test_approval_fix.py](test_approval_fix.py)** - 审批系统修复测试
- **[test_multiple_approvals.py](test_multiple_approvals.py)** - 多重审批测试

### 🎮 演示文件
- **[modern_langchain_demo.py](modern_langchain_demo.py)** - 现代 LangChain 代理演示（集成模块化工具）
- **[modern_langchain_demo_modular.py](modern_langchain_demo_modular.py)** - 模块化版本的演示
- **[streamlit_demo.py](streamlit_demo.py)** - Streamlit Web 界面演示
- **[memory_demo.py](memory_demo.py)** - 内存系统专门演示
- **[debug_agent.py](debug_agent.py)** - 代理调试工具

### 📖 示例文件
- **[tools_example.py](tools_example.py)** - 工具系统使用示例
- **[memory_example.py](memory_example.py)** - 内存系统使用示例

### 📄 备份文件
- **[memory_manager_original.py](memory_manager_original.py)** - 原始内存管理器备份
- **[memory_tools_original.py](memory_tools_original.py)** - 原始内存工具备份

## 🚀 快速开始

### 环境测试
```bash
# 验证环境是否正确配置
python test/test_env.py
```

### 基础演示
```bash
# 运行基础功能演示
python test/modern_langchain_demo.py

# 运行 Web 界面演示
streamlit run test/streamlit_demo.py
```

### 系统测试
```bash
# 运行内存系统测试
python test/test_memory_system.py

# 运行审批系统测试
python test/test_approval_demo.py
```

### 学习示例
```bash
# 学习工具系统使用
python test/tools_example.py

# 学习内存系统使用
python test/memory_example.py
```

## 📊 测试分类

### 🔧 单元测试
- `test_env.py` - 环境和依赖测试
- `test_memory_system.py` - 内存系统功能测试
- `test_approval_fix.py` - 审批系统修复验证

### 🎯 集成测试
- `test_demo.py` - 基础集成测试
- `test_approval_demo.py` - 审批系统集成测试
- `test_multiple_approvals.py` - 复杂场景测试

### 🎮 演示程序
- `modern_langchain_demo.py` - 主要演示程序
- `streamlit_demo.py` - Web 界面演示
- `memory_demo.py` - 内存系统演示
- `debug_agent.py` - 调试工具

### 📚 学习示例
- `tools_example.py` - 工具系统学习示例
- `memory_example.py` - 内存系统学习示例

## 🛠️ 开发指南

### 运行测试
1. 确保已安装所有依赖：`pip install -r requirements.txt`
2. 配置环境变量（API 密钥等）
3. 运行具体的测试文件

### 添加新测试
1. 在相应类别下创建新的测试文件
2. 遵循现有的命名约定（`test_*.py`）
3. 更新本 README 文件

### 调试问题
1. 首先运行 `test_env.py` 确认环境正常
2. 使用 `debug_agent.py` 进行问题诊断
3. 查看相关的测试文件了解预期行为

## 📝 注意事项

- 某些测试需要配置 API 密钥才能运行
- Streamlit 演示需要在终端中使用 `streamlit run` 命令
- 备份文件仅用于参考，不建议直接运行
- 测试文件中可能包含示例数据，请不要在生产环境中使用

## 📞 获取帮助

如果测试运行遇到问题：
1. 检查 [docs/](../docs/) 目录中的相关文档
2. 确认环境配置是否正确
3. 查看错误日志和调试信息 