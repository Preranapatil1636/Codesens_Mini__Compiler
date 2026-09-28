"""
CODE SENSE — AI-Assisted Human-Friendly Mini Compiler.
Main entry point orchestrating the 8-stage compiler pipeline and Tkinter Desktop UI.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, font
from typing import List, Tuple, Dict, Any, Optional

from lexer import Lexer, Token, LexerError
from ast_nodes import ProgramNode
from parser import Parser, ParseError
from symbol_table import SymbolTable, Symbol
from semantic import SemanticAnalyzer, SemanticError
from intermediate_code import TACGenerator
from optimizer import Optimizer
from ai_doctor import AICodeDoctor, AIDoctorReport
from examples import TEST_CASES

class CompilerPipeline:
    """Orchestrates the entire 8-stage compilation process with phase-aware error handling."""
    def __init__(self, source_code: str):
        self.source_code = source_code
        
        self.tokens: List[Token] = []
        self.lexer_errors: List[LexerError] = []
        
        self.ast: Optional[ProgramNode] = None
        self.parser_errors: List[ParseError] = []
        
        self.symbol_table: Optional[SymbolTable] = None
        self.semantic_errors: List[SemanticError] = []
        
        self.unoptimized_tac: List[str] = []
        self.optimized_tac: List[str] = []
        self.opt_logs: List[str] = []
        self.optimized_ast: Optional[ProgramNode] = None
        
        self.doctor_report: Optional[AIDoctorReport] = None
        self.success: bool = False
        self.failed_stage: Optional[str] = None

    def run(self) -> bool:
        doctor = AICodeDoctor()

        # 1. Lexical Analysis
        lexer = Lexer(self.source_code)
        self.tokens, self.lexer_errors = lexer.tokenize()

        if self.lexer_errors:
            self.failed_stage = "Lexical Analysis"
            self.doctor_report = doctor.diagnose_lexer_errors(self.lexer_errors, self.source_code)
            return False

        # 2. Syntax Analysis (Parser & AST Generation)
        parser = Parser(self.tokens)
        self.ast, self.parser_errors = parser.parse()

        if self.parser_errors:
            self.failed_stage = "Syntax Analysis (Parsing)"
            self.doctor_report = doctor.diagnose_parser_errors(self.parser_errors, self.source_code)
            return False

        # 3. Symbol Table & Semantic Analysis
        analyzer = SemanticAnalyzer()
        self.symbol_table, self.semantic_errors = analyzer.analyze(self.ast)

        # 4. Intermediate Code Generation & Optimization (Runs safely if parsing succeeded!)
        if self.ast:
            optimizer = Optimizer()
            self.optimized_ast, self.opt_logs, self.unoptimized_tac, self.optimized_tac = optimizer.optimize(self.ast)

        if self.semantic_errors:
            self.failed_stage = "Semantic Analysis"
            self.doctor_report = doctor.diagnose_semantic_errors(self.semantic_errors, self.source_code)
            self.success = False
            return False

        # 5. AI Doctor Optimization Insights (Valid Program)
        self.doctor_report = doctor.explain_optimizations(self.opt_logs)
        self.success = True
        return True


class CodeSenseGUI:
    """Standalone Desktop Application UI built with Tkinter."""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CodeSense — AI-Assisted Human-Friendly Mini Compiler")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)

        self._configure_styles()
        self._build_ui()
        first_example = list(TEST_CASES.keys())[0] if TEST_CASES else ""
        if first_example:
            self._load_example(first_example)

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Color palette
        self.bg_dark = "#1e1e2e"
        self.fg_light = "#cdd6f4"
        self.accent_blue = "#89b4fa"
        self.accent_green = "#a6e3a1"
        self.accent_red = "#f38ba8"
        self.bg_panel = "#181825"
        
        self.root.configure(bg=self.bg_dark)
        
        style.configure("TFrame", background=self.bg_dark)
        style.configure("TLabel", background=self.bg_dark, foreground=self.fg_light, font=("Consolas", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=self.accent_blue)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "italic"), foreground="#a6adc8")
        
        style.configure("TNotebook", background=self.bg_panel, borderwidth=0)
        style.configure("TNotebook.Tab", background="#313244", foreground=self.fg_light, padding=[10, 5], font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.accent_blue)], foreground=[("selected", "#11111b")])
        
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Compile.TButton", background=self.accent_green, foreground="#11111b")
        style.configure("Clear.TButton", background="#45475a", foreground=self.fg_light)

    def _build_ui(self):
        # Header banner
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(header_frame, text="CodeSense", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame, text="  — AI-Assisted Human-Friendly Mini Compiler", style="SubHeader.TLabel")
        subtitle_label.pack(side=tk.LEFT)

        # Main Paned Window (Left: Code Editor, Right: Compiler Pipeline Notebook)
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.bg_dark, bd=0, sashwidth=6)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left Panel (Source Code Input)
        left_panel = ttk.Frame(main_pane, padding=5)
        main_pane.add(left_panel, minsize=400)

        # Controls & Dropdown
        controls_frame = ttk.Frame(left_panel)
        controls_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(controls_frame, text="Preset Examples:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.example_var = tk.StringVar()
        example_cb = ttk.Combobox(controls_frame, textvariable=self.example_var, values=list(TEST_CASES.keys()), state="readonly", width=42)
        example_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
        example_cb.bind("<<ComboboxSelected>>", lambda e: self._load_example(self.example_var.get()))

        # Editor Frame
        editor_frame = ttk.Frame(left_panel)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(editor_frame, text="Source Code Editor:").pack(anchor=tk.W)

        self.code_text = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg="#11111b",
            fg="#cdd6f4",
            insertbackground="#f5e0dc",
            selectbackground="#45475a",
            bd=1,
            relief=tk.SOLID
        )
        scrollbar_y = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.code_text.yview)
        scrollbar_x = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.code_text.xview)
        self.code_text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.code_text.pack(fill=tk.BOTH, expand=True)

        # Action Buttons
        btn_frame = ttk.Frame(left_panel, padding=(0, 8))
        btn_frame.pack(fill=tk.X)

        compile_btn = tk.Button(btn_frame, text="⚡ COMPILE", bg="#a6e3a1", fg="#11111b", font=("Segoe UI", 11, "bold"), relief=tk.RAISED, command=self.compile_code, cursor="hand2")
        compile_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        clear_btn = tk.Button(btn_frame, text="🧹 CLEAR", bg="#45475a", fg="#cdd6f4", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, command=self.clear_code, cursor="hand2")
        clear_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Right Panel (Notebook Tabs for Compiler Phases)
        right_panel = ttk.Frame(main_pane, padding=5)
        main_pane.add(right_panel, minsize=550)

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.tab_tokens = self._create_tab("Tokens")
        self.tab_ast = self._create_tab("AST")
        self.tab_symbol = self._create_tab("Symbol Table")
        self.tab_semantic = self._create_tab("Semantic")
        self.tab_tac = self._create_tab("3-Addr Code")
        self.tab_opt = self._create_tab("Optimization")
        self.tab_ai = self._create_tab("🤖 AI Doctor")
        self.tab_result = self._create_tab("Result")

        self._setup_token_tab()
        self._setup_symbol_tab()
        self._setup_text_tab(self.tab_ast, "ast_text")
        self._setup_text_tab(self.tab_semantic, "semantic_text")
        self._setup_text_tab(self.tab_tac, "tac_text")
        self._setup_text_tab(self.tab_opt, "opt_text")
        self._setup_text_tab(self.tab_ai, "ai_text")
        self._setup_text_tab(self.tab_result, "result_text")

    def _create_tab(self, title: str) -> ttk.Frame:
        frame = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(frame, text=title)
        return frame

    def _setup_text_tab(self, parent: ttk.Frame, attr_name: str):
        text_widget = tk.Text(
            parent,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#11111b",
            fg="#cdd6f4",
            bd=0,
            padx=10,
            pady=10
        )
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(fill=tk.BOTH, expand=True)
        setattr(self, attr_name, text_widget)

    def _setup_token_tab(self):
        columns = ("Index", "Token Type", "Value", "Line:Col")
        self.token_tree = ttk.Treeview(self.tab_tokens, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.token_tree.heading(col, text=col)
            self.token_tree.column(col, anchor=tk.CENTER, width=120)

        scrollbar = ttk.Scrollbar(self.tab_tokens, orient=tk.VERTICAL, command=self.token_tree.yview)
        self.token_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.token_tree.pack(fill=tk.BOTH, expand=True)

    def _setup_symbol_tab(self):
        columns = ("Name", "Data Type", "Value", "Declared Line", "Scope Level")
        self.symbol_tree = ttk.Treeview(self.tab_symbol, columns=columns, show="headings", height=15)

        for col in columns:
            self.symbol_tree.heading(col, text=col)
            self.symbol_tree.column(col, anchor=tk.CENTER, width=120)

        scrollbar = ttk.Scrollbar(self.tab_symbol, orient=tk.VERTICAL, command=self.symbol_tree.yview)
        self.symbol_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.symbol_tree.pack(fill=tk.BOTH, expand=True)

    def _load_example(self, example_key: str):
        if example_key in TEST_CASES:
            self.example_var.set(example_key)
            self.code_text.delete("1.0", tk.END)
            self.code_text.insert(tk.END, TEST_CASES[example_key].strip())

    def clear_code(self):
        self.code_text.delete("1.0", tk.END)
        self._clear_tabs()

    def _clear_tabs(self):
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
        for item in self.symbol_tree.get_children():
            self.symbol_tree.delete(item)
            
        for attr in ("ast_text", "semantic_text", "tac_text", "opt_text", "ai_text", "result_text"):
            txt = getattr(self, attr)
            txt.delete("1.0", tk.END)

    def compile_code(self):
        self._clear_tabs()
        source = self.code_text.get("1.0", tk.END)
        
        if not source.strip():
            messagebox.showwarning("Empty Source Code", "Please enter or select source code before compiling.")
            return

        pipeline = CompilerPipeline(source)
        success = pipeline.run()

        # 1. Populate Tokens Tab
        if pipeline.tokens:
            for idx, tok in enumerate(pipeline.tokens):
                if tok.type.name != "EOF":
                    self.token_tree.insert("", tk.END, values=(idx + 1, tok.type.name, tok.value, f"{tok.line}:{tok.column}"))
        else:
            self.token_tree.insert("", tk.END, values=("⚠ Not available", "Lexical analysis failed", "-", "-"))

        # 2. Populate AST Tab
        if pipeline.ast and not pipeline.parser_errors:
            self.ast_text.insert(tk.END, "✓ AST Generated Successfully:\n\n" + pipeline.ast.to_tree_string())
        elif pipeline.lexer_errors:
            self.ast_text.insert(tk.END, "⚠ Not available\n\nReason:\nLexical analysis failed, so no valid tokens were passed to the parser.")
        else:
            err_msg = pipeline.parser_errors[0].message if pipeline.parser_errors else "Syntax error"
            self.ast_text.insert(tk.END, f"❌ Syntax Error\n\nReason:\nParsing failed: {err_msg}")

        # 3. Populate Symbol Table Tab
        if pipeline.symbol_table and not pipeline.parser_errors:
            for sym in pipeline.symbol_table.all_symbols:
                val_str = f'"{sym.value}"' if sym.type == "string" and sym.value is not None else (str(sym.value) if sym.value is not None else "None")
                self.symbol_tree.insert("", tk.END, values=(sym.name, sym.type, val_str, sym.line, sym.scope_level))
        else:
            self.symbol_tree.insert("", tk.END, values=("⚠ Not available", "Reason: Parsing failed, symbol table not generated.", "-", "-", "-"))

        # 4. Populate Semantic Tab
        if pipeline.lexer_errors or pipeline.parser_errors:
            self.semantic_text.insert(tk.END, "⚠ Not available\n\nReason:\nSemantic analysis requires a valid AST.")
        elif pipeline.semantic_errors:
            self.semantic_text.insert(tk.END, f"❌ Error (Semantic Analysis Failed)\n\nFound {len(pipeline.semantic_errors)} Semantic Error(s):\n")
            for err in pipeline.semantic_errors:
                self.semantic_text.insert(tk.END, f"• [Line {err.line}] {err.message}\n")
        else:
            self.semantic_text.insert(tk.END, "✓ Completed\n\nSemantic analysis passed cleanly!\n- All variables declared before use.\n- No duplicate declarations.\n- All types compatible.")

        # 5. Populate TAC Tab
        if pipeline.lexer_errors or pipeline.parser_errors:
            self.tac_text.insert(tk.END, "⚠ Not available\n\nReason:\nThree Address Code cannot be generated because parsing failed.")
        elif pipeline.unoptimized_tac:
            status_hdr = "✓ Generated (Intermediate Three-Address Code)\n" if not pipeline.semantic_errors else "✓ Generated (AST-level Intermediate Code)\n"
            self.tac_text.insert(tk.END, status_hdr + "-"*45 + "\n")
            for line in pipeline.unoptimized_tac:
                self.tac_text.insert(tk.END, f"  {line}\n")
        else:
            self.tac_text.insert(tk.END, "⚠ Not available\n\nReason:\nNo TAC instructions generated.")

        # 6. Populate Optimization Tab
        if pipeline.lexer_errors or pipeline.parser_errors:
            self.opt_text.insert(tk.END, "⚠ Not available\n\nReason:\nOptimization requires valid intermediate code.")
        elif pipeline.optimized_tac:
            status_hdr = "✓ Completed\n\n" if not pipeline.semantic_errors else "✓ Completed (Applied on valid AST expressions)\n\n"
            self.opt_text.insert(tk.END, status_hdr)
            self.opt_text.insert(tk.END, "=== BEFORE OPTIMIZATION (TAC) ===\n")
            for line in pipeline.unoptimized_tac:
                self.opt_text.insert(tk.END, f"  {line}\n")
            
            self.opt_text.insert(tk.END, "\n=== OPTIMIZATION LOGS ===\n")
            if pipeline.opt_logs:
                for log in pipeline.opt_logs:
                    self.opt_text.insert(tk.END, f"  {log}\n")
            else:
                self.opt_text.insert(tk.END, "  (No optimizations applicable)\n")

            self.opt_text.insert(tk.END, "\n=== AFTER OPTIMIZATION (TAC) ===\n")
            for line in pipeline.optimized_tac:
                self.opt_text.insert(tk.END, f"  {line}\n")
        else:
            self.opt_text.insert(tk.END, "⚠ Not available\n\nReason:\nNo intermediate code available for optimization.")

        # 7. Populate AI Doctor Tab
        if pipeline.doctor_report:
            self.ai_text.insert(tk.END, pipeline.doctor_report.to_markdown())
            if not success:
                self.notebook.select(self.tab_ai)  # Switch to AI Doctor tab automatically on error!

        # 8. Populate Result Tab
        self._populate_result_tab(pipeline, success)

    def _populate_result_tab(self, pipeline: CompilerPipeline, success: bool):
        self.result_text.delete("1.0", tk.END)

        if success:
            self.result_text.insert(tk.END, "LEXICAL ANALYSIS\n✓ Completed\n\n")
            self.result_text.insert(tk.END, "SYNTAX ANALYSIS\n✓ Completed\n\n")
            self.result_text.insert(tk.END, "AST\n✓ Generated\n\n")
            self.result_text.insert(tk.END, "SYMBOL TABLE\n✓ Generated\n\n")
            self.result_text.insert(tk.END, "SEMANTIC ANALYSIS\n✓ Completed\n\n")
            self.result_text.insert(tk.END, "THREE ADDRESS CODE\n✓ Generated\n\n")
            self.result_text.insert(tk.END, "OPTIMIZATION\n✓ Completed\n\n")
            self.result_text.insert(tk.END, "Compilation Successful!\n")

        elif pipeline.failed_stage == "Lexical Analysis":
            err_msg = pipeline.lexer_errors[0].message if pipeline.lexer_errors else "Invalid character"
            self.result_text.insert(tk.END, f"LEXICAL ANALYSIS\n❌ Error\n{err_msg}\n\n")
            self.result_text.insert(tk.END, "SYNTAX ANALYSIS\n⚠ Not available\nReason: Lexical analysis failed.\n\n")
            self.result_text.insert(tk.END, "SEMANTIC ANALYSIS\n⚠ Not available\nReason: Lexical analysis failed.\n\n")
            self.result_text.insert(tk.END, "THREE ADDRESS CODE\n⚠ Not available\nReason: Three Address Code cannot be generated because lexical analysis failed.\n\n")
            self.result_text.insert(tk.END, "OPTIMIZATION\n⚠ Not available\nReason: Optimization requires valid intermediate code.\n\n")
            self.result_text.insert(tk.END, "❌ Compilation failed during Lexical Analysis.\n")

        elif pipeline.failed_stage == "Syntax Analysis (Parsing)":
            err_msg = pipeline.parser_errors[0].message if pipeline.parser_errors else "Syntax error"
            self.result_text.insert(tk.END, "LEXICAL ANALYSIS\n✓ Completed\n\n")
            self.result_text.insert(tk.END, f"SYNTAX ANALYSIS\n❌ Error\n{err_msg}\n\n")
            self.result_text.insert(tk.END, "SEMANTIC ANALYSIS\n⚠ Not available\nReason: Semantic analysis requires a valid AST.\n\n")
            self.result_text.insert(tk.END, "THREE ADDRESS CODE\n⚠ Not available\nReason: Three Address Code cannot be generated because parsing failed.\n\n")
            self.result_text.insert(tk.END, "OPTIMIZATION\n⚠ Not available\nReason: Optimization requires valid intermediate code.\n\n")
            self.result_text.insert(tk.END, "❌ Compilation failed during Syntax Analysis (Parsing).\n")

        elif pipeline.failed_stage == "Semantic Analysis":
            err_msg = pipeline.semantic_errors[0].message if pipeline.semantic_errors else "Semantic error"
            self.result_text.insert(tk.END, "LEXICAL ANALYSIS\n✓ Completed\n\n")
            self.result_text.insert(tk.END, "SYNTAX ANALYSIS\n✓ Completed\n\n")
            self.result_text.insert(tk.END, "AST\n✓ Generated\n\n")
            self.result_text.insert(tk.END, "SYMBOL TABLE\n✓ Generated\n\n")
            self.result_text.insert(tk.END, f"SEMANTIC ANALYSIS\n❌ Error\n{err_msg}\n\n")
            self.result_text.insert(tk.END, "THREE ADDRESS CODE\n✓ Generated (AST-level intermediate code)\n\n")
            self.result_text.insert(tk.END, "OPTIMIZATION\n✓ Completed (Optimizations applied where safe)\n\n")
            self.result_text.insert(tk.END, "❌ Compilation failed during semantic analysis.\n")


def run_tests():
    """Headless CLI test runner for verifying built-in test cases."""
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    print("="*60)
    print("CODE SENSE - AUTOMATED TEST SUITE VERIFICATION")
    print("="*60)
    
    passed_count = 0
    total_count = len(TEST_CASES)

    for name, code in TEST_CASES.items():
        print(f"\n> Running {name}...")
        pipeline = CompilerPipeline(code)
        success = pipeline.run()
        
        # Test 1, 5, 6 expected success; Test 2, 3, 4 expected failure
        if "Test 1" in name or "Test 5" in name or "Test 6" in name:
            expected_success = True
        else:
            expected_success = False

        if success == expected_success:
            print(f"  [PASS] (Success={success}, FailedStage={pipeline.failed_stage or 'None'})")
            if pipeline.doctor_report:
                print(f"  Headline: {pipeline.doctor_report.headline}")
            passed_count += 1
        else:
            print(f"  [FAIL] (Expected Success={expected_success}, got {success})")
            if pipeline.doctor_report:
                print(f"  Error report: {pipeline.doctor_report.headline}")

    print("\n" + "="*60)
    print(f"TEST RESULT SUMMARY: {passed_count}/{total_count} PASSED")
    print("="*60)
    sys.exit(0 if passed_count == total_count else 1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        root = tk.Tk()
        app = CodeSenseGUI(root)
        root.mainloop()
