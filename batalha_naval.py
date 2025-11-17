import random
import string

tamanho = 10
navios = [4,3,2,1]
ALFABETO = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
LINHAS = ALFABETO[:tamanho]

def criacao_tabuleiro(tamanho):
    #função para a criação do tabuleiro
    return [["." for _ in range(tamanho)] for _ in range(tamanho)]
def imprime_tabuleiro(visivel):
    #cabeçalho de colunas
    cabecalho = ""+"".join(f"{i + 1}" for i in range(tamanho))
    print(cabecalho)
    #linhas
    for i in range(tamanho):
        linha = f"{ALFABETO[i]} " + "".join(visivel[i])
        print(linha)
def indice_para_coordernada(indice):
        #
    if len(indice) <2:
        return None
        #Verifique a Linha 
    linha = indice[0]
    if linha not in ALFABETO:
        return None
        #Verifique a Coluna 
    try:
        coluna = int(indice[1:])
    except ValueError:
        return None
    if coluna < 1 or coluna > tamanho:
        return None
    return (ALFABETO.index(linha),coluna - 1)

def posicao_tabela(tab,r,c,tam,diretriz):
    if diretriz == "H":
        # Começando na coluna x e andar y passos para direita eu vou pra fora do tabuleiro???
        if c + tam > tamanho:
            return False # se a resposta for sim é pra retornar
        for j in range(c,c + tam):
            if tab [r][j] == 'S':
                return False 
        # já tem návio nessa posição!
    else:
        raise ValueError ("Orientação Inválida.")
def posicao_navios (tabuleiro,linha, coluna,tamanho_navio, diretriz):
    if coluna + tamanho_navio > len(tabuleiro[0]):
        return False
    for c in range (coluna, coluna + tamanho_navio):
        if tabuleiro[linha][c] == 'S':
            return False

    return True

def colocar_navio(tabuleiro, tamanho_navio):
    print("escolha a posição para o navio de tamanho {tamanho_navio}")
    











