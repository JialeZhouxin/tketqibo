"""跨框架量子电路优化器使用示例.

这个文件展示了如何使用跨框架量子电路优化器的各种功能和特性。
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# 动态导入依赖
try:
    from qibo import Circuit as QiboCircuit, gates
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False
    QiboCircuit = None
    gates = None

try:
    from qiskit import QuantumCircuit as QiskitCircuit
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None

try:
    from src.cross_framework_interface import (
        optimize_circuit,
        optimize_circuit_with_stats,
        optimize_qasm,
        optimize_qiskit,
        optimize_qibo,
        quick_optimize,
        batch_optimize,
        compare_strategies,
        analyze_circuit,
        load_qasm_file,
        save_optimized_circuit
    )
    INTERFACE_AVAILABLE = True
except ImportError:
    INTERFACE_AVAILABLE = False

try:
    from cross_framework_optimizer import CrossFrameworkOptimizer, OptimizationStrategy
    CROSS_FRAMEWORK_AVAILABLE = True
except ImportError:
    CROSS_FRAMEWORK_AVAILABLE = False


def example_1_basic_usage():
    """示例1: 基本使用方法."""
    print("🔹 示例1: 基本使用方法")
    print("-" * 40)

    if not INTERFACE_AVAILABLE:
        print("❌ 跨框架接口不可用")
        return

    # 从QASM字符串优化电路
    qasm_circuit = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
"""

    print("原始QASM电路:")
    print(qasm_circuit)

    # 快速优化
    optimized = quick_optimize(qasm_circuit)
    print(f"✅ 优化完成: {optimized.ngates} 个门, {optimized.depth()} 深度")
    print()


def example_2_detailed_optimization():
    """示例2: 详细优化信息和统计."""
    print("🔹 示例2: 详细优化信息和统计")
    print("-" * 40)

    if not INTERFACE_AVAILABLE:
        print("❌ 跨框架接口不可用")
        return

    # 创建一个包含冗余操作的电路
    qasm_with_redundancy = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
h q[0];
h q[0];  // 冗余的H门
x q[1];
x q[1];  // 冗余的X门
cx q[0],q[1];
rz(1.57) q[2];
cx q[1],q[2];
"""

    print("原始电路 (包含冗余操作):")
    print(qasm_with_redundancy)

    # 带统计信息的优化
    optimized, stats = optimize_circuit_with_stats(
        qasm_with_redundancy,
        strategy="qiskit_only",
        optimization_level=2
    )

    print("\n📊 优化统计信息:")
    print(f"  输入类型: {stats['input_type']}")
    print(f"  优化策略: {stats['strategy']}")
    print(f"  原始门数: {stats['original_gates']}")
    print(f"  优化后门数: {stats['optimized_gates']}")
    print(f"  门减少: {stats['gate_reduction']} ({stats['gate_reduction_percent']:.1f}%)")
    print(f"  转换时间: {stats['conversion_time']:.4f}s")
    print(f"  优化时间: {stats['optimization_time']:.4f}s")
    print(f"  总时间: {stats['total_time']:.4f}s")
    print()


def example_3_qiskit_circuit_optimization():
    """示例3: Qiskit电路优化."""
    print("🔹 示例3: Qiskit电路优化")
    print("-" * 40)

    if not QISKIT_AVAILABLE:
        print("❌ Qiskit不可用")
        return

    if not INTERFACE_AVAILABLE:
        print("❌ 跨框架接口不可用")
        return

    # 创建Qiskit电路
    qc = QiskitCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.rz(1.57, 2)
    qc.cx(1, 2)
    qc.h(1)
    qc.h(1)  # 冗余操作
    qc.cx(0, 2)

    print(f"Qiskit电路: {len(qc)} 个门, 深度 {qc.depth()}")

    # 优化为Qibo电路
    optimized = optimize_qiskit(qc, strategy="qiskit_only", optimization_level=2)

    print(f"✅ 优化为Qibo电路: {optimized.ngates} 个门, 深度 {optimized.depth()}")
    print()


def example_4_qibo_circuit_optimization():
    """示例4: Qibo电路优化."""
    print("🔹 示例4: Qibo电路优化")
    print("-" * 40)

    if not QIBO_AVAILABLE:
        print("❌ Qibo不可用")
        return

    if not INTERFACE_AVAILABLE:
        print("❌ 跨框架接口不可用")
        return

    # 创建Qibo电路
    qc = QiboCircuit(3)
    qc.add(gates.H(0))
    qc.add(gates.CNOT(0, 1))
    qc.add(gates.RY(0.785, 2))
    qc.add(gates.CNOT(1, 2))
    qc.add(gates.H(1))
    qc.add(gates.H(1))  # 冗余操作
    qc.add(gates.CNOT(0, 2))

    print(f"Qibo电路: {qc.ngates} 个门, 深度 {qc.depth()}")

    # 使用不同策略优化
    strategies = ["none", "sim_fusion", "qiskit_only"]
    for strategy in strategies:
        try:
            optimized = optimize_qibo(qc, strategy=strategy, verbose=False)
            reduction = qc.ngates - optimized.ngates
            print(f"  {strategy}: {qc.ngates} -> {optimized.ngates} 门 (减少 {reduction})")
        except Exception as e:
            print(f"  {strategy}: 错误 - {e}")

    print()


def example_5_batch_optimization():
    """示例5: 批量优化多个电路."""
    print("🔹 示例5: 批量优化多个电路")
    print("-" * 40)

    if not INTERFACE_AVAILABLE:
        print("❌ 跨框架接口不可用")
        return

    # 准备不同类型的电路
    circuits = [
        # Bell态QASM
        """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];""",

        # GHZ态QASM
        """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
