# hybrid-optimizer-interface Specification

## Purpose
TBD - created by archiving change create-hybrid-optimizer-interface. Update Purpose after archive.
## Requirements
### Requirement: Unified Hybrid Optimization Interface
系统 SHALL 提供一个统一的函数接口，将混合优化策略（TKET预处理 + Qibo Fusion）封装为单一函数调用。

#### Scenario: 简单的电路优化调用
- **WHEN** 用户调用 `optimize_qibo_circuit_hybrid(circuit)`
- **AND** 输入有效的 Qibo Circuit 对象
- **THEN** 系统返回经过混合优化的 Qibo Circuit
- **AND** 电路包含 TKET 和 Qibo Fusion 的双重优化效果

#### Scenario: 带统计信息的优化调用
- **WHEN** 用户调用 `optimize_qibo_circuit_hybrid(circuit, return_stats=True)`
- **THEN** 系统返回优化后的电路和统计信息字典
- **AND** 统计信息包含门数量变化、深度变化、优化时间等

#### Scenario: 详细模式输出
- **WHEN** 用户调用 `optimize_qibo_circuit_hybrid(circuit, verbose=True)`
- **THEN** 系统输出优化过程的详细日志
- **AND** 包含 TKET 预处理和 Qibo Fusion 各阶段的执行信息

### Requirement: Mixed Optimization Pipeline
系统 SHALL 按照既定顺序执行 TKET 预处理和 Qibo Fusion 优化。

#### Scenario: TKET 预处理阶段
- **WHEN** 系统执行混合优化
- **THEN** 首先应用 TKET simulation 模式优化
- **AND** 执行门重组、代数简化、门压缩等操作
- **AND** 保持 U3/TK1 融合结构避免过度分解

#### Scenario: Qibo Fusion 阶段
- **WHEN** TKET 预处理完成
- **THEN** 在优化后的电路上调用 Qibo 的 `fuse()` 方法
- **AND** 执行矩阵层面的运算融合优化
- **AND** 优化内存访问模式和计算效率

### Requirement: Optimization Statistics Collection
系统 SHALL 收集并报告混合优化的详细性能指标。

#### Scenario: 门数量和深度统计
- **WHEN** 混合优化执行完成
- **THEN** 记录原始电路的门数量和深度
- **AND** 记录优化后电路的门数量和深度
- **AND** 计算百分比变化

#### Scenario: 时间性能统计
- **WHEN** 混合优化执行完成
- **THEN** 分别记录 TKET 预处理时间
- **AND** 记录 Qibo Fusion 处理时间
- **AND** 计算总体优化时间

### Requirement: Error Handling and Validation
系统 SHALL 提供健壮的错误处理和输入验证机制。

#### Scenario: 输入电路验证
- **WHEN** 用户输入电路到优化函数
- **THEN** 验证输入是否为有效的 Qibo Circuit 对象
- **AND** 检查电路中所有门类型是否受支持
- **AND** 对不支持的门给出明确的错误信息

#### Scenario: 优化过程异常处理
- **WHEN** 优化过程中发生错误
- **THEN** 提供详细的错误信息和建议
- **AND** 在可能的情况下提供降级方案
- **AND** 保护用户原始数据不受损失

