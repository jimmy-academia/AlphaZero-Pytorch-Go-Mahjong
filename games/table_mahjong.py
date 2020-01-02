"""
THE Mahjong Table

'''
        Todo:
            1. execute_move
                has not considered hidden gong
                has not implemented Hu
                may have cleaner way to set actionsize (instead of setting self.actionsize = x in every incident)
                may have cleaner way to write Player_Tiles

            2. cannonicalForm and stringRerpresentation:
                currently cannonicalForm is only set by setting self.active_player = player_id

            3. calculate_result()
                try to return 0 without too many calculations if game not ended
                have not considered how to calculate tai

            4. get_string_repr()
                the monte carlo tree search use this form to record states
                the state is the information a player has,
                i.e. (hand, play_history x 4, front_deck x 4), 
                in (consise) string format

            5. get_net_repr():
                the neural net always inputs this form
                we want 12x12x9, [(the full deck) x (hand, play_history x 4, front_deck x 4)]


                The Full Deck is
                c1 c2 c3 c4 c5 c6 ....  c9 dr dg dw    
                c1 ...                     dr dg dw
                c1 ...                         ...
                c1 ...                         ...
                b1 b2 b3 b4 ...         b9 we ww fg
                b1 ...                      ..   fm
                b1 ...                      ..   fa
                b1 ...                      ..   fw
                m1                      m9 ws wn fp
                .                           ..   fo
                .                           ..   fb
                .                           ..   fc

                or some other way to arrange all tiles into 12x12 sqaure

                for hand: set 1 and 0 for have and havenot
                always set in same order, so e.g. having 1 c1 always shows 1 in top left corner but not other c1 locations.

                for history, we want to set the number to the range 1~0
                1 for haven't played, and the more recent a piece is played, the closer to zero
                always set in same order, so the 4 locations of c1 will have a decresing numeric value from top to bottom

                for front deck, can set 0 as not in front deck, 0.5 as in a eat triplet and 1 as in pong or gong or flower

            ['c'+str(x) for x in list(range(1,10))]*4 \
            + ['b'+str(x) for x in list(range(1,10))]*4 \
            + ['m'+str(x) for x in list(range(1,10))]*4 \
            + ['d'+x for x in ['r', 'g', 'w']]*4 \
            + ['w'+x for x in ['e', 'w', 's', 'n']]*4 \
            + ['f'+x for x in ['g', 'm', 'a', 'w']] \
            + ['f'+x for x in ['p', 'o', 'b', 'c']] \

        future work: 
            other variants, including (Japan, Hong Kong)

        miscellaneous:
            gong_pong action has pong 1, gong 2 because action can be 0,1 for only pong and 0,1,2 for gong. name has 'gong' in front in order to short hand to initial letter 'g'.
            self draw is not an action. The Hu from self draw will be picked up outside execute_move
        '''

"""
import random

class Table():
    def __init__(self, variant):
        
        print('You are playing mahjong variant: ', variant) 

        self.hidden_piece = FULL_DECK
        random.shuffle(self.hidden_piece)

        self.player_list = range(1,5) #1,2,3,4
        self.player_tiles = {player_id: Player_Tiles() for player_id in self.player_list}
        self.deal_cards()
        
        self.gamephase = 'pick_one' # one of 'pick_one', 'gong_pong', 'eat_pass'
        self.askpiece = None
        self.actionsize = 0
        self.active_player = 1 ## for canonicalForm -> string representation

    def deal_cards(self):
        '''
        Can try to deal cards according to Taiwan tradition when playing Mahjong in physical form.
        '''
        for player_id in self.player_list:
            self.player_tiles[player_id].hand = self.hidden_piece[:13]
            self.hidden_piece = self.hidden_piece[13:]
        self.player_tiles[1].hand.append(self.hidden_piece.pop(0))

        for player_id in self.player_list:
            for tile in self.player_tiles[player_id].hand:
                if 'f' in tile:
                    self.player_tiles[player_id].hand_to_deck(tile)
                    self.player_tiles[player_id].hand.fappend(self.hidden_piece)
        
        self.actionsize = len(self.player_tiles[1].hand)


    def execute_move(self, player_id, action):
        if self.is_legal(player_id, action):
            self.prepare()
            if self.gamephase == 'pick_one':
                return self.do_pick_one(player_id, action)
            elif self.gamephase == 'gong_pong':
                return self.do_gong_or_pong(player_id, action)
            elif self.gamephase == 'eat_pass':
                return self.do_eat_or_pass(player_id, action)

    def is_legal(self, player_id, action):
        if action < self.actionsize:
            return True
        else:
            raise IllegalMove(str(action)+','+str(player_id))

    ## the following actions modifies self variables and returns the player_id of next player

    def do_pick_one(player_id, action):
        ## pick the card to play from hand according to action
        self.askpiece = self.player_tiles[player_id].play_card(action)

        ## start evaluating the consequence of playing the card
        # Hu case (drop gun)
        
        '''        
        <pseudo code>
        if any(hashu):
            # will be picked up by game.getGameEnded calling self.calculated_result()
            return player_id
        '''
        self.nextplayer = player_id%4+1
        
        ## gong/pong case
        check2list = [1,2,3,4].remove(player_id)
        has2piece = [self.player_tiles[i].hand.count(self.askpiece) >= 2 for i in check2list]
        if any(has2piece):
            self.gamephase = 'gong_pong'
            askplayer = check2list[has2piece.index(True)] ## there will be only 1
            self.actionsize = self.player_tiles[askplayer].hand.count(self.askpiece)
            return askplayer
        else:
            return self._scan_for_eat()

    def _scan_for_eat(self):
        if self.player_tiles[self.nextplayer].can_eat(self.askpiece):
            self.gamephase = 'eat_pass'
            self.actionsize = len(self.player_tiles[self.nextplayer].eat_possibilities) + 1
        else:
            self.player_tiles[self.nextplayer].fappend(self.hidden_piece)
            self.actionsize = len(self.player_tiles[self.nextplayer].hand)
            self.gamephase = 'pick_one'
        return self.nextplayer

    def do_pong_or_gong(player_id, action):
        ## pass or pong or (gong)
        if not action:  ## i.e. action==0, pass
            return self._scan_for_eat()
        else:
            if action==1: #pong
                self.player_tiles[player_id].hand_to_deck([self.askpiece]*3)
            else:          #gong
                self.player_tiles[player_id].hand_to_deck([self.askpiece]*4)
                self.player_tiles[player_id].fappend(self.hidden_piece)

            self.gamephase = 'pick_one'
            self.actionsize = len(self.player_tiles[player_id].hand)
            return player_id




######################################################################################




    def sort_hand(self, player_id):
        mahjong_sorted(self.player_tiles[player_id].hand)
    def sort_all(self):
        for player_id in self.player_list:
            self.sort_hand(player_id)



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


class Player_Tiles:
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


    

class IllegalMove(Exception):
    pass

deck = [['a','a','a'],['b','b','b'], 'f','f']

strdeck = []
for item in deck:
    if type(item)==list:
        strdeck.append(''.join(item))
    else:
        strdeck.append(item)