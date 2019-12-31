import random

## list of all cards in string
FULL_DECK = ['c'+str(x) for x in list(range(1,10))]*4 \
            + ['b'+str(x) for x in list(range(1,10))]*4 \
            + ['m'+str(x) for x in list(range(1,10))]*4 \
            + ['d'+x for x in ['r', 'g', 'w']]*4 \
            + ['w'+x for x in ['e', 'w', 's', 'n']]*4 \
            + ['f'+x for x in ['g', 'm', 'a', 'w']] \
            + ['f'+x for x in ['p', 'o', 'b', 'c']] \

HAND_OPT = ['c'+str(x) for x in list(range(1,10))] \
            + ['b'+str(x) for x in list(range(1,10))] \
            + ['m'+str(x) for x in list(range(1,10))] \
            + ['d'+x for x in ['r', 'g', 'w']] \
            + ['w'+x for x in ['e', 'w', 's', 'n']] \

prev_ = lambda tile: tile[0]+str(int(tile[1])-1)
pprev_ = lambda tile: tile[0]+str(int(tile[1])-2)
next_ = lambda tile: tile[0]+str(int(tile[1])+1)
nnext_ = lambda tile: tile[0]+str(int(tile[1])+2)
'''
total of 144 cards
c for cookie 餅, b for bamboo 條, m for wan 萬, d for dragon 中發白, w for wind 東西南北風
f for flower 花; g, m, f, w for spring, summer, autumn, winter; 
    p, o, b, c for plum, orchid, bamboo, chrysanthemum 梅蘭竹菊
'''
## final 8*2 tile won't be played

def mahjong_sort(tile_list):
    count = [0 for __ in HAND_OPT]
    for tile in tile_list:
        count[HAND_OPT.index(tile)] += 1
    ans = []
    for tile, cnt in zip(HAND_OPT, count):
        ans += [tile]*cnt
    return ans

def mahjong_sorted(tile_list):
    tile_list = mahjong_sort(tile_list)

class Player_tile:
    def __init__(self):
        self.frontdeck = []
        self.hand = []
        self.eat_possibilities = []

    def hand_to_deck(self, tile):
        first = True
        if type(tile) is not list:
            tile = [tile]
        for t in tile:
            if t in self.hand:
                self.frontdeck.append(self.hand.pop(self.hand.index(t)))
            else:
                raise IllegalMove('frontdeck appended from air')

    def fappend(self, hidden_piece):
        ## append until not flower
        while 'f' in hidden_piece[0]:
            self.frontdeck.append(hidden_piece)
        self.hand.append(hidden_piece[0])

    def can_eat(self, piece):
        p = prev_(piece)
        pp = pprev_(piece)
        n = next_(piece)
        nn = nnext_(piece)
        if p in self.hand and pp in self.hand:
            self.eat_possibilities.append([pp, piece, p])
        elif p in self.hand and n in self.hand:
            self.eat_possibilities.append([p, piece, n])
        elif n in self.hand and nn in self.hand:
            self.eat_possibilities.append([n, piece, nn])
        return len(self.eat_possibilities) > 0


