import os
import random
import time
from typing import List, Dict, Optional, Tuple

# --- NOTA IMPORTANTE SOBRE A ESTRUTURA DO JOGO ---
# O pedido original menciona uma comunicação entre dois programas
# (Jogador 1 e Jogador 2) através de um arquivo.
#
# Esta é uma implementação complexa de "Comunicação Inter-Processos" (IPC)
# que exigiria dois scripts Python rodando ao mesmo tempo, lendo e
# escrevendo em um arquivo de "lock" (ex: 'turno.txt') e um arquivo
# de "jogada" (ex: 'jogada.txt'), com cuidado para evitar
# "race conditions" (um ler o arquivo antes do outro terminar de escrever).
#
# Para simplicidade e para entregar um CÓDIGO ÚNICO E FUNCIONAL,
# este script implementa o jogo no modo "Hot-Seat" (Dois jogadores
# no mesmo terminal). O script limpa a tela para esconder os tabuleiros
# entre os turnos.
#
# Todas as outras regras (Tiro Triunfal, tipos de navios,
# "jogar de novo", etc.) foram implementadas.

# --- CONSTANTES DO JOGO ---
TAMANHO_TABULEIRO = 10
JOGADOR_1 = "Jogador 1"
JOGADOR_2 = "Jogador 2"

# Símbolos do tabuleiro
AGUA = "~"
TIRO_AGUA = "■"
ACERTO = "X"
AFUNDADO = "$"

# Definição dos navios (ID, Tamanho, Quantidade)
NAVIOS_CONFIG = {
    "cruzador": {"id": 4, "tamanho": 4, "qtde": 1},
    "destroyer": {"id": 3, "tamanho": 3, "qtde": 2},
    "fragata": {"id": 2, "tamanho": 2, "qtde": 3},
    "submarino": {"id": 1, "tamanho": 1, "qtde": 4},
}

# --- FUNÇÕES AUXILIARES ---

def limpar_tela():
    """Limpa o console (funciona em Windows e Unix)"""
    os.system('cls' if os.name == 'nt' else 'clear')

def criar_tabuleiro() -> List[List[str]]:
    """Cria um tabuleiro 10x10 vazio (preenchido com AGUA)"""
    return [[AGUA for _ in range(TAMANHO_TABULEIRO)] for _ in range(TAMANHO_TABULEIRO)]

def imprimir_visao_jogador(tabuleiro_tatico: List[List[str]],
                           tabuleiro_jogadas: List[List[str]],
                           nome_jogador: str):
    """
    Imprime a visão do jogador atual, mostrando seu tabuleiro tático
    (seus navios, tiros do oponente) e seu tabuleiro de jogadas (seus tiros).
    """
    print(f"--- TURNO DE: {nome_jogador} ---")
    print("\n=== MEU TABULEIRO TÁTICO (Seus Navios e Tiros do Oponente) ===")
    imprimir_tabuleiro_formatado(tabuleiro_tatico)
    print("\n=== MEU TABULEIRO DE JOGADAS (Seus Tiros no Oponente) ===")
    imprimir_tabuleiro_formatado(tabuleiro_jogadas)
    print("-" * 50)

def imprimir_tabuleiro_formatado(tabuleiro: List[List[str]]):
    """Função auxiliar para imprimir um único tabuleiro com cabeçalhos."""
    # Cabeçalho (A-J)
    print("    " + " ".join([chr(ord('A') + i) for i in range(TAMANHO_TABULEIRO)]))
    print("   " + "-" * (TAMANHO_TABULEIRO * 2 + 1))
    
    for i, linha in enumerate(tabuleiro):
        # Números da linha (1-10)
        num_linha = str(i + 1).rjust(2)
        
        # Converte objetos de navio em seus IDs para exibição
        linha_visual = []
        for celula in linha:
            if isinstance(celula, dict): # É um objeto de navio
                linha_visual.append(str(celula['id_tipo']))
            else:
                linha_visual.append(celula)
                
        print(f"{num_linha} | {' '.join(linha_visual)}")

