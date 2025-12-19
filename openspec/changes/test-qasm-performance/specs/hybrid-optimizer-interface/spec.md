# hybrid-optimizer-interface Specification

## Purpose
提供统一的混合量子电路优化接口，整合TKET预处理和Qibo Fusion优势。

## MODIFIED Requirements

### Requirement: Unified Hybrid Optimization Interface
系统 SHALL 提供一个统一的函数接口，将混合优化策略（TKET预处理 + Qibo Fusion）封装为单一函数调用，并扩展支持QASM电路优化。

#### Scenario: QASM电路的混合优化
- **WHEN** 用户通过QASM加载器传入QASM电路到混合优化函数
- **AND** QASM电路包含标准量子门操作
- **THEN** 系统返回经过混合优化的Qibo Circuit
- **AND** 优化效果与原始生成电路保持一致

#### Scenario: QASM电路的统计信息收集
- **WHEN** 用户对QASM电路调用 `optimize_qibo_circuit_hybrid(circuit, return_stats=True)`
- **THEN** 系统返回优化后的电路和针对QASM电路的统计信息
- **AND** 统计信息包含QASM特有的特征分析（如算法类型、复杂度指标）