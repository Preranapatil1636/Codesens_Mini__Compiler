"""
Semantic Analyzer for CODE SENSE Mini Compiler.
Validates variable declarations, type checking, scoping rules, and expression compatibility.
"""

from typing import List, Optional, Tuple, Any
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignNode, PrintNode,
    IfNode, WhileNode, BinaryOpNode, UnaryOpNode, LiteralNode, VarAccessNode
)
from symbol_table import SymbolTable, Symbol

class SemanticError:
    def __init__(
        self,
        message: str,
        error_type: str,
        line: int,
        var_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        received_type: Optional[str] = None
    ):
        self.message = message
        self.error_type = error_type  # e.g., "UNDECLARED_VARIABLE", "DUPLICATE_DECLARATION", "TYPE_MISMATCH"
        self.line = line
        self.var_name = var_name
        self.expected_type = expected_type
        self.received_type = received_type

    def __str__(self) -> str:
        return f"SemanticError [{self.error_type}] at line {self.line} - {self.message}"

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []

    def analyze(self, ast: ProgramNode) -> Tuple[SymbolTable, List[SemanticError]]:
        self.symbol_table.reset()
        self.errors = []
        self.visit(ast)
        return self.symbol_table, self.errors

    def visit(self, node: ASTNode) -> Optional[str]:
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> Optional[str]:
        return "unknown"

    def visit_ProgramNode(self, node: ProgramNode) -> None:
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDeclNode(self, node: VarDeclNode) -> None:
        init_type = None
        if node.initializer:
            init_type = self.visit(node.initializer)
            if init_type and init_type != "unknown" and not self.types_compatible(node.var_type, init_type):
                self.errors.append(SemanticError(
                    f"Type mismatch in declaration of '{node.name}'. Expected '{node.var_type}', but received '{init_type}'.",
                    "TYPE_MISMATCH",
                    node.line,
                    var_name=node.name,
                    expected_type=node.var_type,
                    received_type=init_type
                ))

        success, err_msg = self.symbol_table.define(node.name, node.var_type, self.evaluate_constant(node.initializer), node.line)
        if not success:
            self.errors.append(SemanticError(
                err_msg or f"Variable '{node.name}' is already declared in this scope.",
                "DUPLICATE_DECLARATION",
                node.line,
                var_name=node.name
            ))

    def visit_AssignNode(self, node: AssignNode) -> None:
        sym = self.symbol_table.lookup(node.name)
        expr_type = self.visit(node.value)

        if not sym:
            self.errors.append(SemanticError(
                f"Variable '{node.name}' used before declaration.",
                "UNDECLARED_VARIABLE",
                node.line,
                var_name=node.name
            ))
            return

        if expr_type and expr_type != "unknown" and not self.types_compatible(sym.type, expr_type):
            self.errors.append(SemanticError(
                f"Type mismatch in assignment to '{node.name}'. Expected '{sym.type}', but received '{expr_type}'.",
                "TYPE_MISMATCH",
                node.line,
                var_name=node.name,
                expected_type=sym.type,
                received_type=expr_type
            ))
        else:
            # Keep a simple compile-time value when the expression is constant.
            # This lets us detect cases such as: int y = 0; x / y;
            self.symbol_table.update_value(node.name, self.evaluate_constant(node.value))

    def visit_PrintNode(self, node: PrintNode) -> None:
        self.visit(node.expression)

    def visit_IfNode(self, node: IfNode) -> None:
        cond_type = self.visit(node.condition)
        
        self.symbol_table.enter_scope()
        for stmt in node.then_body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

        if node.else_body:
            self.symbol_table.enter_scope()
            for stmt in node.else_body:
                self.visit(stmt)
            self.symbol_table.exit_scope()

    def visit_WhileNode(self, node: WhileNode) -> None:
        self.visit(node.condition)

        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_t = self.visit(node.left)
        right_t = self.visit(node.right)

        if left_t == "unknown" or right_t == "unknown":
            return "unknown"

        # Relational/Equality operators return bool
        if node.op in {">", "<", ">=", "<=", "==", "!="}:
            if not self.types_compatible(left_t, right_t):
                self.errors.append(SemanticError(
                    f"Comparison operator '{node.op}' cannot compare types '{left_t}' and '{right_t}'.",
                    "TYPE_MISMATCH",
                    node.line,
                    expected_type=left_t,
                    received_type=right_t
                ))
            return "bool"

        # Division by zero is a semantic error when the denominator is
        # provably zero at compile time (literal, constant expression, or
        # a variable whose current compile-time value is known to be zero).
        if node.op == "/":
            right_value = self.evaluate_constant(node.right)
            if right_value is not None and right_value == 0:
                self.errors.append(SemanticError(
                    "Division by zero is not allowed. The right-hand side of '/' evaluates to 0.",
                    "DIVISION_BY_ZERO",
                    node.line
                ))

        # Arithmetic operators
        if node.op in {"+", "-", "*", "/"}:
            if left_t == "string" or right_t == "string":
                if left_t == "string" and right_t == "string" and node.op == "+":
                    return "string"  # String concatenation
                else:
                    self.errors.append(SemanticError(
                        f"Cannot perform arithmetic operation '{node.op}' between '{left_t}' and '{right_t}'.",
                        "TYPE_MISMATCH",
                        node.line,
                        expected_type="numeric",
                        received_type=f"{left_t} & {right_t}"
                    ))
                    return "unknown"
            
            if left_t == "float" or right_t == "float":
                return "float"
            return "int"

        return "unknown"

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        t = self.visit(node.operand)
        if node.op == "!":
            return "bool"
        return t or "unknown"

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        return node.data_type

    def visit_VarAccessNode(self, node: VarAccessNode) -> str:
        sym = self.symbol_table.lookup(node.name)
        if not sym:
            self.errors.append(SemanticError(
                f"Undeclared variable '{node.name}' referenced in expression.",
                "UNDECLARED_VARIABLE",
                node.line,
                var_name=node.name
            ))
            return "unknown"
        return sym.type

    def evaluate_constant(self, node: Optional[ASTNode]) -> Any:
        """Return a compile-time value when an expression is safely constant.
        Return None when the value cannot be determined at compile time.
        """
        if node is None:
            return None

        if isinstance(node, LiteralNode):
            return node.value

        if isinstance(node, VarAccessNode):
            sym = self.symbol_table.lookup(node.name)
            return sym.value if sym else None

        if isinstance(node, UnaryOpNode):
            value = self.evaluate_constant(node.operand)
            if value is None:
                return None
            if node.op == "-":
                return -value
            if node.op == "!":
                return not value
            return None

        if isinstance(node, BinaryOpNode):
            left = self.evaluate_constant(node.left)
            right = self.evaluate_constant(node.right)
            if left is None or right is None:
                return None

            try:
                if node.op == "+":
                    return left + right
                if node.op == "-":
                    return left - right
                if node.op == "*":
                    return left * right
                if node.op == "/":
                    if right == 0:
                        return None
                    return left / right
                if node.op == ">":
                    return left > right
                if node.op == "<":
                    return left < right
                if node.op == ">=":
                    return left >= right
                if node.op == "<=":
                    return left <= right
                if node.op == "==":
                    return left == right
                if node.op == "!=":
                    return left != right
            except (TypeError, ZeroDivisionError):
                return None

        return None

    def types_compatible(self, type1: str, type2: str) -> bool:
        if type1 == type2:
            return True
        # Allow implicit int -> float widening
        if type1 == "float" and type2 == "int":
            return True
        return False
