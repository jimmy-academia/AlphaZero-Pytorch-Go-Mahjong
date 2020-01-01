import random

"""
class for training AlphaZero implementations on different game,
written to be game independent
"""

class Coacher():

    def __init__(self, game, model, montetree):
        self.game = game
        self.nnet = model
        self.mcts = montetree

    def executeSelfPlay(self):
        env = self.game.getInitState()
        trianingItems = []
        self.currplayer = 1

        while True:
            ## TODO some temp
            canonicalForm = self.game.getCanonicalForm(env, self.currplayer)
            action_p = self.mcts.getActionProb(canonicalForm)
            symmetricForms = self.game.getSymmetricForm(canonicalForm, action_p)
            for b, pi in symmetricForms:
                trianingItems.append([b, self.currplayer, pi, None])

            action = random.choice(population=list(range(len(action_p))), weight=action_p)
            env, self.currplayer = self.game.getNextState(env, self.currplayer, action)

            results = self.game.getGameEnded(env, self.currplayer)
            if results != 0:
                return [self.finalresult(x, results) for x in trianingItems]

    def finalresult(self, x, results):
        return (x[0], x[2], results[x[1]])


    def learn(self):
