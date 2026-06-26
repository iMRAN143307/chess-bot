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
    if board.side_to_move == Color.BLACK:
        best_move = (1_000_000, None)
    else:
        best_move = (-1_000_000, None)

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
            new_move = search(board, depth - 1, eval_fn, alpha, beta)
            alpha = max(alpha, new_move[0])
            if new_move[0] > 900_000:
                new_move = (new_move[0] - 1, move)
            elif new_move[0] < -900_000:
                new_move = (new_move[0] + 1, move)
            else:
                new_move = (new_move[0], move)
            best_move = [best_move, new_move]
            best_move = best_move[[move[0] for move in best_move].index(max([move[0] for move in best_move]))]
        else:
            new_move = search(board, depth - 1, eval_fn, alpha, beta)
            beta = min(beta, new_move[0])
            if new_move[0] > 900_000:
                new_move = (new_move[0] - 1, move)
            elif new_move[0] < -900_000:
                new_move = (new_move[0] + 1, move)
            else:
                new_move = (new_move[0], move)
            best_move = [best_move, new_move]
            best_move = best_move[[move[0] for move in best_move].index(min([move[0] for move in best_move]))]
        board.undo_move()
        if alpha >= beta:
            return best_move

    return best_move

def _decay_mate(score: int) -> int:
    if score >= MATE_SCORE - 1000:
        return score - 1
    if score <= -MATE_SCORE + 1000:
        return score + 1
    return score


def _plain_minimax(board, depth: int) -> int:
    """Reference plain-minimax with mate-distance decay, no pruning."""
    legal = board.legal_moves()
    if not legal:
        if board.is_in_check():
            return -MATE_SCORE if board.side_to_move == Color.WHITE else MATE_SCORE
        return 0
    if depth == 0:
        return evaluate(board)

    if board.side_to_move == Color.WHITE:
        best = -MATE_SCORE - 1
        for move in legal:
            board.make_move(move)
            value = _decay_mate(_plain_minimax(board, depth - 1))
            board.undo_move()
            if value > best:
                best = value
        return best

    best = MATE_SCORE + 1
    for move in legal:
        board.make_move(move)
        value = _decay_mate(_plain_minimax(board, depth - 1))
        board.undo_move()
        if value < best:
            best = value
    return best


POSITIONS = [
    # Starting position
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    # An open middlegame
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 4 4",
    # A tactical position
    "r1bqk2r/ppp2ppp/2n5/3npb2/1bBP4/2NQ1N2/PPP2PPP/R1B1K2R w KQkq - 0 7",
    # A K+P endgame
    "8/8/8/4k3/4P3/4K3/8/8 w - - 0 1",
]

def test_alpha_beta_matches_plain_minimax(fen: str, depth: int):
    board = Board.from_fen(fen)
    ab_score, _ = search(board, depth, evaluate)
    plain_score = _plain_minimax(board, depth)
    assert ab_score == plain_score, (
        f"alpha-beta and plain minimax disagree at depth {depth} on {fen!r}: "
        f"alpha-beta={ab_score}, plain={plain_score}"
    )

for position in POSITIONS:
    test_alpha_beta_matches_plain_minimax(position, 1)
    print("depth 1 good")
for position in POSITIONS:
    test_alpha_beta_matches_plain_minimax(position, 2)
    print("depth 2 good")
for position in POSITIONS:
    test_alpha_beta_matches_plain_minimax(position, 3)
    print("depth 3 good")
