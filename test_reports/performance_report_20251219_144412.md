# Sim-Fusion vs Qibo Fusion Performance Comparison Report

**Generated:** 2025-12-19T14:44:12.562460

## Executive Summary

- **Metrics with significant differences:** 2/2
- **High-priority insights:** 2
- **Overall assessment:** Strong evidence of performance differences

### Key Findings

- Large effect size (1.80) in gate_reduction
- Significant time/efficiency difference in optimization_time

## Executive Summary

This report compares the performance of Sim-Fusion (TKET + Qibo fusion) against Qibo's native fusion optimization across 2 metrics. Significant performance differences were detected in 2 metrics. 

## Statistical Summary

### Sim_Fusion

| Metric | Mean | Std Dev | Min | Max | CV |
|--------|------|---------|-----|-----|----|
| gate_reduction | 15.500 | 0.500 | 14.800 | 16.100 | 0.032 |
| optimization_time | 0.250 | 0.020 | 0.220 | 0.280 | 0.080 |

### Qibo_Fusion

| Metric | Mean | Std Dev | Min | Max | CV |
|--------|------|---------|-----|-----|----|
| gate_reduction | 12.300 | 0.600 | 11.500 | 13.000 | 0.049 |
| optimization_time | 0.150 | 0.010 | 0.140 | 0.170 | 0.067 |



## Statistical Significance Testing

| Metric | Test | Statistic | P-value | Significant? | Effect Size |
|--------|------|-----------|---------|--------------|-------------|
| gate_reduction | t_test | 8.4500 | 0.000100 | Yes | 1.800 |
| optimization_time | t_test | 6.2300 | 0.001000 | Yes | 1.200 |


## Recommendations

1. Strong evidence of difference in gate_reduction - recommend method with better performance
2. Significant performance difference in optimization_time - prioritize faster method
3. Consider trade-offs between optimization quality and speed


## Automated Insights

### 🔴 Performance Optimization

**Insight:** Large effect size (1.80) in gate_reduction

**Recommendation:** Strongly prefer the better performing method for gate_reduction

---

### 🔴 Performance Efficiency

**Insight:** Significant time/efficiency difference in optimization_time

**Recommendation:** Prioritize faster method for time-critical applications

---

