# Sim-Fusion 优化器快速入门指南

## 简介

Sim-Fusion 是一个混合量子电路优化器，结合了 TKET 的优化策略和 Qibo 的门融合技术，能够有效减少量子电路的门数量和深度。

## 安装要求

确保已安装必要的依赖：

```bash
pip install qibo pytket numpy
```

## 基本使用

### 1. 导入模块

```python
from qibo import Circuit, gates
from sim_fusion_optimizer import optimize_with_sim_fusion, quick_optimize
```

### 2. 创建量子电路

```python
# 创建一个简单的贝尔态电路
circuit = Circuit(2)
circuit.add(gates.H(0))        # Hadamard 门
circuit.add(gates.CNOT(0, 1))  # CNOT 门

print(f"原始电路门数: {circuit.ngates}")
```

### 3. 优化电路

#### 方法一：标准优化
```python
optimized = optimize_with_sim_fusion(circuit)
print(f"优化后门数: {optimized.ngates}")
```

#### 方法二：带统计信息
```python
optimized, stats = optimize_with_sim_fusion(circuit, return_stats=True)
print(f"优化效果: {stats.gate_reduction_percent:.1f}%")
print(f"优化时间: {stats.total_time:.3f}s")
```

#### 方法三：快速优化
```python
optimized = quick_optimize(circuit)  # 使用默认参数
```

## 完整示例

```python
from qibo import Circuit, gates
from sim_fusion_optimizer import optimize_with_sim_fusion

def main():
    # 创建一个 3 量子比特的电路
    circuit = Circuit(3)

    # 添加门序列
    circuit.add(gates.H(0))
    circuit.add(gates.CNOT(0, 1))
    circuit.add(gates.RZ(0.5, 1))
    circuit.add(gates.CNOT(1, 2))
    circuit.add(gates.RX(0.3, 2))
    circuit.add(gates.CNOT(0, 2))

    print("=== 优化前 ===")
    print(f"量子比特数: {circuit.nqubits}")
    print(f"门数量: {circuit.ngates}")
    print(f"电路深度: {circuit.depth}")

    # 进行优化
    optimized, stats = optimize_with_sim_fusion(
        circuit,
        return_stats=True,
        verbose=True
    )

    print("\n=== 优化后 ===")
    print(f"量子比特数: {optimized.nqubits}")
    print(f"门数量: {optimized.ngates}")
    print(f"电路深度: {optimized.depth}")

    print("\n=== 优化统计 ===")
    print(f"原始门数: {stats.original_gates}")
    print(f"优化后门数: {stats.optimized_gates}")
    print(f"门减少比例: {stats.gate_reduction_percent:.1f}%")
    print(f"深度减少比例: {stats.depth_reduction_percent:.1f}%")
    print(f"TKET 优化时间: {stats.tket_time:.3f}s")
    print(f"融合优化时间: {stats.fusion_time:.3f}s")
    print(f"总优化时间: {stats.total_time:.3f}s")

if __name__ == "__main__":
    main()
```

## API 参考

### `optimize_with_sim_fusion(circuit, return_stats=False, strategy="sim-fusion", verbose=False)`

**参数：**
- `circuit`: Qibo Circuit 对象，要优化的量子电路
- `return_stats`: bool，是否返回优化统计信息
- `strategy`: str，优化策略（默认为 "sim-fusion"）
- `verbose`: bool，是否输出详细优化信息

**返回值：**
- `optimized_circuit`: 优化后的 Qibo Circuit 对象
- `stats` (可选): SimFusionOptimizationStats 对象，包含优化统计信息

### `quick_optimize(circuit)`

**参数：**
- `circuit`: Qibo Circuit 对象

**返回值：**
- `optimized_circuit`: 优化后的电路

### `optimize_and_analyze(circuit)`

**参数：**
- `circuit`: Qibo Circuit 对象

**返回值：**
- `optimized_circuit`: 优化后的电路
- `analysis`: 优化分析结果

## 常见电路模式

### 1. 贝尔态电路
```python
def create_bell_circuit(n_qubits=2):
    circuit = Circuit(n_qubits)
    circuit.add(gates.H(0))
    for i in range(n_qubits - 1):
        circuit.add(gates.CNOT(i, i + 1))
    return circuit
```

### 2. GHZ 态电路
```python
def create_ghz_circuit(n_qubits=3):
    circuit = Circuit(n_qubits)
    circuit.add(gates.H(0))
    for i in range(1, n_qubits):
        circuit.add(gates.CNOT(0, i))
    return circuit
```

### 3. 随机电路
```python
import numpy as np

def create_random_circuit(n_qubits=3, depth=5):
    circuit = Circuit(n_qubits)
    gate_types = [gates.RX, gates.RY, gates.RZ, gates.H]

    np.random.seed(42)  # 保证可重现性

    for _ in range(depth):
        # 单量子比特门
        for q in range(n_qubits):
            gate_type = np.random.choice(gate_types)
            if gate_type in [gates.RX, gates.RY, gates.RZ]:
                angle = np.random.uniform(0, 2*np.pi)
                circuit.add(gate_type(angle, q))
            else:
                circuit.add(gate_type(q))

        # 双量子比特门
        if n_qubits > 1:
            for _ in range(n_qubits // 2):
                q1, q2 = np.random.choice(n_qubits, 2, replace=False)
                circuit.add(gates.CNOT(q1, q2))

    return circuit
```

## 性能提示

### 1. 电路大小建议
- **小电路** (1-5 量子比特): 优化效果最明显
- **中等电路** (6-10 量子比特): 需要更多时间，但仍有良好效果
- **大电路** (10+ 量子比特): 可能需要较长时间，建议分块处理

### 2. 优化策略
```python
# 对于小电路，可以使用详细输出
optimized, stats = optimize_with_sim_fusion(small_circuit, verbose=True)

# 对于大电路，使用快速优化
optimized = quick_optimize(large_circuit)
```

## 故障排除

### 1. 导入错误
```python
# 确保路径正确
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

### 2. 依赖问题
```bash
# 检查安装
python -c "import qibo, pytket; print('依赖安装成功')"
```

### 3. 电路格式
确保输入是 Qibo Circuit 对象：
```python
# ✅ 正确
circuit = Circuit(2)
# ... 添加门

# ❌ 错误
circuit = some_other_format_circuit
```

## 进阶用法

### 批量优化
```python
def optimize_circuit_batch(circuits):
    results = []
    for i, circuit in enumerate(circuits):
        print(f"优化电路 {i+1}/{len(circuits)}")
        optimized, stats = optimize_with_sim_fusion(circuit, return_stats=True)
        results.append({
            'original': circuit,
            'optimized': optimized,
            'stats': stats
        })
    return results
```

### 自定义评估
```python
def evaluate_optimization(original, optimized):
    gate_reduction = (1 - optimized.ngates/original.ngates) * 100
    depth_reduction = (1 - optimized.depth/original.depth) * 100

    return {
        'gate_reduction_percent': gate_reduction,
        'depth_reduction_percent': depth_reduction,
        'improvement_score': (gate_reduction + depth_reduction) / 2
    }
```

## 下一步

1. **查看测试示例**: `tests/test_sim_fusion_optimizer.py`
2. **阅读详细文档**: `tests/TESTING_GUIDELINES.md`
3. **问题排查**: `tests/TROUBLESHOOTING.md`
4. **运行测试**: `pytest tests/` (需要先安装 pytest)

## 贡献

欢迎提交问题和改进建议！在开始开发前，请先阅读测试指南以确保代码质量。

---

*本指南基于 Sim-Fusion 优化器 v1.0。如有更新，请参考最新文档。*