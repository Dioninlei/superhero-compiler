import sys
import os
import re
import subprocess
import tempfile
import argparse
import shutil
from enum import Enum, auto

class TokenType(Enum):
    COMMENT = auto()
    IRONMAN = auto()
    BATMAN = auto()
    SUPERMAN = auto()
    WONDERWOMAN = auto()
    FLASH = auto()
    SPIDERMAN = auto()
    THOR = auto()
    THORNUM = auto()
    HULK = auto()
    DOCTORSTRANGE = auto()
    BLACKPANTHER = auto()
    CAPTAINAMERICA = auto()
    VISION = auto()
    STARLORD = auto()
    DEADPOOL = auto()
    LOKI = auto()
    FALCON = auto()
    HAWKEYE = auto()
    THANOS = auto()
    ADD = auto()
    SUB = auto()
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    OPERATOR = auto()
    EMPTY = auto()
    INTO = auto()
    CELL_REF = auto()

class Token:
    """A token in the SuperHero language"""
    def __init__(self, token_type, value=None, line_number=0):
        self.type = token_type
        self.value = value
        self.line_number = line_number
    
    def __str__(self):
        return f"Token({self.type}, {self.value}, line {self.line_number})"

class SuperHeroLexer:
    """Lexer for the SuperHero Programming Language"""
    
    def __init__(self):
        self.keywords = {
            "ironman": TokenType.IRONMAN,
            "batman": TokenType.BATMAN,
            "superman": TokenType.SUPERMAN,
            "wonderwoman": TokenType.WONDERWOMAN,
            "flash": TokenType.FLASH,
            "spiderman": TokenType.SPIDERMAN,
            "thor": TokenType.THOR,
            "thornum": TokenType.THORNUM,
            "hulk": TokenType.HULK,
            "doctorstrange": TokenType.DOCTORSTRANGE,
            "blackpanther": TokenType.BLACKPANTHER,
            "captainamerica": TokenType.CAPTAINAMERICA,
            "vision": TokenType.VISION,
            "starlord": TokenType.STARLORD,
            "deadpool": TokenType.DEADPOOL,
            "loki": TokenType.LOKI,
            "falcon": TokenType.FALCON,
            "hawkeye": TokenType.HAWKEYE,
            "thanos": TokenType.THANOS,
            "add": TokenType.ADD,
            "sub": TokenType.SUB,
            "into": TokenType.INTO,
            "empty": TokenType.EMPTY
        }
        
        self.operators = {
            ">": ">",
            "<": "<",
            "=": "==",
            "==": "==",
            "!=": "!=",
            ">=": ">=",
            "<=": "<="
        }
    
    def tokenize(self, code):
        """Convert SuperHero code string into a list of tokens"""
        lines = code.split('\n')
        tokens = []
        multiline_comment = False
        
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines
            if not line.strip():
                continue
                
            # Handle multiline comments
            if multiline_comment:
                if "*heroes" in line:
                    multiline_comment = False
                continue
                
            # Check for multiline comment start
            if "heroes*" in line and not "*heroes" in line:
                multiline_comment = True
                continue
                
            # Handle single line comments
            if line.strip().startswith("hero>"):
                continue
                
            # Count leading spaces for indentation
            indentation = len(line) - len(line.lstrip())
            
            # Process the line
            i = indentation
            line_tokens = []
            
            while i < len(line):
                char = line[i]
                
                # Skip spaces
                if char.isspace():
                    i += 1
                    continue
                
                # Handle string literals
                if char == '"':
                    start = i
                    i += 1
                    while i < len(line) and line[i] != '"':
                        if line[i] == '\\' and i + 1 < len(line):
                            i += 2  # Skip escape sequence
                        else:
                            i += 1
                    if i < len(line):  # Found closing quote
                        string_value = line[start+1:i]
                        line_tokens.append(Token(TokenType.STRING, string_value, line_num))
                        i += 1
                    else:
                        print(f"Error: Unclosed string literal at line {line_num}")
                        sys.exit(1)
                    continue
                
                # Handle numbers
                if char.isdigit():
                    start = i
                    while i < len(line) and line[i].isdigit():
                        i += 1
                    num_value = int(line[start:i])
                    line_tokens.append(Token(TokenType.NUMBER, num_value, line_num))
                    continue
                
                # Handle identifiers and keywords
                if char.isalpha() or char == '_' or char == '#':
                    start = i
                    while i < len(line) and (line[i].isalnum() or line[i] == '_' or line[i] == '#'):
                        i += 1
                    word = line[start:i]
                    
                    # Check if it's a cell reference with #
                    if word.startswith('#'):
                        try:
                            cell_num = int(word[1:])
                            line_tokens.append(Token(TokenType.CELL_REF, cell_num, line_num))
                        except ValueError:
                            print(f"Error: Invalid cell reference '{word}' at line {line_num}")
                            sys.exit(1)
                    # Otherwise check if it's a keyword or identifier
                    elif word in self.keywords:
                        line_tokens.append(Token(self.keywords[word], word, line_num))
                    else:
                        line_tokens.append(Token(TokenType.IDENTIFIER, word, line_num))
                    continue
                
                # Handle operators
                if char in "<>=!":
                    start = i
                    i += 1
                    if i < len(line) and line[i] == '=':
                        i += 1
                    op = line[start:i]
                    if op in self.operators:
                        line_tokens.append(Token(TokenType.OPERATOR, self.operators[op], line_num))
                    else:
                        print(f"Error: Invalid operator '{op}' at line {line_num}")
                        sys.exit(1)
                    continue
                
                # Handle colon for labels
                if char == ':':
                    line_tokens.append(Token(TokenType.IDENTIFIER, ':', line_num))
                    i += 1
                    continue
                
                # Skip other characters
                i += 1
            
            # Add indentation information
            if line_tokens:
                line_tokens[0].indentation = indentation // 4  # Assuming 4 spaces per indentation level
                tokens.extend(line_tokens)
        
        return tokens

