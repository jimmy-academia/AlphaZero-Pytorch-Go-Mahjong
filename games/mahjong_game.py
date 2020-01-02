import copy
from .base_game import BaseGame
from .table_mahjong import Table

class MahJongGame(BaseGame):
    """
    This class implements the MahJong game, for alphazero implementation
    """
    @staticmethod
    def modify_commandline_options(parser, is_train=True):
        parser.add_argument('--mahjong_variant', type=str, default='Taiwan 16 piece', help='choose variant of mahjong [normal]')
        return parser

    def __init__(self, opt):
        BaseGame.__init__(self, opt)
        self.opt = opt

    def getInitState(self):
        table = Table(self.opt.mahjong_variant)
        return table

    def getNextState(self, table, player, action):
        nextplayer = table.execute_move(player, action)
        return (table, player)

    def getCanonicalForm(self, table, player):
        # a copy of table, from the player's perspective
        # also, the hidden piece should be shuffled
        clonedtable = copy.deepcopy(table)
        random.shuffle(clonedtable.hidden_piece)
        clonedtable.acting_player = player
        return clonedtable

    def getSymmetricForm(self, cannonicalForm, action):
        ## return net_repr from cannonicalForm
        ## next player matters, other two can swap
        Sym = copy.deepcopy(cannonicalForm)
        x = Sym.acting_player + 1 % 4 + 1
        y = Sym.acting_player + 2 % 4 + 1
        Sym.player_tiles[x], Sym.player_tiles[y] = Sym.player_tiles[x], Sym.player_tiles[y]
        return [(cannonicalForm.net_repr, action), (Sym.net_repr, action)]

    def getGameResults(self, table):
        return table.calculate_result()

    def getGameEnded(self, cannonicalForm, player):
        return canonicalForm.calculate_result(player)

    def stringRepresentation(self, canonicalForm):
        return canonicalForm.get_string_repr()

    def getValidMoves(self, cannonicalForm):
        ## not needed for Mahjong
        return 1

    def getActionSize(self, cannonicalForm):
        return canonicalForm.actionsize


