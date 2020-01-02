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
        self.play_history = []
        self.eat_possibilities = []
        self.huhuhu = False

    def play_card(self, action):
        piece = self.pop_one_hand(action)
        self.play_history.append(piece)
        return piece

    def pop_one_hand(self, tile):
        if tile is None or \
        type(tile) is int and tile > len(self.hand) or \
        type(tile) is str and tile not in self.hand:
            raise IllegalMove('poped tile from air')
        else:
            if type(tile) is str:
                tile = self.hand.index(tile)
            return self.hand.pop(tile)

    def hand_to_deck(self, tile, askpiece=None):
        if type(tile) is not list:
            # singles, flowers
            self.frontdeck.append(self.pop_one_hand(tile))
        else:
            self.hand.append(askpiece)
            tile.insert(1, askpiece)
            triplet = []
            for t in tile:
                triplet.append(self.pop_one_hand(t))
            self.frontdeck.append(triplet)            

    def fappend(self, hidden_piece):
        ## append until not flower
        while 'f' in hidden_piece[0]:
            self.frontdeck.append(hidden_piece)
        self.hand.append(hidden_piece[0])

    def can_eat(self, piece):
        if not piece[0].isdigit():
            return False
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

    def has_hu(self, piece):



        return self.huhuhu

class Table():
    def __init__(self, variant):
        # print('variant is ', variant)
        self.hidden_piece = FULL_DECK
        random.shuffle(self.hidden_piece)
        self.player_list = range(1,5)
        self.player_tiles = {player_ind: Player_tile() for player_ind in self.player_list}
        ## loosely remember the discarded tiles in the table
        self.deal_cards()
        self.gamephase = 'pick_one' # one of 'pick_one', 'gong_pong', 'eat_pass'
        self.askpiece = None
        self.actionsize = 0
        self.active_player = 1 ## for canonicalForm -> string representation

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
                    self.player_tiles[player_ind].hand.fappend(self.hidden_piece)
        self.actionsize = len(self.player_tiles[1].hand)

    def sort_hand(self, player_ind):
        mahjong_sorted(self.player_tiles[player_ind].hand)
    def sort_all(self):
        for player_ind in self.player_list:
            self.sort_hand(player_ind)

    def execute_move(self, action, player_ind):
        if self.is_legal(action, player_ind):
            self.sort_hand(player_ind)
            if self.gamephase == 'pick_one':
                self.askpiece = self.player_tiles[player_ind].play_card(action)

                # hu case (drop gun)
                checkhulist = [(player_ind+x)%4 + 1 for x in range(3)]
                hashu = [self.player_tiles[i].hashu(self.askpiece) for i in checkhulist]
                if any(hashu):
                    # will be picked up by game.getGameEnded calling self.calculated_result()
                    return player_ind

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

                ## no pong can't eat
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

                    ## no pong can't eat
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
                    self.player_tiles[player_ind].fappend(self.hidden_piece)
                else:
                    self.player_tiles[player_ind].hand_to_deck() #======
                    self.update_hand('eat', player_ind, self.askpiece, action)
                self.gamephase = 'pick_one'
                self.actionsize = len(self.player_tiles[player_ind].hand)
                self.player_tiles[player_ind].eat_possibilities = []
                return player_ind

        else:
            raise IllegalMove(str(action)+','+str(color))

    def calculate_result(self, player=None):
        #return 0 if not ended
        if any([self.player_tiles[i].huhuhu for i in range(1,5)]):
            # ... calculate .........

            return scoress
        if self.hidden_piece <= 16:
            return [0,0,0,0]
        else:
            return 0

    def get_string_repr(self):
        ## canonicalForm, show information of current player in string format
        ## self.player_tiles[1] hand
        ## player_tiles 1,2,3,4 front deck, discardtile
        ## gamephase? askpiece

        '''
        show information starting from self.active_player
    
        '''
        self.sort_all()
        player_list = self.player_list[self.active_player:] + self.player_list[:self.active_player]
        player_list.remove(self.active_player)

        my_cards = self.player_tiles[self.active_player]

        ''.join(my_cards.hand) + ''.join(my_cards.frontdeck)


        self.frontdeck = []
        self.hand = []
        self.play_history = []
        self.eat_possibilities = []
        self.huhuhu = False


    def is_legal(self, action, player):
        return action < self.actionsize

    

class IllegalMove(Exception):
    pass

deck = [['a','a','a'],['b','b','b'], 'f','f']

strdeck = []
for item in deck:
    if type(item)==list:
        strdeck.append(''.join(item))
    else:
        strdeck.append(item)