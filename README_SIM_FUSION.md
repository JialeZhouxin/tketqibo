# Sim-Fusion 独立量子电路优化器

一个完全独立的量子电路优化模块，结合了 TKET 预处理和 Qibo fusion 优化技术，专门针对量子模拟器性能进行优化。

## 特性

- ✅ **完全独立**：仅依赖 qibo 和 pytket，可轻松移植到其他项目
- ✅ **混合优化**：结合 TKET 预处理和 Qibo fusion 的优势
- ✅ **智能回退**：TKET 不可用时自动使用 Qibo fusion 策略
- ✅ **详细统计**：提供完整的优化性能分析
- ✅ **中文文档**：详细的中文注释和文档字符串
- ✅ **类型支持**：完整的类型注解，支持 IDE 智能提示

## 快速开始

### 安装依赖

```bash
pip install qibo pytket
```

### 基本使用

```python
from qibo import Circuit, gates
from sim_fusion import sim_fusion, quick_sim_fusion

# 创建量子电路
circuit = Circuit(2)
circuit.add(gates.H(0))
circuit.add(gates.CNOT(0, 1))
circuit.add(gates.H(1))

print(f"原始电路: {circuit.ngates} 个门")

# 基本优化
optimized = sim_fusion(circuit)
print(f"优化后: {optimized.ngates} 个门")

# 快速优化
quick_optimized = quick_sim_fusion(circuit)
print(f"快速优化后: {quick_optimized.ngates} 个门")
```

### 带统计信息的优化

```python
from sim_fusion import sim_fusion_with_stats

# 带详细统计的优化
optimized, stats = sim_fusion_with_stats(circuit)

print(f"门减少: {stats.gate_reduction} ({stats.gate_reduction_percent:.1f}%)")
print(f"深度减少: {stats.depth_reduction} ({stats.depth_reduction_percent:.1f}%)")
print(f"TKET时间: {stats.tket_time:.4f}s")
print(f"Fusion时间: {stats.fusion_time:.4f}s")
print(f"总时间: {stats.total_time:.4f}s")
print(f"优化效率: {stats.efficiency_score:.1f}%/s")
```

### 详细输出模式

```python
# 查看详细的优化过程
optimized = sim_fusion(circuit, verbose=True)
```

输出示例：
```
开始 sim-fusion 混合优化...
原始电路统计: 3 个门, 深度 2
开始 TKET 预处理...
应用优化步骤 1/6: RemoveRedundancies
应用优化步骤 2/6: CommuteThroughMultis
...
TKET 预处理完成，耗时: 0.0123s
应用 Qibo fusion 优化...
Qibo fusion 完成，耗时: 0.0005s
优化完成!
  最终电路统计: 3 个门, 深度 2
  门减少: 0 (0.0%)
  深度减少: 0 (0.0%)
  TKET预处理时间: 0.0123s
  Qibo融合时间: 0.0005s
  总优化时间: 0.0128s
  优化效率: 0.0%/s
```

## API 参考

### 主要函数

#### `sim_fusion(circuit, return_stats=False, verbose=False, fallback=True)`

主要的优化函数，使用 sim-fusion 混合策略优化量子电路。

**参数：**
- `circuit` (QiboCircuit): 要优化的量子电路
- `return_stats` (bool): 是否返回详细统计信息，默认 False
- `verbose` (bool): 是否输出优化过程详情，默认 False
- `fallback` (bool): TKET 失败时是否使用回退策略，默认 True

**返回：**
- 如果 `return_stats=False`：返回优化后的电路
- 如果 `return_stats=True`：返回 `(优化后的电路, SimFusionStats 对象)` 元组

#### `quick_sim_fusion(circuit)`

快速优化接口，简化版本的主函数。

**参数：**
- `circuit` (QiboCircuit): 要优化的量子电路

**返回：**
- 优化后的量子电路

#### `sim_fusion_with_stats(circuit, verbose=True)`

带统计信息的优化接口。

**参数：**
- `circuit` (QiboCircuit): 要优化的量子电路
- `verbose` (bool): 是否输出详细信息，默认 True

**返回：**
- `(优化后的电路, SimFusionStats 对象)` 元组

#### `analyze_optimization(circuit)`

分析电路的优化潜力，不进行实际优化。

**参数：**
- `circuit` (QiboCircuit): 要分析的量子电路

**返回：**
- 包含分析结果的字典

### 统计信息类

#### `SimFusionStats`

优化统计信息类，包含详细的优化性能指标。

**属性：**
- `original_gates`: 原始电路的门数量
- `optimized_gates`: 优化后电路的门数量
- `gate_reduction`: 门减少数量
- `gate_reduction_percent`: 门减少百分比
- `original_depth`: 原始电路深度
- `optimized_depth`: 优化后电路深度
- `depth_reduction`: 深度减少数量
- `depth_reduction_percent`: 深度减少百分比
- `tket_time`: TKET 预处理时间（秒）
- `fusion_time`: Qibo fusion 时间（秒）
- `total_time`: 总优化时间（秒）
- `efficiency_score`: 优化效率分数（%/秒）

