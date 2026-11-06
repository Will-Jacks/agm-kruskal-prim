#!/usr/bin/env python3
"""
Árvore Geradora Mínima (AGM) com os algoritmos de Kruskal e Prim.

Exemplo didático: ligar os prédios de um campus com cabo de fibra óptica,
gastando o menor custo total e sem criar ciclos. Os nomes dos prédios e os
custos (em R$ mil) são fictícios e servem apenas para ilustrar.

Uso:
    python kruskal_prim.py

Requisitos: Python 3.9+ (somente biblioteca padrão).
"""
from __future__ import annotations

import heapq

# Uma aresta é a tupla (vértice_u, vértice_v, peso). O grafo é não direcionado.
Aresta = tuple[str, str, int]


# ---------------------------------------------------------------------------
# Union-Find (conjuntos disjuntos), usado pelo Kruskal para detectar ciclos
# ---------------------------------------------------------------------------
class UnionFind:
    """Guarda em qual componente cada vértice está.

    find(v)  -> representante (raiz) do componente de v
    union(a, b) -> junta os componentes de a e b; False se já eram o mesmo
    """

    def __init__(self, vertices: list[str]) -> None:
        self.pai = {v: v for v in vertices}      # cada vértice começa sozinho
        self.altura = {v: 0 for v in vertices}   # altura aproximada de cada árvore

    def find(self, v: str) -> str:
        if self.pai[v] != v:
            self.pai[v] = self.find(self.pai[v])  # compressão de caminho
        return self.pai[v]

    def union(self, a: str, b: str) -> bool:
        raiz_a, raiz_b = self.find(a), self.find(b)
        if raiz_a == raiz_b:
            return False                          # já conectados: a aresta fecharia um ciclo
        if self.altura[raiz_a] < self.altura[raiz_b]:
            raiz_a, raiz_b = raiz_b, raiz_a       # a árvore menor entra na maior
        self.pai[raiz_b] = raiz_a
        if self.altura[raiz_a] == self.altura[raiz_b]:
            self.altura[raiz_a] += 1
        return True


# ---------------------------------------------------------------------------
# Kruskal: ordena as arestas e vai juntando componentes
# ---------------------------------------------------------------------------
def kruskal(vertices: list[str], arestas: list[Aresta],
            verbose: bool = False) -> tuple[list[Aresta], int]:
    """Retorna (arestas da AGM, custo total). Levanta ValueError se o grafo for desconexo."""
    uf = UnionFind(vertices)
    arvore: list[Aresta] = []
    custo = 0

    # 1. ordenar as arestas do menor ao maior peso
    for u, v, peso in sorted(arestas, key=lambda a: a[2]):
        if len(arvore) == len(vertices) - 1:      # árvore completa: V - 1 arestas
            break
        if uf.union(u, v):                        # 2. aceitar se liga componentes distintos
            arvore.append((u, v, peso))
            custo += peso
            if verbose:
                print(f"  + {u} — {v} ({peso}): aceita")
        elif verbose:                             # 3. ignorar se fecha ciclo
            print(f"  x {u} — {v} ({peso}): rejeitada (fecharia um ciclo)")

    if len(arvore) != len(vertices) - 1:
        raise ValueError("grafo desconexo: não existe árvore geradora")
    return arvore, custo


# ---------------------------------------------------------------------------
# Prim: faz uma única árvore crescer a partir de um vértice inicial
# ---------------------------------------------------------------------------
def lista_de_adjacencia(vertices: list[str],
                        arestas: list[Aresta]) -> dict[str, list[tuple[str, int]]]:
    adj: dict[str, list[tuple[str, int]]] = {v: [] for v in vertices}
    for u, v, peso in arestas:
        adj[u].append((v, peso))
        adj[v].append((u, peso))
    return adj


