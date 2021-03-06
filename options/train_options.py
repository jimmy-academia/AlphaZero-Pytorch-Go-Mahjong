from .base_options import BaseOptions


class TrainOptions(BaseOptions):
    """This class includes training options.
    It also includes shared options defined in BaseOptions.
    """

    def initialize(self, parser):
        parser = BaseOptions.initialize(self, parser)
        parser.add_argument('--print_freq', type=int, default=100, help='frequency of showing training results on console')
        # network saving and loading parameters
        parser.add_argument('--save_latest_freq', type=int, default=5000, help='frequency of saving the latest results')
        parser.add_argument('--save_epoch_freq', type=int, default=50, help='frequency of saving checkpoints at the end of epochs')
        parser.add_argument('--save_by_iter', action='store_true', help='whether saves model by iteration')
        parser.add_argument('--continue_train', action='store_true', help='continue training: load the latest model')
        parser.add_argument('--epoch_count', type=int, default=1, help='the starting epoch count, we save the model by <epoch_count>, <epoch_count>+<save_latest_freq>, ...')
        parser.add_argument('--phase', type=str, default='train', help='train, val, test, etc')
        # training parameters
        parser.add_argument('--n_epochs', type=int, default=1000, help='number of epochs with the initial learning rate')
        parser.add_argument('--n_episodes', type=int, default=100, help='number of epochs with the initial learning rate')
        parser.add_argument('--n_trainexamples', type=int, default=25, help='number of epochs with the initial learning rate')
        parser.add_argument('--max_queue', type=int, default=200000)
        parser.add_argument('--temp_thresh', type=int, default=15)

        parser.add_argument('--n_montesims', type=int, default=200)
        parser.add_argument('--n_montesims_alt', type=int, default=0)
        parser.add_argument('--arenaCompare', type=int, default=50)
        parser.add_argument('--cpuct', type=int, default=3)

        parser.add_argument('--beta1', type=float, default=0.5, help='momentum term of adam')
        parser.add_argument('--lr', type=float, default=0.0002, help='initial learning rate for adam')

        self.isTrain = True
        return parser
