"""General-purpose training script of AlphaZero for different games
This script works for various games (with option '--game': e.g., go, mahjong) and
different networks (with option '--model': e.g., resnet, vgg).
You need to specify the experiment name ('--name'), and game ('--game').

<todo>
It first creates model, dataset, and visualizer given the option.
It then does standard network training. During the training, it also visualize/save the images, print/save the loss plot, and save models.
The script supports continue/resume training. Use '--continue_train' to resume your previous training.
Example:
    Train a model for the game of Go:
        python train.py --name alphazero_go
    or
        python train.py --name alphazero_go --game go --model resnet

See options/base_options.py and options/train_options.py for more training options.
"""

from options.train_options import TrainOptions
from games import create_game
from models import create_model
from mcts import MonteTree
from coach import Coacher

if __name__ == '__main__':
    opt = TrainOptions().parse()   # get training options
    game = create_game(opt)
    model = create_model(opt, game)      
    montetree = MonteTree(opt, game, model)
    coacher = Coacher(opt, game, model, montetree)
    coacher.learn()

