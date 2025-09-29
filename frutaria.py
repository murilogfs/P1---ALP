#primeiro definimos a quantidade em kgs de morango e maças que o cliente quer comprar
quilogramaMorango = float (input("Qual a quantidade de morangos compradas em kgs?"))
quilogramaMaca = float (input("Qual a quantidade de Maças compradas em kgs?"))
quilogramaCompra = float (quilogramaMaca + quilogramaMorango)
if quilogramaMorango >= 5 or quilogramaMaca >5:
    morango = 2.20
    maca = 1.50
else:
    morango = 2.50
    maca = 1.80
#passando pela condição de valores
valorTotalA = float (quilogramaMorango * morango)
valorTotalB = float (quilogramaMaca * maca)
valorTotalC = float (valorTotalA + valorTotalB)
print("o valor total dos morangos é de:","R$",valorTotalA)
print("o valor total das maças é de:","R$", valorTotalB)
print("o valor total da compra é de:","R$", valorTotalC)
if quilogramaCompra >= 8 or valorTotalC >= 25.00:
    print("você tem direito a 10% de desconto")
    valorDesconto = (valorTotalC * 0.1)
    print("o valor do desconto será de","R$",valorDesconto )
else:
    print("O cliente não tem direito ao desconto")
    valorDesconto = (valorTotalC * 0.1)
valorFinal = ( valorTotalC - valorDesconto)
print("o valor final será de","R$", valorFinal)

    




