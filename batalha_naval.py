import random

# Tamanho do tabuleiro (por exemplo, 6x6)
TAMANHO = 6

# Cria um tabuleiro vazio (0 = água; id>0 será usado para navios)
def criar_tabuleiro():
    tab = []
    for i in range(TAMANHO):
        linha = []
        for j in range(TAMANHO):
            linha.append(0)
        tab.append(linha)
    return tab

# Exibe o tabuleiro de rastreamento (ataques do jogador):
# "~" = desconhecido (não atirado ainda), "O" = água (tiro errado), "X" = acerto.
def exibir_tabuleiro(tab):
    print("   ", end="")
    # Cabeçalho das colunas
    for col in range(TAMANHO):
        print(col+1, end=" ")
    print()
    for i in range(TAMANHO):
        # Número da linha
        print(f"{i+1:2d}", end=" ")
        for j in range(TAMANHO):
            if tab[i][j] == -1:
                print("~", end=" ")
            elif tab[i][j] == 0:
                print("O", end=" ")
            elif tab[i][j] == 1:
                print("X", end=" ")
        print()

# Posiciona aleatoriamente os navios no tabuleiro 'tab':
# Navios e seus tamanhos/IDs: Cruzador=4, Fragata=3, Destroier=2, Submarino=1.
def posicionar_navios(tab):
    navios = [("Cruzador", 4, 4), ("Fragata", 3, 3), ("Destróier", 2, 2), ("Submarino", 1, 1)]
    for nome, tamanho, id_navio in navios:
        colocado = False
        while not colocado:
            orient = random.choice(['H','V'])
            if orient == 'H':
                linha = random.randint(0, TAMANHO-1)
                col_ini = random.randint(0, TAMANHO - tamanho)
                # Verifica se há espaço livre horizontalmente
                livre = True
                for k in range(tamanho):
                    if tab[linha][col_ini+k] != 0:
                        livre = False
                        break
                if livre:
                    # Coloca o navio no tabuleiro
                    for k in range(tamanho):
                        tab[linha][col_ini+k] = id_navio
                    colocado = True
            else:
                linha_ini = random.randint(0, TAMANHO - tamanho)
                col = random.randint(0, TAMANHO-1)
                # Verifica se há espaço livre verticalmente
                livre = True
                for k in range(tamanho):
                    if tab[linha_ini+k][col] != 0:
                        livre = False
                        break
                if livre:
                    for k in range(tamanho):
                        tab[linha_ini+k][col] = id_navio
                    colocado = True

# Solicita ao jogador uma coordenada válida (linha e coluna) para atirar.
def obter_coordenadas():
    while True:
        try:
            linha = int(input("Informe a linha (1-" + str(TAMANHO) + "): ")) - 1
            coluna = int(input("Informe a coluna (1-" + str(TAMANHO) + "): ")) - 1
        except ValueError:
            print("Entrada inválida! Digite números.")
            continue
        if linha < 0 or linha >= TAMANHO or coluna < 0 or coluna >= TAMANHO:
            print("Coordenadas fora do tabuleiro. Tente novamente.")
        else:
            return linha, coluna

