# 跨框架量子电路优化器设计文档

## Context

### 当前项目状态
- 项目已有Qibo↔TKET的双向转换器（circuit_converter.py）
- sim_fusion.py提供TKET+Qibo混合优化策略
- 缺乏QASM和Qiskit电路支持
- 需要统一的优化接口

### 目标用户需求
- 研究者需要处理不同来源的量子电路
- 教育场景需要QASM格式支持
- 工业应用需要Qiskit集成
- 统一输出便于后续处理和比较

## Goals / Non-Goals

### Goals
- ✅ 支持QASM、Qiskit、Qibo电路输入
- ✅ 统一输出优化后的Qibo电路
- ✅ 集成Qiskit Transpiler优化策略
- ✅ 提供简单易用的统一接口
- ✅ 保持向后兼容性

### Non-Goals
- 实现完整的QASM语义验证
- 支持所有Qiskit的专有硬件特性
- 提供电路等价性证明
- 实时电路可视化

## Decisions

### Decision 1: 使用统一接口模式
**What**: 创建`CrossFrameworkOptimizer`类作为主要入口点
**Why**: 提供一致的用户体验，隐藏不同框架的复杂性
**Implementation**: 单一类处理所有输入类型，内部委托给专门的转换器

### Decision 2: 分层转换架构
**What**: 输入 → 框架检测 → 标准化 → Qiskit优化 → Qibo输出
**Why**: 利用Qiskit强大的优化能力，确保输出一致性
**Implementation**: 内部统一转换为Qiskit格式，应用优化后转换为Qibo

### Decision 3: 渐进式依赖管理
**What**: 可选依赖qiskit，提供优雅降级
**Why**: 避免强制用户安装所有依赖
**Implementation**: 动态导入，提供错误提示和替代方案

### Decision 4: 门类型兼容性策略
**What**: 定义核心门集映射，不支持的门发出警告
**Why**: 平衡功能完整性和实现复杂度
**Implementation**: 建立完整的门映射表，提供扩展机制

## Alternatives considered

### Alternative 1: 直接转换策略
- 各框架直接转换为Qibo
- **Pros**: 简单直接
- **Cons**: 无法利用Qiskit优化，需要维护多个转换路径

### Alternative 2: QASM作为中间格式
- 所有输入转换为QASM，再转Qibo
- **Pros**: 标准化格式
- **Cons**: 信息丢失，性能开销

### Alternative 3: 多目标输出
- 支持输出多种格式
- **Pros**: 灵活性高
- **Cons**: 复杂度增加，违背统一输出目标

## Risks / Trade-offs

### Risk 1: 依赖管理复杂性
- **Mitigation**: 可选依赖，清晰的错误提示
- **Trade-off**: 功能完整 vs 安装简便

### Risk 2: 优化效果不一致
- **Mitigation**: 提供多种优化策略选项
- **Trade-off**: 简单性 vs 优化质量

### Risk 3: 门类型支持不全
- **Mitigation**: 明确支持的门类型列表，提供扩展接口
- **Trade-off**: 功能完整 vs 开发维护成本

## Migration Plan

### 阶段1: 核心转换功能
1. 实现基础转换器
2. QASM → Qiskit → Qibo路径
3. 基础门类型支持

### 阶段2: 优化集成
1. 集成Qiskit Transpiler
2. 添加优化策略选项
3. 性能基准测试

### 阶段3: 高级功能
1. 扩展门类型支持
2. 自定义优化配置
3. 批量处理功能

## Open Questions

1. **性能要求**: 是否需要支持大规模电路（>1000门）的优化？
2. **优化级别**: 是否需要提供与Qiskit相同的优化级别控制？
3. **错误处理**: 对于不支持的量子操作，应该报错还是忽略？
4. **扩展机制**: 如何支持用户自定义门类型？