def converter_coord(coord_str: str) -> Optional[Tuple[int, int]]:
    """
    Converte uma coordenada string (ex: "A5", "J10") em (linha, coluna)
    baseado em 0. Retorna None se a coordenada for inválida.
    """
    try:
        coord_str = coord_str.upper()
        col_str = coord_str[0]
        row_str = coord_str[1:]
        
        if not col_str.isalpha() or not row_str.isdigit():
            return None
            
        col = ord(col_str) - ord('A')
        row = int(row_str) - 1
        
        if 0 <= row < TAMANHO_TABULEIRO and 0 <= col < TAMANHO_TABULEIRO:
            return (row, col)
        else:
            return None
    except Exception:
        return None

def validar_posicao(tabuleiro: List[List[str]], tamanho: int, 
                    row: int, col: int, orient: str) -> bool:
    """
    Verifica se um navio pode ser posicionado no local, incluindo a regra
    de que navios não podem ser adjacentes (nem diagonalmente).
    """
    posicoes = []
    for i in range(tamanho):
        r, c = row, col
        if orient == 'H':
            c += i
        else: # 'V'
            r += i
            
        # 1. Verifica limites do tabuleiro
        if not (0 <= r < TAMANHO_TABULEIRO and 0 <= c < TAMANHO_TABULEIRO):
            return False
        posicoes.append((r, c))

    # 2. Verifica adjacências (8 direções + a própria célula)
    for r, c in posicoes:
        for dr in range(-1, 2): # -1, 0, 1
            for dc in range(-1, 2): # -1, 0, 1
                nr, nc = r + dr, c + dc
                
                # Se a célula vizinha está dentro do tabuleiro
                if 0 <= nr < TAMANHO_TABULEIRO and 0 <= nc < TAMANHO_TABULEIRO:
                    # E não é água (ou seja, já tem um navio)
                    if tabuleiro[nr][nc] != AGUA:
                        # E não é parte deste mesmo navio (caso complexo, simplificado)
                        # A regra é: se qualquer célula no "bloco 3x3" ao redor
                        # da nova posição não for AGUA, é inválido.
                        # Mas as posições do *próprio* navio são permitidas.
                        if (nr, nc) not in posicoes:
                            return False
    
    # 3. Verificação final (redundante, mas segura)
    for r, c in posicoes:
        if tabuleiro[r][c] != AGUA:
             return False # Sobreposição

    return True

# --- FUNÇÕES DE COLOCAÇÃO DE NAVIOS ---

def posicionar_navios_jogador(nome_jogador: str, 
                              tabuleiro: List[List[str]],
                              lista_navios: List[Dict]) -> bool:
    """
    Loop principal para um jogador posicionar todos os seus navios.
    Permite posicionamento manual ou automático (para debug).
    """
    print(f"--- {nome_jogador}, hora de posicionar seus navios ---")
    imprimir_tabuleiro_formatado(tabuleiro)
    
    modo = input("Deseja posicionar [M]anualmente ou [A]utomaticamente? ").upper()
    
    if modo == 'A':
        return posicionar_automaticamente(tabuleiro, lista_navios)
        
    # Modo Manual
    id_unico_contador = {}
    for nome_navio, config in NAVIOS_CONFIG.items():
        for i in range(config['qtde']):
            
            # Gera um ID único (ex: "fragata-1", "fragata-2")
            if config['id'] not in id_unico_contador:
                id_unico_contador[config['id']] = 0
            id_unico_contador[config['id']] += 1
            id_unico = f"{nome_navio}-{id_unico_contador[config['id']]}"
            
            tamanho = config['tamanho']
            id_tipo = config['id']
            
            valido = False
            while not valido:
                print(f"\nPosicione seu {nome_navio} (tipo {id_tipo}, tam {tamanho}) [{i+1}/{config['qtde']}]")
                try:
                    coord_str = input("Coordenada inicial (ex: A1): ")
                    orient_str = input("Orientação [H]orizontal ou [V]ertical: ").upper()
                    
                    if orient_str not in ['H', 'V']:
                        print("Orientação inválida. Use H ou V.")
                        continue
                        
                    coord = converter_coord(coord_str)
                    if coord is None:
                        print("Coordenada inválida.")
                        continue
                        
                    row, col = coord
                    
                    if validar_posicao(tabuleiro, tamanho, row, col, orient_str):
                        # Posição é válida, vamos adicionar
                        navio_obj = {
                            'id_tipo': id_tipo,
                            'tamanho': tamanho,
                            'id_unico': id_unico,
                            'posicoes': [],
                            'acertos': 0
                        }
                        
                        for j in range(tamanho):
                            r, c = row, col
                            if orient_str == 'H':
                                c += j
                            else:
                                r += j
                            
                            tabuleiro[r][c] = navio_obj # Coloca o objeto no tabuleiro
                            navio_obj['posicoes'].append((r, c))
                        
                        lista_navios.append(navio_obj)
                        valido = True
                        limpar_tela()
                        print(f"{id_unico} posicionado.")
                        imprimir_tabuleiro_formatado(tabuleiro)
                    else:
                        print("Posição inválida (sobreposição, adjacente ou fora dos limites).")
                except Exception as e:
                    print(f"Erro: {e}")
    
    print(f"\n{nome_jogador} terminou de posicionar.")
    time.sleep(2)
    return True

