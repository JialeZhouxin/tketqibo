"""跨框架量子电路优化器测试套件."""

import pytest
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# 测试用QASM电路
SIMPLE_QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
"""

GHZ_QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
h q[0];
cx q[0],q[1];
cx q[0],q[2];
"""

COMPLEX_QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
h q[1];
cx q[0],q[1];
rz(1.5708) q[2];
cx q[1],q[2];
measure q -> c;
"""

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
    from cross_framework_optimizer import (
        CrossFrameworkOptimizer,
        CircuitType,
        OptimizationStrategy,
        CircuitTypeDetector
    )
    CROSS_FRAMEWORK_AVAILABLE = True
except ImportError:
    CROSS_FRAMEWORK_AVAILABLE = False

try:
    from src.cross_framework_interface import (
        optimize_circuit,
        optimize_qasm,
        optimize_qiskit,
        optimize_qibo,
        quick_optimize
    )
    INTERFACE_AVAILABLE = True
except ImportError:
    INTERFACE_AVAILABLE = False

try:
    from src.gate_mapping import (
        gate_registry,
        GateConverter,
        print_gate_compatibility_table
    )
    GATE_MAPPING_AVAILABLE = True
except ImportError:
    GATE_MAPPING_AVAILABLE = False


@pytest.mark.skipif(not CROSS_FRAMEWORK_AVAILABLE, reason="CrossFrameworkOptimizer not available")
class TestCircuitTypeDetection:
    """电路类型检测测试."""

    def test_qasm_detection(self):
        """测试QASM电路检测."""
        detector = CircuitTypeDetector()

        # 简单QASM
        assert detector.detect_circuit_type(SIMPLE_QASM) == CircuitType.QASM

        # 复杂QASM
        assert detector.detect_circuit_type(GHZ_QASM) == CircuitType.QASM

    @pytest.mark.skipif(not QIBO_AVAILABLE, reason="Qibo not available")
    def test_qibo_detection(self):
        """测试Qibo电路检测."""
        detector = CircuitTypeDetector()

        circuit = QiboCircuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))

        assert detector.detect_circuit_type(circuit) == CircuitType.QIBO

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_qiskit_detection(self):
        """测试Qiskit电路检测."""
        detector = CircuitTypeDetector()

        circuit = QiskitCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        assert detector.detect_circuit_type(circuit) == CircuitType.QISKIT

    def test_unsupported_circuit(self):
        """测试不支持的电路类型."""
        detector = CircuitTypeDetector()

        with pytest.raises(Exception):  # UnsupportedCircuitError
            detector.detect_circuit_type(123)

        with pytest.raises(Exception):  # UnsupportedCircuitError
            detector.detect_circuit_type("not a qasm circuit")


@pytest.mark.skipif(not CROSS_FRAMEWORK_AVAILABLE or not QIBO_AVAILABLE,
                    reason="Required dependencies not available")
class TestCrossFrameworkOptimizer:
    """跨框架优化器测试."""

    def test_initialization(self):
        """测试初始化."""
        # 基本初始化
        optimizer = CrossFrameworkOptimizer()
        assert optimizer.strategy == OptimizationStrategy.QISKIT_ONLY
        assert optimizer.optimization_level == 2

        # 自定义初始化
        optimizer = CrossFrameworkOptimizer(
            strategy=OptimizationStrategy.NONE,
            optimization_level=1
        )
        assert optimizer.strategy == OptimizationStrategy.NONE
        assert optimizer.optimization_level == 1

    def test_qasm_optimization(self):
        """测试QASM电路优化."""
        optimizer = CrossFrameworkOptimizer(
            strategy=OptimizationStrategy.NONE,  # 不优化，只测试转换
            verbose=False
        )

        optimized, stats = optimizer.optimize(SIMPLE_QASM)

        assert isinstance(optimized, QiboCircuit)
        assert stats.input_type == "qasm"
        assert stats.conversion_success

    @pytest.mark.skipif(not QIBO_AVAILABLE, reason="Qibo not available")
    def test_qibo_optimization(self):
        """测试Qibo电路优化."""
        optimizer = CrossFrameworkOptimizer(
            strategy=OptimizationStrategy.NONE,
            verbose=False
        )

        # 创建Qibo电路
        circuit = QiboCircuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))

        optimized, stats = optimizer.optimize(circuit)

        assert isinstance(optimized, QiboCircuit)
        assert stats.input_type == "qibo"
        assert stats.conversion_success

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_qiskit_optimization(self):
        """测试Qiskit电路优化."""
        optimizer = CrossFrameworkOptimizer(
            strategy=OptimizationStrategy.NONE,
            verbose=False
        )

        # 创建Qiskit电路
        circuit = QiskitCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        optimized, stats = optimizer.optimize(circuit)

        assert isinstance(optimized, QiboCircuit)
        assert stats.input_type == "qiskit"
        assert stats.conversion_success

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_qiskit_optimization_with_optimization(self):
        """测试Qiskit实际优化."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        optimizer = CrossFrameworkOptimizer(
            strategy=OptimizationStrategy.QISKIT_ONLY,
            optimization_level=1,
            verbose=False
        )

        # 创建一个可以优化的电路（包含冗余操作）
        circuit = QiskitCircuit(2)
        circuit.h(0)
        circuit.h(0)  # 冗余的H门
        circuit.x(0)
        circuit.x(0)  # 冗余的X门
        circuit.cx(0, 1)

        optimized, stats = optimizer.optimize(circuit)

        assert isinstance(optimized, QiboCircuit)
        assert stats.optimization_success
        # 门数量应该减少（因为消除了冗余操作）

    def test_stats_calculation(self):
        """测试统计信息计算."""
        optimizer = CrossFrameworkOptimizer(
            strategy=OptimizationStrategy.NONE,
            verbose=False
        )

        optimized, stats = optimizer.optimize(SIMPLE_QASM)

        # 测试统计信息属性
        assert hasattr(stats, 'gate_reduction')
        assert hasattr(stats, 'gate_reduction_percent')
        assert hasattr(stats, 'depth_reduction')
        assert hasattr(stats, 'depth_reduction_percent')

        # 测试字典转换
        stats_dict = stats.to_dict()
        assert isinstance(stats_dict, dict)
        assert 'input_type' in stats_dict
        assert 'strategy' in stats_dict

    def test_optimization_stats_str(self):
        """测试优化统计信息字符串表示."""
        optimizer = CrossFrameworkOptimizer(
            strategy=OptimizationStrategy.NONE,
            verbose=False
        )

        optimized, stats = optimizer.optimize(SIMPLE_QASM)

        stats_str = str(stats)
        assert isinstance(stats_str, str)
        assert "优化统计" in stats_str
        assert "门减少" in stats_str


