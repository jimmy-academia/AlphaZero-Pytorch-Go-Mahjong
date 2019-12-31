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
        # everything that in player's knowledge, from his/her perspective
        ## shortened to save space
        phase = table.gamephase[0]
        canonical_field = table.field_tiles[player:] + table.field_tiles[:player]
        player_frontdeck = table.player_tiles[player].frontdeck
        player_hand = table.player_tiles[player].hand
        if phase != 'p':
            player_hand.append(table.askpiece)
        actionsize = table.actionsize

        return (phase, canonical_field, player_frontdeck, player_hand, )

    def getSymmetricForm(self, cannonicalForm, action):
        ## next player matters, other two can swap
        swapped = cannonicalForm.copy()
        swapped[0][2], swapped[0][3] = swapped[0][3], swapped[0][2]
        return [(cannonicalForm, action), (swapped, action)]

    def getGameEnded(self, cannonicalForm, player):

        if table.isTrump_or_Flow():
            return table.calculate_result
        else:
            return 0

    def getActionSize(self):
        return 


if __name__ == '__main__':
    import random
    ##test on game with random moves
    class foobar:
        def __init__(self):
            self.mahjong_variant = 'testing'

    opt = foobar()
    game = MahJongGame(opt)
    env = game.getInitState()
    currplayer = 1
    while True:
        print('first 3 hidden', env.hidden_piece[:3])
        print(env.field_tiles)

        canonicalForm = game.getCanonicalForm(env, currplayer)
        input(canonicalForm)
        action = random.randint(0, env.actionsize(currplayer))
        print(action, 'action')
        env, currplayer = game.getNextState(env, currplayer, action)
        results = game.getGameEnded(env, currplayer)
        print('results is', results)


    