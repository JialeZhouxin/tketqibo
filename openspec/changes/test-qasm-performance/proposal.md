# Test QASM Circuit Performance Comparison

## Why
需要评估现有QASM量子电路在混合优化策略 vs Qibo门融合策略下的性能表现。当前有14个不同复杂度的QASM文件，涵盖多种量子算法（Bell态、Shor算法、VQE、QAOA、HHL等），需要通过实际性能测试来验证混合优化策略在实际电路上的优势，并在必要时使用QiboJIT来加速性能瓶颈。

## What Changes
- **NEW**: 创建QASM文件加载和解析功能
- **NEW**: 实现QASM电路性能测试框架
- **NEW**: 集成QiboJIT作为高性能加速选项
- **NEW**: 实现混合优化策略 vs Qibo融合策略的性能对比
- **NEW**: 生成详细的性能分析报告

## Impact
- **Affected specs**: hybrid-optimizer-interface (add QASM testing capability), quantum-benchmark (add real-world circuit testing)
- **Affected code**:
  - `src/qasm_loader.py` - 新建QASM文件加载模块
  - `src/qasm_performance_tester.py` - 性能测试框架
  - `src/qibojit_integration.py` - QiboJIT集成模块
  - Tests and benchmark reports for QASM circuits
- **Expected outcome**: 获得14个QASM电路的性能对比数据，验证混合优化策略的实际效果，识别最适合优化策略的电路类型