"""跨框架优化器用户友好接口.

这个模块提供了简化的、用户友好的接口来使用跨框架量子电路优化功能。
"""

from typing import Union, Optional, List, Dict, Any
import warnings
from pathlib import Path

from cross_framework_optimizer import (
    CrossFrameworkOptimizer,
    CircuitType,
    OptimizationStrategy,
    CrossFrameworkError,
    UnsupportedCircuitError
)

# 动态导入框架
try:
    from qibo import Circuit as QiboCircuit
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False
    QiboCircuit = None

try:
    from qiskit import QuantumCircuit as QiskitCircuit
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None


def optimize_circuit(circuit: Union[str, QiboCircuit, QiskitCircuit],
                    strategy: str = "qiskit_only",
                    optimization_level: int = 2,
                    verbose: bool = False,
                    **kwargs) -> QiboCircuit:
    """优化量子电路的简化接口.

    Args:
        circuit: 输入电路（QASM字符串、Qiskit或Qibo电路）
        strategy: 优化策略 ("none", "qiskit_only", "sim_fusion", "hybrid")
        optimization_level: 优化级别 (0-3)
        verbose: 是否输出详细信息
        **kwargs: 额外参数

    Returns:
        优化后的Qibo电路

    Example:
        >>> from qibo import Circuit, gates
        >>> qc = Circuit(2)
        >>> qc.add(gates.H(0))
        >>> qc.add(gates.CNOT(0, 1))
        >>> optimized = optimize_circuit(qc, strategy="qiskit_only")
    """
    try:
        strategy_enum = OptimizationStrategy(strategy)
        optimizer = CrossFrameworkOptimizer(
            strategy=strategy_enum,
            optimization_level=optimization_level,
            verbose=verbose
        )

        optimized_circuit, stats = optimizer.optimize(circuit, **kwargs)

        if verbose:
            print(stats)

        return optimized_circuit

    except ValueError as e:
        raise CrossFrameworkError(f"无效的优化策略: {strategy}") from e
    except Exception as e:
        raise CrossFrameworkError(f"电路优化失败: {e}") from e


def optimize_circuit_with_stats(circuit: Union[str, QiboCircuit, QiskitCircuit],
                               strategy: str = "qiskit_only",
                               optimization_level: int = 2,
                               verbose: bool = True,
                               **kwargs) -> tuple[QiboCircuit, Dict[str, Any]]:
    """优化量子电路并返回详细统计信息.

    Args:
        circuit: 输入电路
        strategy: 优化策略
        optimization_level: 优化级别
        verbose: 是否输出详细信息
        **kwargs: 额外参数

    Returns:
        优化后的Qibo电路和统计信息字典

    Example:
        >>> circuit = "OPENQASM 2.0; include \"qelib1.inc\"; qreg q[2]; h q[0]; cx q[0],q[1];"
        >>> optimized, stats = optimize_circuit_with_stats(circuit)
        >>> print(f"门减少: {stats['gate_reduction_percent']:.1f}%")
    """
    try:
        strategy_enum = OptimizationStrategy(strategy)
        optimizer = CrossFrameworkOptimizer(
            strategy=strategy_enum,
            optimization_level=optimization_level,
            verbose=verbose
        )

        optimized_circuit, stats = optimizer.optimize(circuit, **kwargs)

        return optimized_circuit, stats.to_dict()

    except Exception as e:
        raise CrossFrameworkError(f"电路优化失败: {e}") from e


def quick_optimize(circuit: Union[str, QiboCircuit, QiskitCircuit]) -> QiboCircuit:
    """快速优化接口，使用默认设置.

    Args:
        circuit: 输入电路

    Returns:
        优化后的Qibo电路

    Example:
        >>> # 从QASM快速优化
        >>> qasm_str = "OPENQASM 2.0; include \"qelib1.inc\"; qreg q[2]; h q[0]; cx q[0],q[1];"
        >>> optimized = quick_optimize(qasm_str)
        >>> print(f"优化后门数: {optimized.ngates}")
    """
    return optimize_circuit(circuit, strategy="qiskit_only", optimization_level=2, verbose=False)


