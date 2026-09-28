"""
Lexical Analyzer (Lexer) for CODE SENSE Mini Compiler.
Converts source code string into a sequence of structured Tokens.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Optional

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    OPERATOR = auto()
    ASSIGNMENT = auto()
    PARENTHESIS = auto()
    BRACE = auto()
    SEMICOLON = auto()
    EOF = auto()
    UNKNOWN = auto()

KEYWORDS = {"int", "float", "string", "bool", "if", "else", "while", "print"}
BOOLEANS = {"true", "false"}

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.type.name}({self.value}) at line {self.line}:{self.column}"

@dataclass
class LexerError:
    message: str
    line: int
    column: int
    char: str

class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.length = len(source_code)
        self.tokens: List[Token] = []
        self.errors: List[LexerError] = []

    def peek(self) -> Optional[str]:
        if self.position < self.length:
            return self.source[self.position]
        return None

    def advance(self) -> Optional[str]:
        char = self.peek()
        if char is not None:
            self.position += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return char

    def tokenize(self) -> Tuple[List[Token], List[LexerError]]:
        self.tokens = []
        self.errors = []

        while self.position < self.length:
            char = self.peek()

            if char is None:
                break

            # Skip whitespace
            if char in " \t\r\n":
                self.advance()
                continue

            # Semicolon
            if char == ';':
                start_col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ";", self.line, start_col))
                continue

            # Parentheses and Braces
            if char in "()":
                start_col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.PARENTHESIS, char, self.line, start_col))
                continue

            if char in "{}":
                start_col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.BRACE, char, self.line, start_col))
                continue

            # Single-line and Multi-line Comments or Division Operator
            if char == '/':
                start_col = self.column
                if self.position + 1 < self.length and self.source[self.position + 1] == '/':
                    # Single-line comment: skip until newline
                    self.advance() # consume '/'
                    self.advance() # consume '/'
                    while self.position < self.length and self.peek() != '\n':
                        self.advance()
                    continue
                elif self.position + 1 < self.length and self.source[self.position + 1] == '*':
                    # Multi-line comment: skip until */
                    self.advance() # consume '/'
                    self.advance() # consume '*'
                    while self.position < self.length:
                        if self.peek() == '*' and self.position + 1 < self.length and self.source[self.position + 1] == '/':
                            self.advance() # consume '*'
                            self.advance() # consume '/'
                            break
                        self.advance()
                    continue
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.OPERATOR, "/", self.line, start_col))
                    continue

            # Operators (+ - *)
            if char in "+-*":
                start_col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.OPERATOR, char, self.line, start_col))
                continue

            if char in "=!<>":
                start_col = self.column
                first_char = self.advance()
                if self.peek() == '=':
                    op = first_char + self.advance()
                    self.tokens.append(Token(TokenType.OPERATOR, op, self.line, start_col))
                else:
                    if first_char == '=':
                        self.tokens.append(Token(TokenType.ASSIGNMENT, "=", self.line, start_col))
                    elif first_char in ('<', '>'):
                        self.tokens.append(Token(TokenType.OPERATOR, first_char, self.line, start_col))
                    else:
                        self.errors.append(LexerError(f"Unexpected character '{first_char}'", self.line, start_col, first_char))
                continue

            # String literals
            if char == '"':
                start_line = self.line
                start_col = self.column
                self.advance() # Consume opening quote
                val = ""
                terminated = False
                while self.position < self.length:
                    curr = self.peek()
                    if curr == '"':
                        self.advance() # Consume closing quote
                        terminated = True
                        break
                    elif curr == '\n':
                        break
                    else:
                        val += self.advance()

                if terminated:
                    self.tokens.append(Token(TokenType.STRING, val, start_line, start_col))
                else:
                    self.errors.append(LexerError("Unterminated string literal", start_line, start_col, '"'))
                continue

            # Numbers (Integer or Float)
            if char.isdigit():
                start_col = self.column
                val = ""
                has_dot = False
                while self.position < self.length:
                    curr = self.peek()
                    if curr is not None and curr.isdigit():
                        val += self.advance()
                    elif curr == '.' and not has_dot:
                        if self.position + 1 < self.length and self.source[self.position + 1].isdigit():
                            has_dot = True
                            val += self.advance()
                        else:
                            break
                    else:
                        break

                t_type = TokenType.FLOAT if has_dot else TokenType.INTEGER
                self.tokens.append(Token(t_type, val, self.line, start_col))
                continue

            # Identifiers and Keywords
            if char.isalpha() or char == '_':
                start_col = self.column
                val = ""
                while self.position < self.length:
                    curr = self.peek()
                    if curr is not None and (curr.isalnum() or curr == '_'):
                        val += self.advance()
                    else:
                        break

                if val in KEYWORDS:
                    self.tokens.append(Token(TokenType.KEYWORD, val, self.line, start_col))
                elif val in BOOLEANS:
                    self.tokens.append(Token(TokenType.BOOLEAN, val, self.line, start_col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, val, self.line, start_col))
                continue

            # Invalid Character
            start_col = self.column
            bad_char = self.advance()
            self.errors.append(LexerError(f"Invalid character '{bad_char}'", self.line, start_col, bad_char))

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens, self.errors
