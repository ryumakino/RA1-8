"""
Gerador de Assembly ARMv7 (CPULATOR) com suporte a IEEE754 64 bits

Integrantes (ordem alfabética):
Murilo Chandelier Pedrazzani - https://github.com/MuriloPedrazzani
Ricardo Ryu Magalhães Makino - https://github.com/ryumakino
Ricardo Vinicius Moreira Vianna - https://github.com/ricaprof

Grupo no Canvas: RA1 8

Disciplina: Construção de Interpretadores
Professor: Frank Alcantara

---------------------------------------------------------
Programa principal do interpretador

Fluxo do programa:
1) Lê o arquivo de entrada
2) Executa o analisador léxico (lexer)
3) Executa a expressão (executor)
4) Armazena os tokens
5) Gera código Assembly ARMv7
6) Salva resultados
"""

import sys
from lexer import parseExpressao
from executor import executarExpressao
from assembly import gerarAssembly


# LER ARQUIVO DE ENTRADA
def lerArquivo(nomeArquivo):
    try:
        with open(nomeArquivo, "r") as arquivo:
            return arquivo.readlines()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nomeArquivo}' não foi encontrado.")
        sys.exit(1)


# SALVAR TOKENS
def salvarTokens(tokens):
    try:
        with open("tokens.txt", "w") as arquivo:
            for token in tokens:
                arquivo.write(str(token) + "\n")
    except Exception as e:
        print(f"Erro ao salvar tokens: {e}")


# SALVAR ASSEMBLY
def salvarAssembly(codigo):
    try:
        with open("program.s", "w") as arquivo:
            if isinstance(codigo, list):
                arquivo.write("\n".join(codigo) + "\n")
            else:
                arquivo.write(str(codigo) + "\n")
    except Exception as e:
        print(f"Erro ao salvar assembly: {e}")


# EXIBIR RESULTADOS
def exibirResultados(resultados):
    if not resultados:
        print("\nNenhuma expressão válida foi executada.")
        return

    print("\nResultados:")
    for linha, resultado in resultados:
        print(f"Linha {linha}: {resultado}")


# FUNÇÃO PRINCIPAL
def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py teste1.txt")
        sys.exit(1)

    nomeArquivo = sys.argv[1]
    linhas = lerArquivo(nomeArquivo)

    resultados = []
    linha_atual = 1

    tokensUltimaExecucao = []
    linhas_tokens = []

    for linha in linhas:
        linha = linha.strip()

        # ignora linhas vazias
        if not linha:
            linha_atual += 1
            continue

        try:
            # executa o lexer
            tokens = parseExpressao(linha)

            # executa a expressão
            resultado = executarExpressao(tokens)

            resultados.append((linha_atual, resultado))

            tokensUltimaExecucao = tokens
            linhas_tokens.append(tokens)

        except Exception as e:
            print(f"Erro na linha {linha_atual}: {e}")

        linha_atual += 1

    # salva tokens da ultima execução valida
    if tokensUltimaExecucao:
        salvarTokens(tokensUltimaExecucao)

    # gera assembly se houver expressões validas
    if linhas_tokens:
        codigoAssembly = gerarAssembly(linhas_tokens)

        if codigoAssembly:
            salvarAssembly(codigoAssembly)

    # exibe resultados
    exibirResultados(resultados)


# EXECUÇÃO
if __name__ == "__main__":
    main()