def optimize_qasm(qasm_string: str,
                  strategy: str = "qiskit_only",
                  optimization_level: int = 2) -> QiboCircuit:
    """专门优化QASM电路的接口.

    Args:
        qasm_string: QASM格式的电路字符串
        strategy: 优化策略
        optimization_level: 优化级别

    Returns:
        优化后的Qibo电路

    Example:
        >>> qasm = '''
        ... OPENQASM 2.0;
        ... include "qelib1.inc";
        ... qreg q[3];
        ... h q[0];
        ... cx q[0], q[1];
        ... cx q[1], q[2];
        ... '''
        >>> optimized = optimize_qasm(qasm, strategy="hybrid")
    """
    if not isinstance(qasm_string, str):
        raise TypeError("qasm_string必须是字符串类型")

    if not qasm_string.strip().startswith(('OPENQASM', 'include')):
        raise ValueError("无效的QASM格式")

    return optimize_circuit(qasm_string, strategy=strategy, optimization_level=optimization_level)


def optimize_qiskit(circuit: QiskitCircuit,
                   strategy: str = "qiskit_only",
                   optimization_level: int = 2) -> QiboCircuit:
    """专门优化Qiskit电路的接口.

    Args:
        circuit: Qiskit QuantumCircuit对象
        strategy: 优化策略
        optimization_level: 优化级别

    Returns:
        优化后的Qibo电路

    Example:
        >>> from qiskit import QuantumCircuit
        >>> qc = QuantumCircuit(2)
        >>> qc.h(0)
        >>> qc.cx(0, 1)
        >>> optimized = optimize_qiskit(qc)
    """
    if QISKIT_AVAILABLE and not isinstance(circuit, QiskitCircuit):
        raise TypeError("circuit必须是Qiskit QuantumCircuit对象")

    return optimize_circuit(circuit, strategy=strategy, optimization_level=optimization_level)


def optimize_qibo(circuit: QiboCircuit,
                 strategy: str = "sim_fusion",
                 verbose: bool = True) -> QiboCircuit:
    """专门优化Qibo电路的接口.

    Args:
        circuit: Qibo Circuit对象
        strategy: 优化策略
        verbose: 是否输出详细信息

    Returns:
        优化后的Qibo电路

    Example:
        >>> from qibo import Circuit, gates
        >>> qc = Circuit(2)
        >>> qc.add(gates.H(0))
        >>> qc.add(gates.CNOT(0, 1))
        >>> optimized = optimize_qibo(qc)
    """
    if QIBO_AVAILABLE and not isinstance(circuit, QiboCircuit):
        raise TypeError("circuit必须是Qibo Circuit对象")

    return optimize_circuit(circuit, strategy=strategy, verbose=verbose)


def batch_optimize(circuits: List[Union[str, QiboCircuit, QiskitCircuit]],
                  strategy: str = "qiskit_only",
                  optimization_level: int = 2,
                  show_progress: bool = True) -> List[QiboCircuit]:
    """批量优化多个电路.

    Args:
        circuits: 电路列表
        strategy: 优化策略
        optimization_level: 优化级别
        show_progress: 是否显示进度

    Returns:
        优化后的Qibo电路列表

    Example:
        >>> circuits = [qasm1, qasm2, qiskit_circuit]
        >>> optimized_circuits = batch_optimize(circuits, strategy="hybrid")
    """
    if not circuits:
        return []

    optimized_circuits = []

    for i, circuit in enumerate(circuits):
        if show_progress:
            print(f"优化电路 {i+1}/{len(circuits)}...")

        try:
            optimized = optimize_circuit(
                circuit,
                strategy=strategy,
                optimization_level=optimization_level,
                verbose=False
            )
            optimized_circuits.append(optimized)

            if show_progress:
                print(f"  完成: {getattr(circuit, 'ngates', len(circuit))} -> {optimized.ngates} 门")

        except Exception as e:
            print(f"  错误: {e}")
            # 可以选择跳过错误的电路或抛出异常
            optimized_circuits.append(None)

    return optimized_circuits


def compare_strategies(circuit: Union[str, QiboCircuit, QiskitCircuit],
                     strategies: Optional[List[str]] = None,
                     optimization_level: int = 2) -> Dict[str, Dict[str, Any]]:
    """比较不同优化策略的效果.

    Args:
        circuit: 输入电路
        strategies: 要比较的策略列表，默认比较所有策略
        optimization_level: 优化级别

    Returns:
        各策略的优化结果比较

    Example:
        >>> results = compare_strategies(circuit, ["qiskit_only", "sim_fusion", "hybrid"])
        >>> for strategy, stats in results.items():
        ...     print(f"{strategy}: 门减少 {stats['gate_reduction_percent']:.1f}%")
    """
    if strategies is None:
        strategies = ["none", "qiskit_only", "sim_fusion", "hybrid"]

    results = {}

    for strategy in strategies:
        try:
            optimized, stats = optimize_circuit_with_stats(
                circuit,
                strategy=strategy,
                optimization_level=optimization_level,
                verbose=False
            )
            results[strategy] = stats

        except Exception as e:
            results[strategy] = {
                'error': str(e),
                'success': False
            }

    return results


