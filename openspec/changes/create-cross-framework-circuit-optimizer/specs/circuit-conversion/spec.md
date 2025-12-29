## ADDED Requirements

### Requirement: 多框架电路输入支持
跨框架优化器 SHALL 支持从QASM、Qiskit和Qibo三种格式输入量子电路。

#### Scenario: QASM电路输入
- **WHEN** 用户提供QASM格式的量子电路字符串或文件
- **THEN** 系统能够解析QASM并识别电路结构
- **AND** 转换为内部标准格式进行优化

#### Scenario: Qiskit电路输入
- **WHEN** 用户提供Qiskit QuantumCircuit对象
- **THEN** 系统能够直接读取Qiskit电路结构
- **AND** 保留所有量子门和参数信息

#### Scenario: Qibo电路输入
- **WHEN** 用户提供Qibo Circuit对象
- **THEN** 系统能够直接处理Qibo电路
- **AND** 保持与现有sim_fusion模块的兼容性

### Requirement: 统一Qibo电路输出
跨框架优化器 SHALL 始终输出优化后的Qibo Circuit对象，便于后续处理和模拟。

#### Scenario: 标准化输出
- **WHEN** 优化过程完成
- **THEN** 输出统一的Qibo Circuit格式
- **AND** 包含优化统计信息和元数据

#### Scenario: 输出验证
- **WHEN** 生成输出电路
- **THEN** 验证输出电路的功能等价性
- **AND** 确保量子比特数和预期输出一致

### Requirement: 电路类型自动检测
系统 SHALL 能够自动识别输入电路的类型和格式，无需用户手动指定。

#### Scenario: 自动类型识别
- **WHEN** 用户输入未知格式的电路
- **THEN** 系统自动检测是QASM、Qiskit还是Qibo格式
- **AND** 提供类型检测的置信度评分

#### Scenario: 类型检测失败
- **WHEN** 系统无法识别输入格式
- **THEN** 提供清晰的错误信息和格式要求
- **AND** 建议支持的输入格式示例

### Requirement: 门类型映射和转换
系统 SHALL 提供完整的量子门类型映射，确保不同框架间的正确转换。

#### Scenario: 标准量子门转换
- **WHEN** 转换包含标准量子门（H, X, Y, Z, CNOT等）的电路
- **THEN** 准确映射所有标准量子门类型
- **AND** 保持门参数和量子比特映射的正确性

#### Scenario: 参数化门转换
- **WHEN** 电路包含参数化旋转门（RX, RY, RZ等）
- **THEN** 正确转换所有参数和角度值
- **AND** 保持数值精度和符号约定

#### Scenario: 不支持的门类型
- **WHEN** 遇到不支持的量子门类型
- **THEN** 发出明确的警告信息
- **AND** 提供跳过或近似处理的选项