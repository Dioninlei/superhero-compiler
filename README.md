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

# SuperHero Programming Language Compiler

## Introduction

The SuperHero Programming Language is a fun and creative esoteric programming language inspired by superheroes from popular comic universes. Each keyword in the language corresponds to a superhero with functionality that matches their persona. The compiler translates SuperHero code (.hero files) to C as an intermediate representation, then uses gcc to compile to executable machine code.

This project implements a complete compiler toolchain including lexical analysis, parsing, and code generation for the SuperHero language.

## Language Overview

SuperHero is a cell-based language with a memory tape (similar to Brainfuck but with a much friendlier syntax). Each superhero command manipulates the memory tape or program flow in unique ways:

| Superhero | Function |
|-----------|----------|
| IRONMAN | Increment the current cell value |
| BATMAN | Decrement the current cell value |
| SUPERMAN | Move pointer to the right |
| WONDERWOMAN | Move pointer to the left |
| FLASH | Define/call a loop |
| SPIDERMAN | Conditional statement (if) |
| THOR | Print the cell value |
| HULK | Input to cell |
| DOCTORSTRANGE | Array declaration |
| BLACKPANTHER | Array input |
| CAPTAINAMERICA | Array output |
| VISION | Reference to current cell |
| STARLORD | Print string |
| DEADPOOL | Reset pointer to 0 |
| LOKI | Clear cell value |
| FALCON | Define label |
| HAWKEYE | Goto label |
| THANOS | End program |
| ADD | Addition operation |
| SUB | Subtraction operation |

## Compiler Implementation

The compiler is structured into three main components:

1. **Lexical Analyzer (Lexer)**: Tokenizes the SuperHero source code
2. **Parser**: Constructs an abstract syntax tree (AST) from tokens
3. **Code Generator**: Translates the AST into C code

### Lexical Analysis

The lexer scans the source code and converts it into a sequence of tokens. It handles:

