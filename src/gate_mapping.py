"""量子门类型映射和转换表.

这个模块定义了不同框架之间的量子门类型映射关系，以及门转换的具体实现。
"""

from typing import Dict, List, Type, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 动态导入框架
try:
    from qibo import gates as qibo_gates
    QIBO_AVAILABLE = True
except ImportError:
    QIBO_AVAILABLE = False
    qibo_gates = None

try:
    from qiskit.circuit.library import (HGate, XGate, YGate, ZGate, CXGate, CZGate,
                                       RXGate, RYGate, RZGate, U1Gate, U2Gate, U3Gate,
                                       SGate, SdgGate, TGate, TdgGate, SXGate, SwapGate)
    from qiskit.circuit import Gate as QiskitGate
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    HGate = XGate = YGate = ZGate = CXGate = CZGate = None
    RXGate = RYGate = RZGate = U1Gate = U2Gate = U3Gate = None
    SGate = SdgGate = TGate = TdgGate = SXGate = SwapGate = None
    QiskitGate = None

try:
    from pytket.circuit import OpType
    TKET_AVAILABLE = True
except ImportError:
    TKET_AVAILABLE = False
    OpType = None


class GateCategory(Enum):
    """量子门类别."""
    SINGLE_QUBIT = "single_qubit"
    TWO_QUBIT = "two_qubit"
    MULTI_QUBIT = "multi_qubit"
    PARAMETERIZED = "parameterized"
    MEASUREMENT = "measurement"
    BARRIER = "barrier"


@dataclass
class GateInfo:
    """量子门信息."""
    name: str
    category: GateCategory
    num_qubits: int
    num_params: int
    description: str
    supported_frameworks: List[str]


