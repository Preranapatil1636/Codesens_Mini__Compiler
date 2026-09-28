"""
Abstract Syntax Tree (AST) Node definitions for CODE SENSE Mini Compiler.
Defines node classes and human-readable tree visualization utilities.
"""

from typing import List, Optional, Any

class ASTNode:
    """Base class for all AST nodes."""
    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        raise NotImplementedError

class ProgramNode(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        lines = ["Program"]
        for i, stmt in enumerate(self.statements):
            last = (i == len(self.statements) - 1)
            pointer = "└── " if last else "├── "
            child_prefix = prefix + ("    " if last else "│   ")
            child_str = stmt.to_tree_string(child_prefix, last)
            lines.append(f"{prefix}{pointer}{child_str}")
        return "\n".join(lines)

class VarDeclNode(ASTNode):
    def __init__(self, var_type: str, name: str, initializer: Optional[ASTNode], line: int):
        self.var_type = var_type
        self.name = name
        self.initializer = initializer
        self.line = line

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        lines = [f"Declaration ({self.var_type} {self.name})"]
        if self.initializer:
            pointer = "└── Initializer: "
            child_prefix = prefix + "    "
            lines.append(f"{prefix}└── Initializer:")
            init_str = self.initializer.to_tree_string(child_prefix, True)
            lines.append(f"{child_prefix}└── {init_str}")
        return "\n".join(lines)

class AssignNode(ASTNode):
    def __init__(self, name: str, value: ASTNode, line: int):
        self.name = name
        self.value = value
        self.line = line

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        lines = [f"Assignment ({self.name} = )"]
        child_prefix = prefix + "    "
        val_str = self.value.to_tree_string(child_prefix, True)
        lines.append(f"{prefix}└── {val_str}")
        return "\n".join(lines)

class PrintNode(ASTNode):
    def __init__(self, expression: ASTNode, line: int):
        self.expression = expression
        self.line = line

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        lines = ["Print Statement"]
        child_prefix = prefix + "    "
        expr_str = self.expression.to_tree_string(child_prefix, True)
        lines.append(f"{prefix}└── {expr_str}")
        return "\n".join(lines)

class BinaryOpNode(ASTNode):
    def __init__(self, op: str, left: ASTNode, right: ASTNode, line: int):
        self.op = op
        self.left = left
        self.right = right
        self.line = line

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        lines = [f"Binary Operation: {self.op}"]
        child_prefix = prefix + "    "
        left_str = self.left.to_tree_string(child_prefix, False)
        right_str = self.right.to_tree_string(child_prefix, True)
        lines.append(f"{prefix}├── Left: {left_str}")
        lines.append(f"{prefix}└── Right: {right_str}")
        return "\n".join(lines)

class UnaryOpNode(ASTNode):
    def __init__(self, op: str, operand: ASTNode, line: int):
        self.op = op
        self.operand = operand
        self.line = line

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        lines = [f"Unary Operation: {self.op}"]
        child_prefix = prefix + "    "
        op_str = self.operand.to_tree_string(child_prefix, True)
        lines.append(f"{prefix}└── {op_str}")
        return "\n".join(lines)

class LiteralNode(ASTNode):
    def __init__(self, value: Any, data_type: str, line: int):
        self.value = value
        self.data_type = data_type
        self.line = line

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        val_repr = f'"{self.value}"' if self.data_type == "string" else str(self.value)
        return f"Literal ({self.data_type}): {val_repr}"

class VarAccessNode(ASTNode):
    def __init__(self, name: str, line: int):
        self.name = name
        self.line = line

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        return f"Variable: {self.name}"

class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_body: List[ASTNode], else_body: Optional[List[ASTNode]], line: int):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body
        self.line = line

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        lines = ["If Statement"]
        child_prefix = prefix + "    "
        cond_str = self.condition.to_tree_string(child_prefix, False)
        lines.append(f"{prefix}├── Condition: {cond_str}")
        
        lines.append(f"{prefix}├── Then Branch:")
        then_prefix = prefix + "│   "
        for stmt in self.then_body:
            lines.append(f"{then_prefix}└── {stmt.to_tree_string(then_prefix, True)}")

        if self.else_body:
            lines.append(f"{prefix}└── Else Branch:")
            else_prefix = prefix + "    "
            for stmt in self.else_body:
                lines.append(f"{else_prefix}└── {stmt.to_tree_string(else_prefix, True)}")

        return "\n".join(lines)

class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: List[ASTNode], line: int):
        self.condition = condition
        self.body = body
        self.line = line

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        lines = ["While Statement"]
        child_prefix = prefix + "    "
        cond_str = self.condition.to_tree_string(child_prefix, False)
        lines.append(f"{prefix}├── Condition: {cond_str}")
        lines.append(f"{prefix}└── Body:")
        body_prefix = prefix + "    "
        for stmt in self.body:
            lines.append(f"{body_prefix}└── {stmt.to_tree_string(body_prefix, True)}")
        return "\n".join(lines)
