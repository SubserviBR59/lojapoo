"""Demonstração executável dos conceitos de POO."""

from modelos import Pedido, ProdutoDigital, ProdutoFisico


def criar_produtos():
    """Cria dez instâncias: cinco produtos físicos e cinco digitais."""
    return [
        ProdutoFisico("Caderno", "20", "5"),
        ProdutoFisico("Mochila", "100", "15"),
        ProdutoFisico("Caneta", "5", "2"),
        ProdutoFisico("Livro", "50", "8"),
        ProdutoFisico("Fone", "80", "10"),
        ProdutoDigital("Curso Python", "200", "10"),
        ProdutoDigital("E-book", "40", "25"),
        ProdutoDigital("Planilha", "30", "0"),
        ProdutoDigital("Curso Git", "100", "20"),
        ProdutoDigital("Guia de estudos", "20", "50"),
    ]


def main():
    """Exibe polimorfismo, pedido, dunders e falhas tratadas."""
    produtos = criar_produtos()
    pedido = Pedido("Cliente Exemplo", "cliente@example.com", produtos)
    print("LOJAPOO — SPRINT 6")
    print("\nPOLIMORFISMO: mesma chamada, regras diferentes")
    for produto in produtos:
        print(f"{produto.nome}: R$ {produto.calcular_preco_final():.2f}")

    print("\nREPRESENTAÇÃO AMIGÁVEL (__str__)")
    for produto in produtos:
        print(produto)
    print(pedido)

    print("\nORDEM POR PREÇO FINAL (__lt__)")
    for produto in sorted(produtos):
        print(f"{produto.nome}: R$ {produto.calcular_preco_final():.2f}")

    print("\nREPRESENTAÇÃO TÉCNICA (__repr__)")
    print(repr(produtos[0]))
    print(repr(produtos[5]))
    print(repr(pedido))

    print("\nENTRADAS INVÁLIDAS E ESTADO PRESERVADO")
    tentativas = [
        (produtos[0], "preco", -10),
        (produtos[0], "frete", -1),
        (produtos[5], "desconto", 150),
        (pedido, "email", "sem-arroba"),
        (pedido, "cliente", "   "),
    ]
    for objeto, atributo, valor in tentativas:
        valor_anterior = getattr(objeto, atributo)
        try:
            setattr(objeto, atributo, valor)
        except (ValueError, TypeError) as erro:
            print(f"{atributo}: {erro}")
            print(f"Valor mantido: {getattr(objeto, atributo)!r}")
            assert getattr(objeto, atributo) == valor_anterior

    try:
        ProdutoDigital("Produto inválido", "10", -5)
    except ValueError as erro:
        print(f"Construção rejeitada: {erro}")

    try:
        pedido.adicionar_produto("não sou um produto")
    except TypeError as erro:
        print(f"Inclusão rejeitada: {erro}")
    print(f"\nTotal após tentativas inválidas: R$ {pedido.calcular_total():.2f}")


if __name__ == "__main__":
    main()
