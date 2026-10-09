"""Classes de domínio da LojaPOO: produtos e pedidos."""

import re
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


CENTAVO = Decimal("0.01")
LIMITE_VALOR = Decimal("1000000000")


def validar_decimal(valor, campo, limite=LIMITE_VALOR):
    """Converte números/textos decimais; rejeita negativos e não finitos."""
    if isinstance(valor, bool) or not isinstance(valor, (str, int, float, Decimal)):
        raise TypeError(f"{campo} deve ser um número ou texto decimal.")
    try:
        numero = Decimal(str(valor))
    except InvalidOperation as erro:
        raise ValueError(f"{campo} deve ser numérico.") from erro
    if not numero.is_finite() or not Decimal("0") <= numero <= limite:
        raise ValueError(f"{campo} deve estar entre 0 e {limite}.")
    return numero


def validar_texto(valor, campo):
    """Valida texto obrigatório, removendo espaços nas extremidades."""
    if not isinstance(valor, str):
        raise TypeError(f"{campo} deve ser um texto.")
    if not valor.strip():
        raise ValueError(f"{campo} não pode ficar vazio.")
    return valor.strip()


class Produto(ABC):
    """Contrato abstrato para produtos com preço final calculável."""

    def __init__(self, nome, preco):
        """Constrói os atributos comuns passando pelos setters."""
        self.nome = nome
        self.preco = preco

    @property
    def nome(self):
        """Nome não vazio do produto."""
        return self._nome

    @nome.setter
    def nome(self, valor):
        self._nome = validar_texto(valor, "Nome")

    @property
    def preco(self):
        """Preço base não negativo, representado por Decimal."""
        return self._preco

    @preco.setter
    def preco(self, valor):
        numero = validar_decimal(valor, "Preço")
        self._preco = numero.quantize(CENTAVO, rounding=ROUND_HALF_UP)

    @abstractmethod
    def calcular_preco_final(self):
        """Retorna o valor final; cada subclasse define sua regra."""
        raise NotImplementedError

    def __str__(self):
        """Representação amigável dos atributos comuns."""
        return f"{self.nome} | preço base: R$ {self.preco:.2f}"

    def __repr__(self):
        """Representação técnica para inspeção."""
        return f"{type(self).__name__}(nome={self.nome!r}, preco={str(self.preco)!r})"

    def __lt__(self, outro):
        """Permite sorted(produtos) por preço final."""
        if not isinstance(outro, Produto):
            return NotImplemented
        return self.calcular_preco_final() < outro.calcular_preco_final()


class ProdutoFisico(Produto):
    """Produto que acrescenta frete unitário ao preço base."""

    def __init__(self, nome, preco, frete):
        """Reutiliza o construtor da classe mãe e valida o frete."""
        super().__init__(nome, preco)
        self.frete = frete

    @property
    def frete(self):
        """Frete não negativo aplicado a uma unidade."""
        return self._frete

    @frete.setter
    def frete(self, valor):
        numero = validar_decimal(valor, "Frete")
        self._frete = numero.quantize(CENTAVO, rounding=ROUND_HALF_UP)

    def calcular_preco_final(self):
        """Sobrescreve o contrato: preço base mais frete."""
        return self.preco + self.frete

    def __str__(self):
        """Mostra tipo, nome e preço com frete."""
        return (
            f"Físico: {self.nome} | frete: R$ {self.frete:.2f} | "
            f"final: R$ {self.calcular_preco_final():.2f}"
        )

    def __repr__(self):
        """Inclui os dados específicos do produto físico."""
        return (
            f"ProdutoFisico(nome={self.nome!r}, preco={str(self.preco)!r}, "
            f"frete={str(self.frete)!r})"
        )


class ProdutoDigital(Produto):
    """Produto que aplica desconto percentual ao preço base."""

    def __init__(self, nome, preco, desconto):
        """Reutiliza o construtor da classe mãe e valida o desconto."""
        super().__init__(nome, preco)
        self.desconto = desconto

    @property
    def desconto(self):
        """Percentual de desconto, de zero a cem."""
        return self._desconto

    @desconto.setter
    def desconto(self, valor):
        self._desconto = validar_decimal(valor, "Desconto", Decimal("100"))

    def calcular_preco_final(self):
        """Sobrescreve o contrato: preço reduzido pelo desconto."""
        valor = self.preco * (Decimal("1") - self.desconto / Decimal("100"))
        return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)

    def __str__(self):
        """Mostra tipo, nome e preço após o desconto."""
        return (
            f"Digital: {self.nome} | desconto: {self.desconto}% | "
            f"final: R$ {self.calcular_preco_final():.2f}"
        )

    def __repr__(self):
        """Inclui os dados específicos do produto digital."""
        return (
            f"ProdutoDigital(nome={self.nome!r}, preco={str(self.preco)!r}, "
            f"desconto={str(self.desconto)!r})"
        )


class Pedido:
    """Agrupa produtos existentes; cada inclusão representa uma unidade."""

    def __init__(self, cliente, email, produtos=None):
        """Valida o cliente e copia a coleção, sem padrão mutável."""
        self.cliente = cliente
        self.email = email
        self._produtos = []
        if produtos is not None:
            for produto in produtos:
                self.adicionar_produto(produto)

    @property
    def cliente(self):
        """Nome obrigatório do cliente."""
        return self._cliente

    @cliente.setter
    def cliente(self, valor):
        self._cliente = validar_texto(valor, "Cliente")

    @property
    def email(self):
        """Contato com formato simplificado de e-mail."""
        return self._email

    @email.setter
    def email(self, valor):
        texto = validar_texto(valor, "E-mail")
        padrao = (
            r"[A-Za-z0-9_]+(?:[.+-][A-Za-z0-9_]+)*@"
            r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+"
            r"[A-Za-z]{2,}"
        )
        if re.fullmatch(padrao, texto) is None:
            raise ValueError("E-mail com formato inválido.")
        self._email = texto

    @property
    def produtos(self):
        """Tupla para impedir alterações externas na coleção interna."""
        return tuple(self._produtos)

    def adicionar_produto(self, produto):
        """Inclui exclusivamente objetos que implementam Produto."""
        if not isinstance(produto, Produto):
            raise TypeError("O item deve ser um objeto Produto.")
        self._produtos.append(produto)

    def calcular_total(self):
        """Usa polimorfismo, sem consultar o tipo concreto dos produtos."""
        return sum(
            (produto.calcular_preco_final() for produto in self._produtos),
            Decimal("0.00"),
        )

    def __str__(self):
        """Resumo amigável do pedido."""
        return (
            f"Pedido de {self.cliente} | {len(self._produtos)} item(ns) | "
            f"total: R$ {self.calcular_total():.2f}"
        )

    def __repr__(self):
        """Representação técnica do pedido e dos produtos agregados."""
        return (
            f"Pedido(cliente={self.cliente!r}, email={self.email!r}, "
            f"produtos={self._produtos!r})"
        )