class GateMappingRegistry:
    """量子门映射注册表."""

    def __init__(self):
        """初始化门映射注册表."""
        self._qiskit_to_qibo_map: Dict[Type, Type] = {}
        self._qibo_to_qiskit_map: Dict[Type, Type] = {}
        self._qiskit_to_tket_map: Dict[Type, OpType] = {}
        self._tket_to_qiskit_map: Dict[OpType, Type] = {}
        self._name_mapping: Dict[str, Dict[str, Any]] = {}

        self._initialize_mappings()

    def _initialize_mappings(self):
        """初始化门类型映射."""
        # Qiskit到Qibo的映射
        if QIBO_AVAILABLE and QISKIT_AVAILABLE:
            self._qiskit_to_qibo_map.update({
                HGate: qibo_gates.H,
                XGate: qibo_gates.X,
                YGate: qibo_gates.Y,
                ZGate: qibo_gates.Z,
                CXGate: qibo_gates.CNOT,
                CZGate: qibo_gates.CZ,
                SwapGate: qibo_gates.SWAP,
                RXGate: qibo_gates.RX,
                RYGate: qibo_gates.RY,
                RZGate: qibo_gates.RZ,
                U1Gate: qibo_gates.U1,
                U2Gate: qibo_gates.U2,
                U3Gate: qibo_gates.U3,
                SGate: qibo_gates.S,
                SdgGate: qibo_gates.SDG,
                TGate: qibo_gates.T,
                TdgGate: qibo_gates.TDG,
                SXGate: qibo_gates.SX,
            })

            # Qibo到Qiskit的映射
            self._qibo_to_qiskit_map.update({
                qibo_gates.H: HGate,
                qibo_gates.X: XGate,
                qibo_gates.Y: YGate,
                qibo_gates.Z: ZGate,
                qibo_gates.CNOT: CXGate,
                qibo_gates.CZ: CZGate,
                qibo_gates.SWAP: SwapGate,
                qibo_gates.RX: RXGate,
                qibo_gates.RY: RYGate,
                qibo_gates.RZ: RZGate,
                qibo_gates.U1: U1Gate,
                qibo_gates.U2: U2Gate,
                qibo_gates.U3: U3Gate,
                qibo_gates.S: SGate,
                qibo_gates.SDG: SdgGate,
                qibo_gates.T: TGate,
                qibo_gates.TDG: TdgGate,
                qibo_gates.SX: SXGate,
            })

        # Qiskit到TKET的映射
        if QISKIT_AVAILABLE and TKET_AVAILABLE:
            self._qiskit_to_tket_map.update({
                HGate: OpType.H,
                XGate: OpType.X,
                YGate: OpType.Y,
                ZGate: OpType.Z,
                CXGate: OpType.CX,
                CZGate: OpType.CZ,
                SwapGate: OpType.SWAP,
                RXGate: OpType.Rx,
                RYGate: OpType.Ry,
                RZGate: OpType.Rz,
            })

        # TKET到Qiskit的映射
        if QISKIT_AVAILABLE and TKET_AVAILABLE:
            self._tket_to_qiskit_map.update({
                OpType.H: HGate,
                OpType.X: XGate,
                OpType.Y: YGate,
                OpType.Z: ZGate,
                OpType.CX: CXGate,
                OpType.CZ: CZGate,
                OpType.SWAP: SwapGate,
                OpType.Rx: RXGate,
                OpType.Ry: RYGate,
                OpType.Rz: RZGate,
            })

        # 名称映射（用于字符串形式的门识别）
        self._name_mapping.update({
            # 单量子比特门
            'h': GateInfo('h', GateCategory.SINGLE_QUBIT, 1, 0, 'Hadamard gate', ['qibo', 'qiskit', 'tket']),
            'x': GateInfo('x', GateCategory.SINGLE_QUBIT, 1, 0, 'Pauli-X gate', ['qibo', 'qiskit', 'tket']),
            'y': GateInfo('y', GateCategory.SINGLE_QUBIT, 1, 0, 'Pauli-Y gate', ['qibo', 'qiskit', 'tket']),
            'z': GateInfo('z', GateCategory.SINGLE_QUBIT, 1, 0, 'Pauli-Z gate', ['qibo', 'qiskit', 'tket']),
            's': GateInfo('s', GateCategory.SINGLE_QUBIT, 1, 0, 'Phase gate (S)', ['qibo', 'qiskit', 'tket']),
            'sdg': GateInfo('sdg', GateCategory.SINGLE_QUBIT, 1, 0, 'Adjoint S gate', ['qibo', 'qiskit']),
            't': GateInfo('t', GateCategory.SINGLE_QUBIT, 1, 0, 'T gate', ['qibo', 'qiskit', 'tket']),
            'tdg': GateInfo('tdg', GateCategory.SINGLE_QUBIT, 1, 0, 'Adjoint T gate', ['qibo', 'qiskit']),
            'sx': GateInfo('sx', GateCategory.SINGLE_QUBIT, 1, 0, 'Square root of X gate', ['qibo', 'qiskit']),

            # 参数化单量子比特门
            'rx': GateInfo('rx', GateCategory.PARAMETERIZED, 1, 1, 'X-axis rotation', ['qibo', 'qiskit', 'tket']),
            'ry': GateInfo('ry', GateCategory.PARAMETERIZED, 1, 1, 'Y-axis rotation', ['qibo', 'qiskit', 'tket']),
            'rz': GateInfo('rz', GateCategory.PARAMETERIZED, 1, 1, 'Z-axis rotation', ['qibo', 'qiskit', 'tket']),
            'u1': GateInfo('u1', GateCategory.PARAMETERIZED, 1, 1, 'U1 gate', ['qibo', 'qiskit']),
            'u2': GateInfo('u2', GateCategory.PARAMETERIZED, 1, 2, 'U2 gate', ['qibo', 'qiskit']),
            'u3': GateInfo('u3', GateCategory.PARAMETERIZED, 1, 3, 'U3 gate', ['qibo', 'qiskit']),

            # 双量子比特门
            'cx': GateInfo('cx', GateCategory.TWO_QUBIT, 2, 0, 'CNOT gate', ['qibo', 'qiskit', 'tket']),
            'cnot': GateInfo('cnot', GateCategory.TWO_QUBIT, 2, 0, 'CNOT gate (alias)', ['qibo', 'tket']),
            'cz': GateInfo('cz', GateCategory.TWO_QUBIT, 2, 0, 'Controlled-Z gate', ['qibo', 'qiskit', 'tket']),
            'swap': GateInfo('swap', GateCategory.TWO_QUBIT, 2, 0, 'SWAP gate', ['qibo', 'qiskit', 'tket']),

            # 多量子比特门
            'ccx': GateInfo('ccx', GateCategory.MULTI_QUBIT, 3, 0, 'Toffoli gate', ['qiskit']),
            'cswap': GateInfo('cswap', GateCategory.MULTI_QUBIT, 3, 0, 'Controlled SWAP gate', ['qiskit']),
        })

    def get_gate_info(self, gate_name: str) -> Optional[GateInfo]:
        """获取门信息.

        Args:
            gate_name: 门名称

        Returns:
            门信息，如果不存在返回None
        """
        return self._name_mapping.get(gate_name.lower())

    def is_gate_supported(self, gate_name: str, framework: str) -> bool:
        """检查门在指定框架中是否支持.

        Args:
            gate_name: 门名称
            framework: 框架名称 ('qibo', 'qiskit', 'tket')

        Returns:
            是否支持
        """
        gate_info = self.get_gate_info(gate_name)
        if not gate_info:
            return False
        return framework in gate_info.supported_frameworks

    def get_qiskit_to_qibo_mapping(self, qiskit_gate_class: Type) -> Optional[Type]:
        """获取Qiskit门到Qibo门的映射.

        Args:
            qiskit_gate_class: Qiskit门类

        Returns:
            Qibo门类，如果不存在返回None
        """
        return self._qiskit_to_qibo_map.get(qiskit_gate_class)

    def get_qibo_to_qiskit_mapping(self, qibo_gate_class: Type) -> Optional[Type]:
        """获取Qibo门到Qiskit门的映射.

        Args:
            qibo_gate_class: Qibo门类

        Returns:
            Qiskit门类，如果不存在返回None
        """
        return self._qibo_to_qiskit_map.get(qibo_gate_class)

    def get_supported_gates(self, framework: str) -> List[GateInfo]:
        """获取指定框架支持的所有门.

        Args:
            framework: 框架名称

        Returns:
            支持的门信息列表
        """
        return [gate_info for gate_info in self._name_mapping.values()
                if framework in gate_info.supported_frameworks]

    def get_gates_by_category(self, category: GateCategory) -> List[GateInfo]:
        """按类别获取门列表.

        Args:
            category: 门类别

        Returns:
            该类别的门信息列表
        """
        return [gate_info for gate_info in self._name_mapping.values()
                if gate_info.category == category]

    def validate_gate_parameters(self, gate_name: str, params: List[float]) -> bool:
        """验证门参数的有效性.

        Args:
            gate_name: 门名称
            params: 参数列表

        Returns:
            参数是否有效
        """
        gate_info = self.get_gate_info(gate_name)
        if not gate_info:
            return False

        return len(params) == gate_info.num_params

    def get_conversion_path(self, source_framework: str, target_framework: str,
                          gate_name: str) -> Optional[List[str]]:
        """获取门转换路径.

        Args:
            source_framework: 源框架
            target_framework: 目标框架
            gate_name: 门名称

        Returns:
            转换路径列表，如果无法转换返回None
        """
        gate_info = self.get_gate_info(gate_name)
        if not gate_info:
            return None

        if source_framework in gate_info.supported_frameworks and \
           target_framework in gate_info.supported_frameworks:
            return [source_framework, target_framework]

        return None

    def add_custom_gate(self, gate_info: GateInfo,
                      qiskit_class: Optional[Type] = None,
                      qibo_class: Optional[Type] = None,
                      tket_op: Optional[OpType] = None):
        """添加自定义门映射.

        Args:
            gate_info: 门信息
            qiskit_class: Qiskit门类
            qibo_class: Qibo门类
            tket_op: TKET操作类型
        """
        # 添加到名称映射
        self._name_mapping[gate_info.name.lower()] = gate_info

        # 添加到框架映射
        if qiskit_class and qibo_class:
            self._qiskit_to_qibo_map[qiskit_class] = qibo_class
            self._qibo_to_qiskit_map[qibo_class] = qiskit_class

        if qiskit_class and tket_op:
            self._qiskit_to_tket_map[qiskit_class] = tket_op

        if tket_op and qiskit_class:
            self._tket_to_qiskit_map[tket_op] = qiskit_class


