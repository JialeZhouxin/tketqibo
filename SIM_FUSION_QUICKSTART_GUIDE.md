# Sim-Fusion 快速使用指南

## 🚀 5 分钟上手 Sim-Fusion

### 安装依赖
```bash
pip install qibo pytket
```

---

## 基础使用

### 1️⃣ 最简单的用法

```python
from qibo import Circuit, gates
from sim_fusion import sim_fusion

# 创建量子电路
circuit = Circuit(2)
circuit.add(gates.H(0))
circuit.add(gates.CNOT(0, 1))

print(f"原始电路: {circuit.ngates} 个门")

# 一行代码优化
optimized = sim_fusion(circuit)

print(f"优化后: {optimized.ngates} 个门")
```

**输出：**
```
原始电路: 2 个门
优化后: 2 个门
```

---

### 2️⃣ 快速优化接口

```python
from sim_fusion import quick_sim_fusion

# 最简单的调用方式
optimized = quick_sim_fusion(circuit)
```

---

## 进阶使用

### 3️⃣ 带统计信息的优化

```python
from sim_fusion import sim_fusion_with_stats

# 优化并获取详细统计
optimized, stats = sim_fusion_with_stats(circuit)

print(f"门减少: {stats.gate_reduction} ({stats.gate_reduction_percent:.1f}%)")
print(f"优化时间: {stats.total_time:.6f}s")
print(f"TKET时间: {stats.tket_time:.6f}s")
print(f"效率分数: {stats.efficiency_score:.1f}%/s")
```

**输出：**
```
门减少: 0 (0.0%)
优化时间: 0.201881s
TKET时间: 0.201881s
效率分数: 0.0%/s
```

### 4️⃣ 详细优化过程

```python
# 查看优化过程的详细信息
optimized = sim_fusion(circuit, verbose=True)
```

**输出示例：**
```
开始 sim-fusion 混合优化...
原始电路统计: 2 个门, 深度 0
开始 TKET 预处理...
原始电路统计: 2 个门, 深度 1
应用优化步骤 1/6: RemoveRedundancies
应用优化步骤 2/6: CommuteThroughMultis
应用优化步骤 3/6: CliffordSimp
应用优化步骤 4/6: FullPeepholeOptimise
应用优化步骤 5/6: SquashTK1
应用优化步骤 6/6: RemoveRedundancies
TKET 预处理完成，耗时: 0.2019s
应用 Qibo fusion 优化...
Qibo fusion 完成，耗时: 0.0000s
优化完成!
  最终电路统计: 2 个门, 深度 0
  门减少: 0 (0.0%)
  深度减少: 0 (0.0%)
  TKET预处理时间: 0.2019s
  Qibo融合时间: 0.0000s
  总优化时间: 0.2019s
  优化效率: 0.0%/s
```

---

## 实用示例

### 5️⃣ 优化冗余电路

```python
from qibo import Circuit, gates
from sim_fusion import sim_fusion_with_stats

# 创建包含冗余操作的电路
circuit = Circuit(2)
circuit.add(gates.H(0))
circuit.add(gates.H(0))      # H*H = I，可以被消除
circuit.add(gates.X(1))
circuit.add(gates.X(1))      # X*X = I，可以被消除
circuit.add(gates.CNOT(0, 1))

print(f"原始: {circuit.ngates} 个门 (包含冗余操作)")

optimized, stats = sim_fusion_with_stats(circuit)
print(f"优化后: {optimized.ngates} 个门")
print(f"减少: {stats.gate_reduction} 个门 ({stats.gate_reduction_percent:.1f}%)")
```

**输出：**
```
原始: 5 个门 (包含冗余操作)
优化后: 1 个门
减少: 4 个门 (80.0%)
```

### 6️⃣ 优化复杂电路

```python
# 创建更复杂的电路
circuit = Circuit(3)
circuit.add(gates.H(0))
circuit.add(gates.CNOT(0, 1))
circuit.add(gates.RX(0.5, 1))
circuit.add(gates.CNOT(1, 2))
circuit.add(gates.H(2))
circuit.add(gates.RY(0.3, 2))
circuit.add(gates.CNOT(2, 0))

optimized, stats = sim_fusion_with_stats(circuit, verbose=True)
```