**方法：**
- `to_dict()`: 将统计信息转换为字典格式

## 优化策略

Sim-Fusion 使用以下优化序列：

1. **RemoveRedundancies**: 移除冗余门操作
2. **CommuteThroughMultis**: 通过多量子比特门重组来发现可消除的门对
3. **CliffordSimp**: 简化 Clifford 门序列
4. **FullPeepholeOptimise**: 深度局部优化
5. **SquashTK1**: 将单量子比特门合并为 TK1 形式
6. **RemoveRedundancies**: 最终清理
7. **Qibo Fusion**: 矩阵层面的运算融合

## 错误处理

模块提供完善的错误处理机制：

```python
from sim_fusion import SimFusionError

try:
    optimized = sim_fusion(circuit)
except SimFusionError as e:
    print(f"优化失败: {e}")
    if e.suggestion:
        print(f"建议: {e.suggestion}")
```

常见错误类型：
- 输入不是有效的 Qibo Circuit
- TKET 库不可用（自动回退到 Qibo fusion）
- 电路包含不支持的门类型

## 使用示例

### 1. 不同类型电路的优化

```python
# 贝尔态电路
bell_circuit = Circuit(2)
bell_circuit.add(gates.H(0))
bell_circuit.add(gates.CNOT(0, 1))

# GHZ 态电路
ghz_circuit = Circuit(3)
ghz_circuit.add(gates.H(0))
for i in range(1, 3):
    ghz_circuit.add(gates.CNOT(0, i))

# 随机电路
import numpy as np
random_circuit = Circuit(3)
np.random.seed(42)
for i in range(10):
    q = np.random.randint(0, 3)
    angle = np.random.random() * 2 * np.pi
    random_circuit.add(gates.RX(angle, q))

# 优化不同电路
for name, circuit in [("贝尔态", bell_circuit), ("GHZ态", ghz_circuit), ("随机", random_circuit)]:
    optimized, stats = sim_fusion(circuit, return_stats=True)
    print(f"{name}: {circuit.ngates} -> {optimized.ngates} 门 ({stats.gate_reduction_percent:.1f}% 减少)")
```

### 2. 性能测试

```python
import time

def benchmark_optimization(circuit, n_runs=5):
    """基准测试优化性能。"""
    times = []
    reductions = []

    for i in range(n_runs):
        start_time = time.time()
        optimized, stats = sim_fusion(circuit, return_stats=True)
        end_time = time.time()

        times.append(end_time - start_time)
        reductions.append(stats.gate_reduction_percent)

    avg_time = sum(times) / len(times)
    avg_reduction = sum(reductions) / len(reductions)

    print(f"电路大小: {circuit.ngates} 门")
    print(f"平均优化时间: {avg_time:.4f}s")
    print(f"平均门减少: {avg_reduction:.1f}%")
    print(f"优化效率: {avg_reduction / avg_time:.1f}%/s")

# 运行基准测试
benchmark_optimization(random_circuit)
```

### 3. 电路分析

```python
# 分析电路优化潜力
analysis = analyze_optimization(circuit)

print(f"基本统计: {analysis['basic_stats']}")
print(f"门分布: {analysis['gate_distribution']}")
print(f"优化潜力: {analysis['optimization_potential']}")
print(f"建议: {'; '.join(analysis['suggestions'])}")
```

## 运行测试

```bash
# 运行单元测试
python test_sim_fusion.py

# 运行基础示例
python examples/basic_usage.py

# 运行高级示例
python examples/advanced_usage.py
```

## 性能建议

1. **小电路** (< 10 门): 优化效果可能有限，但速度很快
2. **中等电路** (10-50 门): 最佳优化效果区间
3. **大电路** (> 50 门): 需要更多时间，但优化效果显著

## 兼容性

- **Python**: 3.8+
- **Qibo**: 0.1.9+
- **PyTKET**: 1.0.0+ (可选，用于增强优化)

## 故障排除

### 常见问题

1. **ImportError: No module named 'qibo'**
   ```bash
   pip install qibo
   ```

2. **ImportError: No module named 'pytket'**
   ```bash
   pip install pytket
   ```
   注意：即使没有 pytket，模块仍可使用 Qibo fusion 回退策略

3. **优化效果不明显**
   - 检查电路是否已经是最优的
   - 尝试使用 `verbose=True` 查看优化过程
   - 某些简单电路可能没有优化空间

4. **内存使用过高**
   - 对于非常大的电路，考虑分段处理
   - 使用 `analyze_optimization()` 预估优化潜力

### 调试技巧

```python
# 启用详细输出查看优化过程
optimized = sim_fusion(circuit, verbose=True)

# 分析电路后再优化
analysis = analyze_optimization(circuit)
print(f"建议: {analysis['suggestions']}")

# 检查统计信息
optimized, stats = sim_fusion(circuit, return_stats=True)
print(f"详细统计: {stats.to_dict()}")
```

## 贡献

欢迎贡献代码、报告问题或提出改进建议！

## 许可证

本项目遵循 MIT 许可证。

---

*Sim-Fusion 独立模块 v1.0.0*