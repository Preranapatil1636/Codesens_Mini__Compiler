"""
Pre-loaded Example Programs for CODE SENSE Mini Compiler.
Used in GUI dropdown and test suite verification.
"""

TEST_CASES = {
    "Test 1 — Valid Program (Complete Pipeline)": """int x = 10;
int y = 20;
print(x + y);
""",

    "Test 2 — Missing Semicolon (Syntax Error)": """int x = 10
print(x);
""",

    "Test 3 — Type Mismatch (Semantic Error)": """int age = "twenty";
""",

    "Test 4 — Undeclared Variable (Semantic Error)": """x = 50;
print(x);
""",

    "Test 5 — Constant Folding Optimization": """int x = 10 + 20 * 2;
print(x);
""",

    "Test 6 — Control Flow (If / Else & While)": """int count = 0;
int max = 5;

while (count < max) {
    count = count + 1;
}

if (count == 5) {
    print("Reached max!");
} else {
    print("Incomplete");
}
""",

    "Test 7 — Division by Zero (Semantic Error)": """int x = 10;
int y = 0;
print(x / y);
"""
}
