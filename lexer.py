"""
Gerador de Assembly ARMv7 (CPULATOR) com suporte a IEEE754 64 bits

Integrantes (ordem alfabética):
Murilo Chandelier Pedrazzani - https://github.com/MuriloPedrazzani
Ricardo Ryu Magalhães Makino - https://github.com/ryumakino
Ricardo Vinicius Moreira Vianna - https://github.com/ricaprof

Grupo no Canvas: RA1 8

Disciplina: Construção de Interpretadores
Professor: Frank Alcantara
"""



# ESTADO NUMERO 
def estadoNumero(linha, i):
    numero = ""
    tem_ponto = False
    digitos_antes = 0
    digitos_depois = 0

    # trata sinal negativo
    if linha[i] == "-":
        numero += "-"
        i += 1

        if i >= len(linha) or not linha[i].isdigit():
            raise ValueError("Número negativo malformado")

    while i < len(linha):
        char = linha[i]

        if char.isdigit():
            numero += char
            if not tem_ponto:
                digitos_antes += 1
            else:
                digitos_depois += 1
            i += 1
            continue

        if char == ".":
            if tem_ponto:
                raise ValueError("Número malformado")
            tem_ponto = True
            numero += char
            i += 1
            continue

        break

    # valida formato
    if tem_ponto and (digitos_antes == 0 or digitos_depois == 0):
        raise ValueError("Número real inválido")

    return numero, i



# ESTADO PALAVRA (MEM / VAR / RES)
def estadoPalavra(linha, i):
    palavra = ""

    while i < len(linha) and linha[i].isalpha():
        palavra += linha[i]
        i += 1

    # linguagem exige maiusculas
    if not palavra.isupper():
        raise ValueError(f"Variável/Comando inválido (deve ser maiúsculo): {palavra}")

    return palavra, i


# ESTADO OPERADOR
def estadoOperador(linha, i):
    char = linha[i]

    # divisão inteira
    if char == "/" and i + 1 < len(linha) and linha[i + 1] == "/":
        return "//", i + 2

    if char in "+-*/%^":
        return char, i + 1

    raise ValueError(f"Operador inválido: {char}")


# ESTADO PARENTESES
def estadoParenteses(linha, i):
    return linha[i], i + 1


# VALIDAÇÃO DE PARENTESES
def validarParenteses(tokens):
    stack = []

    for t in tokens:
        if t == "(":
            stack.append(t)
        elif t == ")":
            if not stack:
                raise ValueError("Parênteses desbalanceados")
            stack.pop()

    if stack:
        raise ValueError("Parênteses desbalanceados")


# ANALISADOR LEXICO (FSM)
def parseExpressao(linha):
    tokens = []
    i = 0

    while i < len(linha):
        char = linha[i]

        # ignorar espaços
        if char.isspace():
            i += 1
            continue

        # parenteses
        if char in "()":
            token, i = estadoParenteses(linha, i)
            tokens.append(token)
            continue

        # NUMERO
        if char.isdigit() or (
            char == "-" and
            i + 1 < len(linha) and
            linha[i + 1].isdigit() and
            (
                len(tokens) == 0 or
                tokens[-1] in ("(", "+", "-", "*", "/", "//", "%", "^")
            )
        ):
            token, i = estadoNumero(linha, i)
            tokens.append(token)
            continue

        # palavra (MEM / VAR / RES)
        if char.isalpha():
            token, i = estadoPalavra(linha, i)
            tokens.append(token)
            continue

        # operador
        if char in "+-*/%^":
            token, i = estadoOperador(linha, i)
            tokens.append(token)
            continue

        raise ValueError(f"Caractere inválido: {char}")

    validarParenteses(tokens)

    return tokens