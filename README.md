# CODE SENSE
### *An AI-Assisted Human-Friendly Mini Compiler*

CODE SENSE is a complete, educational, 20-mark Compiler Design project built in Python with a Tkinter Desktop GUI. It translates a C-like programming language through a full 8-stage compiler pipeline while integrating an offline rule-based **AI Code Doctor** that explains syntax errors, semantic mismatches, and code optimizations in human-friendly terms.

---

## 📌 Problem Statement

Traditional compiler errors (such as `SyntaxError: unexpected token at line 4, col 12`) can be cryptic and frustrating for novice programmers and students. Moreover, traditional compilers rarely explain *why* optimizations like constant folding occur. 

**CODE SENSE** bridges this gap by acting as both a real compiler and an educational mentor, decomposing every phase of compilation visually while providing clear explanations and fix suggestions.

---

## 🎯 Project Objectives

1. Demonstrate real-world **Compiler Design concepts**:
   - Lexical Analysis (Tokenization)
   - Syntax Analysis (Parsing & AST Generation)
   - Symbol Table & Scope Management
   - Semantic Analysis & Type Checking
   - Intermediate Code Generation (Three-Address Code)
   - Code Optimization (Constant Folding & Algebraic Simplification)
2. Provide a standalone offline **AI Code Doctor** to explain errors and optimizations cleanly.
3. Build a clean, dependency-free Python Desktop application for live viva demonstrations.

---

## 🏗 Compiler Architecture & Pipeline

```
               +-----------------------+
               |      Source Code      |
               +-----------------------+
                           |
                           v
               +-----------------------+
               |   Lexical Analyzer    | ---> Tokens List
               +-----------------------+
                           |
                           v
               +-----------------------+
               |   Recursive Parser    | ---> AST (Tree)
               +-----------------------+
                           |
                           v
               +-----------------------+
               | Symbol Table & Scope  | ---> Variable Records
               +-----------------------+
                           |
                           v
               +-----------------------+
               |   Semantic Analyzer   | ---> Type & Declaration Checks
               +-----------------------+
                           |
                           v
               +-----------------------+
               |  Intermediate Code    | ---> Three-Address Code (TAC)
               +-----------------------+
                           |
                           v
               +-----------------------+
               |    Code Optimizer     | ---> Folded & Simplified TAC
               +-----------------------+
                           |
                           v
               +-----------------------+
               |    AI Code Doctor     | ---> Human-Friendly Advice & Fixes
               +-----------------------+
```

---

## 🔤 Supported Language Specifications

### Data Types:
- `int` (e.g. `int x = 10;`)
- `float` (e.g. `float pi = 3.14;`)
- `string` (e.g. `string name = "alice";`)
- `bool` (e.g. `bool flag = true;`)

### Statements:
- **Variable Declarations**: `int x = 10;`, `float y;`
- **Assignments**: `x = 50;`
- **Output**: `print(z);`
- **Conditionals**: `if (x > 10) { print(x); } else { print(0); }`
- **Loops**: `while (count < 5) { count = count + 1; }`

### Operators & Delimiters:
- **Arithmetic**: `+`, `-`, `*`, `/`
- **Relational**: `>`, `<`, `>=`, `<=`, `==`, `!=`
- **Assignment**: `=`
- **Delimiters**: `(`, `)`, `{`, `}`, `;`

---

## 🚀 Key Features by Compiler Phase

1. **Lexical Analysis (`lexer.py`)**:
   - Converts source code into typed tokens (`KEYWORD`, `IDENTIFIER`, `INTEGER`, `FLOAT`, `STRING`, `BOOLEAN`, `OPERATOR`, `ASSIGNMENT`, `PARENTHESIS`, `BRACE`, `SEMICOLON`).
   - Reports line numbers, column positions, and invalid characters.

2. **Parsing & AST (`parser.py`, `ast_nodes.py`)**:
   - Top-down Recursive Descent Parser.
   - Builds an Abstract Syntax Tree (AST) with tree formatting methods.

3. **Symbol Table (`symbol_table.py`)**:
   - Tracks variable names, data types, values, declaration lines, and scope depth.
   - Detects duplicate definitions in the same scope.

4. **Semantic Analysis (`semantic.py`)**:
   - Ensures variables are declared before use.
   - Performs strict type checking (e.g., prevents assigning string `"twenty"` to `int`).

5. **Intermediate Code Generation (`intermediate_code.py`)**:
   - Translates AST into Three-Address Code (TAC) with temporary variables (`t1`, `t2`, ...) and jump labels (`L1`, `L2`, ...).

6. **Code Optimization (`optimizer.py`)**:
   - **Constant Folding**: Evaluates constant expressions at compile-time (e.g. `10 + 20 * 2` → `50`).
   - **Algebraic Simplification**: Applies identity rules (e.g. `x + 0` → `x`, `x * 1` → `x`, `x * 0` → `0`).

7. **AI Code Doctor (`ai_doctor.py`)**:
   - Rule-based offline error translation engine.
   - Formats errors with supportive emojis, clear explanations, and copy-paste code suggestions.

---

## 🛠 Technology Stack

- **Language**: Python 3.8+
- **GUI Framework**: Tkinter (Python Standard Library)
- **Dependencies**: None (Uses pure standard library: `tkinter`, `re`, `dataclasses`, `enum`, `typing`)

---

## 💻 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/CodeSense.git
   cd CodeSense
   ```

2. **Verify Python Installation**:
   Ensure Python 3.8 or higher is installed:
   ```bash
   python --version
   ```

3. **Run the Application**:
   Launch the Desktop GUI:
   ```bash
   python main.py
   ```

4. **Run Headless Verification Tests**:
   ```bash
   python main.py --test
   ```

---

## 🧪 Built-In Example Test Cases

| Test Case | Scenario Description | Expected Compiler Output |
|---|---|---|
| **Test 1** | Successful Compilation (`int x = 10 + 20; print(x);`) | ✅ Pass (Constant Folding Applied) |
| **Test 2** | Missing Semicolon (`int x = 10 \n print(x);`) | 🤖 AI Doctor suggests adding `;` |
| **Test 3** | Undeclared Variable (`x = 50; print(x);`) | 🤖 AI Doctor suggests declaring `int x;` |
| **Test 4** | Type Mismatch (`int age = "twenty";`) | 🤖 AI Doctor flags string → int mismatch |
| **Test 5** | Constant Folding (`int x = 10 + 20 * 2; print(x);`) | 🧠 `10 + 40` → `50` optimized |
| **Test 6** | Control Flow (If / Else & While) | ✅ Pass (Full control flow TAC generated) |

---

## ⚠️ Limitations

- **Scope Rules**: Scoping is simplified for block levels without function call stacks.
- **Type Widening**: Only basic `int` to `float` implicit conversion is supported.
- **Functions**: Does not support user-defined function declarations or parameters.

---

## 🔮 Future Scope

- Support for user-defined function definitions and call stack frames.
- Machine code / Assembly code generation (x86 or ARM assembly target).
- Syntax-highlighting code editor with inline error underlines.