### 7️⃣ 电路分析

```python
from sim_fusion import analyze_optimization

# 在优化前分析电路
analysis = analyze_optimization(circuit)

print(f"电路统计: {analysis['basic_stats']}")
print(f"门分布: {analysis['gate_distribution']}")
print(f"优化潜力: {analysis['optimization_potential']}")
print(f"建议: {analysis['suggestions']}")
```

**输出：**
```
电路统计: {'gates': 7, 'depth': 0, 'qubits': 3}
门分布: {'H': 2, 'CNOT': 3, 'RX': 1, 'RY': 1}
优化潜力: 中等
建议: ['电路较小，优化效果可能有限']
```

---

## 高级功能

### 8️⃣ 错误处理

```python
from sim_fusion import sim_fusion, SimFusionError

try:
    # 正常优化
    optimized = sim_fusion(circuit)
    print("优化成功")
except SimFusionError as e:
    print(f"优化失败: {e}")
    if e.suggestion:
        print(f"建议: {e.suggestion}")
except Exception as e:
    print(f"其他错误: {e}")
```

### 9️⃣ 回退机制

```python
# 禁用回退机制（如果 TKET 不可用会报错）
try:
    optimized = sim_fusion(circuit, fallback=False)
except SimFusionError:
    print("TKET 不可用且回退被禁用")

# 启用回退机制（默认）
optimized = sim_fusion(circuit, fallback=True)  # 最安全
```

---

## 完整工作流示例

### 🔟 完整的优化工作流

```python
from qibo import Circuit, gates
from sim_fusion import sim_fusion, analyze_optimization, SimFusionStats

def optimize_quantum_circuit():
    """完整的量子电路优化工作流"""

    # 1. 创建电路
    print("=== 创建量子电路 ===")
    circuit = Circuit(3)
    circuit.add(gates.H(0))
    circuit.add(gates.H(0))  # 冗余
    circuit.add(gates.CNOT(0, 1))
    circuit.add(gates.RX(0.5, 1))
    circuit.add(gates.RY(0.3, 1))
    circuit.add(gates.X(1))
    circuit.add(gates.CNOT(1, 2))
    circuit.add(gates.H(2))

    print(f"原始电路: {circuit.ngates} 个门, {circuit.nqubits} 个量子比特")

    # 2. 分析优化潜力
    print("\n=== 分析优化潜力 ===")
    analysis = analyze_optimization(circuit)
    print(f"门分布: {analysis['gate_distribution']}")
    print(f"优化潜力: {analysis['optimization_potential']}")
    print(f"建议: {analysis['suggestions']}")

    # 3. 执行优化
    print("\n=== 执行优化 ===")
    try:
        optimized, stats = sim_fusion_with_stats(circuit, verbose=True)

        print(f"\n=== 优化结果 ===")
        print(f"原始门数: {circuit.ngates}")
        print(f"优化后门数: {optimized.ngates}")
        print(f"门减少: {stats.gate_reduction} ({stats.gate_reduction_percent:.1f}%)")
        print(f"总优化时间: {stats.total_time:.6f}s")
        print(f"优化效率: {stats.efficiency_score:.1f}%/s")

        # 4. 验证功能
        print(f"\n=== 功能验证 ===")
        print(f"优化电路类型: {type(optimized)}")
        print(f"量子比特数: {optimized.nqubits}")
        print("优化成功!")

        return optimized, stats

    except Exception as e:
        print(f"优化失败: {e}")
        return None, None

# 运行完整工作流
if __name__ == "__main__":
    optimized_circuit, optimization_stats = optimize_quantum_circuit()
```

---

## 性能测试

### 1️⃣1️⃣ 性能基准测试

