import random

corredores = 6
voltas = 10

nomes = ["Murilo", "Ricardo", "Mateus", "Marina", "Candinho", "Simone"]
tempos = []

for i in range(corredores):
    voltas_corredor = []
    for j in range(voltas):
        tempo = round(random.uniform(30, 70), 2)
        voltas_corredor.append(tempo)
    tempos.append(voltas_corredor)

melhor_tempo = tempos[0][0]
melhor_nome = nomes[0]

for i in range(corredores):
    for j in range(voltas):
        if tempos[i][j] < melhor_tempo:
            melhor_tempo = tempos[i][j]
            melhor_nome = nomes[i]

totais = []
medias = []
for i in range(corredores):
    total = 0
    for j in range(voltas):
        total += tempos[i][j]
    media = total / voltas
    totais.append(total)
    medias.append(media)

posicoes = [0] * corredores
for i in range(corredores):
    posicao = 1
    for j in range(corredores):
        if totais[j] < totais[i]:
            posicao += 1
    posicoes[i] = posicao

melhor_media = medias[0]
melhor_media_nome = nomes[0]
for i in range(corredores):
    if medias[i] < melhor_media:
        melhor_media = medias[i]
        melhor_media_nome = nomes[i]

print("\n --- TEMPOS DAS VOLTAS ---")
for i in range(corredores):
    print(f"{nomes[i]}: {tempos[i]}")

print("\n --- RESULTADOS ---")
print(f"Melhor volta: {melhor_nome} com {melhor_tempo:.2f}s")

print("\n Classificação final:")
for p in range(1, corredores+1):
    for i in range(corredores):
        if posicoes[i] == p:
            print(f"{p}º - {nomes[i]}: {totais[i]:.2f}s")

print(f"\n Melhor média: {melhor_media_nome} com {melhor_media:.2f}s")