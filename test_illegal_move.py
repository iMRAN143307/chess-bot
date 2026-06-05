from board import Board, move
from bot import choose_move
from chessdk import Move

b = Board()

b.make_move(move("a2a3"))
b.make_move(move("e7e5"))
b.make_move(move("h2h4"))
print(b.to_fen())
# b.make_move(move("h2h4"))
# b.make_move(move("h2h4"))
# b.make_move(move("h2h4"))
# b.make_move(move("h2h4"))
# b.make_move(move("h2h4"))
# b.make_move(move("h2h4"))
# b.make_move(move("h2h4"))
# b.make_move(move("h2h4"))
# b.make_move(move("h2h4"))
# b.make_move(move("h2h4"))
# print(b.to_fen())
