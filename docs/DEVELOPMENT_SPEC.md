# Development Specification
# 开发规范文档

> 版本: v1.0  
> 日期: 2026-04-13  
> 适用范围: industrial-agent-mcp 项目

---

## 1. 项目结构规范

```
industrial-agent-mcp/
├── .github/
│   └── workflows/          # CI/CD 配置
│       └── ci.yml
├── docs/                   # 文档
│   ├── PRD.md             # 产品需求
│   └── DEVELOPMENT_SPEC.md # 本文件
├── src/
│   └── mcp_server/        # 主代码
│       ├── __init__.py    # 入口
│       ├── models.py      # 数据模型
│       ├── tools/         # 工具实现
│       │   ├── equipment.py
│       │   ├── sop.py
│       │   └── production.py
│       └── connectors/    # 数据源连接
│           ├── mes.py
│           └── erp.py
├── tests/                 # 测试
│   ├── conftest.py
│   └── test_*.py
├── scripts/               # 脚本工具
├── pyproject.toml         # 项目配置
├── README.md              # 项目说明
└── LICENSE                # 许可证
```

---

## 2. 代码规范

### 2.1 Python 规范

- **风格**: PEP 8 + Black (line length: 88)
- **类型**: 强制类型提示，mypy 检查通过
- **文档**: Google Style Docstrings

```python
# Good
def query_equipment(line_id: str, eq_type: EquipmentType) -> EquipmentStatus:
    """Query equipment status with AI diagnostics.
    
    Args:
        line_id: Production line identifier (e.g., "LINE_A01")
        eq_type: Type of equipment (cnc, assembly, etc.)
    
    Returns:
        EquipmentStatus object containing status, alarms, and AI analysis
    
    Raises:
        EquipmentNotFoundError: If equipment doesn't exist
    """
    ...

# Bad
def query_equipment(line_id, eq_type):
    # No type hints
    ...
```

### 2.2 命名规范

| 类型 | 规范 | 示例 |
|-----|------|------|
| 模块 | snake_case | `equipment_monitor.py` |
| 类 | PascalCase | `EquipmentStatus` |
| 函数 | snake_case | `query_equipment()` |
| 常量 | UPPER_SNAKE | `MAX_RETRY_COUNT = 3` |
| 变量 | snake_case | `line_id` |
| 类型别名 | PascalCase | `EquipmentType = Literal["cnc", "assembly"]` |

### 2.3 错误处理

```python
# 使用自定义异常
class IndustrialAgentError(Exception):
    """Base exception for industrial agent."""
    pass

class EquipmentNotFoundError(IndustrialAgentError):
    """Raised when equipment is not found."""
    pass

# 函数内部捕获并转换
try:
    data = mes_db.query(line_id)
except MESConnectionError as e:
    logger.error(f"MES query failed: {e}")
    raise EquipmentNotFoundError(f"Cannot query {line_id}: {e}") from e
```

---

## 3. Git 工作流

### 3.1 分支策略

```
main        # 生产分支，保护
  ↑
develop     # 开发分支
  ↑
feature/*   # 功能分支
bugfix/*    # 修复分支
```

### 3.2 Commit 规范 (Conventional Commits)

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式（不影响代码）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

**示例:**
```
feat(equipment): add temperature anomaly detection

- Implement AI-based temperature threshold analysis
- Add unit tests for high temperature scenarios

Closes #12
```

### 3.3 PR 规范

1. **Title**: `[Type] Brief description`
2. **Description**: 
   - What changed
   - Why changed
   - Test evidence (screenshots/logs)
3. **Review**: 至少 1 人 approve
4. **CI**: 必须通过所有检查

---

## 4. 测试规范

### 4.1 测试结构

```python
# tests/test_equipment.py
import pytest
from mcp_server import query_equipment

class TestEquipmentQuery:
    """Test suite for equipment query functionality."""
    
    def test_query_existing_equipment(self):
        """Should return status for valid equipment."""
        result = query_equipment("LINE_A01", "cnc")
        assert result.status == "running"
    
    def test_query_nonexistent_equipment_raises(self):
        """Should raise EquipmentNotFoundError for invalid ID."""
        with pytest.raises(EquipmentNotFoundError):
            query_equipment("INVALID_ID", "cnc")
    
    @pytest.mark.parametrize("temp,expected", [
        (45, "normal"),
        (85, "warning"),
        (105, "critical"),
    ])
    def test_temperature_classification(self, temp, expected):
        """Should classify temperature correctly."""
        ...
```

### 4.2 覆盖率要求

- 单元测试覆盖率 > 80%
- 核心工具 100% 覆盖
- 集成测试覆盖主要场景

---

## 5. CI/CD 规范

### 5.1 流水线阶段

```yaml
1. Lint (ruff + black)
2. Type Check (mypy)
3. Test (pytest)
4. Coverage (codecov)
5. Build (optional)
```

### 5.2 合并要求

- [ ] CI 全部通过
- [ ] 代码审查通过
- [ ] 无冲突
- [ ] 分支 up-to-date

---

## 6. 文档规范

### 6.1 代码注释

```python
# 单行注释用于解释"为什么"
# Use exponential backoff to avoid overwhelming MES API
sleep(2 ** retry_count)

# 复杂逻辑需要注释
# Algorithm: Calculate OEE based on availability, performance, and quality
# Formula: OEE = Availability × Performance × Quality
```

### 6.2 README 结构

```markdown
# Project Name

[![CI](badge)](link)

> One-line description

## Features
## Installation
## Usage
## API Reference
## Development
## License
```

---

## 7. 安全规范

1. **密钥管理**: 使用环境变量，禁止硬编码
2. **依赖安全**: 定期扫描 `pip-audit`
3. **代码安全**: Bandit 静态扫描
4. **日志脱敏**: 不记录敏感信息

---

## 8. 性能规范

| 指标 | 目标 | 警告阈值 |
|-----|------|---------|
| 响应时间 | < 200ms | > 500ms |
| 内存占用 | < 100MB | > 200MB |
| CPU 使用率 | < 50% | > 80% |

---

## 9. 检查清单

**提交代码前检查:**
- [ ] `ruff check .` 通过
- [ ] `black --check .` 通过
- [ ] `mypy src/` 通过
- [ ] `pytest` 全部通过
- [ ] 新功能有测试覆盖
- [ ] 文档已更新

---

**执行检查命令:**
```bash
# 一键检查
make lint && make test

# 或手动
ruff check .
black --check .
mypy src/
pytest -v
```

---

## 10. 参考资源

- [PEP 8](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [MCP Documentation](https://modelcontextprotocol.io/)
