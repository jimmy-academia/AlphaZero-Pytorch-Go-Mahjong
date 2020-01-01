import copy
# from .base_game import BaseGame
# from .table_mahjong import Table
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
        clonedtable.field_tiles = table.field_tiles[player:] + table.field_tiles[:player]
        clonedtable.player_tiles = table.player_tiles[player:] + table.player_tiles[:player]
        return clonedtable

    # methods with canonicalForm as input for mcts

    def getSymmetricForm(self, cannonicalForm, action):
        ## next player matters, other two can swap
        swapped = cannonicalForm.copy()
        swapped[0][2], swapped[0][3] = swapped[0][3], swapped[0][2]
        return [(cannonicalForm, action), (swapped, action)]

    def getGameEnded(self, cannonicalForm, player):
        return canonicalForm.calculate_result(player)

    def stringRepresentation(self, canonicalForm):
        ## shortened to save space
        return canonicalForm.

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
        values = canonicalForm.player_tiles.values()


        input()
        action = random.randint(0, env.actionsize(currplayer))
        print(action, 'action')
        env, currplayer = game.getNextState(env, currplayer, action)
        results = game.getGameEnded(env, currplayer)
        print('results is', results)


    