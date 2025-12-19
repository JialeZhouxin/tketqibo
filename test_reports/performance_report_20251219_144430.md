# Sim-Fusion vs Qibo Fusion Performance Comparison Report

**Generated:** 2025-12-19T14:44:30.881709

## Executive Summary

- **Metrics with significant differences:** 1/1
- **High-priority insights:** 1
- **Overall assessment:** Strong evidence of performance differences

### Key Findings

- Large effect size (1.80) in gate_reduction

## Executive Summary

This report compares the performance of Sim-Fusion (TKET + Qibo fusion) against Qibo's native fusion optimization across 1 metrics. Significant performance differences were detected in 1 metrics. 

## Statistical Summary

### Sim_Fusion

| Metric | Mean | Std Dev | Min | Max | CV |
|--------|------|---------|-----|-----|----|

### Qibo_Fusion

| Metric | Mean | Std Dev | Min | Max | CV |
|--------|------|---------|-----|-----|----|



## Statistical Significance Testing

| Metric | Test | Statistic | P-value | Significant? | Effect Size |
|--------|------|-----------|---------|--------------|-------------|
| gate_reduction | t_test | 8.4500 | 0.000100 | Yes | 1.800 |


## Recommendations

1. Strong evidence of difference in gate_reduction - recommend method with better performance
2. Consider trade-offs between optimization quality and speed


## Automated Insights

### 🔴 Performance Optimization

**Insight:** Large effect size (1.80) in gate_reduction

**Recommendation:** Strongly prefer the better performing method for gate_reduction

---

