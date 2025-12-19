"""Sim-Fusion Hybrid Optimizer.

This module provides a simple, user-friendly function that encapsulates the sim-fusion
hybrid optimization strategy. The function takes a Qibo circuit as input and returns
an optimized circuit after applying TKET preprocessing followed by Qibo fusion,
specifically using the simulation-optimized "sim-fusion" strategy.
"""

from typing import Optional, Tuple, Union
import time

from qibo import Circuit as QiboCircuit

from optimization_engine import TketOptimizer
from hybrid_optimizer import optimize_qibo_circuit_hybrid, HybridOptimizationStats


class SimFusionOptimizationStats:
    """Detailed statistics for sim-fusion optimization process."""

    def __init__(self,
                 original_gates: int = 0,
                 original_depth: int = 0,
                 optimized_gates: int = 0,
                 optimized_depth: int = 0,
                 tket_time: float = 0.0,
                 fusion_time: float = 0.0,
                 total_time: float = 0.0):
        """Initialize sim-fusion optimization statistics.

        Args:
            original_gates: Number of gates in original circuit
            original_depth: Depth of original circuit
            optimized_gates: Number of gates in optimized circuit
            optimized_depth: Depth of optimized circuit
            tket_time: Time taken for TKET preprocessing
            fusion_time: Time taken for Qibo fusion
            total_time: Total optimization time
        """
        self.original_gates = original_gates
        self.original_depth = original_depth
        self.optimized_gates = optimized_gates
        self.optimized_depth = optimized_depth
        self.tket_time = tket_time
        self.fusion_time = fusion_time
        self.total_time = total_time

    @property
    def gate_reduction_percent(self) -> float:
        """Calculate gate reduction percentage."""
        return ((self.original_gates - self.optimized_gates) / self.original_gates * 100) if self.original_gates > 0 else 0.0

    @property
    def depth_reduction_percent(self) -> float:
        """Calculate depth reduction percentage."""
        return ((self.original_depth - self.optimized_depth) / self.original_depth * 100) if self.original_depth > 0 else 0.0

    @property
    def efficiency_score(self) -> float:
        """Calculate optimization efficiency score (gate reduction % per second)."""
        return (self.gate_reduction_percent / self.total_time) if self.total_time > 0 else 0.0

    def to_dict(self) -> dict:
        """Convert statistics to dictionary format."""
        return {
            'original_gates': self.original_gates,
            'optimized_gates': self.optimized_gates,
            'original_depth': self.original_depth,
            'optimized_depth': self.optimized_depth,
            'gate_reduction_percent': self.gate_reduction_percent,
            'depth_reduction_percent': self.depth_reduction_percent,
            'tket_time': self.tket_time,
            'fusion_time': self.fusion_time,
            'total_time': self.total_time,
            'efficiency_score': self.efficiency_score
        }

    def __str__(self) -> str:
        """String representation of statistics."""
        return (f"SimFusionOptimizationStats("
                f"gate_reduction={self.gate_reduction_percent:.1f}%, "
                f"depth_reduction={self.depth_reduction_percent:.1f}%, "
                f"tket_time={self.tket_time:.4f}s, "
                f"fusion_time={self.fusion_time:.4f}s, "
                f"total_time={self.total_time:.4f}s, "
                f"efficiency={self.efficiency_score:.1f})")


