"""
Symbol Table Management for CODE SENSE Mini Compiler.
Manages variable declarations, scoping, types, values, and duplicate definition checks.
"""

from typing import Dict, List, Optional, Any, Tuple

class Symbol:
    def __init__(self, name: str, var_type: str, value: Any = None, line: int = 0, scope_level: int = 0):
        self.name = name
        self.type = var_type
        self.value = value
        self.line = line
        self.scope_level = scope_level

    def __repr__(self) -> str:
        val_str = f'"{self.value}"' if self.type == "string" and self.value is not None else str(self.value)
        return f"Symbol({self.name}, {self.type}, val={val_str}, line={self.line}, scope={self.scope_level})"

class SymbolTable:
    def __init__(self):
        # Stack of scopes: scope[0] is global scope
        self.scopes: List[Dict[str, Symbol]] = [{}]
        self.scope_level = 0
        self.all_symbols: List[Symbol] = []  # Keep record of all symbols ever declared for UI display

    def enter_scope(self):
        self.scope_level += 1
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.scope_level -= 1

    def define(self, name: str, var_type: str, value: Any = None, line: int = 0) -> Tuple[bool, Optional[str]]:
        current_scope = self.scopes[-1]
        if name in current_scope:
            existing = current_scope[name]
            return False, f"Duplicate declaration of variable '{name}'. Already declared on line {existing.line}."

        sym = Symbol(name, var_type, value, line, self.scope_level)
        current_scope[name] = sym
        self.all_symbols.append(sym)
        return True, None

    def lookup(self, name: str) -> Optional[Symbol]:
        # Search from current scope outwards to global scope
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def update_value(self, name: str, value: Any) -> bool:
        sym = self.lookup(name)
        if sym:
            sym.value = value
            return True
        return False

    def reset(self):
        self.scopes = [{}]
        self.scope_level = 0
        self.all_symbols = []
