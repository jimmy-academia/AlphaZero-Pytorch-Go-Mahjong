
"""This module implements an abstract base class (ABC) 'BaseDataset' for datasets.
It also includes common transformation functions (e.g., get_transform, __scale_width), which can be later used in subclasses.
"""
import random
import numpy as np
import torch.utils.data as data
from PIL import Image
import torchvision.transforms as transforms
from abc import ABC, abstractmethod


class BaseGame(ABC):
    """This class is an abstract base class (ABC) for datasets.
    To create a subclass, you need to implement the following four functions:
    -- <__init__>:                      initialize the class, first call BaseDataset.__init__(self, opt).
    -- <__len__>:                       return the size of dataset.
    -- <__getitem__>:                   get a data point.
    -- <modify_commandline_options>:    (optionally) add dataset-specific options and set default options.
    """
    """
    This class specifies the base Game class. To define your own game, subclass
    this class and implement the functions below. This works when the game is
    two-player, adversarial and turn-based.

    Use 1 for player1 and -1 for player2.

    See othello/OthelloGame.py for an example implementation.
    """
    @staticmethod
    def modify_commandline_options(parser, is_train):
        """Add new dataset-specific options, and rewrite default values for existing options.
        Parameters:
            parser          -- original option parser
            is_train (bool) -- whether training phase or test phase. You can use this flag to add training-specific or test-specific options.
        Returns:
            the modified parser.
        """
        return parser

    def __init__(self, opt):
        """Initialize the class; save the options in the class
        Parameters:
            opt (Option class)-- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        self.opt = opt

    ## methods utilized in coach.py 

    def getInitState(self):
        """
        Returns:
            env: a class of the whole game environment that holds all values of all players
        """
        raise NotImplementedError

    def getNextState(self, env, player, action):
        """
        Input:
            env: current environment
            player: the acting player (int starting from 1)
            action: action taken by the acting player (int < len(action_p))

        Returns:
            nextEnvironment: environment after applying action
            nextPlayer: player who plays in the next turn
        """
        raise NotImplementedError

    def getCanonicalForm(self, env, player):
        """
        Input:
            env: current environment
            player: the acting player (int starting from 1)

        Returns:
            cannonicalForm: the canonical form of board, which is what the current player sees, and should be independent of player. For e.g. in chess, the canonical form can be chosen to be the players pieces set to white for both players.
            The cannonicalForm is used for neural nets to make first person decisions and to record states in string representations.
        """
        raise NotImplementedError

    def getSymmetricForm(self, cannonicalForm, action_p):
        """
        Input:
            cannonicalForm: current state in cannonicalForm
            action_p: policy vector of length action_size

        Returns:
            symmForms: a list of [(cannonicalForm.net_repr, action_p)] where each tuple is a symmetrical state of the cannonicalForm in net_repr (for input to neural network) and the corresponding action_p vector. This is used to augment training examples for the neural network.
        """
        raise NotImplementedError

    def getGameResults(self, env):
        """
        Input:
            env: current environment

        Returns:
            results: 0 if game has not ended.
                    dict of value for each player if the game has ended
        """
        raise NotImplementedError

    ## methods utilized in mcts.py 

    def getGameEnded(self, cannonicalForm, player):
        """
        Input:
            cannonicalForm: current environment in cannonicalForm

        Returns:
            result: 0 if game has not ended.
                    the value for current player if the game has ended
        """
        raise NotImplementedError

    def stringRepresentation(self, cannonicalForm):
        """
        Input:
            cannonicalForm: current environment in cannonicalForm

        Returns:
            boardString: a quick record of current environment in string format. Required by MCTS for hashing.
        """
        raise NotImplementedError

    def getValidMoves(self, cannonicalForm):
        """
        Input:
            cannonicalForm: current environment in cannonicalForm

        Returns:
            validMoves: a vector in same size as cannonicalForm.net_repr with 1 and 0 as elements, used as a mask to clear out illegal moves
        """
        raise NotImplementedError
        
    def getActionSize(self, cannonicalForm):
        """
        Input:
            cannonicalForm: current environment in cannonicalForm

        Returns:
            actionSize: int, number of all possible actions
        """
        raise NotImplementedError

    ## methods for neural net creation


    # def getPossibleActionSizes(self):
    #     """
    #     Returns:
    #         [actionSize]: list of numbers of all possible actions in different scenario
    #         for mahjong and other with different action size states
    #     """
    #     pass

    
    

