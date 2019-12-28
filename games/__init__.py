"""This package includes all the modules related to data loading and preprocessing
 To add a custom dataset class called 'dummy', you need to add a file called 'dummy_dataset.py' and define a subclass 'DummyDataset' inherited from BaseDataset.
 You need to implement four functions:
    -- <__init__>:                      initialize the class, first call BaseDataset.__init__(self, opt).
    -- <__len__>:                       return the size of dataset.
    -- <__getitem__>:                   get a data point from data loader.
    -- <modify_commandline_options>:    (optionally) add dataset-specific options and set default options.
Now you can use the dataset class by specifying flag '--dataset_mode dummy'.
See our template dataset class 'template_dataset.py' for more details.
"""
import importlib
from games.base_game import BaseGame


def find_game_using_name(game_name):
    """Import the module "games/[game_name]_game.py".
    In the file, the class called [GameName]Game() will
    be instantiated. It has to be a subclass of BaseGame,
    and it is case-insensitive.
    """
    game_filename = "games." + game_name + "_game"
    gamelib = importlib.import_module(game_filename)

    game = None
    target_game_name = game_name.replace('_', '') + 'game'
    for name, cls in gamelib.__dict__.items():
        if name.lower() == target_game_name.lower() \
           and issubclass(cls, BaseGame):
            game = cls

    if game is None:
        raise NotImplementedError("In %s.py, there should be a subclass of BaseGAME with class name that matches %s in lowercase." % (game_filename, target_game_name))

    return game


def get_option_setter(dataset_name):
    """Return the static method <modify_commandline_options> of the dataset class."""
    # dataset_class = find_dataset_using_name(dataset_name)
    # return dataset_class.modify_commandline_options
    pass


def create_game(opt):
    """Create a game given the option.
        This is the main interface between this package and 'train.py'/'test.py'
    Example:
        >>> from games import create_game
        >>> game = create_game(opt)
    """
    game = find_game_using_name(opt.game)
    instance = game(opt)
    print("game of [%s] was set" % type(instance).__name__)
    return instance

