"""
Recursive Descent Parser for CODE SENSE Mini Compiler.
Parses a list of Tokens into an Abstract Syntax Tree (AST).
"""

from typing import List, Tuple, Optional
from lexer import Token, TokenType
from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, AssignNode, PrintNode,
    IfNode, WhileNode, BinaryOpNode, UnaryOpNode, LiteralNode, VarAccessNode
)

class ParseError:
    def __init__(self, message: str, error_type: str, line: int, column: int, token_found: Token, expected: Optional[str] = None):
        self.message = message
        self.error_type = error_type  # e.g., "MISSING_SEMICOLON", "MISSING_PARENTHESIS", "SYNTAX_ERROR"
        self.line = line
        self.column = column
        self.token_found = token_found
        self.expected = expected

    def __str__(self) -> str:
        return f"ParseError [{self.error_type}] at line {self.line}:{self.column} - {self.message}"

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.errors: List[ParseError] = []

    def current(self) -> Token:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]  # EOF token

    def peek_next(self) -> Token:
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return self.tokens[-1]

    def advance(self) -> Token:
        tok = self.current()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return tok

    def match(self, *types: TokenType) -> bool:
        if self.current().type in types:
            self.advance()
            return True
        return False

    def check(self, t_type: TokenType, value: Optional[str] = None) -> bool:
        tok = self.current()
        if tok.type != t_type:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    def consume(self, t_type: TokenType, expected_desc: str, err_code: str = "SYNTAX_ERROR") -> Token:
        tok = self.current()
        if tok.type == t_type:
            return self.advance()
        
        # Error handling with details for AI Code Doctor
        msg = f"Expected '{expected_desc}', found '{tok.value}'"
        err = ParseError(msg, err_code, tok.line, tok.column, tok, expected=expected_desc)
        self.errors.append(err)
        return tok

    def consume_semicolon(self) -> None:
        tok = self.current()
        if tok.type == TokenType.SEMICOLON:
            self.advance()
        else:
            prev_tok = self.tokens[self.position - 1] if self.position > 0 else tok
            err = ParseError(
                f"Missing semicolon at end of statement",
                "MISSING_SEMICOLON",
                prev_tok.line,
                prev_tok.column + len(prev_tok.value),
                tok,
                expected=";"
            )
            self.errors.append(err)

    def parse(self) -> Tuple[ProgramNode, List[ParseError]]:
        statements: List[ASTNode] = []
        self.errors = []

        while self.current().type != TokenType.EOF:
            try:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
                else:
                    # Synchronization on error
                    self.synchronize()
            except Exception as e:
                tok = self.current()
                self.errors.append(ParseError(str(e), "PARSE_EXCEPTION", tok.line, tok.column, tok))
                self.synchronize()

        return ProgramNode(statements), self.errors

    def synchronize(self):
        """Skip tokens until finding a semicolon or statement start keyword to recover."""
        self.advance()
        while self.current().type != TokenType.EOF:
            if self.tokens[self.position - 1].type == TokenType.SEMICOLON:
                return
            if self.current().type == TokenType.KEYWORD and self.current().value in {"int", "float", "string", "bool", "if", "while", "print"}:
                return
            self.advance()

    def statement(self) -> Optional[ASTNode]:
        tok = self.current()

        if tok.type == TokenType.KEYWORD:
            if tok.value in {"int", "float", "string", "bool"}:
                return self.var_declaration()
            elif tok.value == "print":
                return self.print_statement()
            elif tok.value == "if":
                return self.if_statement()
            elif tok.value == "while":
                return self.while_statement()

        if tok.type == TokenType.IDENTIFIER:
            return self.assignment_statement()

        # If unexpected token
        self.errors.append(ParseError(
            f"Unexpected statement starting with '{tok.value}'",
            "UNEXPECTED_TOKEN",
            tok.line,
            tok.column,
            tok
        ))
        return None

    def var_declaration(self) -> ASTNode:
        type_tok = self.advance()  # int, float, string, bool
        line = type_tok.line

        name_tok = self.current()
        if name_tok.type == TokenType.IDENTIFIER:
            name = self.advance().value
        else:
            self.errors.append(ParseError(
                f"Expected variable identifier after type '{type_tok.value}'",
                "MISSING_IDENTIFIER",
                name_tok.line,
                name_tok.column,
                name_tok
            ))
            name = "unknown"

        initializer: Optional[ASTNode] = None
        if self.current().type == TokenType.ASSIGNMENT:
            self.advance()  # consume '='
            initializer = self.expression()

        self.consume_semicolon()
        return VarDeclNode(type_tok.value, name, initializer, line)

    def assignment_statement(self) -> ASTNode:
        name_tok = self.advance()  # IDENTIFIER
        line = name_tok.line

        if self.current().type == TokenType.ASSIGNMENT:
            self.advance()  # consume '='
        else:
            self.errors.append(ParseError(
                f"Expected '=' in assignment for variable '{name_tok.value}'",
                "MISSING_ASSIGNMENT_OPERATOR",
                self.current().line,
                self.current().column,
                self.current(),
                expected="="
            ))

        expr = self.expression()
        self.consume_semicolon()
        return AssignNode(name_tok.value, expr, line)

    def print_statement(self) -> ASTNode:
        print_tok = self.advance()  # consume 'print'
        line = print_tok.line

        tok = self.current()
        if tok.type == TokenType.PARENTHESIS and tok.value == '(':
            self.advance()
        else:
            self.errors.append(ParseError(
                "Expected '(' after print keyword",
                "MISSING_PARENTHESIS",
                tok.line,
                tok.column,
                tok,
                expected="("
            ))

        expr = self.expression()

        tok_close = self.current()
        if tok_close.type == TokenType.PARENTHESIS and tok_close.value == ')':
            self.advance()
        else:
            self.errors.append(ParseError(
                "Expected ')' after print expression",
                "MISSING_PARENTHESIS",
                tok_close.line,
                tok_close.column,
                tok_close,
                expected=")"
            ))

        self.consume_semicolon()
        return PrintNode(expr, line)

    def if_statement(self) -> ASTNode:
        if_tok = self.advance()  # consume 'if'
        line = if_tok.line

        tok = self.current()
        if tok.type == TokenType.PARENTHESIS and tok.value == '(':
            self.advance()
        else:
            self.errors.append(ParseError(
                "Expected '(' after 'if'",
                "MISSING_PARENTHESIS",
                tok.line,
                tok.column,
                tok,
                expected="("
            ))

        condition = self.expression()

        tok_close = self.current()
        if tok_close.type == TokenType.PARENTHESIS and tok_close.value == ')':
            self.advance()
        else:
            self.errors.append(ParseError(
                "Expected closing ')' after if condition",
                "MISSING_PARENTHESIS",
                tok_close.line,
                tok_close.column,
                tok_close,
                expected=")"
            ))

        then_body = self.statement_block()

        else_body: Optional[List[ASTNode]] = None
        if self.current().type == TokenType.KEYWORD and self.current().value == "else":
            self.advance()  # consume 'else'
            else_body = self.statement_block()

        return IfNode(condition, then_body, else_body, line)

    def while_statement(self) -> ASTNode:
        while_tok = self.advance()  # consume 'while'
        line = while_tok.line

        tok = self.current()
        if tok.type == TokenType.PARENTHESIS and tok.value == '(':
            self.advance()
        else:
            self.errors.append(ParseError(
                "Expected '(' after 'while'",
                "MISSING_PARENTHESIS",
                tok.line,
                tok.column,
                tok,
                expected="("
            ))

        condition = self.expression()

        tok_close = self.current()
        if tok_close.type == TokenType.PARENTHESIS and tok_close.value == ')':
            self.advance()
        else:
            self.errors.append(ParseError(
                "Expected closing ')' after while condition",
                "MISSING_PARENTHESIS",
                tok_close.line,
                tok_close.column,
                tok_close,
                expected=")"
            ))

        body = self.statement_block()
        return WhileNode(condition, body, line)

    def statement_block(self) -> List[ASTNode]:
        statements: List[ASTNode] = []
        if self.current().type == TokenType.BRACE and self.current().value == '{':
            self.advance()  # consume '{'
            while self.current().type != TokenType.EOF and not (self.current().type == TokenType.BRACE and self.current().value == '}'):
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
                else:
                    self.synchronize()

            if self.current().type == TokenType.BRACE and self.current().value == '}':
                self.advance()  # consume '}'
            else:
                tok = self.current()
                self.errors.append(ParseError(
                    "Expected closing brace '}' at end of block",
                    "MISSING_BRACE",
                    tok.line,
                    tok.column,
                    tok,
                    expected="}"
                ))
        else:
            # Single statement block without braces
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return statements

    # --- Expressions ---

    def expression(self) -> ASTNode:
        return self.equality()

    def equality(self) -> ASTNode:
        expr = self.relational()
        while self.current().type == TokenType.OPERATOR and self.current().value in {"==", "!="}:
            op = self.advance().value
            right = self.relational()
            expr = BinaryOpNode(op, expr, right, self.current().line)
        return expr

    def relational(self) -> ASTNode:
        expr = self.additive()
        while self.current().type == TokenType.OPERATOR and self.current().value in {"<", ">", "<=", ">="}:
            op = self.advance().value
            right = self.additive()
            expr = BinaryOpNode(op, expr, right, self.current().line)
        return expr

    def additive(self) -> ASTNode:
        expr = self.multiplicative()
        while self.current().type == TokenType.OPERATOR and self.current().value in {"+", "-"}:
            op = self.advance().value
            right = self.multiplicative()
            expr = BinaryOpNode(op, expr, right, self.current().line)
        return expr

    def multiplicative(self) -> ASTNode:
        expr = self.unary()
        while self.current().type == TokenType.OPERATOR and self.current().value in {"*", "/"}:
            op = self.advance().value
            right = self.unary()
            expr = BinaryOpNode(op, expr, right, self.current().line)
        return expr

    def unary(self) -> ASTNode:
        if self.current().type == TokenType.OPERATOR and self.current().value in {"-", "!"}:
            op = self.advance().value
            operand = self.unary()
            return UnaryOpNode(op, operand, self.current().line)
        return self.primary()

    def primary(self) -> ASTNode:
        tok = self.current()

        if tok.type == TokenType.INTEGER:
            self.advance()
            return LiteralNode(int(tok.value), "int", tok.line)

        if tok.type == TokenType.FLOAT:
            self.advance()
            return LiteralNode(float(tok.value), "float", tok.line)

        if tok.type == TokenType.STRING:
            self.advance()
            return LiteralNode(tok.value, "string", tok.line)

        if tok.type == TokenType.BOOLEAN:
            self.advance()
            val = True if tok.value == "true" else False
            return LiteralNode(val, "bool", tok.line)

        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            return VarAccessNode(tok.value, tok.line)

        if tok.type == TokenType.PARENTHESIS and tok.value == '(':
            self.advance()
            expr = self.expression()
            if self.current().type == TokenType.PARENTHESIS and self.current().value == ')':
                self.advance()
            else:
                c_tok = self.current()
                self.errors.append(ParseError(
                    "Expected closing ')' in expression",
                    "MISSING_PARENTHESIS",
                    c_tok.line,
                    c_tok.column,
                    c_tok,
                    expected=")"
                ))
            return expr

        # Unknown primary token
        self.advance()
        self.errors.append(ParseError(
            f"Unexpected expression token '{tok.value}'",
            "INVALID_EXPRESSION",
            tok.line,
            tok.column,
            tok
        ))
        return LiteralNode(0, "int", tok.line)
