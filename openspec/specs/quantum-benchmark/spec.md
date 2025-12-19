# quantum-benchmark Specification

## Purpose
TBD - created by archiving change build-quantum-benchmark-framework. Update Purpose after archive.
## Requirements
### Requirement: Quantum Circuit Converter
系统 SHALL 提供 QIBO Circuit 和 TKET Circuit 之间的双向转换功能。

#### Scenario: 成功转换 QIBO 到 TKET
- **WHEN** 用户输入一个 QIBO Circuit 对象
- **AND** 线路包含支持的门类型（H, X, Y, Z, CX, CZ, RX, RY, RZ）
- **THEN** 系统返回等价的 TKET Circuit 对象
- **AND** 所有的门操作保持相同的效果

#### Scenario: 成功转换 TKET 到 QIBO
- **WHEN** 用户输入一个 TKET Circuit 对象
- **AND** 线路包含支持的门类型
- **THEN** 系统返回等价的 QIBO Circuit 对象
- **AND** 转换后的线路状态保真度 > 0.999

### Requirement: TKET Optimization Engine
系统 SHALL 封装 TKET 的优化策略，提供统一的优化接口。

#### Scenario: 应用 FullPeepholeOptimise
- **WHEN** 用户调用 optimize_circuit 函数
- **AND** 指定优化策略为 "full_peephole"
- **THEN** 系统对输入的 TKET Circuit 应用 FullPeepholeOptimise
- **AND** 返回优化后的 Circuit

#### Scenario: 应用 RemoveRedundancies
- **WHEN** 用户调用 optimize_circuit 函数
- **AND** 指定优化策略为 "remove_redundancies"
- **THEN** 系统对输入的 TKET Circuit 应用 RemoveRedundancies
- **AND** 移除所有可约简的门操作

### Requirement: Benchmark Experiment Runner
系统 SHALL 支持执行不同类型的 benchmark 实验。

#### Scenario: 运行 VQE/QAOA 风格实验
- **WHEN** 用户创建参数化线路（如 5 层深度，10 量子比特）
- **AND** 指定运行次数为 100
- **THEN** 系统记录无优化的总运行时间
- **AND** 系统记录优化后的总运行时间
- **AND** 输出加速比 (Speedup = 无优化时间 / 优化时间)

#### Scenario: 运行 QFT 规模扩展实验
- **WHEN** 用户指定量子比特数（10, 15, 20）
- **THEN** 系统为每个规模创建 QFT 线路
- **AND** 分别测试优化前后的性能
- **AND** 记录门数量、深度、编译时间、模拟时间

### Requirement: Performance Metrics Collection
系统 SHALL 收集和报告详细的性能指标。

#### Scenario: 收集线路统计信息
- **WHEN** 系统处理一个量子线路
- **THEN** 记录线路的门数量
- **AND** 记录线路的深度
- **AND** 记录不同类型门的分布

#### Scenario: 测量执行时间
- **WHEN** 系统执行优化或模拟操作
- **THEN** 使用高精度计时器（纳秒级）记录时间
- **AND** 区分编译时间和模拟时间
- **AND** 对于重复实验，计算平均值和标准差

### Requirement: Report Generation
系统 SHALL 生成 Markdown 格式的性能对比报告。

#### Scenario: 生成对比表格
- **WHEN** benchmark 实验完成
- **THEN** 生成包含以下列的 Markdown 表格：
  - 实验名称/规模
  - 优化前门数量
  - 优化后门数量
  - 优化前深度
  - 优化后深度
  - 编译时间
  - 模拟时间
  - 加速比

#### Scenario: 添加性能趋势图
- **WHEN** 报告包含规模扩展实验（如 QFT）
- **THEN** 生成加速比随量子比特数变化的趋势描述
- **AND** 识别最优化的规模区间

