razao = int(input("digite um número para a razão da progressão:"))
p_aritmetica = [0,1]

while len(p_aritmetica) < 5:
    p_aritmetica.append(p_aritmetica[-1] + razao)

print(p_aritmetica)