# 全局门映射注册表实例
gate_registry = GateMappingRegistry()


def get_supported_gates_summary() -> Dict[str, List[str]]:
    """获取各框架支持的门汇总.

    Returns:
        框架到支持门列表的映射
    """
    frameworks = ['qibo', 'qiskit', 'tket']
    summary = {}

    for framework in frameworks:
        gates = gate_registry.get_supported_gates(framework)
        summary[framework] = [gate.name for gate in gates]

    return summary


def print_gate_compatibility_table():
    """打印门兼容性表格."""
    frameworks = ['qibo', 'qiskit', 'tket']

    print("门类型兼容性表:")
    print("-" * 80)
    print(f"{'门名称':<10} {'类别':<15} {'Qibo':<6} {'Qiskit':<8} {'TKET':<6} {'描述':<20}")
    print("-" * 80)

    all_gates = set()
    for framework in frameworks:
        all_gates.update([gate.name for gate in gate_registry.get_supported_gates(framework)])

    for gate_name in sorted(all_gates):
        gate_info = gate_registry.get_gate_info(gate_name)
        if not gate_info:
            continue

        qibo_support = "✓" if "qibo" in gate_info.supported_frameworks else "✗"
        qiskit_support = "✓" if "qiskit" in gate_info.supported_frameworks else "✗"
        tket_support = "✓" if "tket" in gate_info.supported_frameworks else "✗"

        print(f"{gate_info['name']:<10} {gate_info['category'].value:<15} "
              f"{qibo_support:<6} {qiskit_support:<8} {tket_support:<6} "
              f"{gate_info['description']:<20}")

    print("-" * 80)


