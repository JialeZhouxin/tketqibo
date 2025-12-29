#!/usr/bin/env python3
"""
修复Qiskit 2.x兼容性问题的脚本
"""

def fix_qiskit_compatibility():
    """修复cross_framework_optimizer.py中的Qiskit 2.x兼容性问题"""

    file_path = "E:/02_Projects/tketqibo/cross_framework_optimizer.py"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 找到需要修改的行
        new_lines = []
        for i, line in enumerate(lines):
            line_num = i + 1
            if line_num == 401:
                # 替换有问题的行
                new_lines.append("""                # 兼容Qiskit 1.2+的新API
                if hasattr(instruction, 'operation'):
                    gate = instruction.operation
                    qubits_list = instruction.qubits
                else:
                    # 兼容旧版本Qiskit
                    gate = instruction[0]
                    qubits_list = instruction[1]

                # 兼容Qiskit 2.x的Qubit索引访问
                try:
                    qubits = [q._index for q in qubits_list]
                except AttributeError:
                    # 如果_q._index不存在，尝试其他方法
                    qubits = [circuit.qubits.index(q) for q in qubits_list]
""")
            elif line_num == 402 and "instruction[0].params" in line:
                # 替换params访问方式
                new_lines.append("                params = gate.params if hasattr(gate, 'params') else []\n")
            else:
                new_lines.append(line)

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print(f"✅ 成功修复 {file_path}")
        return True

    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == "__main__":
    fix_qiskit_compatibility()