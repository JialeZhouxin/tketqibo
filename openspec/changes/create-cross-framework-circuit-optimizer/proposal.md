# Change: 创建跨框架量子电路优化器

## Why
目前项目仅支持Qibo和TKET框架的电路优化，用户无法直接使用QASM或Qiskit电路。需要创建一个通用的跨框架电路优化器，支持QASM、Qiskit和Qibo电路输入，统一输出为优化后的Qibo电路，提升项目的通用性和用户友好性。

## What Changes
- 创建跨框架电路转换模块（cross_framework_optimizer.py）
- 实现QASM到Qibo的转换功能
- 实现Qiskit到Qibo的转换功能
- 集成Qiskit Transpiler优化策略
- 提供统一的优化接口
- 添加跨框架电路测试套件

## Impact
- Affected specs: circuit-conversion, optimization-engine
- Affected code: 新增模块，扩展现有转换器
- 用户可以输入任何主流格式的量子电路
- 提供更广泛的优化策略选择
- 增强项目的生态系统兼容性