class SuperHeroParser:
    """Parser for the SuperHero Programming Language"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.indent_stack = [0]
        self.labels = set()
        self.flashes = {}  # Flash loops
        self.doctorstranges = {}  # Doctor Strange arrays
    
    def parse(self):
        """Parse the tokens into an AST or intermediate representation"""
        code_blocks = []
        self.first_pass()  # Collect all labels and flash loops
        
        while not self.is_at_end():
            statement = self.parse_statement()
            if statement:
                code_blocks.append(statement)
        
        return code_blocks
    
    def first_pass(self):
        """First pass to collect all labels and flash loops"""
        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            
            # Collect falcon (label) declarations
            if token.type == TokenType.FALCON:
                if i + 1 < len(self.tokens) and self.tokens[i + 1].type == TokenType.IDENTIFIER:
                    label_name = self.tokens[i + 1].value
                    if label_name.endswith(':'):
                        label_name = label_name[:-1]
                    self.labels.add(label_name)
                i += 2  # Skip falcon and label name
            
            # Collect flash (loop) definitions
            elif token.type == TokenType.FLASH:
                if i + 1 < len(self.tokens) and self.tokens[i + 1].type == TokenType.IDENTIFIER:
                    flash_name = self.tokens[i + 1].value
                    if flash_name.endswith(':'):
                        flash_name = flash_name[:-1]
                    
                    # Collect the flash body
                    flash_body = []
                    i += 2  # Skip flash and name
                    
                    # TODO: Proper indentation handling for flash bodies
                    while i < len(self.tokens) and not (self.tokens[i].type in [TokenType.FALCON, TokenType.FLASH] and 
                                                       getattr(self.tokens[i], 'indentation', 0) == 0):
                        flash_body.append(self.tokens[i])
                        i += 1
                    
                    self.flashes[flash_name] = flash_body
                    continue  # We've already incremented i
            
            # Collect doctorstrange (array) declarations
            elif token.type == TokenType.DOCTORSTRANGE:
                if i + 1 < len(self.tokens):
                    size = None
                    name = None
                    
                    # Check if the next token is a number (size)
                    if self.tokens[i + 1].type == TokenType.NUMBER:
                        size = self.tokens[i + 1].value
                        if i + 2 < len(self.tokens) and self.tokens[i + 2].type == TokenType.IDENTIFIER:
                            name = self.tokens[i + 2].value
                    # If not, it's just the name
                    elif self.tokens[i + 1].type == TokenType.IDENTIFIER:
                        name = self.tokens[i + 1].value
                    
                    if name:
                        self.doctorstranges[name] = size  # Size might be None
            
            i += 1
    
    def is_at_end(self):
        """Check if we've reached the end of the tokens"""
        return self.current >= len(self.tokens)
    
    def advance(self):
        """Advance to the next token"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def previous(self):
        """Get the previous token"""
        return self.tokens[self.current - 1]
    
    def peek(self):
        """Look at the current token without advancing"""
        if self.is_at_end():
            return None
        return self.tokens[self.current]
    
    def check(self, token_type):
        """Check if the current token is of the given type"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def match(self, *token_types):
        """Match the current token against the given types"""
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def consume(self, token_type, error_message):
        """Consume a token of the expected type or throw an error"""
        if self.check(token_type):
            return self.advance()
        
        token = self.peek()
        line = token.line_number if token else "unknown"
        print(f"Parser error at line {line}: {error_message}")
        sys.exit(1)
    
    def parse_statement(self):
        """Parse a statement"""
        token = self.peek()
        if not token:
            return None
        
        if token.type == TokenType.IRONMAN:
            self.advance()
            return {"type": "ironman"}
        
        elif token.type == TokenType.BATMAN:
            self.advance()
            return {"type": "batman"}
        
        elif token.type == TokenType.SUPERMAN:
            self.advance()
            return {"type": "superman"}
        
        elif token.type == TokenType.WONDERWOMAN:
            self.advance()
            return {"type": "wonderwoman"}
        
        elif token.type == TokenType.THOR:
            self.advance()
            return {"type": "thor"}
        
        elif token.type == TokenType.THORNUM:
            self.advance()
            return {"type": "thornum"}
        
        elif token.type == TokenType.HULK:
            self.advance()
            args = []
            if not self.is_at_end() and (self.peek().type == TokenType.STRING or self.peek().type == TokenType.NUMBER):
                args.append(self.advance().value)
            return {"type": "hulk", "args": args}
        
        elif token.type == TokenType.DOCTORSTRANGE:
            self.advance()
            size = None
            name = None
            
            if not self.is_at_end() and self.peek().type == TokenType.NUMBER:
                size = self.advance().value
            
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                name = self.advance().value
            else:
                print(f"Error at line {token.line_number}: Expected array name")
                sys.exit(1)
            
            return {"type": "doctorstrange", "name": name, "size": size}
        
        elif token.type == TokenType.BLACKPANTHER:
            self.advance()
            target = None
            content = None
            
            if not self.is_at_end() and self.peek().type == TokenType.INTO:
                self.advance()  # Consume "into"
                
                if not self.is_at_end():
                    if self.peek().type == TokenType.IDENTIFIER:
                        target = self.advance().value
                    elif self.peek().type == TokenType.NUMBER:
                        target = self.advance().value
            
            if not self.is_at_end() and self.peek().type == TokenType.STRING:
                content = self.advance().value
            
            return {"type": "blackpanther", "target": target, "content": content}
        
        elif token.type == TokenType.CAPTAINAMERICA:
            self.advance()
            target = None
            
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                target = self.advance().value
            
            return {"type": "captainamerica", "target": target}
        
        elif token.type == TokenType.STARLORD:
            self.advance()
            text = None
            
            if not self.is_at_end() and self.peek().type == TokenType.STRING:
                text = self.advance().value
            else:
                print(f"Error at line {token.line_number}: Expected string after starlord")
                sys.exit(1)
            
            return {"type": "starlord", "text": text}
        
        elif token.type == TokenType.DEADPOOL:
            self.advance()
            return {"type": "deadpool"}
        
        elif token.type == TokenType.LOKI:
            self.advance()
            return {"type": "loki"}
        
        elif token.type == TokenType.FALCON:
            self.advance()
            name = None
            
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                name = self.advance().value
                if name.endswith(':'):
                    name = name[:-1]  # Remove trailing colon
            
            return {"type": "falcon", "name": name}
        
        elif token.type == TokenType.HAWKEYE:
            self.advance()
            target = None
            
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                target = self.advance().value
            
            return {"type": "hawkeye", "target": target}
        
        elif token.type == TokenType.SPIDERMAN:
            self.advance()
            target = None
            left = None
            op = None
            right = None
            
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                target = self.advance().value
            
            if not self.is_at_end():
                if self.peek().type == TokenType.VISION:
                    left = "vision"
                    self.advance()
                elif self.peek().type == TokenType.NUMBER:
                    left = self.advance().value
            
            if not self.is_at_end() and self.peek().type == TokenType.OPERATOR:
                op = self.advance().value
            
            if not self.is_at_end():
                if self.peek().type == TokenType.EMPTY:
                    right = "empty"
                    self.advance()
                elif self.peek().type == TokenType.NUMBER:
                    right = self.advance().value
                elif self.peek().type == TokenType.VISION:
                    right = "vision"
                    self.advance()
            
            return {"type": "spiderman", "target": target, "left": left, "op": op, "right": right}
        
        elif token.type == TokenType.ADD or token.type == TokenType.SUB:
            op_type = "add" if token.type == TokenType.ADD else "sub"
            self.advance()
            left = None
            left_is_cell = False
            right = None
            right_is_cell = False
            
            if not self.is_at_end():
                if self.peek().type == TokenType.VISION:
                    left = "vision"
                    self.advance()
                elif self.peek().type == TokenType.NUMBER:
                    left = self.advance().value
                elif self.peek().type == TokenType.CELL_REF:
                    left = self.advance().value
                    left_is_cell = True
            
            if not self.is_at_end():
                if self.peek().type == TokenType.NUMBER:
                    right = self.advance().value
                elif self.peek().type == TokenType.VISION:
                    right = "vision"
                    self.advance()
                elif self.peek().type == TokenType.CELL_REF:
                    right = self.advance().value
                    right_is_cell = True
            
            return { "type": op_type, "left": left, "right": right, "left_is_cell": left_is_cell, "right_is_cell": right_is_cell}
        
        elif token.type == TokenType.THANOS:
            self.advance()
            return {"type": "thanos"}
        
        elif token.type == TokenType.IDENTIFIER:
            # This could be a flash (loop) call
            name = self.advance().value
            if name in self.flashes:
                return {"type": "flash_call", "name": name}
        
        else:
            # Skip unknown token
            self.advance()
        
        return None

