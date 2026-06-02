

# class Produto:
#     def __init__(self, nome, preco):
#         self.nome = nome
#         self.preco = preco



# p  = Produto('Camiseta', 50)
# p.preco = -10

# print(p.preco)


class Produto:

    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco

    @property
    def preco(self):
        return self._preco

    @preco.setter
    def preco(self, valor):
        if isinstance(valor, str):
            valor = float(valor.replace('R$', ''))

        self._preco = valor


p = Produto('Camiseta', 50)
p.preco = 'R$150'

print(p.preco)  