def analyze_circuit(circuit: Union[str, QiboCircuit, QiskitCircuit]) -> Dict[str, Any]:
    """分析电路的基本信息.

    Args:
        circuit: 输入电路

    Returns:
        电路分析结果

    Example:
        >>> info = analyze_circuit(qasm_string)
        >>> print(f"电路类型: {info['type']}")
        >>> print(f"量子比特数: {info['n_qubits']}")
        >>> print(f"门数量: {info['n_gates']}")
    """
    from cross_framework_optimizer import CircuitTypeDetector

    try:
        detector = CircuitTypeDetector()
        circuit_type = detector.detect_circuit_type(circuit)

        analysis = {
            'type': circuit_type.value,
            'success': True
        }

        # 根据类型分析具体信息
        if circuit_type == circuit_type.QASM:
            lines = circuit.strip().split('\n')
            qreg_lines = [line for line in lines if line.strip().startswith('qreg')]
            if qreg_lines:
                import re
                match = re.search(r'qreg\s+\w+\[(\d+)\]', qreg_lines[0])
                if match:
                    analysis['n_qubits'] = int(match.group(1))

            # 粗略计算门数量
            gate_lines = [line for line in lines
                         if any(gate in line for gate in ['h', 'x', 'y', 'z', 'cx', 'cz', 'rx', 'ry', 'rz'])
                         and not line.strip().startswith(('qreg', 'creg', 'include', 'OPENQASM'))]
            analysis['n_gates'] = len(gate_lines)

        elif circuit_type == circuit_type.QISKIT and QISKIT_AVAILABLE:
            analysis['n_qubits'] = circuit.num_qubits
            analysis['n_gates'] = len(circuit)
            analysis['depth'] = circuit.depth()

        elif circuit_type == circuit_type.QIBO and QIBO_AVAILABLE:
            analysis['n_qubits'] = circuit.nqubits
            analysis['n_gates'] = circuit.ngates
            analysis['depth'] = circuit.depth()

        return analysis

    except Exception as e:
        return {
            'type': 'unknown',
            'success': False,
            'error': str(e)
        }


# 便捷函数
def load_qasm_file(file_path: Union[str, Path]) -> str:
    """从文件加载QASM电路.

    Args:
        file_path: QASM文件路径

    Returns:
        QASM字符串

    Example:
        >>> qasm = load_qasm_file("my_circuit.qasm")
        >>> optimized = optimize_qasm(qasm)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if path.suffix.lower() != '.qasm':
        warnings.warn(f"文件扩展名不是.qasm: {file_path}")

    return path.read_text(encoding='utf-8')


def save_optimized_circuit(circuit: QiboCircuit, file_path: Union[str, Path], format: str = 'qasm'):
    """保存优化后的电路.

    Args:
        circuit: Qibo电路
        file_path: 输出文件路径
        format: 输出格式 ('qasm', 'qibo')
    """
    path = Path(file_path)

    if format.lower() == 'qasm':
        if QISKIT_AVAILABLE:
            # 转换为Qiskit再输出QASM
            from cross_framework_optimizer import CrossFrameworkOptimizer
            optimizer = CrossFrameworkOptimizer()
            qiskit_circuit = optimizer._convert_qibo_to_qiskit(circuit)
            qasm_string = qiskit_circuit.qasm()
            path.write_text(qasm_string, encoding='utf-8')
        else:
            raise CrossFrameworkError("Qiskit不可用，无法保存QASM格式")

    elif format.lower() == 'qibo':
        # 保存Qibo电路的Python代码
        code = f"""# Qibo电路 - 自动生成
from qibo import Circuit, gates

# 创建{circuit.nqubits}量子比特电路
qc = Circuit({circuit.nqubits})

# 添加量子门
"""
        # 这里可以添加更详细的门转换逻辑
        path.write_text(code, encoding='utf-8')

    else:
        raise ValueError(f"不支持的格式: {format}")