# Função principal que gerencia o jogo completo
def jogo_batalha_naval():
    # Cria tabuleiros de navios ocultos para cada jogador
    tabuleiros_navios = [criar_tabuleiro(), criar_tabuleiro()]
    # Cria tabuleiros de ataques (conhecimento do adversário) iniciados com -1 (desconhecido)
    tabuleiros_ataque = [
        [[-1]*TAMANHO for _ in range(TAMANHO)],
        [[-1]*TAMANHO for _ in range(TAMANHO)]
    ]
    # Posiciona aleatoriamente navios dos dois jogadores
    random.seed()
    posicionar_navios(tabuleiros_navios[0])
    posicionar_navios(tabuleiros_navios[1])
    # Contador de partes restantes dos navios de cada jogador (inicialmente 4+3+2+1 = 10)
    partes_restantes = [10, 10]
    # Contador de acertos consecutivos atuais de cada jogador
    acertos_consecutivos = [0, 0]
    # Flags para saber se cada jogador já usou o tiro triunfal
    tiro_triunfal_usado = [False, False]
    jogador_atual = 0  # 0 = Jogador1, 1 = Jogador2

    # Loop principal até alguém vencer
    while True:
        oponente = 1 - jogador_atual
        print(f"\n-- Turno do Jogador {jogador_atual+1} --")
        print("Seu mapa de ataque:")
        exibir_tabuleiro(tabuleiros_ataque[jogador_atual])

        # Jogador escolhe onde atirar
        linha, coluna = obter_coordenadas()
        # Verifica se já foi atirado nessa posição
        if tabuleiros_ataque[jogador_atual][linha][coluna] != -1:
            print("Você já atirou nessa posição. Tente outra vez.")
            continue

        # Verifica se acertou um navio inimigo
        if tabuleiros_navios[oponente][linha][coluna] > 0:
            # Acerto em um navio
            id_navio = tabuleiros_navios[oponente][linha][coluna]
            # Marca a célula como atingida (nega o valor)
            tabuleiros_navios[oponente][linha][coluna] = -id_navio
            tabuleiros_ataque[jogador_atual][linha][coluna] = 1
            print(">>> Acertou um navio!")
            acertos_consecutivos[jogador_atual] += 1
            partes_restantes[oponente] -= 1

            # Verifica se o navio foi completamente afundado
            afundou = True
            for i in range(TAMANHO):
                for j in range(TAMANHO):
                    if tabuleiros_navios[oponente][i][j] == id_navio:
                        afundou = False
            if afundou:
                # Converte todas as partes atingidas desse navio de volta para o identificador positivo
                for i in range(TAMANHO):
                    for j in range(TAMANHO):
                        if tabuleiros_navios[oponente][i][j] == -id_navio:
                            tabuleiros_navios[oponente][i][j] = id_navio
                # Obtém nome do navio afundado
                nome_navio = ""
                if id_navio == 4: nome_navio = "Cruzador"
                elif id_navio == 3: nome_navio = "Fragata"
                elif id_navio == 2: nome_navio = "Destróier"
                elif id_navio == 1: nome_navio = "Submarino"
                print(f">>> Afundou o {nome_navio} inimigo!")

            # Verifica condição de vitória
            if partes_restantes[oponente] == 0:
                print(f"\n*** Jogador {jogador_atual+1} venceu! Todos os navios inimigos foram destruídos! ***")
                break

            # Verifica tiro triunfal (3 acertos consecutivos)
            if acertos_consecutivos[jogador_atual] == 3 and not tiro_triunfal_usado[jogador_atual]:
                print("Você fez 3 acertos consecutivos e ganhou um TIRO TRIUNFAL!")
                tiro_triunfal_usado[jogador_atual] = True
                acertos_consecutivos[jogador_atual] = 0  # zera contagem após ganhar o tiro triunfal

                # Solicita direção do tiro triunfal
                while True:
                    direcao = input("Escolha direção do tiro triunfal (H-horizontal ou V-vertical): ").strip().upper()
                    if direcao in ["H", "V"]:
                        break
                    print("Opção inválida. Digite H ou V.")

                # Solicita posição central do tiro triunfal
                while True:
                    try:
                        linha_c = int(input("Linha central do tiro triunfal: ")) - 1
                        coluna_c = int(input("Coluna central do tiro triunfal: ")) - 1
                    except ValueError:
                        print("Entrada inválida! Digite números.")
                        continue
                    # Verifica limites do tabuleiro
                    if linha_c < 0 or linha_c >= TAMANHO or coluna_c < 0 or coluna_c >= TAMANHO:
                        print("Posição fora do tabuleiro. Tente novamente.")
                        continue
                    # Verifica se o tiro caberá no tabuleiro
                    if direcao == "H":
                        if coluna_c-1 < 0 or coluna_c+1 >= TAMANHO:
                            print("Não cabe horizontalmente. Escolha outra posição central.")
                            continue
                    else:  # vertical
                        if linha_c-1 < 0 or linha_c+1 >= TAMANHO:
                            print("Não cabe verticalmente. Escolha outra posição central.")
                            continue
                    break

                # Define as 3 células afetadas pelo tiro triunfal
                if direcao == "H":
                    alvos = [(linha_c, coluna_c-1), (linha_c, coluna_c), (linha_c, coluna_c+1)]
                else:  # "V"
                    alvos = [(linha_c-1, coluna_c), (linha_c, coluna_c), (linha_c+1, coluna_c)]

                # Executa o tiro triunfal nas 3 células
                ultimo_acertou = False
                for (li, co) in alvos:
                    # Verifica se já não havia sido atacado antes
                    if tabuleiros_ataque[jogador_atual][li][co] != -1:
                        continue
                    if tabuleiros_navios[oponente][li][co] > 0:
                        # Acerto no tiro triunfal
                        id_navio2 = tabuleiros_navios[oponente][li][co]
                        tabuleiros_navios[oponente][li][co] = -id_navio2
                        tabuleiros_ataque[jogador_atual][li][co] = 1
                        print(f"(Triunfal) Acertou na posição ({li+1},{co+1})!")
                        partes_restantes[oponente] -= 1
                        ultimo_acertou = True

                        # Verifica se esse navio foi afundado pelo tiro triunfal
                        afundou2 = True
                        for x in range(TAMANHO):
                            for y in range(TAMANHO):
                                if tabuleiros_navios[oponente][x][y] == id_navio2:
                                    afundou2 = False
                        if afundou2:
                            for x in range(TAMANHO):
                                for y in range(TAMANHO):
                                    if tabuleiros_navios[oponente][x][y] == -id_navio2:
                                        tabuleiros_navios[oponente][x][y] = id_navio2
                            nome_navio2 = ""
                            if id_navio2 == 4: nome_navio2 = "Cruzador"
                            elif id_navio2 == 3: nome_navio2 = "Fragata"
                            elif id_navio2 == 2: nome_navio2 = "Destróier"
                            elif id_navio2 == 1: nome_navio2 = "Submarino"
                            print(f"(Triunfal) Afundou o {nome_navio2} inimigo!")
                    else:
                        # Erro no tiro triunfal
                        tabuleiros_ataque[jogador_atual][li][co] = 0
                        print(f"(Triunfal) Água em ({li+1},{co+1}).")

                # Verifica vitória após o tiro triunfal
                if partes_restantes[oponente] == 0:
                    print(f"\n*** Jogador {jogador_atual+1} venceu! Todos os navios inimigos foram destruídos! ***")
                    break

                # Se o último tiro triunfal acertou, o jogador continua (conta 1 acerto consecutivo)
                if ultimo_acertou:
                    acertos_consecutivos[jogador_atual] = 1
                    continue  # mantém o jogador atual
                else:
                    # Se não acertou no último disparo, termina o turno (troca jogador)
                    acertos_consecutivos[jogador_atual] = 0
                    jogador_atual = oponente
                    continue

            # Se não houve tiro triunfal, o jogador acerta e joga de novo (sem trocar de jogador)
            continue

        else:
            # Errou (água): marca e troca de jogador
            tabuleiros_ataque[jogador_atual][linha][coluna] = 0
            print(">>> Água!")
            acertos_consecutivos[jogador_atual] = 0
            jogador_atual = oponente
            continue

# Inicia o jogo
jogo_batalha_naval()













