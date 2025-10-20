razao = int(input("digite um número para a razão da progressão:"))
p_geometrica = [0,1]

while len(p_geometrica) < 5:
    p_geometrica.append(p_geometrica[-1] * razao)

print(p_geometrica)