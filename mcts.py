class MonteTree():

    def __init__(self, opt, game, model):
        self.opt = opt
        self.game = game
        self.nnet = model

        ## s is state in string form, a is action
        self.Qsa = {} # Q value for s,a
        self.Nsa = {} # # of time s,a was visited
        self.Ns = {} # # of times s was visited
        self.Ps = {} # previous? policy returned from neural net

        self.Es = {} # game.getGameEnded ?
        self.Vs = {}

    @staticmethod
    def list_by_action(state_action_dict, state, actionsize):
        return [state_action_dict[(state, a)] if (state, a) in state_action_dict else 0 for a in range(actionsize)]

    def getActionProb(self, canonicalForm, temp=1):
        """
        perform n_montesims simulations of Monte Carlo Tree Search starting from CanonicalForm. Then choose return policy vector calculated by N, i.e. we choose the most traversed pass during the monte carlo sims from current state.
        During each node, player plays in first person view, thus canonicalForm.
        Returns:
            probs: a policy vector of probability of action proportional to Nsa[(s,a)]**(1./temp)
        """

        for i in range(self.opt.n_montesims):
            # traverse the state tree and expand 1 more node for multiple times
            self.search(canonicalForm)

        s = self.game.stringRepresentation(canonicalForm)

        N = self.list_by_action(self.Nsa, s, self.game.getActionSize())
        if temp != 0:
            N = [x**(1./temp) for x in N]
            Nsum = sum(N)
            N = [x/sum(N)-x if sum(N)-x > 0 else 0 for x in N]
            valids = self.game.getValidMoves(canonicalForm, player=1) #mask illegal moves
        else:
            # deterministic, temp==0
            argmaxN = N.index(max(N))
            N = [0 for x in N]
            N[argmaxN] = 1
            assert valid[argmaxN] > 0

        return N*valids


    def search(self, canonicalForm):
        """
        performs one iteration of Monte Carlo Tree Search, and recursively calling itself untill a leaf node is found. Expand on the leaf node. The action chosen at each node is the one that has max upper confidence bound
        During each node, player plays in first person view, thus canonicalForm.
        """

        endresult = self.game.getGameEnded(canonicalForm)
        if endresult !=0:
            return endresult

        s = self.game.stringRepresentation(canonicalForm)

        if s not in self.Ps:
            # is leaf node
            self.Ps[s], v = self.nnet.predict(canonicalForm.get_net_repr())

            valids = self.game.getValidMoves(canonicalForm)
            self.Ps[s] = self.Ps[s]*valids  ## mask invalid moves
            sum_Ps_s = 

            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s # normalize
            else:
                print("All valid moves were masked, no legal move.")

            self.Vs[s] = valids
            self.Ns[s] = 0
            return -v

        valids = self.Vs[s]
        currbest = -float('inf')
        best_act = -1
        
        for a in range(self.game.getActionSize(canonicalForm)):
            if valids[a] != 0:
                if (s,a) in self.Qsa and self.Qsa[(s,a)] != None:
                    u = self.Qsa[(s,a)] + self.opt.c_puct*self.Ps[s][a]*math.sqrt(self.Ns[s])/(1+self.Nsa[(s,a)])
                else:
                    u = self.opt.c_puct*self.Ps[s][a]*math.sqrt(self.Ns[s])

                if u > currbest:
                    currbest = u
                    best_act = a

        a = best_act
        assert(valids[a]!=0)

        next_s, next_player = self.game.getNextState(canonicalForm, 1, a)

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


?????