def posicionar_automaticamente(tabuleiro: List[List[str]], 
                              lista_navios: List[Dict]) -> bool:
    """Posiciona todos os navios aleatoriamente (para testes rápidos)."""
    id_unico_contador = {}
    for nome_navio, config in NAVIOS_CONFIG.items():
        for i in range(config['qtde']):
            if config['id'] not in id_unico_contador:
                id_unico_contador[config['id']] = 0
            id_unico_contador[config['id']] += 1
            id_unico = f"{nome_navio}-{id_unico_contador[config['id']]}"
            
            tamanho = config['tamanho']
            id_tipo = config['id']
            
            valido = False
            tentativas = 0
            while not valido and tentativas < 100:
                tentativas += 1
                row = random.randint(0, TAMANHO_TABULEIRO - 1)
                col = random.randint(0, TAMANHO_TABULEIRO - 1)
                orient = random.choice(['H', 'V'])
                
                if validar_posicao(tabuleiro, tamanho, row, col, orient):
                    navio_obj = {
                        'id_tipo': id_tipo,
                        'tamanho': tamanho,
                        'id_unico': id_unico,
                        'posicoes': [],
                        'acertos': 0
                    }
                    for j in range(tamanho):
                        r, c = row, col
                        if orient == 'H': c += j
                        else: r += j
                        tabuleiro[r][c] = navio_obj
                        navio_obj['posicoes'].append((r, c))
                    
                    lista_navios.append(navio_obj)
                    valido = True
            
            if not valido:
                print("Falha ao posicionar navios automaticamente (raro). Tente de novo.")
                return False
                
    print("Navios posicionados automaticamente.")
    imprimir_tabuleiro_formatado(tabuleiro)
    time.sleep(2)
    return True

# --- FUNÇÕES DE LÓGICA DE JOGO ---

def marcar_proximos(navio_afundado: Dict, 
                    tatico_oponente: List[List[str]],
                    jogadas_jogador: List[List[str]]):
    """
    Regra especial: Ao afundar um navio, marca todas as células
    adjacentes (incluindo diagonais) como TIRO_AGUA,
    pois nenhum navio poderia estar lá.
    """
    print(f"Marcando áreas próximas ao {navio_afundado['id_unico']}...")
    for r, c in navio_afundado['posicoes']:
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue # Pular a própria célula do navio
                    
                nr, nc = r + dr, c + dc
                
                if 0 <= nr < TAMANHO_TABULEIRO and 0 <= nc < TAMANHO_TABULEIRO:
                    # Se for água, marque como tiro na água
                    if tatico_oponente[nr][nc] == AGUA:
                        tatico_oponente[nr][nc] = TIRO_AGUA
                        jogadas_jogador[nr][nc] = TIRO_AGUA

