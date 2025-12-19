# Sim-Fusion 核心函数详细介绍

## 核心函数分类

### 1. 主要优化函数

#### `sim_fusion(circuit, return_stats=False, verbose=False, fallback=True)`
**作用：** 主要的 sim-fusion 混合优化函数，结合 TKET 预处理和 Qibo fusion 优化

**参数：**
- `circuit` (QiboCircuit): 要优化的量子电路
- `return_stats` (bool): 是否返回详细统计信息，默认 False
- `verbose` (bool): 是否输出优化过程详情，默认 False
- `fallback` (bool): TKET不可用时是否使用回退策略，默认 True

**返回值：**
- 如果 `return_stats=False`：返回优化后的电路
- 如果 `return_stats=True`：返回 `(优化后的电路, SimFusionStats对象)` 元组

**优化流程：**
1. 统计原始电路信息（门数量、深度）
2. **TKET 预处理阶段**（如果可用）：
   - 通过 QASM 将 Qibo 电路转换为 TKET 电路
   - 应用 6 步 TKET 优化序列
   - 通过 QASM 将优化后的 TKET 电路转回 Qibo
3. **Qibo Fusion 优化阶段**：
   - 应用 Qibo 的矩阵融合优化
4. 计算优化统计信息

---

### 2. 快速优化函数

#### `quick_sim_fusion(circuit)`
**作用：** 简化版本的主函数，使用默认参数进行快速优化

**参数：**
- `circuit` (QiboCircuit): 要优化的量子电路

**返回值：**
- 优化后的量子电路

**特点：**
- 调用 `sim_fusion(circuit, return_stats=False, verbose=False, fallback=True)`
- 最简化的接口，适合快速使用

---

### 3. 统计信息函数

#### `sim_fusion_with_stats(circuit, verbose=True)`
**作用：** 带统计信息的优化接口

**参数：**
- `circuit` (QiboCircuit): 要优化的量子电路
- `verbose` (bool): 是否输出详细信息，默认 True

**返回值：**
- `(优化后的电路, SimFusionStats对象)` 元组

**特点：**
- 自动启用详细输出模式
- 返回完整的性能统计数据

---

### 4. 分析函数

#### `analyze_optimization(circuit)`
**作用：** 分析电路的优化潜力，不进行实际优化

**参数：**
- `circuit` (QiboCircuit): 要分析的量子电路

**返回值：**
- 包含分析结果的字典：
  - `basic_stats`: 基本统计信息（门数、深度、量子比特数）
  - `gate_distribution`: 门类型分布统计
  - `optimization_potential`: 优化潜力评估（低/中/高）
  - `suggestions`: 优化建议列表
  - `tket_available`: TKET 是否可用
  - `fallback_available`: 回退机制是否可用

**用途：**
- 在优化前评估电路的优化潜力
- 提供个性化的优化建议
- 帮助用户决定是否值得进行优化

---

### 5. 桥接转换函数

#### `qibo_to_tket_via_qasm(qibo_circuit)`
**作用：** 通过 QASM 将 Qibo 电路转换为 TKET 电路

**参数：**
- `qibo_circuit` (QiboCircuit): Qibo 电路对象

**返回值：**
- `TketCircuit`: TKET 电路对象

**转换流程：**
1. 调用 `qibo_circuit.to_qasm()` 生成 QASM 字符串
2. 使用 `pytket.qasm.circuit_from_qasm_str(qasm_code)` 创建 TKET 电路

#### `tket_to_qibo_via_qasm(tket_circuit)`
**作用：** 通过 QASM 将 TKET 电路转换为 Qibo 电路

**参数：**
- `tket_circuit` (TketCircuit): TKET 电路对象

**返回值：**
- `QiboCircuit`: Qibo 电路对象

**转换流程：**
1. 使用 `pytket.qasm.circuit_to_qasm_str(tket_circuit)` 生成 QASM 字符串
2. 调用 `QiboCircuit.from_qasm(qasm_code)` 创建 Qibo 电路

---

### 6. 统计信息类

#### `SimFusionStats`
**作用：** 详细的优化性能统计信息类

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

---

## 优化方法详解

### TKET 优化序列

Sim-Fusion 使用以下 6 步 TKET 优化策略：

1. **RemoveRedundancies**
   - 移除冗余门操作（如连续的 X 门、恒等操作）
   - 消除明显的门序列优化

2. **CommuteThroughMultis**
   - 通过多量子比特门重组来发现可消除的门对
   - 重新排列门序列以发现优化机会

3. **CliffordSimp**
   - 简化 Clifford 门序列
   - 使用 Clifford 代数进行优化

4. **FullPeepholeOptimise**
   - 深度局部优化（窥视孔优化）
   - 在小的窗口内寻找最优的门序列

5. **SquashTK1**
   - 将单量子比特门合并为 TK1 形式
   - 减少单量子比特门的数量

6. **RemoveRedundancies** (最终清理)
   - 再次移除可能产生的冗余门
   - 确保电路的最优性

### QASM 桥接技术

**为什么使用 QASM 桥接：**
- QASM 是标准的量子电路描述语言
- 避免了复杂的直接框架集成
- 确保兼容性和可移植性
- 支持双向无损转换

**桥接流程：**
```
Qibo Circuit → QASM String → TKET Circuit → TKET Optimization → QASM String → Qibo Circuit
```

### Qibo Fusion 优化

在 TKET 预处理后，应用 Qibo 的融合优化：
- 矩阵级别的运算融合
- 减少矩阵乘法次数
- 优化量子模拟器性能

---

## 使用示例

### 基本使用
```python
from qibo import Circuit, gates
from sim_fusion import sim_fusion

# 创建电路
circuit = Circuit(2)
circuit.add(gates.H(0))
circuit.add(gates.CNOT(0, 1))

# 优化电路
optimized = sim_fusion(circuit)
```

### 带统计信息的优化
```python
from sim_fusion import sim_fusion_with_stats

optimized, stats = sim_fusion_with_stats(circuit)
print(f"门减少: {stats.gate_reduction} ({stats.gate_reduction_percent:.1f}%)")
print(f"优化时间: {stats.total_time:.6f}s")
```

### 电路分析
```python
from sim_fusion import analyze_optimization

analysis = analyze_optimization(circuit)
print(f"优化潜力: {analysis['optimization_potential']}")
print(f"建议: {analysis['suggestions']}")
```

---

## 性能特点

### 优化效果
- **门减少率**: 通常可达到 10-30% 的门数量减少
- **深度优化**: 可能减少电路深度
- **性能提升**: 针对量子模拟器优化

### 时间复杂度
- **TKET 预处理**: O(n²) 其中 n 是门数量
- **QASM 转换**: O(n) 线性时间
- **Qibo Fusion**: O(n) 线性时间

### 内存使用
- 转换过程中会创建中间电路
- 内存使用量约为原电路的 2-3 倍
- 适合中小型电路（< 1000 门）

---

## 错误处理

### SimFusionError
专门为 Sim-Fusion 定义的错误类：
- 提供详细的错误信息
- 包含修复建议
- 区分不同类型的优化错误

### 回退机制
当 TKET 不可用时：
- 自动切换到纯 Qibo fusion 策略
- 警告用户功能受限
- 确保基本功能可用