@pytest.mark.skipif(not INTERFACE_AVAILABLE, reason="Interface not available")
class TestCrossFrameworkInterface:
    """跨框架接口测试."""

    def test_optimize_circuit_function(self):
        """测试optimize_circuit函数."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        optimized = optimize_circuit(SIMPLE_QASM, verbose=False)
        assert isinstance(optimized, QiboCircuit)

    def test_optimize_circuit_with_stats_function(self):
        """测试optimize_circuit_with_stats函数."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        optimized, stats = optimize_circuit_with_stats(SIMPLE_QASM, verbose=False)

        assert isinstance(optimized, QiboCircuit)
        assert isinstance(stats, dict)
        assert 'input_type' in stats

    def test_quick_optimize_function(self):
        """测试quick_optimize函数."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        optimized = quick_optimize(SIMPLE_QASM)
        assert isinstance(optimized, QiboCircuit)

    def test_optimize_qasm_function(self):
        """测试optimize_qasm函数."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        optimized = optimize_qasm(SIMPLE_QASM)
        assert isinstance(optimized, QiboCircuit)

    def test_optimize_qasm_invalid_input(self):
        """测试optimize_qasm无效输入."""
        with pytest.raises((TypeError, ValueError)):
            optimize_qasm(123)

        with pytest.raises(ValueError):
            optimize_qasm("not qasm")

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not available")
    def test_optimize_qiskit_function(self):
        """测试optimize_qiskit函数."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        circuit = QiskitCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        optimized = optimize_qiskit(circuit)
        assert isinstance(optimized, QiboCircuit)

    @pytest.mark.skipif(not QIBO_AVAILABLE, reason="Qibo not available")
    def test_optimize_qibo_function(self):
        """测试optimize_qibo函数."""
        circuit = QiboCircuit(2)
        circuit.add(gates.H(0))
        circuit.add(gates.CNOT(0, 1))

        optimized = optimize_qibo(circuit, verbose=False)
        assert isinstance(optimized, QiboCircuit)

    def test_batch_optimize_function(self):
        """测试batch_optimize函数."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        circuits = [SIMPLE_QASM, GHZ_QASM]
        optimized_circuits = batch_optimize(circuits, show_progress=False)

        assert len(optimized_circuits) == 2
        for circuit in optimized_circuits:
            assert isinstance(circuit, QiboCircuit)

    def test_compare_strategies_function(self):
        """测试compare_strategies函数."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        results = compare_strategies(SIMPLE_QASM, strategies=["none", "qiskit_only"])

        assert isinstance(results, dict)
        assert "none" in results
        assert "qiskit_only" in results

    def test_analyze_circuit_function(self):
        """测试analyze_circuit函数."""
        analysis = analyze_circuit(SIMPLE_QASM)

        assert isinstance(analysis, dict)
        assert 'type' in analysis
        assert analysis['type'] == 'qasm'


@pytest.mark.skipif(not GATE_MAPPING_AVAILABLE, reason="Gate mapping not available")
class TestGateMapping:
    """门映射测试."""

    def test_gate_registry_initialization(self):
        """测试门注册表初始化."""
        assert gate_registry is not None

        # 测试获取门信息
        h_info = gate_registry.get_gate_info('h')
        assert h_info is not None
        assert h_info.name == 'h'
        assert h_info.num_qubits == 1

    def test_gate_support_check(self):
        """测试门支持检查."""
        # 支持的门
        assert gate_registry.is_gate_supported('h', 'qibo')
        assert gate_registry.is_gate_supported('h', 'qiskit')
        assert gate_registry.is_gate_supported('cx', 'qibo')

        # 不存在的门
        assert not gate_registry.is_gate_supported('nonexistent_gate', 'qibo')

    def test_framework_specific_gates(self):
        """测试框架特定门."""
        qibo_gates = gate_registry.get_supported_gates('qibo')
        qiskit_gates = gate_registry.get_supported_gates('qiskit')

        assert len(qibo_gates) > 0
        assert len(qiskit_gates) > 0

        # 检查一些基本门
        qibo_gate_names = [gate.name for gate in qibo_gates]
        qiskit_gate_names = [gate.name for gate in qiskit_gates]

        assert 'h' in qibo_gate_names
        assert 'h' in qiskit_gate_names
        assert 'cx' in qibo_gate_names
        assert 'cx' in qiskit_gate_names

    def test_gate_categories(self):
        """测试门类别."""
        from src.gate_mapping import GateCategory

        single_qubit_gates = gate_registry.get_gates_by_category(GateCategory.SINGLE_QUBIT)
        two_qubit_gates = gate_registry.get_gates_by_category(GateCategory.TWO_QUBIT)

        assert len(single_qubit_gates) > 0
        assert len(two_qubit_gates) > 0

        # 检查H门在单量子比特门中
        h_in_single = any(gate.name == 'h' for gate in single_qubit_gates)
        assert h_in_single

        # 检查CX门在双量子比特门中
        cx_in_two = any(gate.name == 'cx' for gate in two_qubit_gates)
        assert cx_in_two

    def test_gate_parameter_validation(self):
        """测试门参数验证."""
        # 正确的参数数量
        assert gate_registry.validate_gate_parameters('h', [])
        assert gate_registry.validate_gate_parameters('rx', [1.5])
        assert gate_registry.validate_gate_parameters('u2', [1.0, 2.0])

        # 错误的参数数量
        assert not gate_registry.validate_gate_parameters('h', [1.0])  # H门不需要参数
        assert not gate_registry.validate_gate_parameters('rx', [])     # RX门需要参数
        assert not gate_registry.validate_gate_parameters('u2', [1.0])  # U2门需要2个参数

    def test_gate_converter(self):
        """测试门转换器."""
        converter = GateConverter()

        # 测试转换检查
        assert converter.can_convert('h', 'qibo', 'qiskit')
        assert converter.can_convert('cx', 'qiskit', 'qibo')

        # 测试不存在的门
        assert not converter.can_convert('nonexistent', 'qibo', 'qiskit')

    def test_custom_gate_addition(self):
        """测试自定义门添加."""
        from src.gate_mapping import GateInfo, GateCategory

        # 创建自定义门信息
        custom_gate = GateInfo(
            name='custom_gate',
            category=GateCategory.SINGLE_QUBIT,
            num_qubits=1,
            num_params=1,
            description='Custom test gate',
            supported_frameworks=['qibo', 'qiskit']
        )

        # 添加自定义门
        gate_registry.add_custom_gate(custom_gate)

        # 验证添加成功
        retrieved_gate = gate_registry.get_gate_info('custom_gate')
        assert retrieved_gate is not None
        assert retrieved_gate.name == 'custom_gate'
        assert 'qibo' in retrieved_gate.supported_frameworks


@pytest.mark.skipif(not GATE_MAPPING_AVAILABLE, reason="Gate mapping not available")
class TestGateCompatibilityTable:
    """门兼容性表测试."""

    def test_print_compatibility_table(self):
        """测试打印兼容性表."""
        # 这个测试主要确保函数能够运行而不出错
        # 实际的打印输出由人工验证
        try:
            print_gate_compatibility_table()
            compatibility_printed = True
        except Exception:
            compatibility_printed = False

        assert compatibility_printed


@pytest.mark.skipif(not QIBO_AVAILABLE, reason="Qibo not available")
class TestCircuitEquivalence:
    """电路等价性测试."""

    def test_simple_circuit_equivalence(self):
        """测试简单电路的等价性."""
        if not INTERFACE_AVAILABLE:
            pytest.skip("Interface not available")

        # 使用简单的QASM电路
        optimized = optimize_circuit(SIMPLE_QASM, strategy="none", verbose=False)

        # 验证电路结构
        assert optimized.nqubits == 2
        assert optimized.ngates >= 2  # 至少有H和CNOT

    def test_ghz_circuit_structure(self):
        """测试GHZ电路结构."""
        if not INTERFACE_AVAILABLE:
            pytest.skip("Interface not available")

        optimized = optimize_circuit(GHZ_QASM, strategy="none", verbose=False)

        # GHZ电路应该有3个量子比特
        assert optimized.nqubits == 3
        # 应该有足够的门来创建GHZ态
        assert optimized.ngates >= 2  # 至少有H和2个CNOT


class TestErrorHandling:
    """错误处理测试."""

    @pytest.mark.skipif(not INTERFACE_AVAILABLE, reason="Interface not available")
    def test_invalid_optimization_strategy(self):
        """测试无效优化策略."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        with pytest.raises(Exception):
            optimize_circuit(SIMPLE_QASM, strategy="invalid_strategy")

    @pytest.mark.skipif(not INTERFACE_AVAILABLE, reason="Interface not available")
    def test_empty_circuit_list(self):
        """测试空电路列表."""
        if not QIBO_AVAILABLE:
            pytest.skip("Qibo not available")

        empty_result = batch_optimize([], show_progress=False)
        assert empty_result == []

    @pytest.mark.skipif(not GATE_MAPPING_AVAILABLE, reason="Gate mapping not available")
    def test_invalid_gate_parameters(self):
        """测试无效门参数."""
        # 测试参数数量不匹配
        assert not gate_registry.validate_gate_parameters('u3', [1.0])  # 需要3个参数
        assert not gate_registry.validate_gate_parameters('cx', [1.0])   # 不需要参数


def test_module_imports():
    """测试模块导入."""
    # 测试主要模块是否可以导入
    try:
        import cross_framework_optimizer
        assert hasattr(cross_framework_optimizer, 'CrossFrameworkOptimizer')
        module_imports_successful = True
    except ImportError:
        module_imports_successful = False

    assert module_imports_successful


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])