def prim(vertices: list[str], arestas: list[Aresta], inicio: str | None = None,
         verbose: bool = False) -> tuple[list[Aresta], int]:
    """Retorna (arestas da AGM, custo total). Levanta ValueError se o grafo for desconexo."""
    adj = lista_de_adjacencia(vertices, arestas)
    # 1. começar por um vértice qualquer
    inicio = inicio if inicio is not None else vertices[0]

    na_arvore = [inicio]
    visitados = {inicio}
    # fronteira: heap com as arestas que saem da árvore, ordenado por peso
    fronteira = [(peso, inicio, v) for v, peso in adj[inicio]]
    heapq.heapify(fronteira)
    arvore: list[Aresta] = []
    custo = 0

    while fronteira and len(visitados) < len(vertices):
        peso, u, v = heapq.heappop(fronteira)    # 2. menor aresta da fronteira
        if v in visitados:                       # aresta "velha": v já entrou na árvore
            if verbose:
                print(f"  - {u} — {v} ({peso}): descartada ({v} já está na árvore)")
            continue
        visitados.add(v)                         # 3. expandir: v entra na árvore
        na_arvore.append(v)
        arvore.append((u, v, peso))
        custo += peso
        if verbose:
            print(f"  + {u} — {v} ({peso}): aceita  | árvore: {', '.join(na_arvore)}")
        for w, p in adj[v]:                                  # novas arestas na fronteira
            if w not in visitados:
                heapq.heappush(fronteira, (p, v, w))

    if len(visitados) != len(vertices):
        raise ValueError("grafo desconexo: não existe árvore geradora")
    return arvore, custo


# ---------------------------------------------------------------------------
# Exemplo: rede de fibra óptica do campus (custos fictícios, em R$ mil)
# CT = Centro de Tecnologia, RU = Restaurante Universitário
# ---------------------------------------------------------------------------
VERTICES = ["Reitoria", "Biblioteca", "CT", "RU", "Ginásio", "Lab", "Portaria"]

ARESTAS: list[Aresta] = [
    ("Reitoria", "Biblioteca", 7),
    ("Reitoria", "RU", 5),
    ("Biblioteca", "CT", 8),
    ("Biblioteca", "RU", 9),
    ("Biblioteca", "Ginásio", 6),
    ("CT", "Ginásio", 4),
    ("RU", "Ginásio", 15),
    ("RU", "Lab", 10),
    ("Ginásio", "Lab", 12),
    ("Ginásio", "Portaria", 11),
    ("Lab", "Portaria", 13),
]


def mostrar(titulo: str, arvore: list[Aresta], custo: int) -> None:
    print(f"\n{titulo}")
    for u, v, peso in arvore:
        print(f"  {u} — {v}: {peso}")
    print(f"  Custo total: {custo}")


def main() -> None:
    soma_todas = sum(p for _, _, p in ARESTAS)
    print(f"Grafo: {len(VERTICES)} vértices, {len(ARESTAS)} arestas "
          f"(custo de ligar tudo: {soma_todas}).")

    print("\n=== Kruskal (arestas em ordem crescente de peso) ===")
    arvore_k, custo_k = kruskal(VERTICES, ARESTAS, verbose=True)

    print("\n=== Prim (começando por Reitoria) ===")
    arvore_p, custo_p = prim(VERTICES, ARESTAS, inicio="Reitoria", verbose=True)

    mostrar("AGM por Kruskal:", arvore_k, custo_k)
    mostrar("AGM por Prim:", arvore_p, custo_p)

    # Todo grafo conexo com V vértices tem AGM com exatamente V - 1 arestas.
    assert len(arvore_k) == len(arvore_p) == len(VERTICES) - 1
    # Os dois algoritmos sempre chegam ao mesmo custo mínimo ...
    assert custo_k == custo_p
    # ... e, como os pesos deste exemplo são todos diferentes, a AGM é única:
    # as arestas escolhidas também coincidem (apenas a ordem muda).
    assert {frozenset((u, v)) for u, v, _ in arvore_k} == \
           {frozenset((u, v)) for u, v, _ in arvore_p}
    print(f"\nOK: mesma árvore e mesmo custo ({custo_k}); "
          f"economia de {soma_todas - custo_k} em relação a ligar tudo.")


if __name__ == "__main__":
    main()
