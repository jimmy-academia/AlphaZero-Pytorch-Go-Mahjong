
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


    def __init__(self, opt):
        """Initialize the class; save the options in the class
        Parameters:
            opt (Option class)-- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        self.opt = opt

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


    def getInitState(self):
        """
        Returns:
            startBoard: a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
        raise NotImplementedError

    def getNextState(self, env, player, action):
        """
        Input:
            env: current board/environment
            player: current player (1 or -1)
            action: action taken by current player

        Returns:
            nextEnvironment: board/environment after applying action
            nextPlayer: player who plays in the next turn
        """
        raise NotImplementedError

    def getCanonicalForm(self, env, player):
        """
        Input:
            env: current board/environment
            player: current player (1 or -1)

        Returns:
            canonicalBoard: returns canonical form of board, which is what the current player sees, and should be independent of player. For e.g. in chess, the canonical form can be chosen to be the players pieces set to white (and his opponent black).
        """
        raise NotImplementedError

    def getSymmetricForm(self, cannonicalForm, action_p):
        """
        Input:
            cannonicalForm: current state in cannonicalForm
            action_p: policy vector

        Returns:
            symmForms: a list of [(cannonicalForm, action_p)] where each tuple is a symmetrical state of the cannonicalForm and the corresponding action_p vector. This is used when training the neural network from examples.
        """
        raise NotImplementedError

    def getGameEnded(self, env, player):
        """
        Input:
            env: current board/environment
            player: current player

        Returns:
            result: 0 if game has not ended.
                    list of value for each player if the game has ended
        """
        raise NotImplementedError
        
    def getPossibleActionSizes(self):
        """
        Returns:
            [actionSize]: list of numbers of all possible actions in different scenario
            for mahjong and other with different action size states
        """
        pass

    def getActionSize(self):
        """
        Returns:
            actionSize: number of all possible actions
        """
        pass


    def getValidMoves(self, board, player):
        """
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        pass




    def stringRepresentation(self, board):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        pass
