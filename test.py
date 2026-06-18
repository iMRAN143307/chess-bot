
from board import Board
from evaluation import evaluate
from bot import choose_move
from chessdk import Move

fen = "6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1"
board = Board.from_fen(fen)
moves = board.legal_moves()
for i, m in enumerate(board.legal_moves()):
    board.make_move(m)
    moves[i] = evaluate(board)
    board.undo_move()
print(moves)
print(board.legal_moves())
board.make_move(Move(3, 59))
