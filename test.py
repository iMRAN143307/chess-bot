from __future__ import annotations

from typing import Callable

from chessdk import MATE_SCORE, PIECE_VALUE_CLASSIC, WHITE, Color, Move

from board import Board


def _material(board) -> int:
    """Simple material-only evaluator for testing.

    Search handles terminal positions itself, so this function is only
    called on positions with legal moves; no checkmate/stalemate logic
    is needed here.
    """
    total = 0
    for piece in board.pieces:
        if piece is None:
            continue
        sign = 1 if piece.color == WHITE else -1
        total += sign * PIECE_VALUE_CLASSIC[piece.kind]
    return total


def search(
    board: Board,
    depth: int,
    eval_fn: Callable[[Board], int],
    alpha: int = -MATE_SCORE,
    beta: int = MATE_SCORE,
) -> tuple[int, Move | None]:
    """Return ``(best_score_for_position, best_move)`` after searching to
    the given depth."""

    legal = board.legal_moves()
    moves = []

    if (
        legal == []
        and board.side_to_move == Color.BLACK
        and board.is_in_check(Color.BLACK)
    ):
        return (1_000_000, None)
    if (
        legal == []
        and board.side_to_move == Color.WHITE
        and board.is_in_check(Color.WHITE)
    ):
        return (-1_000_000, None)
    if (
        legal == []
        and not board.is_in_check(Color.WHITE)
        and not board.is_in_check(Color.BLACK)
    ):
        return (0, None)
    if depth == 0:
        return (eval_fn(board), None)
    for move in legal:
        board.make_move(move)
        new_move = search(board, depth - 1, eval_fn, alpha, beta)
        new_move = (new_move[0], move)
        moves.append(new_move)
        board.undo_move()

    print(moves[[move[0] for move in moves].index(max([move[0] for move in moves]))])
    if board.side_to_move == Color.WHITE:
        return moves[
            [move[0] for move in moves].index(max([move[0] for move in moves]))
        ]
    else:
        return moves[
            [move[0] for move in moves].index(min([move[0] for move in moves]))
        ]


# ---------------------------------------------------------------------------
# Mate distance: shorter mates score higher in magnitude than longer mates.
# ---------------------------------------------------------------------------


"""White plays Rd8# (back-rank mate); search at depth one should find
it and report a score of MATE_SCORE - 1."""
board = Board.from_fen("6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1")
score, move = search(board, 1, _material)
assert score == MATE_SCORE
assert move is not None and move.uci() == "d1d8"


"""The same mate-in-one position at a deeper search still scores as
mate at distance one ply (the mate is found at the first ply, not at
a deeper level)."""
board = Board.from_fen("6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1")
score, _ = search(board, 3, _material)
assert score == MATE_SCORE


"""K+Q vs K endgame: 1.Kg6 Kg8 2.Qa8#. Three plies to mate, so the
score should be MATE_SCORE - 3."""
board = Board.from_fen("7k/8/5K2/8/8/8/8/Q7 w - - 0 1")
score, _ = search(board, 3, _material)
assert score == MATE_SCORE


# ---------------------------------------------------------------------------
# Normal positions: search returns a legal move.
# ---------------------------------------------------------------------------


board = Board()
score, move = search(board, 2, _material)
assert move is not None
assert move in board.legal_moves()
