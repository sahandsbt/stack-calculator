import re

ICP = {
    '+': 2,
    '-': 2,
    '*': 4,
    '/': 4,
    '^': 6,
    '(': 7,
    ')': 1
}

ISP = {
    '+': 3,
    '-': 3,
    '*': 5,
    '/': 5,
    '^': 5,
    '(': 1,
    ')': 1
}

def change_eval_symbols(text):
    if '÷' in text:
        text = text.replace('÷', '/')
    if '×' in text:
        text = text.replace('×', '*')
    return text

def tokenize(text):
    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isdigit() or ch == '.':
            num = ch
            i += 1
            dot_used = (ch == '.')
            while i < len(text):
                if text[i].isdigit():
                    num += text[i]
                elif text[i] == '.' and not dot_used:
                    num += '.'
                    dot_used = True
                else:
                    break
                i += 1
            tokens.append(num)
            continue
        if ch in "+-*/()^":
            tokens.append(ch)
            i += 1
            continue
    return tokens

def token_to_postfix(token):
    stack = []
    postfix = []
    for i in token:
        if i in "+-*/()^":
            if stack == []:
                stack.append(i)
            elif ISP[stack[-1]] < ICP[i]:
                stack.append(i)
            else :
                while True:
                    if stack == []:
                        stack.append(i)
                        break
                    elif ISP[stack[-1]] < ICP[i]: 
                        stack.append(i)
                        break
                    else:
                        postfix.append(stack[-1])
                        stack.pop(-1)
        else:
            postfix.append(i)
    postfix.extend(reversed(stack))
    postfix_o = []
    for i in postfix:
        if i not in '()':
            postfix_o.append(i)
    return postfix_o

def postfix_to_number(postfix):
    stack = []
    for i in postfix:
        if i in "+-*/^":
            if i == '+':
                stack[-2] = stack[-2] + stack[-1]
                stack.pop()
            elif i == '-':
                stack[-2] = stack[-2] - stack[-1]
                stack.pop()
            elif i == '*':
                stack[-2] = stack[-2] * stack[-1]
                stack.pop()
            elif i == '/':
                stack[-2] = stack[-2] / stack[-1]
                stack.pop()
            elif i == '^':
                stack[-2] = stack[-2] ** stack[-1]
                stack.pop()
        else:
            stack.append(float(i))
    return stack[0]

def calculate(text):
    text = change_eval_symbols(text)
    token = tokenize(text)
    postfix = token_to_postfix(token)
    number = postfix_to_number(postfix)
    return str(round(number,8))