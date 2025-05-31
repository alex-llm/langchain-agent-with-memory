# 🧠 LangChain Agent with Memory

一个基于 LangChain 0.3.x 的现代化智能代理系统，具有完整的记忆管理和模块化工具架构。

## 🎯 项目特色

- **🔧 模块化工具系统**: 19+ 个工具，支持 7 个功能类别
- **🧠 智能记忆管理**: 多种存储方式，会话隔离，持久化支持
- **🔒 安全审批机制**: 敏感操作需要用户确认
- **🌐 Web 界面**: Streamlit 支持的交互式界面
- **📱 多种交互方式**: 命令行、Web界面、API等

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加您的 API 密钥
# OPENROUTER_API_KEY=your_api_key_here
```

### 运行演示

#### 🚀 推荐方式（统一入口）
```bash
# 快速开始模式（推荐）
python src/main.py --quick-start

# 直接启动 Web 界面
python src/main.py --web

# 交互式菜单模式
python src/main.py
```

#### 🎯 直接运行方式
```bash
# 命令行演示
python test/modern_langchain_demo.py

# Web 界面演示
streamlit run test/streamlit_demo.py

# 工具系统示例
python test/tools_example.py

# 内存系统示例  
python test/memory_example.py
```

## 📁 项目结构

```
langchain-agent-with-memory/
├── 📦 src/                     # 源代码目录
│   ├── main.py                 # 🚀 项目主入口文件
│   └── README.md               # 源代码说明
├── 📚 docs/                    # 项目文档
│   ├── README.md               # 完整的项目说明
│   ├── INDEX.md                # 文档索引
│   └── *.md                    # 各种指南和说明
├── 🧪 test/                    # 测试和示例
│   ├── README.md               # 测试文件说明
│   ├── *_demo.py              # 演示脚本
│   ├── test_*.py              # 测试文件
│   └── *_example.py           # 学习示例
├── 🔧 tools/                   # 模块化工具系统
│   ├── __init__.py            # 工具注册中心
│   ├── registry.py            # 工具注册器
│   ├── basic_tools.py         # 基础工具
│   ├── advanced_tools.py      # 高级工具
│   └── memory_tools_module.py # 内存工具
├── 🧠 memory/                  # 记忆管理系统
│   ├── __init__.py            # 模块接口
│   ├── manager.py             # 内存管理器
│   └── tools.py               # 内存工具
├── README.md                   # 项目概览
├── memory_manager.py           # 向后兼容包装器
├── memory_tools.py             # 向后兼容包装器
└── requirements.txt            # Python 依赖
```

## 💡 核心功能

### 🔧 模块化工具系统
- **7 个工具类别**: UTILITY, INFORMATION, PRODUCTIVITY, COMMUNICATION, SYSTEM, ENTERTAINMENT, MEMORY
- **19+ 专用工具**: 计算器、时间工具、文本分析、网页搜索等
- **安全控制**: 风险评估和用户审批机制
- **动态加载**: 支持按类别或工具名选择性加载

### 🧠 智能记忆管理
- **多种存储**: 内存存储、文件存储
- **会话隔离**: 独立的对话会话管理
- **统计分析**: 详细的内存使用统计
- **数据导入导出**: JSON 格式的会话数据备份

### 🌐 多种交互方式
- **命令行界面**: 传统终端交互
- **Web 界面**: Streamlit 支持的现代 UI
- **API 集成**: 支持多种 AI 模型提供商

## 📖 详细文档

- **[完整项目文档](docs/README.md)** - 详细的安装、配置和使用指南
- **[文档索引](docs/INDEX.md)** - 所有文档的分类索引
- **[工具系统指南](docs/TOOLS_MODULARIZATION_GUIDE.md)** - 工具系统详细说明
- **[内存系统指南](docs/MEMORY_SYSTEM_GUIDE.md)** - 内存管理详细说明
- **[测试和示例](test/README.md)** - 所有测试文件和示例的说明

## 🧪 测试和示例

```bash
# 环境测试
python test/test_env.py

# 基础功能演示
python test/modern_langchain_demo.py

# 内存系统测试
python test/test_memory_system.py

# 工具系统示例
python test/tools_example.py
```

## 🔧 开发者指南

### 添加新工具
1. 在 `tools/` 目录中创建新的工具模块
2. 在 `tools/registry.py` 中注册新工具
3. 更新相关文档和测试

### 扩展内存系统
1. 在 `memory/` 目录中扩展存储类型
2. 实现 `BaseMemoryStore` 接口
3. 更新内存管理器配置

### 贡献代码
1. Fork 项目并创建分支
2. 添加测试用例
3. 更新相关文档
4. 提交 Pull Request

## 📊 版本信息

- **当前版本**: 2.0.0 (模块化版本)
- **LangChain**: 0.3.x
- **Python**: 3.8+
- **更新历史**: 查看 [docs/VERSION_INFO.md](docs/VERSION_INFO.md)

## 🤝 获取帮助

- **📚 查看文档**: [docs/](docs/) 目录包含详细指南
- **🧪 运行示例**: [test/](test/) 目录包含各种示例
- **🐛 报告问题**: 在 GitHub Issues 中提交问题
- **💡 功能建议**: 查看 [docs/IMPROVEMENTS.md](docs/IMPROVEMENTS.md)

## 📄 许可证

本项目基于 MIT 许可证开源。详见 LICENSE 文件。

---

**💡 开始探索**: 推荐从 `streamlit run test/streamlit_demo.py` 开始体验完整功能！ 