class CodeGenerator:
    """Generate C code from the parsed SuperHero code"""
    
    def __init__(self, ast, doctorstranges):
        self.ast = ast
        self.doctorstranges = doctorstranges
        self.code = []
        self.indent_level = 0
    
    def generate(self):
        """Generate C code from the AST"""
        # Add standard C headers and setup
        self.code.append("""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
""")

        # Add platform-specific headers
        if os.name == 'nt':
            self.code.append("""
#include <windows.h>
#define sleep(x) Sleep((x) * 1000)
""")
        else:
            self.code.append("""
#include <unistd.h>
""")

        self.code.append("""
#include <stdint.h>

#define TAPE_SIZE 30000
#define MAX_INPUT 1024

// Globals
uint8_t tape[TAPE_SIZE] = {0};
int ptr = 0;
char input_buffer[MAX_INPUT];

// Forward declarations
void thor();
void hulk(int direct_val, char direct_char);
""")

        # Define doctorstrange arrays
        for name, size in self.doctorstranges.items():
            size_val = size if size is not None else 1024  # Default size
            self.code.append(f"uint8_t doctorstrange_{name}[{size_val}] = {{0}};")
        
        self.code.append("""
// Helper functions
void thor() {
    printf("%c\\n", tape[ptr]);
}

void thornum() {
    printf("%d\\n", tape[ptr]);
}

void hulk(int direct_val, char direct_char) {
    if (direct_val != -1) {
        tape[ptr] = direct_val;
        return;
    }
    
    if (direct_char != 0) {
        tape[ptr] = direct_char;
        return;
    }
    
    printf("Hulk smash input: ");
    fflush(stdout);
    
    int ch = getchar();
    if (ch == EOF || ch == '\\n') {
        tape[ptr] = 0;  // Set to empty on EOF or newline
    } else {
        tape[ptr] = ch;
        // Eat up rest of the line
        while ((ch = getchar()) != '\\n' && ch != EOF);
    }
}

void blackpanther(uint8_t *target, const char *content) {
    if (content != NULL) {
        // Direct content provided
        int i = 0;
        while (content[i] != '\\0') {
            target[i] = content[i];
            i++;
        }
        target[i] = 0;  // Null-terminate
    } else {
        // User input
        printf("Wakanda forever: ");
        fflush(stdout);
        
        fgets(input_buffer, MAX_INPUT, stdin);
        size_t len = strlen(input_buffer);
        
        // Remove trailing newline if present
        if (len > 0 && input_buffer[len-1] == '\\n') {
            input_buffer[len-1] = '\\0';
            len--;
        }
        
        // Copy to target
        for (size_t i = 0; i < len; i++) {
            target[i] = input_buffer[i];
        }
        target[len] = 0;  // Null-terminate
    }
}

void captainamerica(uint8_t *source) {
    int i = 0;
    while (source[i] != 0) {
        putchar(source[i]);
        i++;
    }
    printf("\\n");
}

int main() {
""")
        
        # Generate code for the AST
        self.indent_level = 1
        for node in self.ast:
            self.generate_node(node)
        
        # Close main function and return 0
        self.code.append("    return 0;\n}")
        
        return "\n".join(self.code)
    
    def indent(self):
        """Return the current indentation as a string"""
        return "    " * self.indent_level
    
    def generate_node(self, node):
        """Generate C code for a specific AST node"""
        if not node:
            return
        
        node_type = node.get("type", "")
        
        if node_type == "ironman":
            self.code.append(f"{self.indent()}tape[ptr]++;")
        
        elif node_type == "batman":
            self.code.append(f"{self.indent()}tape[ptr]--;")
        
        elif node_type == "superman":
            self.code.append(f"{self.indent()}ptr++;")
        
        elif node_type == "wonderwoman":
            self.code.append(f"{self.indent()}ptr--;")
        
        elif node_type == "hulk":
            args = node.get("args", [])
            if args and isinstance(args[0], int):
                self.code.append(f"{self.indent()}hulk({args[0]}, 0);")
            elif args and isinstance(args[0], str):
                self.code.append(f"{self.indent()}hulk(-1, '{args[0]}');")
            else:
                self.code.append(f"{self.indent()}hulk(-1, 0);")
        
        elif node_type == "thor":
            self.code.append(f"{self.indent()}thor();")
        
        elif node_type == "thornum":
            self.code.append(f"{self.indent()}thornum();")
        
        elif node_type == "starlord":
            text = node.get("text", "")
            self.code.append(f'{self.indent()}printf("{text}\\n");')
        
        elif node_type == "deadpool":
            self.code.append(f"{self.indent()}ptr = 0;")
        
        elif node_type == "loki":
            self.code.append(f"{self.indent()}tape[ptr] = 0;")
            self.code.append(f'{self.indent()}printf("Loki cleared cell %d\\n", ptr);')
        
        elif node_type == "falcon":
            name = node.get("name", "")
            self.code.append(f"{self.indent()[:-4]}{name}:")
        
        elif node_type == "hawkeye":
            target = node.get("target", "")
            self.code.append(f"{self.indent()}goto {target};")
        
        elif node_type == "spiderman":
            target = node.get("target", "")
            left = node.get("left", "")
            op = node.get("op", "")
            right = node.get("right", "")
            
            left_expr = "tape[ptr]" if left == "vision" else str(left)
            
            if right == "empty":
                right_expr = "0"
            elif right == "vision":
                right_expr = "tape[ptr]"
            else:
                right_expr = str(right)
            
            self.code.append(f"{self.indent()}if ({left_expr} {op} {right_expr}) {{")
            self.code.append(f"{self.indent()}    goto {target};")
            self.code.append(f"{self.indent()}}}")
        
        elif node_type == "add":
            left = node.get("left", "")
            right = node.get("right", "")
            left_is_cell = node.get("left_is_cell", False)
            right_is_cell = node.get("right_is_cell", False)
            
            if left == "vision":
                left_expr = "tape[ptr]"
            elif left_is_cell:
                left_expr = f"tape[{left}]"
            else:
                left_expr = f"tape[{left}]"

            if right == "vision":
                right_expr = "tape[ptr]"
            elif right_is_cell:
                right_expr = f"tape[{right}]"
            else:
                right_expr = str(right)
            
            self.code.append(f"{self.indent()}{left_expr} += {right_expr};")
        
        elif node_type == "sub":
            left = node.get("left", "")
            right = node.get("right", "")
            left_is_cell = node.get("left_is_cell", False)
            right_is_cell = node.get("right_is_cell", False)
            
            if left == "vision":
                left_expr = "tape[ptr]"
            elif left_is_cell:
                left_expr = f"tape[{left}]"
            else:
                left_expr = f"tape[{left}]"
            
            if right == "vision":
                right_expr = "tape[ptr]"
            elif right_is_cell:
                right_expr = f"tape[{right}]"
            else:
                right_expr = str(right)
            
            self.code.append(f"{self.indent()}{left_expr} -= {right_expr};")
        
        elif node_type == "doctorstrange":
            # Already declared in the globals section
            pass
        
        elif node_type == "blackpanther":
            target = node.get("target", None)
            content = node.get("content", None)
            
            if target is None:
                target_expr = "tape + ptr"
            elif isinstance(target, str) and target in self.doctorstranges:
                target_expr = f"doctorstrange_{target}"
            else:
                target_expr = f"tape + {target}"
            
            content_expr = f"\"{content}\"" if content is not None else "NULL"
            
            self.code.append(f"{self.indent()}blackpanther({target_expr}, {content_expr});")
        
        elif node_type == "captainamerica":
            target = node.get("target", None)
            
            if target is None:
                source_expr = "tape + ptr"
            elif target in self.doctorstranges:
                source_expr = f"doctorstrange_{target}"
            else:
                source_expr = "tape + ptr"
            
            self.code.append(f"{self.indent()}captainamerica({source_expr});")
        
        elif node_type == "flash_call":
            name = node.get("name", "")
            self.code.append(f"{self.indent()}// Flash loop: {name}")
        
        elif node_type == "thanos":
            self.code.append(f'{self.indent()}printf("Thanos snapped his fingers...\\n");')
            self.code.append(f"{self.indent()}return 0;")

