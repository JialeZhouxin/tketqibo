# Sim-Fusion Standalone Module Specification

## ADDED Requirements

### Requirement: SF-001 - Core Sim-Fusion Optimization Function
系统 SHALL 提供一个独立的 `sim_fusion()` 函数作为主要入口点，该函数 SHALL 封装完整的 sim-fusion 混合优化策略，包括 TKET 预处理和 Qibo fusion 优化。

#### Scenario: 基本的电路优化调用
- **WHEN** 用户调用 `sim_fusion(circuit)`
- **AND** 输入有效的 Qibo Circuit 对象
- **THEN** 系统 SHALL 返回经过 sim-fusion 优化的 Qibo Circuit
- **AND** 优化后的电路门数量 SHALL 小于或等于原始电路
- **AND** 系统 SHALL 记录优化过程的详细时间信息

#### Scenario: 带统计信息的优化调用
- **WHEN** 用户调用 `sim_fusion(circuit, return_stats=True)`
- **THEN** 系统 SHALL 返回优化后的电路和 SimFusionStats 对象
- **AND** 统计信息 SHALL 包含原始和优化后的门数量、深度、时间分解等详细信息

### Requirement: SF-002 - Optimization Statistics Tracking
系统 SHALL 提供 `SimFusionStats` 类来跟踪和报告优化的详细统计信息，包括门数量变化、深度变化、各个优化阶段的时间分解等指标。

#### Scenario: 优化统计信息生成
- **WHEN** sim-fusion 优化执行完成
- **THEN** 系统 SHALL 创建 SimFusionStats 对象
- **AND** 对象 SHALL 包含 original_gates、optimized_gates、gate_reduction_percent 等属性
- **AND** 系统 SHALL 计算 tket_time、fusion_time、total_time 等时间指标
- **AND** 系统 SHALL 提供 efficiency_score 性能评估指标

#### Scenario: 统计信息序列化
- **WHEN** 用户调用 stats.to_dict()
- **THEN** 系统 SHALL 返回包含所有统计信息的字典
- **AND** 字典 SHALL 包含所有数值指标和计算属性

### Requirement: SF-003 - TKET Integration and Strategy
系统 SHALL 直接集成 TKET 优化器，实现 sim-fusion 特定的优化策略序列，包括移除冗余门、门重组、Clifford 简化等步骤。

#### Scenario: TKET 预处理应用
- **WHEN** sim-fusion 优化开始执行
- **THEN** 系统 SHALL 按 RemoveRedundancies -> CommuteThroughMultis -> CliffordSimp -> FullPeepholeOptimise -> SquashTK1 -> RemoveRedundancies 的顺序应用 TKET 优化
- **AND** 系统 SHALL 正确处理 Qibo Circuit 到 TKET Circuit 的转换
- **AND** 系统 SHALL 在优化后将结果转换回 Qibo Circuit 格式

#### Scenario: TKET 处理时间测量
- **WHEN** TKET 优化执行时
- **THEN** 系统 SHALL 精确测量每个优化步骤的时间
- **AND** 系统 SHALL 记录总体 TKET 预处理时间

### Requirement: SF-004 - Fallback Mechanism
系统 SHALL 在 TKET 不可用或编译失败时提供回退机制，确保优化仍能使用纯 Qibo fusion 策略进行。

#### Scenario: TKET 失败回退
- **WHEN** TKET 优化过程中发生异常
- **AND** fallback 参数设置为 True
- **THEN** 系统 SHALL 捕获异常并记录错误信息
- **AND** 系统 SHALL 自动切换到纯 Qibo fusion 策略
- **AND** 系统 SHALL 使用 circuit.fuse() 方法进行基础融合优化

#### Scenario: 回退统计信息
- **WHEN** 使用回退策略完成优化
- **THEN** 系统 SHALL 生成相应的 SimFusionStats 对象
- **AND** tket_time SHALL 设置为 0.0
- **AND** fusion_time SHALL 记录 Qibo fusion 的执行时间

### Requirement: SF-005 - Convenience Functions
系统 SHALL 提供便捷函数以支持不同的使用模式，包括快速优化接口、带统计信息的接口等。

#### Scenario: 快速优化接口
- **WHEN** 用户调用 `quick_sim_fusion(circuit)`
- **THEN** 系统 SHALL 调用 `sim_fusion(circuit, return_stats=False, verbose=False)`
- **AND** 仅返回优化后的电路对象

#### Scenario: 带统计信息的便捷接口
- **WHEN** 用户调用 `sim_fusion_with_stats(circuit)`
- **THEN** 系统 SHALL 调用 `sim_fusion(circuit, return_stats=True, verbose=True)`
- **AND** 返回优化后的电路和详细统计信息

