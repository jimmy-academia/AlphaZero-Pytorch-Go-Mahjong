import copy
# from .base_game import BaseGame
# from .table_mahjong import Table

### so can test by runnnig python prev_mahjong_game.py

from base_game import BaseGame
from table_mahjong import Table

class MahJongGame(BaseGame):
    """
    This class implements the MahJong game, for alphazero implementation
    """
    @staticmethod
    def modify_commandline_options(parser, is_train=True):
        parser.add_argument('--mahjong_variant', type=str, default='normal', help='choose variant of mahjong [normal]')
        return parser

    def __init__(self, opt):
        BaseGame.__init__(self, opt)
        self.opt = opt

    def getInitState(self):
        table = Table(self.opt.mahjong_variant)
        return table

    def getNextState(self, table, player, action):
        nextplayer = table.execute_move(action, player)
        return (table, player)

    def getCanonicalForm(self, table, player):
        # a copy of table, from the player's perspective
        # also, the hidden piece should be shuffled
        clonedtable = copy.deepcopy(table)
        random.shuffle(clonedtable.hidden_piece)
        clonedtable.acting_player = player
        return clonedtable

    # methods with canonicalForm as input for mcts

    def getSymmetricForm(self, cannonicalForm, action):
        ## return net_repr from cannonicalForm
        ## next player matters, other two can swap
        Sym = copy.deepcopy(cannonicalForm)
        x = Sym.acting_player + 1 % 4 + 1
        y = Sym.acting_player + 2 % 4 + 1
        Sym.player_tiles[x], Sym.player_tiles[y] = Sym.player_tiles[x], Sym.player_tiles[y]
        return [(cannonicalForm.net_repr, action), (Sym.net_repr, action)]

    def getGameEnded(self, cannonicalForm, player):
        return canonicalForm.calculate_result(player)

    def stringRepresentation(self, canonicalForm):
        ## shortened to save space
        return canonicalForm.get_string_repr()

    def getActionSize(self, cannonicalForm):
        return canonicalForm.actionsize


if __name__ == '__main__':
    import random
    ## folow coach.py    
    ## test on game with random moves
    class foobar:
        def __init__(self):
            self.mahjong_variant = 'testing'

    opt = foobar()
    game = MahJongGame(opt)
    env = game.getInitState()
    currplayer = 1

    # for __ in range(10000):
    #     env = game.getInitState()
    #     values = env.player_tiles.values()
    #     flatt = [x.hand for x in values]
    #     nflatt = []
    #     for x in flatt:
    #         nflatt+= x
    #     # input(nflatt)
    #     if any('f' in x for x in flatt):
    #         print(flatt)
    #         input()

    # input('done')


    while True:
        print('first 3 hidden', env.hidden_piece[:3])
        print(env.field_tiles)

        canonicalForm = game.getCanonicalForm(env, currplayer)
        print(stringRepresentation(canonicalForm))
        input()
        action = random.randint(0, env.actionsize(currplayer))
        print(action, 'action')
        env, currplayer = game.getNextState(env, currplayer, action)
        results = game.getGameEnded(env, currplayer)
        print('results is', results)


    