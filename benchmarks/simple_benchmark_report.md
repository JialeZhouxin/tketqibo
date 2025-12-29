# Simple Quantum Algorithms Optimization Report

Generated on: 2025-12-19 17:55:02

## Overall Statistics

- Total tests: 30
- Successful tests: 26
- Success rate: 86.7%

## Top Performing Tests (Gate Reduction)

1. **Bell State** (qiskit_only)
   - Gates: 3 ¡ú 2 (33.3% reduction)
   - Depth: 3 ¡ú 2 (33.3% reduction)
   - Time: 0.000s

2. **Bell State** (qiskit_only)
   - Gates: 5 ¡ú 4 (20.0% reduction)
   - Depth: 5 ¡ú 4 (20.0% reduction)
   - Time: 0.002s

3. **QFT** (qiskit_only)
   - Gates: 160 ¡ú 136 (15.0% reduction)
   - Depth: 57 ¡ú 52 (8.8% reduction)
   - Time: 0.009s

4. **Bell State** (qiskit_only)
   - Gates: 7 ¡ú 6 (14.3% reduction)
   - Depth: 7 ¡ú 6 (14.3% reduction)
   - Time: 0.001s

5. **Deutsch-Jozsa** (qiskit_only)
   - Gates: 8 ¡ú 7 (12.5% reduction)
   - Depth: 4 ¡ú 3 (25.0% reduction)
   - Time: 0.001s

## Strategy Comparison

### none
- Average gate reduction: 0.0%
- Average depth reduction: 0.0%
- Average time: 0.002s
- Tests: 13

### qiskit_only
- Average gate reduction: 11.5%
- Average depth reduction: 16.9%
- Average time: 0.002s
- Tests: 13

## Failed Tests

- **Grover** (none)
  - Error: "<input>:3,32: 'cp' is not defined in this scope"

- **Grover** (qiskit_only)
  - Error: "<input>:3,32: 'cp' is not defined in this scope"

- **Grover** (none)
  - Error: "<input>:3,50: 'p' is not defined in this scope"

- **Grover** (qiskit_only)
  - Error: "<input>:3,50: 'p' is not defined in this scope"
