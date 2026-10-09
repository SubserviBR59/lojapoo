"""Testes de contratos, validações e relações entre os objetos."""

import unittest
from decimal import Decimal

from main import criar_produtos
from modelos import Pedido, Produto, ProdutoDigital, ProdutoFisico


class TestModelos(unittest.TestCase):
    def test_classe_abstrata(self):
        with self.assertRaises(TypeError):
            Produto("Teste", 10)

    def test_dez_instancias_e_heranca(self):
        produtos = criar_produtos()
        self.assertEqual(len(produtos), 10)
        self.assertEqual(len({id(p) for p in produtos}), 10)
        self.assertTrue(all(isinstance(p, Produto) for p in produtos))
        self.assertEqual(sum(isinstance(p, ProdutoFisico) for p in produtos), 5)

    def test_polimorfismo(self):
        produtos = [ProdutoFisico("A", 100, 10), ProdutoDigital("B", 100, 10)]
        self.assertEqual([p.calcular_preco_final() for p in produtos], [Decimal("110"), Decimal("90")])

    def test_total_exemplo(self):
        pedido = Pedido("Teste", "teste@example.com", criar_produtos())
        self.assertEqual(pedido.calcular_total(), Decimal("625.00"))

    def test_nome_e_cliente(self):
        p = ProdutoFisico("  Livro  ", 10, 0)
        self.assertEqual(p.nome, "Livro")
        for valor in ("", "   ", None, 123):
            with self.subTest(valor=valor):
                with self.assertRaises((ValueError, TypeError)):
                    p.nome = valor
                self.assertEqual(p.nome, "Livro")
        with self.assertRaises(ValueError):
            Pedido(" ", "a@example.com")

    def test_precos_invalidos(self):
        p = ProdutoFisico("A", 10, 2)
        for valor in (-1, "abc", "NaN", "Infinity", True, None, "1000000001"):
            with self.subTest(valor=valor):
                with self.assertRaises((ValueError, TypeError)):
                    p.preco = valor
                self.assertEqual(p.preco, Decimal("10"))
                with self.assertRaises((ValueError, TypeError)):
                    ProdutoFisico("A", valor, 0)

    def test_frete_preservado(self):
        p = ProdutoFisico("A", 10, 2)
        with self.assertRaises(ValueError):
            p.frete = -1
        self.assertEqual(p.frete, Decimal("2"))

    def test_desconto_limites(self):
        p = ProdutoDigital("A", 10, 0)
        self.assertEqual(p.calcular_preco_final(), Decimal("10"))
        p.desconto = 100
        self.assertEqual(p.calcular_preco_final(), Decimal("0"))
        for valor in (-1, 101, "NaN"):
            with self.assertRaises(ValueError):
                p.desconto = valor
            self.assertEqual(p.desconto, Decimal("100"))

    def test_email_preservado(self):
        pedido = Pedido("Teste", "a@example.com")
        for valor in ("invalido", "a..b@example.com", "a@-example.com", ""):
            with self.assertRaises(ValueError):
                pedido.email = valor
            self.assertEqual(pedido.email, "a@example.com")

    def test_arredondamento_monetario(self):
        p = ProdutoFisico("A", "10.005", "0.005")
        self.assertEqual(p.calcular_preco_final(), Decimal("10.02"))
        d = ProdutoDigital("B", "0.05", 50)
        self.assertEqual(d.calcular_preco_final(), Decimal("0.03"))

    def test_lista_copiada_e_tupla(self):
        p = ProdutoDigital("A", 10, 0)
        origem = [p]
        pedido = Pedido("Teste", "a@example.com", origem)
        origem.clear()
        self.assertEqual(pedido.produtos, (p,))
        self.assertIsInstance(pedido.produtos, tuple)
        with self.assertRaises(AttributeError):
            pedido.produtos = ()

    def test_pedidos_independentes(self):
        a = Pedido("A", "a@example.com")
        b = Pedido("B", "b@example.com")
        a.adicionar_produto(ProdutoDigital("Curso", 10, 0))
        self.assertEqual(len(b.produtos), 0)
        self.assertEqual(b.calcular_total(), Decimal("0"))

    def test_produto_invalido(self):
        pedido = Pedido("A", "a@example.com")
        with self.assertRaises(TypeError):
            pedido.adicionar_produto("produto")
        self.assertEqual(len(pedido.produtos), 0)
        with self.assertRaises(TypeError):
            Pedido("A", "a@example.com", [123])

    def test_ordenacao(self):
        a = ProdutoFisico("A", 10, 10)
        b = ProdutoDigital("B", 10, 50)
        self.assertEqual(sorted([a, b]), [b, a])
        self.assertIs(a.__lt__("texto"), NotImplemented)

    def test_representacoes(self):
        objetos = criar_produtos()
        objetos.append(Pedido("A", "a@example.com"))
        for objeto in objetos:
            self.assertTrue(str(objeto))
            self.assertIn(type(objeto).__name__, repr(objeto))


if __name__ == "__main__":
    unittest.main()
