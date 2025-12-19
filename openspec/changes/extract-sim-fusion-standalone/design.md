# Sim-Fusion 独立模块设计

## 架构决策

### 1. 模块独立性

**决策**：创建完全独立的 `sim_fusion.py` 文件，不依赖项目内部其他模块。

**理由**：
- 提高代码重用性，可轻松复制到其他项目
- 减少模块间的耦合度
- 简化依赖管理和部署

**影响**：
- 需要在文件中重新实现一些通用功能
- 代码量会有所增加，但独立性更强

### 2. 依赖策略

**决策**：仅依赖核心第三方库（qibo, pytket），不依赖项目内部模块。

**理由**：
- 这些是量子计算的标准库，用户通常已经安装
- 避免引入额外的依赖复杂性
- 确保模块的可移植性

**影响**：
- 需要直接使用 TKET 和 Qibo 的 API
- 不能复用现有的抽象层

### 3. 接口设计

**决策**：提供多层接口以适应不同使用场景。

**理由**：
- 简单场景下用户希望快速调用
- 复杂场景下用户需要详细控制
- 保持向后兼容性

**接口层次**：
1. `sim_fusion()` - 主要接口，支持所有参数
2. `quick_sim_fusion()` - 简化接口，最常用场景
3. `sim_fusion_with_stats()` - 带统计信息的接口

## 核心组件设计

### 1. SimFusionStats 类

```python
class SimFusionStats:
    """Sim-fusion 优化统计信息"""

    def __init__(self, original, optimized, timings):
        # 基本信息
        self.original_gates = original.ngates
        self.optimized_gates = optimized.ngates
        self.original_depth = getattr(original, 'depth', 0)
        self.optimized_depth = getattr(optimized, 'depth', 0)

        # 时间统计
        self.tket_time = timings.get('tket', 0)
        self.fusion_time = timings.get('fusion', 0)
        self.total_time = timings.get('total', 0)

        # 计算指标
        self.gate_reduction_percent = ...
        self.depth_reduction_percent = ...
```

### 2. 主优化函数

```python
def sim_fusion(circuit: QiboCircuit,
               return_stats: bool = False,
               verbose: bool = False,
               fallback: bool = True) -> Union[QiboCircuit, Tuple[QiboCircuit, SimFusionStats]]:
    """使用 sim-fusion 策略优化量子电路

    Args:
        circuit: 要优化的 Qibo 电路
        return_stats: 是否返回统计信息
        verbose: 是否输出详细信息
        fallback: 是否在 TKET 失败时使用回退策略

    Returns:
        优化后的电路，或 (电路, 统计信息) 元组
    """
```

### 3. TKET 策略定义

```python
# Sim-fusion 使用的 TKET 优化策略序列
SIM_FUSION_PASSES = [
    "RemoveRedundancies",      # 移除冗余门
    "CommuteThroughMultis",    # 门重组
    "CliffordSimp",           # Clifford 简化
    "FullPeepholeOptimise",   # 局部优化
    "SquashTK1",              # 单量子比特门合并
    "RemoveRedundancies"      # 最终清理
]
```

## 实现细节

### 1. TKET 集成

直接使用 pytket 的 PassManager 和编译功能：

```python
from pytket import PassManager
from pytket.passes import (
    RemoveRedundancies,
    CommuteThroughMultis,
    CliffordSimp,
    FullPeepholeOptimise,
    SquashTK1
)
```

### 2. 错误处理策略

1. **TKET 不可用**：回退到纯 Qibo fusion
2. **编译错误**：尝试部分优化策略
3. **类型错误**：提供清晰的错误信息

### 3. 性能考虑

1. **延迟计算**：只在需要时计算深度等信息
2. **内存优化**：避免不必要的电路复制
3. **时间测量**：精确测量各个优化阶段的时间

## 测试策略

### 1. 单元测试

- 测试各种电路类型的优化效果
- 测试错误处理机制
- 测试统计信息的准确性

### 2. 集成测试

- 与现有模块的兼容性测试
- 不同版本的 Qibo/TKET 兼容性测试

### 3. 性能测试

- 对比与原始实现的性能
- 不同规模电路的优化效果

## 文档规范

### 1. 代码注释

- 所有函数使用中文注释
- 关键算法步骤添加详细说明
- 参数和返回值使用类型注解

### 2. 文档字符串

- 使用标准的 docstring 格式
- 提供使用示例
- 说明可能的异常情况

### 3. README

- 独立的使用说明
- 安装和配置指南
- 常见问题解答