h q[0];
cx q[0],q[1];
cx q[0],q[2];""",

        # 简单电路QASM
        """OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
h q[0];""",
    ]

    print(f"批量优化 {len(circuits)} 个电路...")

    # 批量优化
    optimized_circuits = batch_optimize(circuits, strategy="qiskit_only", show_progress=True)

    print("批量优化结果:")
    for i, (original, optimized) in enumerate(zip(circuits, optimized_circuits)):
        if optimized is not None:
            print(f"  电路 {i+1}: 优化成功 -> {optimized.ngates} 个门")
        else:
            print(f"  电路 {i+1}: 优化失败")

    print()


def example_6_strategy_comparison():
    """示例6: 比较不同优化策略."""
    print("🔹 示例6: 比较不同优化策略")
    print("-" * 40)

    if not INTERFACE_AVAILABLE:
        print("❌ 跨框架接口不可用")
        return

    # 创建测试电路
    test_qasm = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
h q[0];
h q[0];  // 冗余
x q[1];
x q[1];  // 冗余
cx q[0],q[1];
rz(1.57) q[2];
cx q[1],q[2];
"""

    print("比较不同优化策略的效果:")
    print("-" * 30)

    # 比较策略
    strategies = ["none", "qiskit_only", "sim_fusion"]
    results = compare_strategies(test_qasm, strategies=strategies)

    for strategy, stats in results.items():
        if 'error' in stats:
            print(f"  {strategy}: ❌ 错误 - {stats['error']}")
        else:
            reduction = stats.get('gate_reduction_percent', 0)
            time_taken = stats.get('total_time', 0)
            print(f"  {strategy}: 门减少 {reduction:.1f}%, 时间 {time_taken:.4f}s")

    print()


def example_7_circuit_analysis():
    """示例7: 电路分析."""
    print("🔹 示例7: 电路分析")
    print("-" * 40)

    if not INTERFACE_AVAILABLE:
        print("❌ 跨框架接口不可用")
        return

    # 分析不同类型的电路
    test_circuits = [
        ("简单QASM", """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];"""),
    ]

    for name, circuit in test_circuits:
        print(f"\n分析 {name}:")
        analysis = analyze_circuit(circuit)

        if analysis['success']:
            print(f"  类型: {analysis['type']}")
            print(f"  量子比特数: {analysis.get('n_qubits', 'N/A')}")
            print(f"  门数量: {analysis.get('n_gates', 'N/A')}")
            print(f"  深度: {analysis.get('depth', 'N/A')}")
        else:
            print(f"  分析失败: {analysis['error']}")

    print()


def example_8_file_operations():
    """示例8: 文件操作."""
    print("🔹 示例8: 文件操作")
    print("-" * 40)

    if not INTERFACE_AVAILABLE:
        print("❌ 跨框架接口不可用")
        return

    # 创建临时QASM文件
    qasm_content = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
