alphabet = "abcdefghijklmnopqrstuvwxyz"
alphaBET = alphabet + alphabet.upper()
variables = alphaBET + "_"
operators = ["+", "-", "*", "**", "/", "//", "%", "&", "!", "|", "<", "<=", ">", ">=", "==", "!="]
precedence = {"**": 10,"~": 9.5,"!": 9.5,"*": 9,"/": 9,"//": 9,"%": 9,"+": 8,"-": 8,"<": 7,"<=": 7,">": 7,">=": 7,"==": 7,"!=": 7,"&": 6,"|": 5}
numbers = "0.123456789"

objects = {
    "true": True,
    "false": False,
    "True": True,
    "False": False,
    "null": None
}

import time
from functions import functions, operator_functions
from inspect import signature

def is_operator(data, i):
    return any([i + len(op) < len(data) and data[i:i+len(op)] == op for op in operators])

def find_operator(data, i):
    return max([op for op in operators if i + len(op) < len(data) and data[i:i+len(op)] == op], key = lambda op : len(op))

def tokenize(data):
    tokens = []
    i = 0
    token = ""
    while i < len(data):
        char = data[i]
        if char in "(),:":
            if len(token) > 0:
                tokens.append(token)
            token = ""
            tokens.append(char)
            i += 1
        elif char in " \t":
            if len(token) > 0:
                tokens.append(token)
            token = ""
            i += 1
        elif char == '"':
            if len(token) > 0:
                tokens.append(token)
            token = ""
            token += char
            i += 1
            while i < len(data) and not(data[i] == '"' and data[i - 1] != "\\"):
                token += data[i]
                i += 1
            token += char
            i += 1
            tokens.append(token)
            token = ""
        elif is_operator(data, i):
            if len(token) > 0:
                tokens.append(token)
            op = find_operator(data, i)
            if op == "-" and not (tokens[-1] == ")" or all([letter in variables for letter in tokens[-1]]) or all([letter in numbers for letter in tokens[-1]])):
                token = "~"
            else:
                token = op
            i += len(op)
        elif char in variables:
            if len(token) > 0:
                tokens.append(token)
            token = ""
            while i < len(data) and data[i] in variables:
                token += data[i]
                i += 1
        elif char in numbers:
            if len(token) > 0:
                tokens.append(token)
            token = ""
            while i < len(data) and data[i] in numbers:
                token += data[i]
                i += 1
        else:
            i += 1
    if len(token) > 0:
        tokens.append(token)
    return tokens

def postfix(tokens):
    output = []
    stack = []
    while tokens:
        token = tokens.pop(0)
        if all([letter in numbers for letter in token]):
            output.append(token)
        elif token[0] == '"':
            output.append(token)
        elif all([letter in variables for letter in token]) and not tokens[0] == "(":
            output.append(token)
        elif all([letter in variables for letter in token]):
            stack.append(token)
        elif token in operators:
            while stack and stack[-1] in operators and precedence[stack[-1]] >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
        elif token == "(":
            stack.append(token)
        elif token == ")":
            while stack[-1] != "(":
                output.append(stack.pop())
            stack.pop()
            if stack and all([letter in variables for letter in stack[-1]]):
                output.append(stack.pop())
    while stack:
        output.append(stack.pop())
    return output

def evaluate(tokens):
    stack = []
    for token in tokens:
        if token[0] == '"' or all([letter in numbers for letter in token]) or all([letter in variables for letter in token]) and not token in functions:
            if all([letter in numbers for letter in token]):
                token = float(token)
            stack.append(token)
        elif token in operators:
            if token == "!":
                stack[-1] = not stack[-1]
            elif token == "~":
                stack[-1] = -1 * stack[-1]
            else:
                b, a = stack.pop(), stack.pop()
                if str(b)[0] == '"':
                    b = b[1:-1]
                elif all([letter in variables for letter in str(b)]):
                    b = objects[str(b)]
                if str(a)[0] == '"':
                    a = a[1:-1]
                elif all([letter in variables for letter in str(a)]):
                    a = objects[str(a)]
                stack.append(operator_functions[token](a, b))
        else:
            params = len(signature(functions[token]).parameters)
            args = [stack.pop() for i in range(params)][::-1]
            for i in range(params):
                arg = args[i]
                if str(arg)[0] == '"':
                    args[i] = arg[1:-1]
                elif all([letter in variables for letter in str(arg)]):
                    args[i] = objects[str(arg)]
            stack.append(functions[token](*args))
    return stack[-1]

data = []
with open("Big Project 1/input.esar", "r") as file:
    data = file.readlines()

labelled_lines = {}
lines = []
for i, line in enumerate(data):
    line = tokenize(line)
    if ":" in line:
        labelled_lines[line[0]] = i
        line = line[2:]
    if "=" in line:
        lines.append((line[0], postfix(line[2:])))
    else:
        lines.append(postfix(line))

line_number = 0
while line_number < len(lines):
    if isinstance(lines[line_number], tuple):
        objects[lines[line_number][0]] = evaluate(lines[line_number][1])
    else:
        value = evaluate(lines[line_number])
        if str(value)[0] == "*":
            line_number = labelled_lines[value[1:]]
            continue
    line_number += 1

print(evaluate(postfix(tokenize('1 + 1 < 3 & 22 == 22'))))