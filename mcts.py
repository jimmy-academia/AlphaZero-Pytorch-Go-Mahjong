class MonteTree():

    def __init__(self, opt, game, model):
        self.opt = opt
        self.game = game
        self.nnet = model

        ## s is state in string form, a is action
        self.Qsa = {} # Q value for s,a
        self.Nsa = {} # # of time s,a was visited
        self.Ns = {} # # of times s was visited
        self.Ps = {} # initial policy returned from neural net

        self.Es = {} # game.getGameEnded ?
        self.Vs = {}

    def getActionProb(self, canonicalForm, temp=1):
        """
        perform n_sims simulations of Monte Carlo Tree Search starting from CanonicalForm.
        Retruns:
            probs: a policy vector of probability of action proportional to Nsa[(s,a)]**(1./temp)
        """

        for i in range(self.opt.n_montesims):
            self.search(canonicalForm)

        s = self.game.stringRepresentation(canonicalForm)

    def search(self, canonicalForm):
        """
        performs one iteration of Monte Carlo Tree Search, and recursively calling itself untill a leaf node is found. The action chosen at each node is the one that has max upper confidence bound
        """

        