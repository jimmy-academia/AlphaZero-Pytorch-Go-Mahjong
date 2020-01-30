import numpy as np

from .base_game import BaseGame, gamespecs
from .logic_go import Board

class GoGame(BaseGame):
    """
    This class implements the Go game, for alphazero implementation
    the two players are 1 and -1
    """
    @staticmethod
    def modify_commandline_options(parser, is_train=True):
        parser.add_argument('--boardsize', type=int, default=19, help='boardsize, one int for square board, two int for rectangle')
        opt = parser.parse_known_args()

        boardarea = opt.boardsize**2 if type(opt.boardsize)==int else opt.boardsize[0]*opt.boardsize[1]
        parser.set_defaults(n_montesims_alt=10*boardarea)
        return parser

    def __init__(self, opt):
        BaseGame.__init__(self, opt)
        if type(opt.boardsize)==int:
            self.n = self.n2 = opt.boardsize
        else:
            self.n, self.n2 = opt.boardsize


    ### coach methods ###

    def getInitState(self):
        # return initial board (numpy board)
        ## rectangle board possible
        b = Board(self.n, self.n2)
        return b

    # def getBoardSize(self):
        # return (self.n, self.n2)

    def getNextState(self, board, player, action):
        # return next (board, player) after current player, action on board
        # b = board.copy() ##no need?
        if action == self.n * self.n2:
            return (b, -player)
        else:
            move = (int(action / self.n), action % self.n)
            board.execute_move(move,player)
            return (board, -player)


    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        canonicalBoard=board.copy()

        canonicalBoard.pieces= board.pieces* player

        # print('getting canon:')
        # print(b_pieces)
        return canonicalBoard

    # modified
    def getSymmetricForm(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n**2 + 1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []
        b_pieces = board.pieces
        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(b_pieces, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l


    ### mcts methods ###

    def getGameEnded(self, board, player,returnScore=False):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1

        winner = 0
        (score_black, score_white) = self.getScore(board)
        by_score = 0.5 * (board.n*board.n + board.komi)

        if len(board.history) > 1:
            if (board.history[-1] is None and board.history[-2] is None\
                    and player == -1):
                if score_black > score_white:
                    winner = -1
                elif score_white > score_black:
                    winner = 1
                else:
                    # Tie
                    winner = 1e-4
            elif score_black > by_score or score_white > by_score:
                if score_black > score_white:
                    winner = -1
                elif score_white > score_black:
                    winner = 1
                else:
                    # Tie
                    winner = 1e-4
        if returnScore:
            return winner,(score_black, score_white)
        return winner

    def getScore(self, board):
        score_white = np.sum(board.pieces == -1)
        score_black = np.sum(board.pieces == 1)
        empties = zip(*np.where(board.pieces == 0))
        for empty in empties:
            # Check that all surrounding points are of one color
            if board.is_eyeish(empty, 1):
                score_black += 1
            elif board.is_eyeish(empty, -1):
                score_white += 1
        score_white += board.komi
        score_white -= board.passes_white
        score_black -= board.passes_black
        return (score_black, score_white)

    def stringRepresentation(self, board):
        # nxn numpy array (canonical board)
        return np.array(board.pieces).tostring()

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0 for i in range(self.getActionSize())]
        b = board.copy()
        legalMoves = b.get_legal_moves(player)
        # display(board)
        # print("legal moves{}".format(legalMoves))
        if len(legalMoves) == 0:
            valids[-1] = 1
            return np.array(valids)
        for x, y in legalMoves:
            valids[self.n * x + y] = 1
        # display(b)
        # print(legalMoves)
        return np.array(valids)

    def getActionSize(self):
        return self.n * self.n2 + 1


    ## model specs
    def getGameSpecsList(self):
        gospecs = gamespecs()
        gospecs.in_channels = 

        return gamespecs


def display(board):
    b_pieces = np.array(board.pieces)

    n = b_pieces.shape[0]

    for y in range(n):
        print(y, "|", end="")
    print("")
    print(" -----------------------")
    for y in range(n):
        print(y, "|", end="")    # print the row #
        for x in range(n):
            piece = b_pieces[y][x]    # get the piece to print
            if piece == 1:
                print("B ", end="")
            elif piece == -1:
                print("W ", end="")
            else:
                if x == n:
                    print("-", end="")
                else:
                    print("- ", end="")
        print("|")

    print("   -----------------------")

if __name__ == '__main__':
    ## test
    print('hi')
    