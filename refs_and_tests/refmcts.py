import math
import numpy as np
import time

    
class MCTS():
    """
    This class handles the MCTS tree.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.Qsa = {}       # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}       # stores #times edge s,a was visited
        self.Ns = {}        # stores #times board s was visited
        self.Ps = {}        # stores initial policy (returned by neural net)
        self.smartSimNum=10*(self.game.getBoardSize()[0]**2)
        self.Es = {}        # stores game.getGameEnded ended for board s
        self.Vs = {}        # stores game.getValidMoves for board s

    def getActionProb(self, canonicalBoard, temp=1):
        """
        This function performs n_mctssims simulations of MCTS starting from
        canonicalBoard.
        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """

        # display(canonicalBoard)
        
        #print('current sim numbers:{}'.format(max(self.args.n_mctssims,self.smartSimNum)))
        for i in range(max(self.args.n_mctssims,self.smartSimNum)):

            self.search(canonicalBoard)

        s = self.game.stringRepresentation(canonicalBoard)

        counts = np.array([self.Nsa[(s,a)] if (s,a) in self.Nsa else 0 for a in range(self.game.getActionSize())])
        valids=self.game.getValidMoves(canonicalBoard,player=1)
        self.smartSimNum=10*(np.count_nonzero(valids))

        if np.sum(counts)==0:
            counts=valids
        else:
            counts*=valids


        if temp==0:
            bestA = np.argmax(counts)

            try:
                assert(valids[bestA]!=0)
            except:
                print("temp=0, assert valids[bestA]!=0 !!!")
                print("current valids:",valids)
                flag_Qsa=False
                flag_Nsa=False
                if s in self.Ps:
                    print("s in p! Which measn it's been visited, has the probability of each action",self.Ps[s])
                for _ in range(self.game.getActionSize()):
                    if (s,_) in self.Nsa:
                        print(_,"in Nsa! which measn its value is calculated to ",self.Nsa[(s,_)])
                    else:
                        flag_Nsa=True
                        print(_,"no Nsa value, set 0 by default in counts=[...]!")

                    if (s,_) in self.Qsa:
                        print(_,"in! Qsa with value:",self.Qsa[(s,_)])
                    else:
                        flag_Qsa=True
                        print(_,"no Qsa value")

                    if flag_Nsa and flag_Qsa:
                        print("no nsa, no qsa")
                    if flag_Nsa and not flag_Qsa:
                        print("no nsa, has qsa")
                    if not flag_Nsa and flag_Qsa:
                        print("has nsa, no qsa")
                print(counts)

            probs = [0 for i in range(len(counts))]
            probs[bestA]=1

            for _ in range(self.game.getActionSize()):
                if probs[_]>0:
                    assert(valids[_]>0)

            return probs

        counts = [x**(1./temp) for x in counts]
        probs = [x/float(sum(counts)) for x in counts]

        for _ in range(self.game.getActionSize()):
            if probs[_]>0:
                assert(valids[_]>0)

        return probs*valids


    def search(self, canonicalBoard):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.
        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propogated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propogated up the search path. The values of Ns, Nsa, Qsa are
        updated.
        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.
        Returns:
            v: the negative of the value of the current canonicalBoard
        """
        # print("doing mcts on board:")
        # display(canonicalBoard)


        gameEnd=self.game.getGameEnded(canonicalBoard, 1)
        if gameEnd!=0:
            return -gameEnd
        s = self.game.stringRepresentation(canonicalBoard)

        if s not in self.Ps:
            # print("leaf node")
            self.Ps[s], v = self.nnet.predict(canonicalBoard.pieces)

            valids = self.game.getValidMoves(canonicalBoard, 1)
            self.Ps[s] = self.Ps[s]*valids      # masking invalid moves
            sum_Ps_s = np.sum(self.Ps[s])
            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s    # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable

                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                print("All valid moves were masked, do workaround.")
                self.Ps[s] = self.Ps[s] + valids
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valids
            self.Ns[s] = 0
            return -v

        valids = self.Vs[s]
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(self.game.getActionSize()):
            if valids[a]!=0:
                if (s,a) in self.Qsa and self.Qsa[(s,a)]!=None:
                    u = self.Qsa[(s,a)] + self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])/(1+self.Nsa[(s,a)])
                else:
                    u = self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])     # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act
        assert(valids[a]!=0)
        # print("in MCTS.search, need next search, shifting player from 1")

        try:
            next_s, next_player = self.game.getNextState(canonicalBoard, 1, a)

            # print("in MCTS.search, need next search, next player is {}".format(next_player))
        except:
            # print("###############在search内部节点出现错误：###########")
            #display(canonicalBoard)
            # print("action:{},valids:{},Vs:{}".format(a,valids,self.Vs[s]))
            valids=self.game.getValidMoves(canonicalBoard,1)
            self.Vs[s]=valids
            cur_best = -float('inf')
            best_act = -1

            # pick the action with the highest upper confidence bound
            for a in range(self.game.getActionSize()):
                if valids[a]!=0:
                    if (s,a) in self.Qsa and self.Qsa[(s,a)]!=None:
                        u = self.Qsa[(s,a)] + self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])/(1+self.Nsa[(s,a)])
                    else:
                        u = self.args.cpuct*self.Ps[s][a]*math.sqrt(self.Ns[s])     # Q = 0 ?

                    if u > cur_best:
                        cur_best = u
                        best_act = a

            a = best_act
            # print("recalculate the valids vector:{} ".format(valids))
            try:
                next_s, next_player = self.game.getNextState(canonicalBoard, 1, a)
            except:
                return

        next_s = self.game.getCanonicalForm(next_s, next_player)

        v = self.search(next_s)

        if (s,a) in self.Qsa:
            assert(valids[a]!=0)
            self.Qsa[(s,a)] = (self.Nsa[(s,a)]*self.Qsa[(s,a)] + v)/(self.Nsa[(s,a)]+1)
            self.Nsa[(s,a)] += 1

        else:
            self.Qsa[(s,a)] = v
            self.Nsa[(s,a)] = 1

        self.Ns[s] += 1

        return -v