class GateConverter:
    """量子门转换器."""

    def __init__(self, registry: Optional[GateMappingRegistry] = None):
        """初始化门转换器.

        Args:
            registry: 门映射注册表，默认使用全局实例
        """
        self.registry = registry or gate_registry

    def convert_gate_parameters(self, gate_name: str, params: List[float],
                              source_framework: str, target_framework: str) -> List[float]:
        """转换门参数.

        Args:
            gate_name: 门名称
            params: 源框架的参数
            source_framework: 源框架
            target_framework: 目标框架

        Returns:
            目标框架的参数
        """
        # 大多数情况下参数是相同的，特殊处理可以在这里添加
        if gate_name.lower() in ['u1', 'u2', 'u3']:
            # U系列门的参数在不同框架中可能有不同的约定
            if source_framework == 'qiskit' and target_framework == 'qibo':
                return params  # 通常相同
            elif source_framework == 'qibo' and target_framework == 'qiskit':
                return params  # 通常相同

        return params

    def can_convert(self, gate_name: str, source_framework: str,
                   target_framework: str) -> bool:
        """检查是否可以转换门.

        Args:
            gate_name: 门名称
            source_framework: 源框架
            target_framework: 目标框架

        Returns:
            是否可以转换
        """
        path = self.registry.get_conversion_path(source_framework, target_framework, gate_name)
        return path is not None

    def get_conversion_info(self, gate_name: str) -> Optional[Dict[str, Any]]:
        """获取门的转换信息.

        Args:
            gate_name: 门名称

        Returns:
            转换信息字典
        """
        gate_info = self.registry.get_gate_info(gate_name)
        if not gate_info:
            return None

        return {
            'name': gate_info.name,
            'category': gate_info.category.value,
            'num_qubits': gate_info.num_qubits,
            'num_params': gate_info.num_params,
            'supported_frameworks': gate_info.supported_frameworks,
            'description': gate_info.description
        }