"""

    temp_file = Path("temp_test_circuit.qasm")
    try:
        # 保存到文件
        temp_file.write_text(qasm_content, encoding='utf-8')
        print(f"✅ 创建测试文件: {temp_file}")

        # 从文件加载并优化
        loaded_qasm = load_qasm_file(temp_file)
        print("✅ 从文件加载QASM电路")

        optimized = optimize_qasm(loaded_qasm)
        print(f"✅ 优化完成: {optimized.ngates} 个门")

        # 保存优化结果
        output_file = Path("optimized_circuit.qasm")
        save_optimized_circuit(optimized, output_file, format='qasm')
        print(f"✅ 优化结果已保存到: {output_file}")

    except Exception as e:
        print(f"❌ 文件操作错误: {e}")

    finally:
        # 清理临时文件
        if temp_file.exists():
            temp_file.unlink()
            print("🧹 清理临时文件")

    print()


def example_9_advanced_usage():
    """示例9: 高级使用方法."""
    print("🔹 示例9: 高级使用方法")
    print("-" * 40)

    if not CROSS_FRAMEWORK_AVAILABLE:
        print("❌ 跨框架优化器不可用")
        return

    if not QIBO_AVAILABLE:
        print("❌ Qibo不可用")
        return

    # 创建优化器实例
    optimizer = CrossFrameworkOptimizer(
        strategy=OptimizationStrategy.HYBRID,
        optimization_level=3,
        verbose=True
    )

    # 创建复杂的Qibo电路
    circuit = QiboCircuit(4)

    # 添加多层操作
    for layer in range(3):
        circuit.add(gates.H(0))
        circuit.add(gates.H(1))
        circuit.add(gates.H(2))
        circuit.add(gates.H(3))

        circuit.add(gates.CNOT(0, 1))
        circuit.add(gates.CNOT(1, 2))
        circuit.add(gates.CNOT(2, 3))

        circuit.add(gates.RY(0.785, 0))
        circuit.add(gates.RY(0.785, 1))
        circuit.add(gates.RY(0.785, 2))
        circuit.add(gates.RY(0.785, 3))

    print(f"原始电路: {circuit.ngates} 个门, 深度 {circuit.depth()}")

    # 使用混合策略优化
    try:
        optimized, stats = optimizer.optimize(circuit)
        print(f"✅ 混合策略优化完成:")
        print(f"  优化后: {optimized.ngates} 个门, 深度 {optimized.depth()}")
        print(stats)
    except Exception as e:
        print(f"❌ 混合策略优化失败: {e}")

    print()


def example_10_error_handling():
    """示例10: 错误处理."""
    print("🔹 示例10: 错误处理")
    print("-" * 40)

    if not INTERFACE_AVAILABLE:
        print("❌ 跨框架接口不可用")
        return

    # 测试各种错误情况
    test_cases = [
        ("无效QASM", "not a valid qasm circuit"),
        ("空电路", ""),
        ("错误的门", """OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
invalid_gate q[0];"""),
    ]

    for name, circuit in test_cases:
        print(f"测试 {name}:")
        try:
            optimized = optimize_circuit(circuit, verbose=False)
            print(f"  意外成功: {optimized.ngates} 个门")
        except Exception as e:
            print(f"  预期错误: {type(e).__name__}: {e}")

    print()


def main():
    """运行所有示例."""
    print("🚀 跨框架量子电路优化器使用示例")
    print("=" * 60)
    print()

    # 检查依赖
    missing_deps = []
    if not INTERFACE_AVAILABLE:
        missing_deps.append("跨框架接口")
    if not QIBO_AVAILABLE:
        missing_deps.append("Qibo")
    if not QISKIT_AVAILABLE:
        missing_deps.append("Qiskit")
    if not CROSS_FRAMEWORK_AVAILABLE:
        missing_deps.append("跨框架优化器")

    if missing_deps:
        print("⚠️  缺少以下依赖:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("某些示例可能无法正常运行")
        print()

    # 运行示例
    examples = [
        example_1_basic_usage,
        example_2_detailed_optimization,
        example_3_qiskit_circuit_optimization,
        example_4_qibo_circuit_optimization,
        example_5_batch_optimization,
        example_6_strategy_comparison,
        example_7_circuit_analysis,
        example_8_file_operations,
        example_9_advanced_usage,
        example_10_error_handling,
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"❌ 示例 {i} 运行失败: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("✅ 所有示例运行完成!")


if __name__ == "__main__":
    main()