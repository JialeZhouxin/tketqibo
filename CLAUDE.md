<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

---

# Project Lessons Learned

## Cross-Framework Quantum Circuit Optimization

Key lessons from debugging Qiskit ↔ Qibo integration issues:

### 1. Trust Mature Frameworks
- **Lesson**: Mature frameworks like Qibo rarely have low-level bugs
- **Example**: Initial diagnosis blamed Qibo's `unitary()` method, but the actual issue was incorrect API usage in our code
- **Action**: When encountering unexpected behavior, first verify your code against official documentation before assuming framework bugs

### 2. Always Consult Official Documentation
- **Lesson**: Use Context7 or official docs to verify correct API usage
- **Tool**: Context7 (`mcp__context7__*`) provides quick access to official documentation
- **Example**: `gates.RX(qubit, theta)` not `gates.RX(theta, qubit)` in Qibo
- **Action**: Before refactoring framework code, spend 5 minutes checking the official API

### 3. Parameter Order Matters Across Frameworks
- **Lesson**: Different quantum frameworks may have different parameter order conventions
- **Examples**:
  - Qiskit: `U3Gate(theta, phi, lam, qubit)`
  - Qibo: `gates.U3(qubit, theta, phi, lam)`
  - Qiskit: `rx(angle, qubit)` vs Qibo: `RX(qubit, angle)`
- **Action**: When converting between frameworks, always verify parameter order with official docs
- **Testing**: Create unit tests for each gate type to catch parameter order issues early

## Technical Details

### Qibo Gate API Reference
```python
# Correct Qibo API
gates.RX(qubit, theta=angle)   # Rotation gates
gates.RY(qubit, theta=angle)
gates.RZ(qubit, theta=angle)
gates.U1(qubit, theta)          # Single-parameter gates
gates.U2(qubit, phi, lam)       # Two-parameter gates
gates.U3(qubit, theta, phi, lam)  # Three-parameter gates
```

### Qiskit vs Qibo Conventions
- **Qubit Ordering**:
  - Qiskit: big-endian |q_{n-1}...q_0⟩
  - Qibo: little-endian |q_0...q_{n-1}⟩
  - **Solution**: Use bit-reversal permutation for unitary matrix verification

- **Transpiler Behavior**:
  - `optimization_level=0`: No gate decomposition (when `basis_gates` not specified)
  - `optimization_level>=1`: Decomposes gates to basis set ['u3', 'cx']

## Related Files

- `GATE_SUPPORT_VERIFICATION_FINAL_REPORT.md` - Complete gate support audit
- `PARAMETRIC_GATES_FIX_REPORT.md` - Detailed parameter order fix documentation
- `cross_framework_optimizer.py` - Main implementation with all fixes