- Keywords (superhero names)
- Identifiers
- String literals
- Numbers
- Operators
- Cell references (using # prefix)
- Comments (single line with "hero>" prefix and multiline with "heroes*" and "*heroes")

```python
class SuperHeroLexer:
    def __init__(self):
        self.keywords = {
            "ironman": TokenType.IRONMAN,
            "batman": TokenType.BATMAN,
            # Additional keywords omitted for brevity
        }
        
    def tokenize(self, code):
        lines = code.split('\n')
        tokens = []
        multiline_comment = False
        
        for line_num, line in enumerate(lines, 1):
            # Handle comments and tokenization
            # ...
```

### Parser

The parser converts the token stream into an abstract syntax tree (AST). It performs:

- First pass to collect all labels and loops
- Statement parsing for each superhero command
- Error handling for invalid syntax

```python
class SuperHeroParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.indent_stack = [0]
        self.labels = set()
        self.flashes = {}  # Flash loops
        self.doctorstranges = {}  # Doctor Strange arrays
    
    def parse(self):
        code_blocks = []
        self.first_pass()  # Collect all labels and flash loops
        
        while not self.is_at_end():
            statement = self.parse_statement()
            if statement:
                code_blocks.append(statement)
        
        return code_blocks
```

### Code Generator

The code generator translates the AST into C code, which is then compiled to machine code:

```python
class CodeGenerator:
    def __init__(self, ast, doctorstranges):
        self.ast = ast
        self.doctorstranges = doctorstranges
        self.code = []
        self.indent_level = 0
    
    def generate(self):
        # Generate C code preamble with necessary headers
        # Generate C code for each AST node
        # Return the complete C program
```

## Compilation Process

The overall compilation process follows these steps:

1. Read the SuperHero source file (.hero)
2. Lexical analysis to produce tokens
3. Parsing tokens into an AST
4. Generating C code from the AST
5. Compiling the C code to an executable with gcc
6. Outputting the final executable

```python
def compile_superhero(source_file, output_file=None, verbose=False):
    # Read source code
    with open(source_file, 'r') as f:
        source_code = f.read()
    
    # Lexical analysis
    lexer = SuperHeroLexer()
    tokens = lexer.tokenize(source_code)
    
    # Parsing
    parser = SuperHeroParser(tokens)
    ast = parser.parse()
    
    # Code generation
    code_gen = CodeGenerator(ast, parser.doctorstranges)
    c_code = code_gen.generate()
    
    # Compile C code to executable
    # ...
```

## Installation and Usage

### Prerequisites

- Python 3.6 or higher
- GCC compiler (or MSVC on Windows)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/superhero-compiler.git
   cd superhero-compiler
   ```

2. Make the compiler script executable (Linux/Mac):
   ```
   chmod +x superhero_compiler.py
   ```

### Usage

```
python superhero_compiler.py source_file.hero [-o output_file] [-v]
```

Options:
- `-o, --output`: Specify the output executable name
- `-v, --verbose`: Enable verbose output (shows tokens, AST, and generated C code)

## Example Programs

### Hello World

```
hero> This is a hello world program in SuperHero language
starlord "Hello, World!"
thanos
```

### Simple Counter

```
hero> Initialize counter
deadpool
ironman
ironman
ironman

hero> Print counter value 3 times
thor
thor
thor

hero> Increment and print again
ironman
thor

thanos
```

### Cell Manipulation

```
deadpool
hulk 65   hero> Input ASCII 'A' to cell
superman  hero> Move to next cell
hulk 66   hero> Input ASCII 'B' to cell
superman  hero> Move to next cell
hulk 67   hero> Input ASCII 'C' to cell

wonderwoman
wonderwoman  hero> Go back to first cell

thor      hero> Print 'A'
superman
thor      hero> Print 'B'
superman
thor      hero> Print 'C'

thanos
```

### Conditional Jumps

```
deadpool
hulk 10     hero> Set cell to 10

falcon loop:
    batman    hero> Decrement
    thor      hero> Print value
    spiderman check vision > 0
    hawkeye loop

thanos
```

### Array Operations

```
doctorstrange 10 myarray   hero> Declare array of size 10

blackpanther into myarray "Hello"  hero> Initialize array with string
captainamerica myarray     hero> Print the array content

thanos
```

## Challenges and Solutions

### Challenge 1: Parsing Nested Structures

**Problem**: The original design didn't properly handle nested control structures like loops and conditional statements.

**Solution**: Implemented a two-pass parsing strategy. The first pass collects all labels and loops while the second pass builds the complete AST with proper nesting.

### Challenge 2: Cross-Platform Compilation

**Problem**: Ensuring the compiler works on both Windows and Unix-based systems.

**Solution**: Added platform detection to:
1. Use appropriate sleep functions
2. Choose between GCC and MSVC compilers on Windows
3. Handle file extension differences (.exe on Windows)

### Challenge 3: String and Array Handling

**Problem**: Managing string literals and array operations in a memory-cell-based language.

**Solution**: Implemented specialized functions in the generated C code to handle:
- String input/output with proper null termination
- Array declaration and manipulation
- Character-by-character processing

## Future Enhancements

1. **Type System**: Add basic type checking to the language
2. **Functions**: Support for user-defined functions beyond simple loops
3. **Standard Library**: Implement common operations as built-in functions
4. **Optimization**: Add optimization passes to the compiler
5. **Debugger**: Create a simple debugging tool for SuperHero programs

## Test Cases and Outputs

### Test Case 1: Basic Operations

**Input (basic.hero):**
```
deadpool
ironman
ironman
thor
batman
thor
thanos
```

**Expected Output:**
```
2
1
Thanos snapped his fingers...
```

### Test Case 2: Loops and Conditions

**Input (loop.hero):**
```
deadpool
hulk 5

falcon loop:
    thor
    batman
    spiderman continue vision > 0
    hawkeye loop
    
falcon continue:
starlord "Done counting down!"
thanos
```

**Expected Output:**
```
5
4
3
2
1
Done counting down!
Thanos snapped his fingers...
```

### Test Case 3: Array Operations

**Input (array.hero):**
```
doctorstrange 20 message
blackpanther into message "Avengers Assemble!"
captainamerica message
thanos
```

**Expected Output:**
```
Avengers Assemble!
Thanos snapped his fingers...
```

### Test Case 4: String Processing

**Input (string.hero):**
```
doctorstrange 100 input
blackpanther into input "Hello World"

deadpool
falcon process:
    vision
    thor
    superman
    spiderman process vision != 0
    hawkeye process

starlord "Processing complete!"
thanos
```

**Expected Output:**
```
H
e
l
l
o
 
W
o
r
l
d
Processing complete!
Thanos snapped his fingers...
```

## Conclusion

The SuperHero Programming Language Compiler demonstrates how to build a complete compiler for a custom esoteric language. While designed for fun, it implements important compiler concepts:

- Lexical analysis
- Parsing
- Abstract syntax trees
- Code generation
- Cross-platform compatibility

Feel free to contribute to the project by adding new superhero commands or enhancing the compiler capabilities!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
