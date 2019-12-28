import torch
import itertools
from util.image_pool import ImagePool
from .base_model import BaseModel
from . import networks


class GoGame(BaseGame):
    """
    This class implements the Go game, for alphazero implementation
    """
    @staticmethod
    def modify_commandline_options(parser, is_train=True):
        return parser

    def __init__(self, opt):
        """Initialize the CycleGAN class.
        Parameters:
            opt (Option class)-- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseGame.__init__(self, opt)

    ### write game of go !!!@

    https://github.com/joelmichelson/alpha-zero-general-with-Go-game/blob/master/go/GoGame.py