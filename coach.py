import random
from collections import deque

"""
Game, model independent class Coacher
    for training AlphaZero implementations on different games.
"""

class Coacher():

    def __init__(self, opt, game, model, montetree, advmodels):
        self.opt = opt
        self.game = game
        self.nnet = model
        self.advnets = advmodels
        self.mcts = montetree

        self.TrainExamples = deque([], maxlen=self.args.max_queue)

    def executeSelfPlay(self):
        env = self.game.getInitState()
        trianingItems = []
        self.currplayer = 1
        temperature = 1

        while True:
            temperature *= 0.99 
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
        return (x[0], x[2], results[x[1]])  ## results is a dict!!!
        # board, action, value

    def learn(self):
        for epoch in range(self.opt.n_epochs):
            episodeExample = deque([], maxlen=self.args.max_queue)
            for eps in range(self.opt.n_episodes):
                self.mcts.reset()
                episodeExample += self.executeSelfPlay()

            self.TrainExamples.append(episodeExample)

            is self.TrainExamples > self.opt.num_TrainExamples:
                self.TrainExamples.pop(0)

            epochExamples = []
            for ex in self.TrainExamples:
                epochExamples.extend(ex)
            random.shuffle(epochExamples)

            # temp save
            self.nnet.save_checkpoint()
            for pnet in self.advnets:
                pnet.load_checkpoint()

            #train
            self.nnet.train(epochExamples)

            #self play
            arena = Arena(self.nnet, self.advnets, self.game)
            arena.playGames()

            if arena.better():
                self.nnet.save_checkpoint('best')
            else:
                self.nnet.load_checkpoint()

                


