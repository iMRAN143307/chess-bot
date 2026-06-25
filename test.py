"""Stage 17: ``search`` runs minimax with terminal handling and mate distance.

The tests supply a simple material-only evaluation function so that the
student's evaluator is not under test here, only their search. We verify:

  - On a position with no legal moves, the search returns the right score
    (mate magnitude with the right sign, or zero for stalemate).
  - Mate-in-one is found at depth one and scored as ``MATE_SCORE - 1``.
  - The same mate-in-one is still scored as ``MATE_SCORE - 1`` at deeper
    searches (the mate distance does not change with depth).
  - A mate-in-two position at depth three returns ``MATE_SCORE - 3``.
  - On a normal position, the search returns a legal move.
"""

from __future__ import annotations

from typing import Callable

from chessdk import MATE_SCORE, Color, Move

from board import Board
from evaluation import evaluate


def search(
    board: Board,
    depth: int,
    eval_fn: Callable[[Board], int],
    alpha: int = -1_000_000,
    beta: int = 1_000_000,
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
        return (evaluate(board), None)
    for move in legal:
        board.make_move(move)
        if board.side_to_move == Color.BLACK:
            if evaluate(board) >= alpha:
                new_move = search(board, depth - 1, eval_fn, alpha, beta)
                alpha = max(alpha, new_move[0])
                if new_move[0] > 900_000:
                    new_move = (new_move[0] - 1, move)
                elif new_move[0] < -900_000:
                    new_move = (new_move[0] + 1, move)
                else:
                    new_move = (new_move[0], move)
                moves.append(new_move)
            else:
                pass
        else:
            if evaluate(board) <= beta:
                new_move = search(board, depth - 1, eval_fn, alpha, beta)
                beta = min(beta, new_move[0])
                if new_move[0] > 900_000:
                    new_move = (new_move[0] - 1, move)
                elif new_move[0] < -900_000:
                    new_move = (new_move[0] + 1, move)
                else:
                    new_move = (new_move[0], move)
                moves.append(new_move)
            else:
                pass
        board.undo_move()

    if moves == []:
        if board.side_to_move == Color.BLACK:
            return (1_000_000, None)
        else:
            return (-1_000_000, None)

    if board.side_to_move == Color.WHITE:
        return moves[
            [move[0] for move in moves].index(max([move[0] for move in moves]))
        ]
    else:
        return moves[
            [move[0] for move in moves].index(min([move[0] for move in moves]))
        ]


# ---------------------------------------------------------------------------
# Terminal positions: checkmate and stalemate handling lives in search.
# ---------------------------------------------------------------------------


"""Black has been mated on the back rank; from White's POV the score
is mate-magnitude positive."""
board = Board.from_fen("R5k1/5ppp/8/8/8/8/8/6K1 b - - 1 1")
score, _ = search(board, 0, evaluate)
assert score == MATE_SCORE


"""White has been mated by fool's mate; mate-magnitude negative."""
board = Board.from_fen("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1")
score, _ = search(board, 0, evaluate)
assert score == -MATE_SCORE


"""Black to move with no legal moves and not in check; stalemate is a draw."""
board = Board.from_fen("k7/8/1Q6/2K5/8/8/8/8 b - - 0 1")
score, _ = search(board, 0, evaluate)
assert score == 0


# ---------------------------------------------------------------------------
# Mate distance: shorter mates score higher in magnitude than longer mates.
# ---------------------------------------------------------------------------


"""White plays Rd8# (back-rank mate); search at depth one should find
it and report a score of MATE_SCORE - 1."""
board = Board.from_fen("6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1")
score, move = search(board, 1, evaluate)
assert score == MATE_SCORE - 1
assert move is not None and move.uci() == "d1d8"


"""The same mate-in-one position at a deeper search still scores as
mate at distance one ply (the mate is found at the first ply, not at
a deeper level)."""
board = Board.from_fen("6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1")
score, _ = search(board, 3, evaluate)
assert score == MATE_SCORE - 1


"""K+Q vs K endgame: 1.Kg6 Kg8 2.Qa8#. Three plies to mate, so the
score should be MATE_SCORE - 3."""
board = Board.from_fen("7k/8/5K2/8/8/8/8/Q7 w - - 0 1")
score, _ = search(board, 3, evaluate)
assert score == MATE_SCORE - 3


# ---------------------------------------------------------------------------
# Normal positions: search returns a legal move.
# ---------------------------------------------------------------------------


board = Board()
score, move = search(board, 2, evaluate)
assert move is not None
assert move in board.legal_moves()