def compile_superhero(source_file, output_file=None, verbose=False):
    """Compile a SuperHero source file to an executable"""
    if not output_file:
        output_file = os.path.splitext(source_file)[0]
        if os.name == 'nt' and not output_file.endswith('.exe'):
            output_file += '.exe'
    
    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Source file '{source_file}' not found")
        return 1
    
    lexer = SuperHeroLexer()
    tokens = lexer.tokenize(source_code)
    
    if verbose:
        print("Tokens:")
        for token in tokens:
            print(f"  {token}")
    
    parser = SuperHeroParser(tokens)
    ast = parser.parse()
    
    if verbose:
        print("\nAST:")
        for node in ast:
            print(f"  {node}")
    
    code_gen = CodeGenerator(ast, parser.doctorstranges)
    c_code = code_gen.generate()
    
    with tempfile.NamedTemporaryFile(suffix='.c', delete=False) as temp_file:
        temp_filename = temp_file.name
        temp_file.write(c_code.encode('utf-8'))
    
    if verbose:
        print(f"\nGenerated C code saved to {temp_filename}")
        print(c_code)
    
    try:
        if os.name == 'nt':
            if shutil.which('gcc'):
                compiler_cmd = ['gcc']
            elif shutil.which('cl'):
                compiler_cmd = ['cl']
            else:
                print("Error: No C compiler found. Please install MinGW or MSVC.")
                return 1
        else:
            compiler_cmd = ['gcc']
            
        result = subprocess.run(compiler_cmd + [temp_filename, '-o', output_file], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error compiling C code: {result.stderr}")
            return 1
        
        if os.name != 'nt':
            os.chmod(output_file, 0o755)
        
        print(f"Successfully compiled {source_file} to {output_file}")
        return 0
    
    except Exception as e:
        print(f"Error during compilation: {e}")
        return 1
    finally:
        try:
            os.unlink(temp_filename)
        except:
            pass

def main():
    """Main entry point for the SuperHero compiler"""
    parser = argparse.ArgumentParser(description='SuperHero Programming Language Compiler')
    parser.add_argument('source', help='Source file (.hero)')
    parser.add_argument('-o', '--output', help='Output executable file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.source.endswith('.hero'):
        print("Warning: Source file doesn't have .hero extension")
    
    return compile_superhero(args.source, args.output, args.verbose)

if __name__ == "__main__":
    sys.exit(main())