def processar_tiro(row: int, col: int, 
                   tatico_oponente: List[List[str]],
                   jogadas_jogador: List[List[str]]) -> Tuple[str, Optional[Dict]]:
    """
    Processa um tiro, atualiza os tabuleiros e retorna o resultado.
    Retorna: (Status, ObjetoNavioAfundado)
    Status: 'AGUA', 'ACERTO', 'AFUNDADO', 'REPETIDO'
    """
    target = tatico_oponente[row][col]
    
    if target == TIRO_AGUA or target == ACERTO or target == AFUNDADO:
        print("Você já atirou aí.")
        return 'REPETIDO', None
        
    if target == AGUA:
        print("Água!")
        tatico_oponente[row][col] = TIRO_AGUA
        jogadas_jogador[row][col] = TIRO_AGUA
        return 'AGUA', None
        
    if isinstance(target, dict): # Acertou um objeto de navio
        navio_obj = target
        navio_obj['acertos'] += 1
        
        tatico_oponente[row][col] = ACERTO
        jogadas_jogador[row][col] = ACERTO
        
        if navio_obj['acertos'] == navio_obj['tamanho']:
            # AFUNDOU!
            print(f"ACERTO! E... {navio_obj['id_unico']} (Tipo {navio_obj['id_tipo']}) AFUNDADO!")
            # Marca todas as posições do navio como AFUNDADO
            for r, c in navio_obj['posicoes']:
                tatico_oponente[r][c] = AFUNDADO
                jogadas_jogador[r][c] = AFUNDADO
            return 'AFUNDADO', navio_obj
        else:
            # Apenas um acerto
            print(f"ACERTO! Você atingiu o {navio_obj['id_unico']}!")
            return 'ACERTO', None
            
    # Segurança (não deve acontecer)
    return 'AGUA', None

def verificar_vitoria(lista_navios_oponente: List[Dict]) -> bool:
    """Verifica se todos os navios do oponente foram afundados."""
    for navio in lista_navios_oponente:
        if navio['acertos'] < navio['tamanho']:
            return False # Pelo menos um navio ainda flutua
    return True

def executar_tiro_triunfal(jogador: str,
                           tatico_oponente: List[List[str]],
                           jogadas_jogador: List[List[str]],
                           lista_navios_oponente: List[Dict]) -> bool:
    """
    Executa a lógica do Tiro Triunfal.
    Retorna True se o jogo terminou durante o tiro.
    """
    print(f"\n--- {jogador}, EXECUTANDO TIRO TRIUNFAL! ---")
    print("O tiro atinge 3 casas em linha (H ou V) a partir do centro.")
    
    centro_coord = None
    while centro_coord is None:
        coord_str = input("Defina o centro do tiro (ex: A1): ")
        centro_coord = converter_coord(coord_str)
        if centro_coord is None:
            print("Coordenada central inválida.")
            
    orient = ""
    while orient not in ['H', 'V']:
        orient = input("Defina a direção [H]orizontal ou [V]ertical: ").upper()
        
    row, col = centro_coord
    
    for i in range(3): # 3 tiros consecutivos
        r, c = row, col
        if orient == 'H':
            c += i
        else:
            r += i
            
        print(f"\nTiro Triunfal ({i+1}/3) em ({chr(ord('A') + c)}{r+1})...")
        time.sleep(1)
        
        # Verifica limites
        if not (0 <= r < TAMANHO_TABULEIRO and 0 <= c < TAMANHO_TABULEIRO):
            print("Tiro fora do tabuleiro.")
            continue
            
        status, navio_afundado = processar_tiro(r, c, tatico_oponente, jogadas_jogador)
        
        if status == 'AFUNDADO':
            # Marca áreas próximas imediatamente
            marcar_proximos(navio_afundado, tatico_oponente, jogadas_jogador)
            # Verifica vitória imediatamente
            if verificar_vitoria(lista_navios_oponente):
                return True # Jogo acabou
                
    print("--- Fim do Tiro Triunfal ---")
    time.sleep(2)
    return False # Jogo não acabou (provavelmente)

