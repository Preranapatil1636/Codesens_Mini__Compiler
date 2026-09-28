"""
AI Code Doctor for CODE SENSE Mini Compiler.
Analyzes lexical, syntactic, semantic, and optimization events to produce
human-friendly, educational explanations and actionable suggestions with context.
"""

from typing import List, Optional
from lexer import LexerError
from parser import ParseError
from semantic import SemanticError

class AIDoctorReport:
    def __init__(
        self,
        headline: str,
        explanation: str,
        suggestion: Optional[str] = None,
        phase: str = "General",
        line: Optional[int] = None,
        why: Optional[str] = None
    ):
        self.headline = headline
        self.explanation = explanation
        self.suggestion = suggestion
        self.phase = phase
        self.line = line
        self.why = why

    def to_markdown(self) -> str:
        res = f"### 🤖 CODE DOCTOR DIAGNOSIS\n\n"
        res += f"**Issue:** {self.headline}\n\n"
        if self.line:
            res += f"📍 **Location:** Line {self.line}\n\n"
        res += f"**What happened:**\n{self.explanation}\n\n"
        if self.why:
            res += f"**Why:**\n{self.why}\n\n"
        if self.suggestion:
            res += "💡 **Suggested Fix:**\n```c\n" + self.suggestion + "\n```\n"
        return res

class AICodeDoctor:
    def diagnose_lexer_errors(self, errors: List[LexerError], source_code: str) -> AIDoctorReport:
        err = errors[0]
        if "Unterminated string" in err.message:
            return AIDoctorReport(
                headline="Unterminated String Literal",
                explanation=f"I noticed an opened string literal on line {err.line} that was not closed with double quotes before the line ended.",
                why="String constants in C-like languages must begin and end with double quotes on the same line.",
                suggestion='string greeting = "Hello, World!";',
                phase="Lexical Analysis",
                line=err.line
            )
        return AIDoctorReport(
            headline="Invalid Character Encountered",
            explanation=f"The compiler encountered an unrecognized character '{err.char}' on line {err.line}, column {err.column}.",
            why="The lexical analyzer breaks code into valid tokens (keywords, numbers, operators, identifiers). This symbol is not recognized.",
            suggestion="// Check for unintended special characters or typos",
            phase="Lexical Analysis",
            line=err.line
        )

    def diagnose_parser_errors(self, errors: List[ParseError], source_code: str) -> AIDoctorReport:
        err = errors[0]
        
        if err.error_type == "MISSING_SEMICOLON":
            lines = source_code.split('\n')
            offending_line = lines[err.line - 1] if err.line <= len(lines) else ""
            fixed_line = offending_line.strip() + ";"
            return AIDoctorReport(
                headline="Missing Semicolon",
                explanation=f"I think the statement on line {err.line} is missing a semicolon at the end.",
                why="The parser needs the semicolon to know where the statement ends and where the next statement begins.",
                suggestion=fixed_line if offending_line else "int x = 10;",
                phase="Syntax Analysis (Parsing)",
                line=err.line
            )

        if err.error_type == "MISSING_PARENTHESIS":
            return AIDoctorReport(
                headline="Missing Parenthesis",
                explanation=f"It looks like a closing ')' or opening '(' is missing around line {err.line}.",
                why="Conditions in control statements (if/while) and function calls require enclosing parentheses.",
                suggestion="if (x > 10) {\n    print(x);\n}",
                phase="Syntax Analysis (Parsing)",
                line=err.line
            )

        if err.error_type == "MISSING_BRACE":
            return AIDoctorReport(
                headline="Missing Block Brace",
                explanation=f"It looks like the closing brace '}}' is missing for a statement block around line {err.line}.",
                why="Curly braces '{{' and '}}' group multiple statements together into a single block.",
                suggestion="if (x > 0) {\n    print(x);\n}",
                phase="Syntax Analysis (Parsing)",
                line=err.line
            )

        return AIDoctorReport(
            headline="Syntax Error",
            explanation=f"The parser expected '{err.expected or 'a valid token'}' on line {err.line}, but found '{err.token_found.value}' instead.",
            why="The sequence of tokens does not conform to the formal grammar rules of the language.",
            suggestion="// Review syntax structure around line " + str(err.line),
            phase="Syntax Analysis (Parsing)",
            line=err.line
        )

    def diagnose_semantic_errors(self, errors: List[SemanticError], source_code: str) -> AIDoctorReport:
        err = errors[0]

        if err.error_type == "UNDECLARED_VARIABLE":
            var_name = err.var_name or "variable"
            return AIDoctorReport(
                headline=f"Undeclared Variable '{var_name}'",
                explanation=f"I couldn't find a declaration for '{var_name}'. You may want to declare it before using it.",
                why=f"Variables in strongly-typed languages must be declared with a data type before being assigned or referenced.",
                suggestion=f"int {var_name} = 50;\nprint({var_name});",
                phase="Semantic Analysis",
                line=err.line
            )

        if err.error_type == "DUPLICATE_DECLARATION":
            var_name = err.var_name or "variable"
            return AIDoctorReport(
                headline=f"Duplicate Variable Declaration '{var_name}'",
                explanation=f"Variable '{var_name}' is declared multiple times in the same scope around line {err.line}.",
                why="Redeclaring an existing variable causes identifier collisions in the Symbol Table.",
                suggestion=f"// Declare once:\nint {var_name} = 10;\n// Then assign without repeating type:\n{var_name} = 20;",
                phase="Semantic Analysis",
                line=err.line
            )

        if err.error_type == "DIVISION_BY_ZERO":
            return AIDoctorReport(
                headline="Division by Zero",
                explanation="The expression attempts to divide a value by zero.",
                why="Division by zero is undefined, so the compiler stops before generating a successful program result.",
                suggestion="Change the denominator so it cannot be zero.\nExample: print(x / 2);",
                phase="Semantic Analysis",
                line=err.line
            )

        if err.error_type == "TYPE_MISMATCH":
            var_name = err.var_name or "variable"
            exp = err.expected_type or "target type"
            rec = err.received_type or "value type"
            return AIDoctorReport(
                headline="Type Mismatch",
                explanation=f"There is a type mismatch. '{var_name}' expects an {exp}, but a {rec} was provided.",
                why=f"Variable '{var_name}' was declared as '{exp}', which cannot store values of type '{rec}'.",
                suggestion=f"int age = 20; // Provide an integer value",
                phase="Semantic Analysis",
                line=err.line
            )

        return AIDoctorReport(
            headline="Semantic Error",
            explanation=err.message,
            why="Semantic analysis verifies type consistency and declaration scoping rules.",
            suggestion="// Check variable types and scoping",
            phase="Semantic Analysis",
            line=err.line
        )

    def explain_optimizations(self, opt_logs: List[str]) -> AIDoctorReport:
        if not opt_logs:
            return AIDoctorReport(
                headline="Code Clean & Optimal",
                explanation="No compile-time optimizations were required for this program.",
                why="All expressions are already minimal or depend on dynamic values.",
                suggestion=None,
                phase="Code Optimization"
            )

        explanation = "The compiler performed the following optimizations during compilation:\n\n"
        for log in opt_logs:
            explanation += f"- {log}\n"

        return AIDoctorReport(
            headline="Optimization Insights",
            explanation=explanation,
            why="Evaluating constant values and simplifying expressions at compile time avoids unnecessary runtime arithmetic, making the compiled program run faster!",
            suggestion=None,
            phase="Code Optimization"
        )
