import torch
from .base_model import BaseModel
import numpy as np
from .network import AlphaNet

class ResNetModel(BaseModel):
    def __init__(self, opt, game):
        BaseModel.__init__(self, opt)
        self.nnet = create_model(opt, game)
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()

        self.optimizer = torch.optim.Adam(self.nnet.parameters())

    def modify_commandline_options(parser, is_train=True):
        """Add new model-specific options, and rewrite default values for existing options.
        Parameters:
            parser          -- original option parser
            is_train (bool) -- whether training phase or test phase. You can use this flag to add training-specific or test-specific options.
        Returns:
            the modified parser.
        """
        parser.add_argument('--pretrained', action='store_true', help='whether use pretrained model of resnet')
        return parser

    def loss_pi(self, targets, outputs):
        return -torch.sum(targets*outputs)/targets.size()[0]

    def loss_v(self, targets, outputs):
        return torch.sum((targets-outputs.view(-1))**2)/targets.size()[0]

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        self.nnet.train()

        for epoch in range(args.epochs):
            
            for __ in range(int(len(examples)/args.batch_size)):
                sample_ids = np.random.randint(len(examples), size=args.batch_size)
                boards, pis, vs = list(zip(*[examples[i] for i in sample_ids]))
                boards = torch.FloatTensor(np.array(boards).astype(np.float64))
                target_pis = torch.FloatTensor(np.array(pis))
                target_vs = torch.FloatTensor(np.array(vs).astype(np.float64))

                # predict
                # if args.cuda:
                    # boards, target_pis, target_vs = boards.contiguous().cuda(), target_pis.contiguous().cuda(), target_vs.contiguous().cuda()
                # boards, target_pis, target_vs = Variable(boards), Variable(target_pis), Variable(target_vs)

                out_pi, out_v = self.nnet(boards)

                l_pi = self.loss_pi(target_pis, out_pi)
                l_v = self.loss_v(target_vs, out_v)
                total_loss = l_pi + l_v

                self.optimizer.zero_grad()
                total_loss.backward()
                self.optimizer.step()

    def predict(self, board):
        """
        board: np array with board
        """
        # preparing input
        board = torch.FloatTensor(board.astype(np.float64))
        # if args.cuda: board = board.contiguous().cuda()
        # print(board)
        # board = Variable(board,requires_grad=False)
        board = board.view(1, self.board_x, self.board_y)

        self.nnet.eval()

        pi, v = self.nnet(board)

        return torch.exp(pi).data.cpu().numpy()[0], v.data.cpu().numpy()[0]


    def save_checkpoint(self, folder='R_checkpoint', filename='R_checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        torch.save({
            'state_dict' : self.nnet.state_dict(),
        }, filepath)

    def load_checkpoint(self, folder='R_checkpoint', filename='R_checkpoint.pth.tar'):
        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise BaseException("No model in path {}".format(filepath))
        checkpoint = torch.load(filepath)
        self.nnet.load_state_dict(checkpoint['state_dict'])


model_urls = {
    'resnet18': 'https://download.pytorch.org/models/resnet18-5c106cde.pth',
    'resnet34': 'https://download.pytorch.org/models/resnet34-333f7ec4.pth',
    'resnet50': 'https://download.pytorch.org/models/resnet50-19c8e357.pth',
    'resnet101': 'https://download.pytorch.org/models/resnet101-5d3b4d8f.pth',
    'resnet152': 'https://download.pytorch.org/models/resnet152-b121ed2d.pth',
}

def create_model(opt, game):
    n,n = game.getBoardSize()
    resn = 18 if n <= 11 else 34
    layers = [2, 2, 2, 2] if n<=11 else [3, 4, 6, 3]
    print("[LOG]:Input board size is {}*{}, using ResNet-{}.".format(n,n,resn))
    model = AlphaNet(opt, game, layers)

    if opt.pretrained:
        model.load_state_dict(torch.utils.model_zoo.load_url(model_urls['resnet'+str(resn)]))
    return model

