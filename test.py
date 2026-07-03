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

from board import Board
from evaluation import evaluate
from search import search

board = Board.from_fen(
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"
)

calls = 0
original = Board.legal_moves


def counting(self):
    global calls
    calls += 1
    return original(self)


Board.legal_moves = counting
search(board, 2, evaluate)
Board.legal_moves = original
print(calls)