def optimize_with_sim_fusion(circuit: QiboCircuit,
                           return_stats: bool = False,
                           verbose: bool = False) -> Union[QiboCircuit, Tuple[QiboCircuit, SimFusionOptimizationStats]]:
    """优化Qibo电路使用sim-fusion混合优化策略。

    此函数封装了完整的sim-fusion优化流程，包括TKET预处理和Qibo融合优化，
    专门针对量子模拟器性能进行优化。

    优化策略序列：
    1. RemoveRedundancies - 移除冗余门
    2. CommuteThroughMultis - 门重组以发现可消除的门对
    3. CliffordSimp - 简化Clifford门序列
    4. FullPeepholeOptimise - 深度优化
    5. SquashTK1 - 将单量子比特门合并为TK1形式
    6. RemoveRedundancies - 最终清理
    7. Qibo Fusion - 矩阵层面的运算融合

    Args:
        circuit: 输入的Qibo Circuit对象
        return_stats: 是否返回详细统计信息，默认False
        verbose: 是否输出详细优化过程信息，默认False

    Returns:
        如果return_stats=False，返回优化后的Qibo Circuit
        如果return_stats=True，返回(优化后的电路, 统计信息对象)元组

    Raises:
        ValueError: 当输入不是有效的Qibo Circuit时
        RuntimeError: 当优化过程中发生错误时

    Examples:
        >>> from qibo import Circuit, gates
        >>> from sim_fusion_optimizer import optimize_with_sim_fusion
        >>>
        >>> # 创建简单电路
        >>> circuit = Circuit(2)
        >>> circuit.add(gates.H(0))
        >>> circuit.add(gates.CNOT(0, 1))
        >>> circuit.add(gates.H(1))
        >>>
        >>> # 基本优化
        >>> optimized = optimize_with_sim_fusion(circuit)
        >>>
        >>> # 带统计信息的优化
        >>> optimized, stats = optimize_with_sim_fusion(circuit, return_stats=True)
        >>> print(f"门减少: {stats.gate_reduction_percent:.1f}%")
        >>> print(f"总时间: {stats.total_time:.4f}s")
        >>>
        >>> # 详细输出模式
        >>> optimized = optimize_with_sim_fusion(circuit, verbose=True)
    """

    # 输入验证
    if not isinstance(circuit, QiboCircuit):
        raise ValueError("输入必须是一个有效的 Qibo Circuit 对象")

    if circuit.ngates == 0:
        if verbose:
            print("警告: 电路为空，直接返回原电路")
        if return_stats:
            empty_stats = SimFusionOptimizationStats()
            return circuit, empty_stats
        return circuit

    if verbose:
        print("开始 sim-fusion 混合优化...")
        print(f"原始电路统计: {circuit.ngates} 个门")

    try:
        # 使用现有的hybrid_optimizer实现sim-fusion策略
        start_time = time.time()

        # 调用现有的混合优化函数，指定sim-fusion策略
        optimized_circuit, hybrid_stats = optimize_qibo_circuit_hybrid(
            circuit=circuit,
            strategy="sim-fusion",
            return_stats=True,
            verbose=verbose
        )

        total_time = time.time() - start_time

        # 创建详细统计信息
        detailed_stats = SimFusionOptimizationStats(
            original_gates=hybrid_stats.original_gates,
            original_depth=hybrid_stats.original_depth,
            optimized_gates=hybrid_stats.optimized_gates,
            optimized_depth=hybrid_stats.optimized_depth,
            tket_time=hybrid_stats.tket_compile_time,
            fusion_time=hybrid_stats.fusion_time,
            total_time=total_time
        )

        if verbose:
            print(f"优化完成!")
            print(f"  最终电路统计: {optimized_circuit.ngates} 个门, ")
            print(f"  门减少: {detailed_stats.gate_reduction_percent:.1f}%")
            print(f"  深度减少: {detailed_stats.depth_reduction_percent:.1f}%")
            print(f"  TKET预处理时间: {detailed_stats.tket_time:.4f}s")
            print(f"  Qibo融合时间: {detailed_stats.fusion_time:.4f}s")
            print(f"  总优化时间: {detailed_stats.total_time:.4f}s")
            print(f"  优化效率: {detailed_stats.efficiency_score:.1f}%/s")

        # 返回结果
        if return_stats:
            return optimized_circuit, detailed_stats
        else:
            return optimized_circuit

    except Exception as e:
        error_msg = f"Sim-fusion优化过程中发生错误: {str(e)}"

        if verbose:
            print(f"错误: {error_msg}")
            print("尝试回退到纯Qibo Fusion策略...")

        # 回退策略：纯Qibo Fusion
        try:
            if verbose:
                print("应用回退策略：纯Qibo Fusion")

            fallback_start = time.time()

            # 直接应用Qibo fusion
            fallback_circuit = circuit.copy()
            fallback_circuit = fallback_circuit.fuse()

            fallback_time = time.time() - fallback_start

            # 创建回退统计信息
            fallback_stats = SimFusionOptimizationStats(
                original_gates=circuit.ngates,
                original_depth=circuit.depth,
                optimized_gates=fallback_circuit.ngates,
                optimized_depth=fallback_circuit.depth,
                tket_time=0.0,
                fusion_time=fallback_time,
                total_time=fallback_time
            )

            if verbose:
                print(f"回退策略完成!")
                print(f"  回退后电路统计: {fallback_circuit.ngates} 个门, ")
                print(f"  回退时间: {fallback_time:.4f}s")

            if return_stats:
                return fallback_circuit, fallback_stats
            else:
                return fallback_circuit

        except Exception as fallback_error:
            error_msg = f"所有优化策略均失败: 原始错误={str(e)}, 回退错误={str(fallback_error)}"
            raise RuntimeError(error_msg) from e


# 向后兼容的别名
SimFusionOptimizer = optimize_with_sim_fusion


def quick_optimize(circuit: QiboCircuit) -> QiboCircuit:
    """快速优化接口，仅返回优化后的电路。

    这是optimize_with_sim_fusion(circuit)的简化版本，用于最常用的场景。

    Args:
        circuit: 输入的Qibo Circuit对象

    Returns:
        优化后的Qibo Circuit

    Examples:
        >>> from qibo import Circuit, gates
        >>> from sim_fusion_optimizer import quick_optimize
        >>>
        >>> circuit = Circuit(2)
        >>> circuit.add(gates.H(0))
        >>> circuit.add(gates.CNOT(0, 1))
        >>>
        >>> optimized = quick_optimize(circuit)
    """
    return optimize_with_sim_fusion(circuit, return_stats=False, verbose=False)


def optimize_and_analyze(circuit: QiboCircuit, verbose: bool = True) -> Tuple[QiboCircuit, SimFusionOptimizationStats]:
    """优化并分析电路，返回优化结果和详细统计。

    这是optimize_with_sim_fusion(circuit, return_stats=True, verbose=True)的
    便捷包装函数。

    Args:
        circuit: 输入的Qibo Circuit对象
        verbose: 是否输出详细信息，默认True

    Returns:
        (优化后的电路, 统计信息对象)元组

    Examples:
        >>> from qibo import Circuit, gates
        >>> from sim_fusion_optimizer import optimize_and_analyze
        >>>
        >>> circuit = Circuit(2)
        >>> circuit.add(gates.H(0))
        >>> circuit.add(gates.CNOT(0, 1))
        >>>
        >>> optimized, stats = optimize_and_analyze(circuit)
        >>> print(f"优化效果: {stats.gate_reduction_percent:.1f}% 门减少")
    """
    return optimize_with_sim_fusion(circuit, return_stats=True, verbose=verbose)