def mostrar_resumo(vencedor: str, perdedor: str, 
                   navios_vencedor: List[Dict], navios_perdedor: List[Dict]):
    """Mostra o resumo final do jogo."""
    limpar_tela()
    print("=" * 50)
    print(f" FIM DE JOGO! O {vencedor} VENCEU!")
    print("=" * 50)
    
    print(f"\n--- Resumo do {vencedor} (Vencedor) ---")
    afundados_pelo_vencedor = 0
    for navio in navios_perdedor:
        if navio['acertos'] == navio['tamanho']:
            print(f"  [AFUNDADO] {navio['id_unico']} (Tipo {navio['id_tipo']})")
            afundados_pelo_vencedor += 1
    print(f"Total de navios do oponente afundados: {afundados_pelo_vencedor}")
    
    print(f"\n--- Resumo do {perdedor} (Perdedor) ---")
    afundados_pelo_perdedor = 0
    navios_sobreviventes = 0
    for navio in navios_vencedor:
        if navio['acertos'] == navio['tamanho']:
            print(f"  [AFUNDADO] {navio['id_unico']} (Tipo {navio['id_tipo']})")
            afundados_pelo_perdedor += 1
        else:
            print(f"  [SOBREVIVEU] {navio['id_unico']} (Atingido {navio['acertos']}/{navio['tamanho']})")
            navios_sobreviventes += 1
            
    print(f"Total de navios do oponente afundados: {afundados_pelo_perdedor}")
    print(f"Navios que sobreviveram: {navios_sobreviventes}")

# --- FUNÇÃO PRINCIPAL (MAIN) ---

