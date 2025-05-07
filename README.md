# 🦸‍♂️ SuperHero Programming Language Compiler

A mini-compiler for the custom-designed **SuperHero Programming Language**, written in Python. The compiler translates `.hero` source code into C, compiles it using `gcc`, and generates executable machine code.

---

## 📦 Features

✅ Lexical analysis  
✅ Parsing into AST  
✅ C code generation  
✅ Compilation to executable using GCC or MSVC  
✅ Supports keywords like `ironman`, `thor`, `starlord`, `spiderman`, `falcon`, `hawkeye`, `loki`, and more.

---

## 💻 Usage

1. Prepare a `.hero` source file (example: `hello.hero`):

```hero
starlord "Hello, World!"

```bash
python superhero_compiler.py hello.hero -o hello.exe -v

```run
.\hello.exe  # Windows
./hello      # Linux/Mac