class Table():
    def __init__(self, variant):
        print('variant is ', variant)
        self.hidden_piece = FULL_DECK
        random.shuffle(self.hidden_piece)
        self.player_list = range(1,5)
        self.player_tiles = {player_ind: Player_tile() for player_ind in self.player_list}
        self.field_tiles = [[] for player_ind in self.player_list]
        ## loosely remember the discarded tiles in the table
        self.deal_cards()
        self.gamephase = 'pick_one' # one of 'pick_one', 'gong_pong', 'eat_pass'
        self.askpiece = None
        self.askroundlist = []
        self.actionsize = 0

    def deal_cards(self):
        '''
        we shall not be superstitious and implement the same order of taking cards as in Taiwan tradition, but will just take 13 consecutive tiles from hidden_piece for each player, and also take consecutive tiles from front for each flower
        '''
        for player_ind in self.player_list:
            self.player_tiles[player_ind].hand = self.hidden_piece[:13]
            self.hidden_piece = self.hidden_piece[13:]
        self.player_tiles[1].hand.append(self.hidden_piece.pop(0))
        for player_ind in self.player_list:
            for tile in self.player_tiles[player_ind].hand:
                if 'f' in tile:
                    self.player_tiles[player_ind].hand_to_deck(tile)
                    self.player_tiles[player_ind].hand.append(self.hidden_piece.pop(-1))
                    ## append at back, will be traversed if it is another flower
        self.actionsize = len(self.player_tiles[1].hand)

    def sort_hand(self, player_ind):
        print('hello')
        mahjong_sorted(self.player_tiles[player_ind].hand)
        print('bye')

    def execute_move(self, action, player_ind):
        if self.is_legal(action, player_ind):
            self.sort_hand(player_ind)
            if self.gamephase == 'pick_one':
                self.askpiece = self.player_tiles[player_ind].hand.pop(action)
                self.player_askpiece = player_ind
                self.nextplayer = player_ind%4+1
                ## pong case
                check2list = [1,2,3,4].remove(player_ind)
                has2piece = [self.player_tiles[i].hand.count(self.askpiece) >= 2 for i in check2list]
                if any(has2piece):
                    self.gamephase = 'gong_pong'
                    askplayer = check2list[has2piece.index(True)]
                    self.actionsize = self.player_tiles[askplayer].hand.count(self.askpiece)
                    return askplayer

                ## eat case
                if self.player_tiles[self.nextplayer].can_eat(self.askpiece):
                    self.gamephase = 'eat_pass'
                    self.actionsize = len(self.player_tiles[self.nextplayer].eat_possibilities) + 1
                    return self.nextplayer

                ## no pong don't eat
                self.field_tiles[self.player_askpiece].append(self.askpiece)
                self.player_tiles[self.nextplayer].fappend(self.hidden_piece)
                self.actionsize = len(self.player_tiles[self.nextplayer].hand)
                self.gamephase = 'pick_one'

            elif self.gamephase == 'gong_pong':
                if not action:  ## i.e. action==0, pass
                    ## eat case
                    if self.player_tiles[self.nextplayer].can_eat(self.askpiece):
                        self.gamephase = 'eat_pass'
                        self.actionsize = len(self.player_tiles[self.nextplayer].eat_possibilities) + 1
                        return self.nextplayer

                    ## no pong don't eat
                    self.field_tiles[self.player_askpiece].append(self.askpiece)
                    self.player_tiles[self.nextplayer].fappend(self.hidden_piece)
                    self.gamephase = 'pick_one'
                    self.actionsize = len(self.player_tiles[self.nextplayer].hand)

                else:
                    if action==1:
                        self.player_tiles[player_ind].hand_to_deck([self.askpiece]*3)
                        self.player_tiles[player_ind].fappend(self.hidden_piece)
                    else:
                        self.player_tiles[player_ind].hand_to_deck([self.askpiece]*4)

                        self.player_tiles[player_ind].fappend(self.hidden_piece)

                    self.gamephase = 'pick_one'
                    self.actionsize = len(self.player_tiles[self.nextplayer].hand)
                    return player_ind

            elif self.gamephase == 'eat_pass':
                if not action:
                    self.field_tiles[self.player_askpiece].append(self.askpiece)
                    self.player_tiles[player_ind].fappend(self.hidden_piece)
                else:
                    self.player_tiles[player_ind].hand_to_deck(self.)
                    ......
                    self.update_hand('eat', player_ind, self.askpiece, action)
                self.gamephase = 'pick_one'
                self.actionsize = len(self.player_tiles[player_ind].hand)
                self.player_tiles[player_ind].eat_possibilities = []
                return player_ind

        else:
            raise IllegalMove(str(action)+','+str(color))

    def actionsize(self, player_ind):
        if self.gamephase == 'pick_one':
            return len(self.player_tiles[player_ind].hand) 
        else:
            return 3

    # update includes sort
    def update_hand(self, operation, player_ind, num=None):
        if operation == 'eat':
            self.player_tiles[player_ind].hand_to_deck


    def update_field(self):
        pass

    def isTrump_or_Flow(self):
        pass

    def is_legal(self, action, player):
        return True


class IllegalMove(Exception):
    pass

