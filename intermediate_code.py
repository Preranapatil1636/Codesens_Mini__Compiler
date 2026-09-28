"""
Intermediate Code Generator (Three-Address Code) for CODE SENSE Mini Compiler.
Translates Abstract Syntax Tree (AST) into clean Three-Address Code (TAC).
"""

from typing import List, Tuple, Optional, Any
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignNode, PrintNode,
    IfNode, WhileNode, BinaryOpNode, UnaryOpNode, LiteralNode, VarAccessNode
)

class TACInstruction:
    def __init__(self, result: str, arg1: str, op: Optional[str] = None, arg2: Optional[str] = None):
        self.result = result
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2

    def __str__(self) -> str:
        if self.op is None:
            if self.result.startswith("label_"):
                return f"{self.result}:"
            elif self.result.startswith("goto"):
                return f"{self.result} {self.arg1}"
            elif self.result == "print":
                return f"print {self.arg1}"
            elif self.result == "if_false":
                return f"if_false {self.arg1} goto {self.arg2}"
            else:
                return f"{self.result} = {self.arg1}"
        else:
            if self.arg2 is not None:
                return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
            else:
                return f"{self.result} = {self.op}{self.arg1}"

class TACGenerator:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.instructions: List[TACInstruction] = []

    def new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def generate(self, ast: ProgramNode) -> List[str]:
        self.temp_count = 0
        self.label_count = 0
        self.instructions = []
        self.visit(ast)
        return [str(instr) for instr in self.instructions]

    def visit(self, node: ASTNode) -> str:
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> str:
        return ""

    def visit_ProgramNode(self, node: ProgramNode) -> str:
        for stmt in node.statements:
            self.visit(stmt)
        return ""

    def visit_VarDeclNode(self, node: VarDeclNode) -> str:
        if node.initializer:
            expr_res = self.visit(node.initializer)
            self.instructions.append(TACInstruction(node.name, expr_res))
        return node.name

    def visit_AssignNode(self, node: AssignNode) -> str:
        expr_res = self.visit(node.value)
        self.instructions.append(TACInstruction(node.name, expr_res))
        return node.name

    def visit_PrintNode(self, node: PrintNode) -> str:
        expr_res = self.visit(node.expression)
        self.instructions.append(TACInstruction("print", expr_res))
        return ""

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_res = self.visit(node.left)
        right_res = self.visit(node.right)
        temp = self.new_temp()
        self.instructions.append(TACInstruction(temp, left_res, node.op, right_res))
        return temp

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        operand_res = self.visit(node.operand)
        temp = self.new_temp()
        self.instructions.append(TACInstruction(temp, operand_res, node.op))
        return temp

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if node.data_type == "string":
            return f'"{node.value}"'
        return str(node.value)

    def visit_VarAccessNode(self, node: VarAccessNode) -> str:
        return node.name

    def visit_IfNode(self, node: IfNode) -> str:
        cond_res = self.visit(node.condition)
        else_label = self.new_label()
        end_label = self.new_label()

        target_label = else_label if node.else_body else end_label
        self.instructions.append(TACInstruction("if_false", cond_res, arg2=target_label))

        for stmt in node.then_body:
            self.visit(stmt)

        if node.else_body:
            self.instructions.append(TACInstruction("goto", end_label))
            self.instructions.append(TACInstruction(else_label, ""))
            for stmt in node.else_body:
                self.visit(stmt)

        self.instructions.append(TACInstruction(end_label, ""))
        return ""

    def visit_WhileNode(self, node: WhileNode) -> str:
        start_label = self.new_label()
        end_label = self.new_label()

        self.instructions.append(TACInstruction(start_label, ""))
        cond_res = self.visit(node.condition)
        self.instructions.append(TACInstruction("if_false", cond_res, arg2=end_label))

        for stmt in node.body:
            self.visit(stmt)

        self.instructions.append(TACInstruction("goto", start_label))
        self.instructions.append(TACInstruction(end_label, ""))
        return ""
