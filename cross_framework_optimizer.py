"""跨框架量子电路优化器.

本模块提供了一个统一的接口，支持从QASM、Qiskit和Qibo三种格式输入量子电路，
使用Qiskit Transpiler进行优化，并统一输出为优化后的Qibo电路。

主要功能：
- CrossFrameworkOptimizer: 跨框架优化主类
- 多框架电路输入支持（QASM、Qiskit、Qibo）
- Qiskit Transpiler集成
- 统一Qibo电路输出
- 完整的错误处理和统计信息

依赖：
- qibo: 目标量子电路框架
- qiskit: 优化和转换引擎（可选）
- pytket: 现有TKET集成

作者: Cross-Framework Team
版本: 1.0.0
"""

from __future__ import annotations

import time
import sys
import logging
from typing import Optional, Union, Dict, Any, List, Tuple
from pathlib import Path
from enum import Enum

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入必要的依赖库
try:
    from qibo import Circuit as QiboCircuit
    from qibo import gates
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False
    QiboCircuit = None
    gates = None
    logger.warning("Qibo未安装，相关功能将不可用")

try:
    from qiskit import QuantumCircuit as QiskitCircuit
    from qiskit import transpile
    from qiskit.transpiler import Target, CouplingMap
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QiskitCircuit = None
    transpile = None
    Target = None
    CouplingMap = None
    logger.warning("Qiskit未安装，相关功能将使用回退策略")

try:
    from pytket import Circuit as TketCircuit
    from pytket.circuit import OpType
    TKET_AVAILABLE = True
except ImportError:
    TKET_AVAILABLE = False
    TketCircuit = None
    OpType = None


class CircuitType(Enum):
    """电路类型枚举."""
    UNKNOWN = "unknown"
    QASM = "qasm"
    QISKIT = "qiskit"
    QIBO = "qibo"


class OptimizationStrategy(Enum):
    """优化策略枚举."""
    NONE = "none"
    QISKIT_ONLY = "qiskit_only"
    SIM_FUSION = "sim_fusion"
    HYBRID = "hybrid"  # Qiskit + Sim-Fusion


