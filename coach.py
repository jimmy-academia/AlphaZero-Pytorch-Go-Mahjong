import random

"""
Game, model independent class Coacher
    for training AlphaZero implementations on different games.
"""

class Coacher():

    def __init__(self, opt, game, model, montetree):
        self.opt = opt
        self.game = game
        self.nnet = model
        self.mcts = montetree

        self.TrainExamples = deque([], maxlen=self.args.max_queue)

    def executeSelfPlay(self):
        env = self.game.getInitState()
        trianingItems = []
        self.currplayer = 1

        while True:
            ## TODO some temperature
            canonicalForm = self.game.getCanonicalForm(env, self.currplayer)
            action_list, action_p = self.mcts.getActionProb(canonicalForm, temperature)
            symmetricForms = self.game.getSymmetricForm(canonicalForm, action_p)
            for b, pi in symmetricForms:
                trianingItems.append([b, self.currplayer, pi])

            action = random.choice(population=action_list, weight=action_p)
            env, self.currplayer = self.game.getNextState(env, self.currplayer, action)

            results = self.game.getGameResults(env, self.currplayer)
            if results != 0:
                return [self.finalresult(x, results) for x in trianingItems]

    def finalresult(self, x, results):
        return (x[0], x[2], results[x[1]])
        # board, action, value

    def learn(self):
        for epoch in range(self.opt.n_epochs):
            episodeExample = deque([], maxlen=self.args.max_queue)
            for eps in range(self.opt.n_episodes):
                self.mcts.reset()
                episodeExample += self.executeSelfPlay()

            self.TrainExamples.append(episodeExample)

            # save example

            # shuffle and flatten
            # train


