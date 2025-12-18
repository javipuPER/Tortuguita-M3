from __future__ import annotations
'''
Trabajo hecho por:
    Fco javier Pérez Ulgar
    Leo Utrera Nieto
    Alejandro Osuna de Alba
    Ivan Sánchez Corujo
'''

"""Plantilla con las funciones que el alumnado debe completar para M3.

La capa gráfica llama a estas funciones para mover el estado del juego. No es
necesario crear clases; basta con manipular listas, diccionarios y tuplas.
"""


import random
from typing import Dict, List, Tuple

STATE_HIDDEN = "hidden"
STATE_VISIBLE = "visible"
STATE_FOUND = "found"

Card = Dict[str, str]
Board = List[List[Card]]
Position = Tuple[int, int]
GameState = Dict[str, object]


def build_symbol_pool(filas: int, columnas: int) -> List[str]:
    """Crea la lista de símbolos necesaria para rellenar todo el tablero.

    Cada símbolo aparece exactamente dos veces.
    """
    total_cards = filas * columnas
    total_pairs = total_cards // 2

    # Pool base de símbolos (se amplía repitiendo si hiciera falta)
    letras = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    symbols: List[str] = []

    # Asegurarse de que hay símbolos suficientes para el número de parejas
    while len(symbols) < total_pairs:
        for sym in letras:
            symbols.append(sym)
            if len(symbols) >= total_pairs:
                break

    # Cortar justo al número de parejas y duplicar para tener las dos cartas
    symbols = symbols[:total_pairs]
    pool = symbols * 2

    random.shuffle(pool)
    return pool


def create_game(filas: int, columnas: int) -> GameState:
    """Genera el diccionario con el estado inicial del juego."""
    symbol_pool = build_symbol_pool(filas, columnas)

    board: Board = []
    contador = 0
    for i in range(filas):
        row_cards: List[Card] = []
        for i in range(columnas):
            card: Card = {
                "symbol": symbol_pool[contador],
                "state": STATE_HIDDEN,
            }
            row_cards.append(card)
            contador += 1
        board.append(row_cards)

    total_pairs = (filas * columnas) // 2

    game: GameState = {
        "board": board,
        "pending": [],  # type: ignore[list-item]
        "moves": 0,
        "matches": 0,
        "total_pairs": total_pairs,
        "rows": filas,
        "cols": columnas,
    }
    return game


def _in_bounds(game: GameState, fila: int, columna: int) -> bool:
    filas = int(game.get("rows", 0))
    columnas = int(game.get("cols", 0))
    return 0 <= fila < filas and 0 <= columna < columnas

def reveal_card(game: GameState, fila: int, columna: int) -> bool:
    """Intenta descubrir la carta ubicada en (row, col)."""
    # Validar coordenadas
    if not _in_bounds(game, fila, columna):
        return False

    pending: List[Position] = game.get("pending", [])  # type: ignore[assignment]
    # Si ya hay dos cartas visibles en este turno, no se permite más
    if len(pending) >= 2:
        return False

    board: Board = game.get("board", [])  # type: ignore[assignment]
    card = board[fila][columna]

    # No revelar si ya está visible o encontrada
    if card.get("state") in (STATE_VISIBLE, STATE_FOUND):
        return False

    # Marcar como visible y añadir a pending
    card["state"] = STATE_VISIBLE
    pending.append((fila, columna))
    game["pending"] = pending
    return True


def resolve_pending(game: GameState) -> Tuple[bool, bool]:
    """Resuelve el turno si hay dos cartas pendientes.

    Devuelve (resuelto, pareja_encontrada).
    """
    pending: List[Position] = game.get("pending", [])  # type: ignore[assignment]
    if len(pending) != 2:
        return False, False

    board: Board = game.get("board", [])  # type: ignore[assignment]
    moves = int(game.get("moves", 0))
    matches = int(game.get("matches", 0))

    (r1, c1), (r2, c2) = pending
    card1 = board[r1][c1]
    card2 = board[r2][c2]

    pareja_encontrada = False
    if card1.get("symbol") == card2.get("symbol"):
        # Marcar como encontradas
        card1["state"] = STATE_FOUND
        card2["state"] = STATE_FOUND
        pareja_encontrada = True
        matches += 1
    else:
        # Volver a ocultar las cartas
        card1["state"] = STATE_HIDDEN
        card2["state"] = STATE_HIDDEN

    moves += 1
    game["moves"] = moves
    game["matches"] = matches
    game["pending"] = []

    return True, pareja_encontrada


def has_won(game: GameState) -> bool:
    """Indica si se han encontrado todas las parejas."""
    matches = int(game.get("matches", 0))
    total_pairs = int(game.get("total_pairs", 0))
    return matches >= total_pairs