class CrossFrameworkError(Exception):
    """跨框架优化错误基类."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        """初始化错误.

        Args:
            message: 错误消息
            suggestion: 可选的修复建议
        """
        super().__init__(message)
        self.suggestion = suggestion


class UnsupportedCircuitError(CrossFrameworkError):
    """不支持的电路类型错误."""
    pass


class GateConversionError(CrossFrameworkError):
    """门转换错误."""
    pass


class VerificationError(CrossFrameworkError):
    """等价性验证错误."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        """初始化验证错误.

        Args:
            message: 错误消息
            suggestion: 可选的修复建议
        """
        super().__init__(message, suggestion)
        self.message = message
        self.suggestion = suggestion

    def __str__(self):
        if self.suggestion:
            return f"{self.message}\n建议: {self.suggestion}"
        return self.message


class OptimizationStats:
    """优化统计信息类."""

    def __init__(self,
                 input_type: str = "unknown",
                 strategy: str = "none",
                 original_gates: int = 0,
                 original_depth: int = 0,
                 optimized_gates: int = 0,
                 optimized_depth: int = 0,
                 conversion_time: float = 0.0,
                 optimization_time: float = 0.0,
                 total_time: float = 0.0,
                 conversion_success: bool = True,
                 optimization_success: bool = True,
                 error_message: Optional[str] = None):
        """初始化统计信息.

        Args:
            input_type: 输入电路类型
            strategy: 使用的优化策略
            original_gates: 原始电路的门数量
            original_depth: 原始电路的深度
            optimized_gates: 优化后电路的门数量
            optimized_depth: 优化后电路的深度
            conversion_time: 转换时间
            optimization_time: 优化时间
            total_time: 总时间
            conversion_success: 转换是否成功
            optimization_success: 优化是否成功
            error_message: 错误信息
        """
        self.input_type = input_type
        self.strategy = strategy
        self.original_gates = original_gates
        self.original_depth = original_depth
        self.optimized_gates = optimized_gates
        self.optimized_depth = optimized_depth
        self.conversion_time = conversion_time
        self.optimization_time = optimization_time
        self.total_time = total_time
        self.conversion_success = conversion_success
        self.optimization_success = optimization_success
        self.error_message = error_message

    @property
    def gate_reduction(self) -> int:
        """门减少数量."""
        return self.original_gates - self.optimized_gates

    @property
    def gate_reduction_percent(self) -> float:
        """门减少百分比."""
        if self.original_gates == 0:
            return 0.0
        return (self.gate_reduction / self.original_gates) * 100

    @property
    def depth_reduction(self) -> int:
        """深度减少数量."""
        return self.original_depth - self.optimized_depth

    @property
    def depth_reduction_percent(self) -> float:
        """深度减少百分比."""
        if self.original_depth == 0:
            return 0.0
        return (self.depth_reduction / self.original_depth) * 100

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return {
            'input_type': self.input_type,
            'strategy': self.strategy,
            'original_gates': self.original_gates,
            'optimized_gates': self.optimized_gates,
            'gate_reduction': self.gate_reduction,
            'gate_reduction_percent': self.gate_reduction_percent,
            'original_depth': self.original_depth,
            'optimized_depth': self.optimized_depth,
            'depth_reduction': self.depth_reduction,
            'depth_reduction_percent': self.depth_reduction_percent,
            'conversion_time': self.conversion_time,
            'optimization_time': self.optimization_time,
            'total_time': self.total_time,
            'conversion_success': self.conversion_success,
            'optimization_success': self.optimization_success,
            'error_message': self.error_message
        }

    def __str__(self) -> str:
        """字符串表示."""
        return (f"优化统计 (策略: {self.strategy}):\n"
                f"  输入类型: {self.input_type}\n"
                f"  门减少: {self.gate_reduction} ({self.gate_reduction_percent:.1f}%)\n"
                f"  深度减少: {self.depth_reduction} ({self.depth_reduction_percent:.1f}%)\n"
                f"  转换时间: {self.conversion_time:.4f}s\n"
                f"  优化时间: {self.optimization_time:.4f}s\n"
                f"  总时间: {self.total_time:.4f}s")


class CircuitTypeDetector:
    """电路类型检测器."""

    @staticmethod
    def detect_circuit_type(circuit: Union[str, QiboCircuit, QiskitCircuit, Any]) -> CircuitType:
        """检测电路类型.

        Args:
            circuit: 输入电路

        Returns:
            检测到的电路类型

        Raises:
            UnsupportedCircuitError: 不支持的电路类型
        """
        if isinstance(circuit, str):
            # 检查是否为QASM格式
            if circuit.strip().startswith(('OPENQASM', 'OPENQASM 2.0', 'include "qelib1.inc"')):
                return CircuitType.QASM
            else:
                raise UnsupportedCircuitError(
                    "无法识别的字符串格式，期望QASM格式",
                    "确保字符串以'OPENQASM'开头"
                )
        elif QISKIT_AVAILABLE and hasattr(circuit, '__class__') and circuit.__class__.__name__ == 'QuantumCircuit':
            # Qiskit QuantumCircuit: 框架可用 AND 类名精确匹配
            return CircuitType.QISKIT
        elif QIBO_AVAILABLE and hasattr(circuit, '__class__') and circuit.__class__.__name__ == 'Circuit' and hasattr(circuit, 'ngates'):
            # Qibo Circuit: 框架可用 AND 类名精确匹配 AND 具有ngates属性
            return CircuitType.QIBO

        raise UnsupportedCircuitError(
            f"不支持的电路类型: {type(circuit)}",
            "支持的类型: QASM字符串、Qiskit QuantumCircuit、Qibo Circuit"
        )


class CrossFrameworkOptimizer:
    """跨框架量子电路优化器主类."""

    def __init__(self,
                 strategy: OptimizationStrategy = OptimizationStrategy.QISKIT_ONLY,
                 optimization_level: int = 2,
                 verbose: bool = False):
        """初始化优化器.

        Args:
            strategy: 优化策略
            optimization_level: Qiskit优化级别 (0-3)
            verbose: 是否输出详细信息
        """
        self.strategy = strategy
        self.optimization_level = optimization_level
        self.verbose = verbose

        if verbose:
            logger.setLevel(logging.DEBUG)

        self._check_dependencies()
        self._detector = CircuitTypeDetector()

        # 初始化转换器
        self._qasm_converter = None
        self._qiskit_converter = None

    def _check_dependencies(self) -> None:
        """检查依赖是否可用."""
        if not QIBO_AVAILABLE:
            raise CrossFrameworkError(
                "Qibo是必需的依赖，请安装: pip install qibo",
                "Qibo是目标输出格式"
            )

        if self.strategy in [OptimizationStrategy.QISKIT_ONLY, OptimizationStrategy.HYBRID]:
            if not QISKIT_AVAILABLE:
                logger.warning("Qiskit未安装，将使用回退策略")
                self.strategy = OptimizationStrategy.SIM_FUSION

        if self.strategy in [OptimizationStrategy.SIM_FUSION, OptimizationStrategy.HYBRID]:
            try:
                import sim_fusion
                self._sim_fusion = sim_fusion
            except ImportError:
                logger.warning("Sim-Fusion未安装，将使用基础策略")
                self.strategy = OptimizationStrategy.QISKIT_ONLY if QISKIT_AVAILABLE else OptimizationStrategy.NONE

    def detect_circuit_type(self, circuit: Union[str, QiboCircuit, QiskitCircuit, Any]) -> CircuitType:
        """检测电路类型.

        Args:
            circuit: 输入电路

        Returns:
            电路类型
        """
        return self._detector.detect_circuit_type(circuit)

    def optimize(self,
                 circuit: Union[str, QiboCircuit, QiskitCircuit, Any],
                 verify: bool = False,
                 verify_tolerance: float = 1e-8,
                 **kwargs) -> Tuple[QiboCircuit, OptimizationStats]:
        """优化量子电路（支持等价性验证）.

        Args:
            circuit: 输入电路（QASM字符串、Qiskit或Qibo电路）
            verify: 是否进行酉矩阵等价性验证（默认 False）
            verify_tolerance: 验证的数值容差（默认 1e-8）
            **kwargs: 额外参数

        Returns:
            优化后的Qibo电路和统计信息

        Raises:
            UnsupportedCircuitError: 不支持的电路类型
            GateConversionError: 门转换失败
            VerificationError: 等价性验证失败
            CrossFrameworkError: 其他错误
        """
        start_time = time.time()
        input_type = self.detect_circuit_type(circuit)

        logger.info(f"检测到输入类型: {input_type.value}")

        try:
            # 第一步：转换为Qiskit格式（如果需要）
            conversion_start = time.time()
            qiskit_circuit = self._convert_to_qiskit(circuit, input_type)
            conversion_time = time.time() - conversion_start

            original_gates = qiskit_circuit.size()
            original_depth = qiskit_circuit.depth()

            # 保存原始酉矩阵（用于验证）
            original_unitary = None
            if verify:
                original_unitary = self._get_unitary(qiskit_circuit)

            # 第二步：应用优化策略
            optimization_start = time.time()
            optimized_qiskit = self._apply_optimization(qiskit_circuit, **kwargs)
            optimization_time = time.time() - optimization_start

            # 第三步：转换为Qibo格式
            final_circuit = self._convert_to_qibo(optimized_qiskit)

            # 验证等价性
            if verify and original_unitary is not None:
                self._verify_equivalence(
                    original_unitary,
                    final_circuit,
                    tolerance=verify_tolerance
                )

            total_time = time.time() - start_time
            optimized_gates = final_circuit.ngates
            optimized_depth = final_circuit.depth

            stats = OptimizationStats(
                input_type=input_type.value,
                strategy=self.strategy.value,
                original_gates=original_gates,
                original_depth=original_depth,
                optimized_gates=optimized_gates,
                optimized_depth=optimized_depth,
                conversion_time=conversion_time,
                optimization_time=optimization_time,
                total_time=total_time,
                conversion_success=True,
                optimization_success=True
            )

            logger.info(f"优化完成: 门数 {original_gates} -> {optimized_gates}")

            if verify:
                logger.info(f"✓ 等价性验证通过（容差: {verify_tolerance:.0e}）")

            return final_circuit, stats

        except Exception as e:
            total_time = time.time() - start_time
            error_stats = OptimizationStats(
                input_type=input_type.value,
                strategy=self.strategy.value,
                total_time=total_time,
                conversion_success=False,
                optimization_success=False,
                error_message=str(e)
            )
            logger.error(f"优化失败: {e}")
            raise CrossFrameworkError(f"优化过程失败: {e}") from e

    def _convert_to_qiskit(self, circuit: Any, input_type: CircuitType) -> QiskitCircuit:
        """将电路转换为Qiskit格式."""
        if input_type == CircuitType.QIBO:
            return self._convert_qibo_to_qiskit(circuit)
        elif input_type == CircuitType.QISKIT:
            return circuit
        elif input_type == CircuitType.QASM:
            return self._convert_qasm_to_qiskit(circuit)
        else:
            raise UnsupportedCircuitError(f"不支持的输入类型: {input_type}")

    def _convert_to_qibo(self, circuit: QiskitCircuit) -> QiboCircuit:
        """将Qiskit电路转换为Qibo格式."""
        try:
            n_qubits = circuit.num_qubits
            qibo_circuit = QiboCircuit(n_qubits)

            # 转换量子门
            for instruction in circuit.data:
                # 兼容Qiskit 1.2+的新API
                if hasattr(instruction, 'operation'):
                    gate = instruction.operation
                    qubits_list = instruction.qubits
                else:
                    # 兼容旧版本Qiskit
                    gate = instruction[0]
                    qubits_list = instruction[1]

                # 兼容Qiskit 2.x的Qubit索引访问
                try:
                    qubits = [q._index for q in qubits_list]
                except AttributeError:
                    # 如果_q._index不存在，尝试其他方法
                    qubits = [circuit.qubits.index(q) for q in qubits_list]

                params = gate.params if hasattr(gate, 'params') else []

                self._convert_gate_to_qibo(gate, qubits, params, qibo_circuit)

            return qibo_circuit

        except Exception as e:
            raise GateConversionError(f"Qiskit到Qibo转换失败: {e}") from e

    def _convert_qibo_to_qiskit(self, circuit: QiboCircuit) -> QiskitCircuit:
        """将Qibo电路转换为Qiskit格式."""
        try:
            n_qubits = circuit.nqubits
            qiskit_circuit = QiskitCircuit(n_qubits)

            # 转换量子门
            for gate in circuit.queue:
                gate_name = gate.__class__.__name__
                qubits = gate.qubits
                params = gate.parameters if hasattr(gate, 'parameters') else []

                self._convert_gate_to_qiskit(gate_name, gate, qubits, params, qiskit_circuit)

            return qiskit_circuit

        except Exception as e:
            raise GateConversionError(f"Qibo到Qiskit转换失败: {e}") from e

    def _convert_qasm_to_qiskit(self, qasm_string: str) -> QiskitCircuit:
        """将QASM字符串转换为Qiskit电路."""
        try:
            return QiskitCircuit.from_qasm_str(qasm_string)
        except Exception as e:
            raise GateConversionError(f"QASM解析失败: {e}") from e

    def _convert_gate_to_qibo(self, gate: Any, qubits: List[int], params: List[float],
                             qibo_circuit: QiboCircuit) -> None:
        """将单个量子门转换为Qibo格式."""
        gate_name = gate.name if hasattr(gate, 'name') else gate.__class__.__name__

        # 门类型映射（简化版本）
        gate_mapping = {
            'h': gates.H,
            'x': gates.X,
            'y': gates.Y,
            'z': gates.Z,
            'cx': gates.CNOT,
            'cz': gates.CZ,
            'swap': gates.SWAP,
            'rx': gates.RX,
            'ry': gates.RY,
            'rz': gates.RZ,
            'u1': gates.U1,
            'u2': gates.U2,
            'u': gates.U3,
            'u3': gates.U3,  # Qiskit 使用 u3 作为通用单量子比特门
            's': gates.S,
            'sdg': gates.SDG,
            't': gates.T,
            'tdg': gates.TDG,
            'sx': gates.SX,
        }

        gate_lower = gate_name.lower()
        if gate_lower in gate_mapping:
            gate_class = gate_mapping[gate_lower]

            if gate_lower in ['h', 'x', 'y', 'z', 's', 'sdg', 't', 'tdg']:
                qibo_circuit.add(gate_class(qubits[0]))
            elif gate_lower in ['rx', 'ry', 'rz']:
                # Qibo rotation gates: RX(qubit, theta), RY(qubit, theta), RZ(qubit, theta)
                angle = params[0] if params else 0
                qibo_circuit.add(gate_class(qubits[0], angle))
            elif gate_lower in ['u1']:
                # Qibo U1: U1(qubit, theta)
                angle = params[0] if params else 0
                qibo_circuit.add(gate_class(qubits[0], angle))
            elif gate_lower in ['u2']:
                # Qibo U2: U2(qubit, phi, lam)
                phi = params[0] if len(params) > 0 else 0
                lam = params[1] if len(params) > 1 else 0
                qibo_circuit.add(gate_class(qubits[0], phi, lam))
            elif gate_lower in ['u', 'u3']:
                # Qibo U3: U3(qubit, theta, phi, lam)
                theta = params[0] if len(params) > 0 else 0
                phi = params[1] if len(params) > 1 else 0
                lam = params[2] if len(params) > 2 else 0
                qibo_circuit.add(gate_class(qubits[0], theta, phi, lam))
            elif gate_lower in ['cx', 'cz', 'swap']:
                qibo_circuit.add(gate_class(*qubits))
        else:
            raise GateConversionError(
                f"不支持的门类型: {gate_name}",
                suggestion=(
                    f"支持的门类型: h, x, y, z, cx, cz, swap, rx, ry, rz, "
                    f"u1, u2, u3, s, sdg, t, tdg, sx。"
                    f"如需使用 {gate_name}，请: "
                    f"1) 添加到 gate_mapping，或 "
                    f"2) 确保 optimization_level >= 1 以启用 Transpiler 分解。"
                )
            )

    def _convert_gate_to_qiskit(self, gate_name: str, gate: Any, qubits: List[int],
                               params: List[float], qiskit_circuit: QiskitCircuit) -> None:
        """将单个量子门转换为Qiskit格式."""
        # 使用Qiskit的门类
        if gate_name == 'H':
            qiskit_circuit.h(*qubits)
        elif gate_name == 'X':
            qiskit_circuit.x(*qubits)
        elif gate_name == 'Y':
            qiskit_circuit.y(*qubits)
        elif gate_name == 'Z':
            qiskit_circuit.z(*qubits)
        elif gate_name == 'CNOT':
            qiskit_circuit.cx(*qubits)
        elif gate_name == 'CZ':
            qiskit_circuit.cz(*qubits)
        elif gate_name == 'SWAP':
            qiskit_circuit.swap(*qubits)
        elif gate_name == 'RX':
            angle = params[0] if params else 0
            qiskit_circuit.rx(angle, *qubits)
        elif gate_name == 'RY':
            angle = params[0] if params else 0
            qiskit_circuit.ry(angle, *qubits)
        elif gate_name == 'RZ':
            angle = params[0] if params else 0
            qiskit_circuit.rz(angle, *qubits)
        else:
            logger.warning(f"不支持的门类型: {gate_name}，将被跳过")

    def _get_unitary(self, circuit: Union[QiskitCircuit, QiboCircuit]) -> Any:
        """获取电路的酉矩阵表示.

        Args:
            circuit: 电路（Qiskit 或 Qibo）

        Returns:
            酉矩阵（2^n × 2^n，n 为量子比特数）

        Raises:
            ImportError: Qibo 或 NumPy 未安装
            TypeError: 不支持的电路类型
        """
        if not QIBO_AVAILABLE:
            raise ImportError("Qibo 未安装，无法获取酉矩阵")

        # 导入 numpy
        try:
            import numpy as np
        except ImportError:
            raise ImportError("NumPy 未安装，无法获取酉矩阵")

        if isinstance(circuit, QiskitCircuit):
            # 使用 Qiskit 的 Operator 直接获取酉矩阵（避免转换问题）
            try:
                from qiskit.quantum_info import Operator
                import numpy as np
                operator = Operator(circuit)
                return operator.data
            except ImportError:
                # 如果 qiskit.quantum_info 不可用，回退到 Qibo 转换
                n_qubits = circuit.num_qubits
                qibo_circuit = QiboCircuit(n_qubits)

                # 转换门（使用 _convert_to_qibo 的完整逻辑）
                for instruction in circuit.data:
                    if hasattr(instruction, 'operation'):
                        gate = instruction.operation
                        qubits_list = instruction.qubits
                    else:
                        gate = instruction[0]
                        qubits_list = instruction[1]

                    try:
                        qubits = [q._index for q in qubits_list]
                    except AttributeError:
                        qubits = [circuit.qubits.index(q) for q in qubits_list]

                    params = gate.params if hasattr(gate, 'params') else []

                    # 调用门转换
                    self._convert_gate_to_qibo(gate, qubits, params, qibo_circuit)

                return qibo_circuit.unitary()

        elif isinstance(circuit, QiboCircuit):
            return circuit.unitary()

        else:
            raise TypeError(f"不支持的电路类型: {type(circuit)}")

    def _verify_equivalence(self,
                          original_unitary: Any,
                          optimized_circuit: QiboCircuit,
                          tolerance: float = 1e-8):
        """验证原始电路和优化电路的等价性.

        注意: Qiskit 和 Qibo 使用不同的量子比特排序约定
        - Qiskit: big-endian (|q_{n-1} ... q_0⟩)
        - Qibo: little-endian (|q_0 ... q_{n-1}⟩)
        此方法会自动处理这种差异。

        Args:
            original_unitary: 原始电路的酉矩阵（Qiskit）
            optimized_circuit: 优化后的 Qibo 电路
            tolerance: 数值容差

        Raises:
            ImportError: Qibo 或 NumPy 未安装
            VerificationError: 等价性验证失败
        """
        if not QIBO_AVAILABLE:
            raise ImportError("Qibo 未安装，无法进行验证")

        # 导入 numpy
        try:
            import numpy as np
        except ImportError:
            raise ImportError("NumPy 未安装，无法进行验证")

        optimized_unitary = optimized_circuit.unitary()

        # 检查维度
        if original_unitary.shape != optimized_unitary.shape:
            raise VerificationError(
                f"酉矩阵维度不匹配: {original_unitary.shape} vs {optimized_unitary.shape}",
                suggestion="优化过程中量子比特数发生了变化"
            )

        # 关键修复: Qiskit 和 Qibo 使用不同的量子比特排序约定
        # Qiskit: |q_{n-1} ... q_1 q_0⟩ (big-endian)
        # Qibo:  |q_0 q_1 ... q_{n-1}⟩ (little-endian)
        # 需要对 Qibo 的酉矩阵应用位逆序排列以匹配 Qiskit 的约定

        # 示例：对于 2 量子比特 (N=4)
        # Qiskit 列索引: |q1 q0⟩ (00, 01, 10, 11) -> (0, 1, 2, 3)
        # Qibo 列索引:  |q0 q1⟩ (00, 01, 10, 11) -> (0, 1, 2, 3)
        # 位逆序: 0(00)->0, 1(01)->2(10), 2(10)->1(01), 3(11)->3
        # 排列向量: [0, 2, 1, 3]

        # 计算位逆序排列
        n_qubits = optimized_circuit.nqubits
        dim = 2 ** n_qubits  # 酉矩阵维度

        # 生成位逆序排列
        # 对于索引 i，将其 n_qubits 位二进制表示翻转
        bit_reversal = []
        for i in range(dim):
            # 将 i 转换为 n_qubits 位二进制，翻转，再转回整数
            reversed_bits = format(i, f'0{n_qubits}b')[::-1]
            reversed_idx = int(reversed_bits, 2)
            bit_reversal.append(reversed_idx)

        # 应用位逆序排列到行和列
        # U_adj = P * U * P^T，其中 P 是位逆序排列矩阵
        # 这相当于同时重排行和列
        optimized_unitary_adjusted = optimized_unitary[np.ix_(bit_reversal, bit_reversal)]

        # 计算差异
        diff = np.linalg.norm(original_unitary - optimized_unitary_adjusted, 'fro')

        # 检查等价性（考虑全局相位）
        try:
            product = np.dot(original_unitary.conj().T, optimized_unitary_adjusted)
            first_element = product[0, 0]

            # 归一化第一元素
            if np.abs(first_element) > 1e-15:
                phase = first_element / np.abs(first_element)

                # 消除全局相位
                normalized_diff = np.linalg.norm(
                    original_unitary - phase * optimized_unitary_adjusted, 'fro'
                )
            else:
                normalized_diff = diff
        except:
            # 如果无法计算相位，使用原始差异
            normalized_diff = diff

        if normalized_diff > tolerance:
            raise VerificationError(
                f"等价性验证失败: Frobenius 范数差异 = {normalized_diff:.2e} "
                f"(容差 = {tolerance:.0e})。",
                suggestion="这表明优化过程中丢失了门或转换不正确，请检查 gate_mapping"
            )

    def _apply_optimization(self, circuit: QiskitCircuit, **kwargs) -> QiskitCircuit:
        """应用优化策略."""
        if self.strategy == OptimizationStrategy.NONE:
            return circuit
        elif self.strategy == OptimizationStrategy.QISKIT_ONLY:
            return self._apply_qiskit_optimization(circuit, **kwargs)
        elif self.strategy == OptimizationStrategy.SIM_FUSION:
            return self._apply_sim_fusion_optimization(circuit, **kwargs)
        elif self.strategy == OptimizationStrategy.HYBRID:
            return self._apply_hybrid_optimization(circuit, **kwargs)
        else:
            logger.warning(f"未知优化策略: {self.strategy}，返回原始电路")
            return circuit

    def _apply_qiskit_optimization(self, circuit: QiskitCircuit, **kwargs) -> QiskitCircuit:
        """应用Qiskit优化."""
        if not QISKIT_AVAILABLE:
            logger.warning("Qiskit不可用，跳过优化")
            return circuit

        try:
            optimization_level = kwargs.get('optimization_level', self.optimization_level)

            # 当 optimization_level=0 时，不指定 basis_gates，避免分解门
            # 只有在 optimization_level>0 时才使用 basis_gates 进行优化
            if optimization_level == 0:
                logger.info(f"应用Qiskit优化级别 {optimization_level} (无门分解)")
                optimized = transpile(
                    circuit,
                    optimization_level=optimization_level
                )
            else:
                basis_gates = kwargs.get('basis_gates', ['u3', 'cx'])
                logger.info(f"应用Qiskit优化级别 {optimization_level} (basis_gates: {basis_gates})")
                optimized = transpile(
                    circuit,
                    optimization_level=optimization_level,
                    basis_gates=basis_gates
                )
            return optimized

        except Exception as e:
            logger.error(f"Qiskit优化失败: {e}")
            return circuit

    def _apply_sim_fusion_optimization(self, circuit: QiskitCircuit, **kwargs) -> QiskitCircuit:
        """应用Sim-Fusion优化."""
        try:
            # 先转换为Qibo，应用Sim-Fusion，再转回Qiskit
            qibo_circuit = self._convert_to_qibo(circuit)

            if hasattr(self, '_sim_fusion'):
                optimized_qibo = self._sim_fusion.sim_fusion(qibo_circuit)
                return self._convert_qibo_to_qiskit(optimized_qibo)
            else:
                logger.warning("Sim-Fusion不可用，跳过优化")
                return circuit

        except Exception as e:
            logger.error(f"Sim-Fusion优化失败: {e}")
            return circuit

    def _apply_hybrid_optimization(self, circuit: QiskitCircuit, **kwargs) -> QiskitCircuit:
        """应用混合优化策略."""
        # 先应用Qiskit优化，再应用Sim-Fusion
        qiskit_optimized = self._apply_qiskit_optimization(circuit, **kwargs)
        sim_fusion_optimized = self._apply_sim_fusion_optimization(qiskit_optimized, **kwargs)
        return sim_fusion_optimized