from chessdk import Move

from board import Board

my_board = Board()
my_board.make_move(Move(15, 31))
for move_obj in my_board.legal_moves():
    my_board.make_move(move_obj)
    print(my_board.to_fen())
    for submove_obj in my_board.legal_moves():
        if submove_obj.to_sq == my_board.state.en_passant:
            print(my_board.to_fen())
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            my_board.make_move(submove_obj)
            print(my_board.to_fen())
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            my_board.undo_move()
    my_board.undo_move()
