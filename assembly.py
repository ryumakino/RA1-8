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

def isNumero(token):
    try:
        float(token)
        return True
    except ValueError:
        return False


def gerarAssembly(linhas_tokens):

    assembly_data = []
    assembly_text = []
    constants = []


    # DATA SECTION
    assembly_data.append(".data")
    assembly_data.append("    .align 3")

    assembly_data.append("historico: .space 800")

    variaveis = set()

    for tokens in linhas_tokens:
        for t in tokens:
            if t.isalpha() and t != "RES":
                variaveis.add(t)

    # vai ordena variaveis para saida deterministica
    for v in sorted(variaveis):
        assembly_data.append(f"var_{v}: .double 0.0")

    # TEXT SECTION
    assembly_text.append(".text")
    assembly_text.append(".global _start")
    assembly_text.append("_start:")

    label_id = 0

    for linha_idx, tokens in enumerate(linhas_tokens):

        stack = []

        for i, token in enumerate(tokens):

            if token in ("(", ")"):
                continue

            # NuMEROS
            if isNumero(token):

                freg = len(stack) % 16
                reg = f"D{freg}"

                assembly_text.append(f"    LDR R0, =const_{label_id}")
                assembly_text.append(f"    VLDR.F64 {reg}, [R0]")

                constants.append(f"const_{label_id}: .double {float(token)}")

                stack.append(reg)
                label_id += 1
                continue

            # OPERADORES FLOAT
            if token in ("+", "-", "*", "/"):

                if len(stack) < 2:
                    continue

                r2 = stack.pop()
                r1 = stack.pop()

                if token == "+":
                    assembly_text.append(f"    VADD.F64 {r1}, {r1}, {r2}")

                elif token == "-":
                    assembly_text.append(f"    VSUB.F64 {r1}, {r1}, {r2}")

                elif token == "*":
                    assembly_text.append(f"    VMUL.F64 {r1}, {r1}, {r2}")

                elif token == "/":
                    assembly_text.append(f"    VDIV.F64 {r1}, {r1}, {r2}")

                stack.append(r1)
                continue

            if token in ("//", "%"):

                if len(stack) < 2:
                    continue

                r2 = stack.pop()
                r1 = stack.pop()

                # float -> int
                assembly_text.append(f"    VCVT.S32.F64 S30, {r1}")
                assembly_text.append("    VMOV R0, S30")

                assembly_text.append(f"    VCVT.S32.F64 S31, {r2}")
                assembly_text.append("    VMOV R1, S31")

                # R0 = dividendo
                # R1 = divisor

                assembly_text.append("    MOV R2, #0")   # quociente
                assembly_text.append("    MOV R3, R0")   # resto temporário

                loop = f"div_loop_{label_id}"
                end = f"div_end_{label_id}"

                label_id += 1

                assembly_text.append(f"{loop}:")
                assembly_text.append("    CMP R3, R1")
                assembly_text.append(f"    BLT {end}")
                assembly_text.append("    SUB R3, R3, R1")
                assembly_text.append("    ADD R2, R2, #1")
                assembly_text.append(f"    B {loop}")

                assembly_text.append(f"{end}:")

                # escolher resultado
                if token == "//":
                    assembly_text.append("    MOV R4, R2")   # quociente
                else:
                    assembly_text.append("    MOV R4, R3")   # resto

                # int -> float
                assembly_text.append("    VMOV S30, R4")
                assembly_text.append(f"    VCVT.F64.S32 {r1}, S30")

                stack.append(r1)
                continue

            if token == "^":

                if len(stack) < 2:
                    continue

                r2 = stack.pop()  # expoente
                r1 = stack.pop()  # base

                start = f"pow_loop_{label_id}"
                end = f"pow_end_{label_id}"

                label_id += 1

                # converte expoente para inteiro de forma segura
                assembly_text.append(f"    VCVT.S32.F64 S31, {r2}")
                assembly_text.append("    VMOV R2, S31")

                # acumulador = 1.0 usando D30
                assembly_text.append("    VMOV.F64 D30, #1.0")

                assembly_text.append(f"{start}:")
                assembly_text.append("    CMP R2, #0")
                assembly_text.append(f"    BEQ {end}")

                assembly_text.append(f"    VMUL.F64 D30, D30, {r1}")
                assembly_text.append("    SUB R2, R2, #1")
                assembly_text.append(f"    B {start}")

                assembly_text.append(f"{end}:")

                # mover resultado para registrador da base
                assembly_text.append(f"    VMOV.F64 {r1}, D30")

                stack.append(r1)
                continue

            # RES
            if token == "RES":

                if not stack:
                    continue

                r_n = stack.pop()

                assembly_text.append(f"    VCVT.S32.F64 S31, {r_n}")
                assembly_text.append("    VMOV R1, S31")

                assembly_text.append(f"    LDR R2, ={linha_idx}")
                assembly_text.append("    SUB R2, R2, R1")

                assembly_text.append("    MOV R3, #8")
                assembly_text.append("    MUL R2, R2, R3")

                assembly_text.append("    LDR R4, =historico")
                assembly_text.append("    ADD R4, R4, R2")

                assembly_text.append(f"    VLDR.F64 {r_n}, [R4]")

                stack.append(r_n)
                continue

            # VARIÁVEIS
            if token.isalpha():

                is_read = (i > 0 and tokens[i - 1] == "(")

                if is_read:

                    freg = len(stack) % 16
                    reg = f"D{freg}"

                    assembly_text.append(f"    LDR R0, =var_{token}")
                    assembly_text.append(f"    VLDR.F64 {reg}, [R0]")

                    stack.append(reg)

                else:

                    if not stack:
                        continue

                    reg = stack.pop()

                    assembly_text.append(f"    LDR R0, =var_{token}")
                    assembly_text.append(f"    VSTR.F64 {reg}, [R0]")

                    stack.append(reg)

        # SALVA RESULTADO
        if stack:

            final_reg = stack.pop()

            assembly_text.append(f"    LDR R0, =historico")
            assembly_text.append(f"    LDR R1, ={linha_idx * 8}")
            assembly_text.append("    ADD R0, R0, R1")
            assembly_text.append(f"    VSTR.F64 {final_reg}, [R0]")

            if final_reg != "D0":
                assembly_text.append(f"    VMOV.F64 D0, {final_reg}")

    # OUTPUT FINAL
    assembly_text.append("")

    assembly_text.append("    VCVT.S32.F64 S31, D0")
    assembly_text.append("    VMOV R1, S31")
    assembly_text.append("    LDR R0, =0xFF200000")
    assembly_text.append("    STR R1, [R0]")
    assembly_text.append("    B .")


    # CONSTANTES
    for const in constants:
        assembly_data.append("    " + const)

    # juntar tudo
    return assembly_data + [""] + assembly_text


def salvarAssembly(codigo):

    try:
        with open("program.s", "w") as f:
            for linha in codigo:
                f.write(linha + "\n")

        print("Assembly salvo em program.s")

    except Exception as e:
        print(f"Erro ao salvar assembly: {e}")