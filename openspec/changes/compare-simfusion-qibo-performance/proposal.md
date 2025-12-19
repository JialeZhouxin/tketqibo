# Compare Sim-Fusion vs Qibo Native Fusion Performance

## Why
需要系统性地比较 Sim-Fusion 混合优化策略（TKET 预处理 + Qibo fusion）与 Qibo 原生 fusion 的性能差异。当前用户需要了解在哪些场景下 Sim-Fusion 提供真正的优势，以及两种优化方法的适用边界。虽然 QASM 文件已被删除，但我们可以通过生成多样化的基准电路来进行全面的性能对比分析。

## What Changes
- **NEW**: 创建标准量子电路基准测试套件，涵盖不同算法类型
- **NEW**: 实现 Sim-Fusion 与 Qibo 原生 fusion 的性能对比框架
- **NEW**: 生成详细的性能分析和可视化报告
- **MODIFIED**: 增强 Sim-Fusion 统计信息以支持性能对比
- **NEW**: 提供优化策略推荐系统

## Impact
- **Affected specs**: quantum-benchmark (add performance comparison capabilities)
- **Affected code**:
  - `src/performance_comparison.py` - 新建性能对比框架
  - `src/benchmark_circuits.py` - 新建基准电路生成器
  - `sim_fusion.py` - 增强统计信息收集
  - 生成性能对比报告和可视化图表
- **Expected outcome**:
  - 获得不同类型电路的性能对比数据
  - 确定每种优化策略的优势场景
  - 为用户提供优化策略选择指导
  - 验证 Sim-Fusion 相对于 Qibo 原生 fusion 的实际价值