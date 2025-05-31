# 🔄 向后兼容层 (legacy/)

本目录包含项目的向后兼容包装器文件，确保现有代码在模块化重构后仍能正常工作。

## 📁 目录结构

```
src/legacy/
├── memory_manager.py    # 内存管理器向后兼容包装器
├── memory_tools.py      # 内存工具向后兼容包装器
└── README.md            # 本说明文档
```

## 🎯 向后兼容文件说明

### 📦 memory_manager.py
- **用途**: 为原 `memory_manager.py` 导入提供兼容性
- **重定向到**: `memory/` 模块
- **兼容导入**: 
  ```python
  from memory_manager import MemoryManager, create_memory_manager
  ```

### 📦 memory_tools.py
- **用途**: 为原 `memory_tools.py` 导入提供兼容性
- **重定向到**: `memory/` 模块
- **兼容导入**:
  ```python
  from memory_tools import MemoryTools, create_memory_tools
  ```

## 🔧 使用方式

### 新项目（推荐）
```python
# 使用新的模块化导入
from memory import MemoryManager, MemoryTools
from memory import create_memory_manager, create_memory_tools
```

### 现有项目（兼容）
```python
# 使用向后兼容导入（仍然有效）
from memory_manager import MemoryManager, create_memory_manager
from memory_tools import MemoryTools, create_memory_tools
```

## ⚠️ 注意事项

1. **兼容性保证**: 这些文件确保现有代码无需修改即可运行
2. **推荐迁移**: 新代码建议使用 `from memory import ...` 方式
3. **长期支持**: 这些兼容文件将长期维护，确保稳定性
4. **性能影响**: 向后兼容层有轻微的导入开销，但功能完全一致

## 🚀 迁移指南

### 逐步迁移
1. **第一步**: 确保现有代码正常运行（使用兼容层）
2. **第二步**: 逐步将导入语句迁移到新方式
3. **第三步**: 测试确保功能无变化
4. **第四步**: 完成迁移，享受新的模块化优势

### 迁移示例
```python
# 旧方式
from memory_manager import MemoryManager
from memory_tools import MemoryTools

# 新方式
from memory import MemoryManager, MemoryTools
```

## 📞 获取帮助

- **迁移问题**: 查看 `docs/MEMORY_MIGRATION_SUMMARY.md`
- **使用示例**: 运行 `python test/memory_example.py`
- **技术支持**: 查看 `docs/MEMORY_SYSTEM_GUIDE.md`

---

**💡 提示**: 兼容层确保了平滑迁移，您可以按自己的节奏逐步升级到新的模块化架构！ 