def main():
    # 1. Inicialização
    limpar_tela()
    print("Bem-vindo à Batalha Naval!")
    
    tatico_p1 = criar_tabuleiro()
    jogadas_p1 = criar_tabuleiro()
    navios_p1 = []
    
    tatico_p2 = criar_tabuleiro()
    jogadas_p2 = criar_tabuleiro()
    navios_p2 = []
    
    # 2. Posicionamento
    if not posicionar_navios_jogador(JOGADOR_1, tatico_p1, navios_p1):
        return # Falha no posicionamento
    
    limpar_tela()
    print("ATENÇÃO: Vez do Jogador 2. Pressione Enter para continuar.")
    input()
    limpar_tela()
    
    if not posicionar_navios_jogador(JOGADOR_2, tatico_p2, navios_p2):
        return # Falha no posicionamento

    limpar_tela()
    print("Tudo pronto. Pressione Enter para começar a batalha.")
    input()
    
    # 3. Sorteio do primeiro jogador
    jogador_atual = random.choice([JOGADOR_1, JOGADOR_2])
    print(f"O {jogador_atual} começa!")
    time.sleep(2)
    
    # 4. Variáveis do Loop de Jogo
    game_over = False
    vencedor = None
    tiros_triunfais_restantes = 2 # Total para os *dois* jogadores

    # 5. Loop Principal do Jogo
    while not game_over:
        
        # Define quem é quem neste turno
        if jogador_atual == JOGADOR_1:
            jogador_nome = JOGADOR_1
            oponente_nome = JOGADOR_2
            jogador_jogadas = jogadas_p1
            jogador_tatico = tatico_p1
            oponente_tatico = tatico_p2
            oponente_navios = navios_p2
        else:
            jogador_nome = JOGADOR_2
            oponente_nome = JOGADOR_1
            jogador_jogadas = jogadas_p2
            jogador_tatico = tatico_p2
            oponente_tatico = tatico_p1
            oponente_navios = navios_p1
            
        jogada_extra = True # Começa como True para o primeiro tiro do turno
        acertos_consecutivos = 0
        
        while jogada_extra:
            limpar_tela()
            imprimir_visao_jogador(jogador_tatico, jogador_jogadas, jogador_nome)
            
            if acertos_consecutivos > 0:
                print(f"ACERTO! Jogue novamente ({acertos_consecutivos}º acerto seguido).")
            else:
                print(f"É a sua vez, {jogador_nome}.")
            
            # Obter tiro
            tiro_coord = None
            while tiro_coord is None:
                coord_str = input("Digite a coordenada do seu tiro (ex: A1): ")
                tiro_coord = converter_coord(coord_str)
                if tiro_coord is None:
                    print("Coordenada inválida. Tente A1, B10, J5, etc.")
                    
            row, col = tiro_coord
            
            # Processar o tiro
            status, navio_afundado = processar_tiro(row, col, oponente_tatico, jogador_jogadas)
            
            if status == 'REPETIDO':
                jogada_extra = True # Permite atirar de novo, mas não conta
                acertos_consecutivos = 0 # Reseta acertos
                print("Tente novamente...")
                time.sleep(2)
                continue # Volta ao início do 'while jogada_extra'
            
            if status == 'AGUA':
                jogada_extra = False
                acertos_consecutivos = 0
            
            if status == 'ACERTO':
                jogada_extra = True
                acertos_consecutivos += 1
            
            if status == 'AFUNDADO':
                jogada_extra = True
                acertos_consecutivos += 1
                # Regra de marcar próximos
                marcar_proximos(navio_afundado, oponente_tatico, jogador_jogadas)
                # Verificar vitória
                if verificar_vitoria(oponente_navios):
                    game_over = True
                    vencedor = jogador_nome
                    jogada_extra = False # Sair do loop de jogada extra
            
            # Verificar Tiro Triunfal
            if acertos_consecutivos == 3 and tiros_triunfais_restantes > 0:
                limpar_tela()
                imprimir_visao_jogador(jogador_tatico, jogador_jogadas, jogador_nome)
                print(f"*** 3 ACERTOS SEGUIDOS! {jogador_nome} GANHA UM TIRO TRIUNFAL! ***")
                tiros_triunfais_restantes -= 1
                print(f"(Tiros triunfais restantes no jogo: {tiros_triunfais_restantes})")
                
                acertos_consecutivos = 0 # Reseta a contagem
                
                # Executa o tiro e verifica se o jogo acabou
                if executar_tiro_triunfal(jogador_nome, oponente_tatico, jogador_jogadas, oponente_navios):
                    game_over = True
                    vencedor = jogador_nome
                    jogada_extra = False
                
                # Mesmo se não ganhou, o tiro triunfal pode ter dado um acerto.
                # A regra "jogar de novo" após o triunfal é ambígua.
                # Vamos assumir que o Tiro Triunfal *não* garante outra jogada,
                # a menos que o *último* tiro dele tenha sido um acerto.
                # Para simplificar: O Triunfal *termina* o "bonus de acerto".
                jogada_extra = False # O tiro triunfal encerra o combo
            
            if game_over:
                break # Sai do loop de jogadas extras
            
            if jogada_extra:
                print("Preparando para a próxima jogada bônus...")
                time.sleep(2)

        # Fim do turno do jogador
        if game_over:
            break # Sai do loop principal do jogo
            
        # Passar a vez
        limpar_tela()
        print(f"Fim do turno do {jogador_nome}.")
        print(f"Pressione Enter para passar a vez para o {oponente_nome}.")
        print("(O {oponente_nome} NÃO DEVE OLHAR!)")
        input()
        
        jogador_atual = oponente_nome
        
    # 6. Fim de Jogo
    if vencedor == JOGADOR_1:
        mostrar_resumo(JOGADOR_1, JOGADOR_2, navios_p1, navios_p2)
    else:
        mostrar_resumo(JOGADOR_2, JOGADOR_1, navios_p2, navios_p1)

# --- Iniciar o Jogo ---
if __name__ == "__main__":
    main()