```python
import time
from qibo import Circuit, gates
from sim_fusion import sim_fusion_with_stats

def benchmark_circuit_sizes():
    """测试不同规模电路的性能"""

    sizes = [5, 10, 15, 20, 25]

    print("=== 性能基准测试 ===")
    print(f"{'规模':<6} {'原始门数':<8} {'优化后':<8} {'减少率':<8} {'时间(s)':<10}")
    print("-" * 50)

    for size in sizes:
        # 创建随机电路
        circuit = Circuit(3)
        for i in range(size):
            import random
            gate_type = random.choice(['H', 'X', 'CNOT', 'RX', 'RY'])
            if gate_type == 'H':
                circuit.add(gates.H(i % 3))
            elif gate_type == 'X':
                circuit.add(gates.X(i % 3))
            elif gate_type == 'CNOT':
                circuit.add(gates.CNOT(i % 3, (i+1) % 3))
            elif gate_type == 'RX':
                circuit.add(gates.RX(random.random(), i % 3))
            elif gate_type == 'RY':
                circuit.add(gates.RY(random.random(), i % 3))

        # 优化并计时
        start_time = time.time()
        optimized, stats = sim_fusion_with_stats(circuit, verbose=False)
        total_time = time.time() - start_time

        print(f"{size:<6} {circuit.ngates:<8} {optimized.ngates:<8} "
              f"{stats.gate_reduction_percent:<8.1f} {total_time:<10.6f}")

# 运行基准测试
benchmark_circuit_sizes()
```

---

## 常见问题

### ❓ 常见问题解答

**Q: TKET 不可用怎么办？**
```python
# Sim-Fusion 会自动使用 Qibo fusion 回退策略
# 会显示警告但仍然能工作
optimized = sim_fusion(circuit)  # 自动回退
```

**Q: 如何检查环境是否正确安装？**
```python
import sim_fusion
print(f"QIBO_AVAILABLE: {sim_fusion.QIBO_AVAILABLE}")
print(f"TKET_AVAILABLE: {sim_fusion.TKET_AVAILABLE}")
```

**Q: 优化效果不明显怎么办？**
```python
# 1. 分析电路
analysis = analyze_optimization(circuit)
print(f"优化潜力: {analysis['optimization_potential']}")

# 2. 检查是否包含冗余操作
# 3. 尝试更复杂的电路
# 4. 使用 verbose=True 查看优化过程
```

**Q: 如何处理大电路？**
```python
# 对于大型电路 (> 1000 门)
# 1. 分段处理
# 2. 监控内存使用
# 3. 考虑使用更简单的优化策略
```

---

## 最佳实践

### 💡 优化建议

1. **小电路优化**：对于小于 10 门的电路，优化效果可能有限
2. **冗余检测**：优先优化包含明显冗余操作的电路
3. **批量优化**：对多个相似电路使用相同的优化策略
4. **性能监控**：使用统计信息监控优化效果
5. **错误处理**：始终使用 try-catch 包装优化调用

### 🚀 进阶技巧

```python
# 技巧1: 条件优化
if analysis['optimization_potential'] in ['高', '中等']:
    optimized = sim_fusion(circuit)
else:
    print("电路优化潜力低，跳过优化")

# 技巧2: 性能阈值
if stats.total_time > 1.0:
    print("优化时间较长，考虑使用快速模式")
    optimized = quick_sim_fusion(circuit)

# 技巧3: 结果验证
if optimized.ngates > circuit.ngates:
    print("警告：优化后门数增加，可能需要手动检查")
```

---

## 📚 更多资源

- **详细文档**: `SIM_FUSION_CORE_FUNCTIONS.md`
- **API 参考**: 函数签名和参数说明
- **示例代码**: 查看项目中的 example 文件夹
- **问题反馈**: 在 GitHub 上提交 issue

---

**🎯 快速入门总结：**

1. **导入**: `from sim_fusion import sim_fusion`
2. **创建电路**: 使用 Qibo 创建量子电路
3. **优化调用**: `optimized = sim_fusion(circuit)`
4. **查看结果**: 检查门数减少和性能统计

就这么简单！🚀