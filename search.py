"""Your search function.

``search(board, depth, eval_fn, alpha, beta)`` runs minimax with alpha-beta
pruning. It returns ``(score, best_move)``: a White-relative centipawn score
for the position under optimal play to the given depth, and the move that
achieves that score (or ``None`` at terminal or leaf nodes).

The search handles terminal positions itself (a side with no legal moves
that's in check is mated; not in check is stalemated), so the ``eval_fn``
parameter only ever sees positions with legal moves left to play. Phase 5
builds this up across four stages: Stage 17 introduces minimax with mate
distance, Stage 18 adds alpha-beta cutoffs, Stage 19 adds the move-ordering
helper below, and Stage 20 instruments the whole thing.
"""

from __future__ import annotations

from typing import Callable

from chessdk import Color, Move
from chessdk.evaluation import PIECE_VALUE_KAUFMAN

from board import Board


def order_moves(board: Board, moves: list[Move]) -> list[Move]:
    """Return ``moves`` sorted to put likely-strong moves first."""
    if moves != []:
        move_value_dict = dict()
        for move_obj in moves:
            move_value_dict[move_obj] = 0
            to_piece = board.pieces[move_obj.to_sq]
            from_piece = board.pieces[move_obj.from_sq]
            if to_piece is not None and from_piece is not None:
                move_value_dict[move_obj] += PIECE_VALUE_KAUFMAN[to_piece.kind]
                move_value_dict[move_obj] -= PIECE_VALUE_KAUFMAN[from_piece.kind] / 100
        sorted_move_value_dict = [
            k
            for k, v in sorted(
                move_value_dict.items(), key=lambda item: item[1], reverse=True
            )
        ]
        moves = sorted_move_value_dict

    return moves


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
        return (eval_fn(board), None)
    legal = order_moves(board, legal)
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
            best_move = best_move[
                [move[0] for move in best_move].index(
                    max([move[0] for move in best_move])
                )
            ]
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
            best_move = best_move[
                [move[0] for move in best_move].index(
                    min([move[0] for move in best_move])
                )
            ]
        board.undo_move()
        if alpha >= beta:
            return best_move

    return best_move