### Requirement: SF-006 - Error Handling and Validation
系统 SHALL 实现健壮的错误处理和输入验证机制，对无效输入提供清晰的错误信息，并优雅地处理各种异常情况。

#### Scenario: 输入类型验证
- **WHEN** 用户传入非 Circuit 对象到 sim_fusion 函数
- **THEN** 系统 SHALL 抛出 ValueError 异常
- **AND** 错误信息 SHALL 明确指出输入必须是 Qibo Circuit 对象

#### Scenario: 空电路处理
- **WHEN** 用户传入空电路（ngates = 0）
- **THEN** 系统 SHALL 直接返回原电路
- **AND** 如果 return_stats=True，系统 SHALL 返回空的统计信息对象

#### Scenario: TKET 不可用处理
- **WHEN** 系统检测到 TKET 模块不可用
- **THEN** 系统 SHALL 记录警告信息
- **AND** 系统 SHALL 自动使用 Qibo fusion 回退策略
- **AND** 系统 SHALL 在 verbose 模式下通知用户

### Requirement: SF-007 - Verbose Output Support
系统 SHALL 支持详细的优化过程输出用于调试和分析，显示各个优化阶段的详细信息。

#### Scenario: 详细优化过程输出
- **WHEN** 用户设置 verbose=True
- **AND** sim-fusion 优化开始执行
- **THEN** 系统 SHALL 输出 "开始 sim-fusion 混合优化..." 消息
- **AND** 系统 SHALL 显示原始电路的门数量统计
- **AND** 系统 SHALL 报告 TKET 预处理的进度和结果
- **AND** 系统 SHALL 显示 Qibo fusion 的执行情况
- **AND** 系统 SHALL 输出最终的优化结果统计

#### Scenario: 错误时的详细输出
- **WHEN** verbose=True 且优化过程发生错误
- **THEN** 系统 SHALL 输出详细的错误信息
- **AND** 系统 SHALL 说明回退策略的执行情况

### Requirement: SF-008 - Type Annotations and Documentation
系统 SHALL 为所有公共接口提供完整的类型注解和中文文档字符串，以改善代码的可读性和 IDE 支持。

#### Scenario: 函数类型注解
- **WHEN** 定义公共函数时
- **THEN** 系统 SHALL 使用 Union[QiboCircuit, Tuple[QiboCircuit, SimFusionStats]] 等类型注解
- **AND** 所有参数 SHALL 有明确的类型声明
- **AND** 返回值类型 SHALL 与实际实现一致

#### Scenario: 中文文档字符串
- **WHEN** 为函数编写文档字符串时
- **THEN** 系统 SHALL 使用中文描述函数功能
- **AND** 文档 SHALL 包含 Args、Returns、Raises、Examples 等标准部分
- **AND** 所有示例代码 SHALL 可以直接执行

### Requirement: SF-009 - Module Independence
模块 SHALL 是完全独立的，不依赖项目内部的其他模块，仅使用外部依赖（qibo, pytket），以便在其他项目中重用。

#### Scenario: 独立模块导入
- **WHEN** 在新的 Python 环境中导入 sim_fusion 模块
- **THEN** 导入 SHALL 成功，无需项目内部的其他模块
- **AND** 系统 SHALL 仅依赖 qibo、pytket 等外部库
- **AND** 所有核心功能 SHALL 可正常使用

#### Scenario: 模块接口暴露
- **WHEN** 用户导入 sim_fusion 模块
- **THEN** __all__ 列表 SHALL 包含所有公共接口
- **AND** 模块 SHALL 暴露 sim_fusion、SimFusionStats、quick_sim_fusion 等主要接口
- **AND** 内部辅助函数 SHALL 以下划线开头表示私有

### Requirement: SF-010 - Performance Metrics
系统 SHALL 提供性能评估指标，包括优化效率（门减少百分比/秒）、执行时间分解等，帮助用户评估优化效果。

#### Scenario: 性能指标计算
- **WHEN** 优化执行完成
- **THEN** 系统 SHALL 计算 gate_reduction_percent = ((original_gates - optimized_gates) / original_gates) * 100
- **AND** 系统 SHALL 计算 depth_reduction_percent = ((original_depth - optimized_depth) / original_depth) * 100
- **AND** 系统 SHALL 计算 efficiency_score = gate_reduction_percent / total_time

#### Scenario: 时间分解统计
- **WHEN** 优化执行时
- **THEN** 系统 SHALL 分别测量 tket_time、fusion_time
- **AND** 系统 SHALL 计算 total_time = tket_time + fusion_time + overhead_time
- **AND** 时间测量精度 SHALL 达到毫秒级别