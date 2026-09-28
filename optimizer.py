"""
Code Optimizer for CODE SENSE Mini Compiler.
Implements AST-level Constant Folding and Algebraic Simplifications,
producing optimized Three-Address Code (TAC).
"""

import copy
from typing import List, Tuple, Any
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignNode, PrintNode,
    IfNode, WhileNode, BinaryOpNode, UnaryOpNode, LiteralNode, VarAccessNode
)
from intermediate_code import TACGenerator

class Optimizer:
    def __init__(self):
        self.logs: List[str] = []

    def optimize(self, ast: ProgramNode) -> Tuple[ProgramNode, List[str], List[str], List[str]]:
        """
        Optimizes the AST and generates before/after TAC.
        Returns: (optimized_ast, logs, unoptimized_tac, optimized_tac)
        """
        self.logs = []
        
        # 1. Generate unoptimized TAC
        unopt_gen = TACGenerator()
        unoptimized_tac = unopt_gen.generate(ast)

        # 2. Perform AST optimizations on a deep copy
        opt_ast = copy.deepcopy(ast)
        opt_ast = self.visit(opt_ast)

        # 3. Generate optimized TAC
        opt_gen = TACGenerator()
        optimized_tac = opt_gen.generate(opt_ast)

        return opt_ast, self.logs, unoptimized_tac, optimized_tac

    def visit(self, node: ASTNode) -> ASTNode:
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> ASTNode:
        return node

    def visit_ProgramNode(self, node: ProgramNode) -> ProgramNode:
        node.statements = [self.visit(stmt) for stmt in node.statements]
        return node

    def visit_VarDeclNode(self, node: VarDeclNode) -> VarDeclNode:
        if node.initializer:
            node.initializer = self.visit(node.initializer)
        return node

    def visit_AssignNode(self, node: AssignNode) -> AssignNode:
        node.value = self.visit(node.value)
        return node

    def visit_PrintNode(self, node: PrintNode) -> PrintNode:
        node.expression = self.visit(node.expression)
        return node

    def visit_IfNode(self, node: IfNode) -> IfNode:
        node.condition = self.visit(node.condition)
        node.then_body = [self.visit(stmt) for stmt in node.then_body]
        if node.else_body:
            node.else_body = [self.visit(stmt) for stmt in node.else_body]
        return node

    def visit_WhileNode(self, node: WhileNode) -> WhileNode:
        node.condition = self.visit(node.condition)
        node.body = [self.visit(stmt) for stmt in node.body]
        return node

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> ASTNode:
        # First optimize children recursively
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        # --- 1. Constant Folding ---
        if isinstance(node.left, LiteralNode) and isinstance(node.right, LiteralNode):
            l_val, r_val = node.left.value, node.right.value
            l_type, r_type = node.left.data_type, node.right.data_type

            if node.op == '+':
                if l_type in ("int", "float") and r_type in ("int", "float"):
                    res = l_val + r_val
                    res_type = "float" if (l_type == "float" or r_type == "float") else "int"
                    self.logs.append(f"🧠 Constant Folding: Folded '{l_val} + {r_val}' → '{res}'")
                    return LiteralNode(res, res_type, node.line)
                elif l_type == "string" and r_type == "string":
                    res = l_val + r_val
                    self.logs.append(f'🧠 Constant Folding: Concatenated strings "{l_val}" + "{r_val}" → "{res}"')
                    return LiteralNode(res, "string", node.line)
            elif node.op == '-':
                if l_type in ("int", "float") and r_type in ("int", "float"):
                    res = l_val - r_val
                    res_type = "float" if (l_type == "float" or r_type == "float") else "int"
                    self.logs.append(f"🧠 Constant Folding: Folded '{l_val} - {r_val}' → '{res}'")
                    return LiteralNode(res, res_type, node.line)
            elif node.op == '*':
                if l_type in ("int", "float") and r_type in ("int", "float"):
                    res = l_val * r_val
                    res_type = "float" if (l_type == "float" or r_type == "float") else "int"
                    self.logs.append(f"🧠 Constant Folding: Folded '{l_val} * {r_val}' → '{res}'")
                    return LiteralNode(res, res_type, node.line)
            elif node.op == '/':
                if l_type in ("int", "float") and r_type in ("int", "float") and r_val != 0:
                    res = l_val / r_val
                    res_type = "float" if isinstance(res, float) else "int"
                    if res.is_integer():
                        res = int(res)
                        res_type = "int"
                    self.logs.append(f"🧠 Constant Folding: Folded '{l_val} / {r_val}' → '{res}'")
                    return LiteralNode(res, res_type, node.line)

        # --- 2. Algebraic Simplification ---
        # Additive identity: x + 0 -> x, 0 + x -> x
        if node.op == '+':
            if isinstance(node.right, LiteralNode) and node.right.value == 0:
                self.logs.append(f"⚡ Algebraic Simplification: Simplified expression + 0 → returned left operand.")
                return node.left
            if isinstance(node.left, LiteralNode) and node.left.value == 0:
                self.logs.append(f"⚡ Algebraic Simplification: Simplified 0 + expression → returned right operand.")
                return node.right

        # Subtractive identity: x - 0 -> x
        if node.op == '-':
            if isinstance(node.right, LiteralNode) and node.right.value == 0:
                self.logs.append(f"⚡ Algebraic Simplification: Simplified expression - 0 → returned left operand.")
                return node.left

        # Multiplicative identity: x * 1 -> x, 1 * x -> x
        if node.op == '*':
            if isinstance(node.right, LiteralNode) and node.right.value == 1:
                self.logs.append(f"⚡ Algebraic Simplification: Simplified expression * 1 → returned left operand.")
                return node.left
            if isinstance(node.left, LiteralNode) and node.left.value == 1:
                self.logs.append(f"⚡ Algebraic Simplification: Simplified 1 * expression → returned right operand.")
                return node.right
            # Multiplication by zero: x * 0 -> 0, 0 * x -> 0
            if (isinstance(node.right, LiteralNode) and node.right.value == 0) or (isinstance(node.left, LiteralNode) and node.left.value == 0):
                self.logs.append(f"⚡ Algebraic Simplification: Multiplied by 0 → evaluated to constant 0.")
                return LiteralNode(0, "int", node.line)

        return node
