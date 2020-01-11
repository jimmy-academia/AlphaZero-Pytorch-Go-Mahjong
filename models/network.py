"""

LSTM (x): future work

IntuitiveMachine:
    nxn input to nxn output

    game_specs:
        in_channels
        block_nums
        sample_input
        action_size
    
"""
import torch

class IntuitiveMachine(torch.nn.Module):
    
    def __init__(self, game_specs):
        super(IntuitiveMachine, self).__init__()
        self.frontcourt = self.create_frontcourt(game_specs.in_channels)
        self.mainbuild = self.create_mainbuild(game_specs.block_nums)
        self.build_finalgarage(game_specs.sample_input, game_specs.action_size)

    def forward(self, x):
        x = self.frontcourt(x)
        x = self.mainbuild(x)
        x = self.backcourt(x)
        p, v = self.fc_p(x), self.fc_v(x)
        return p, v

    def create_frontcourt(self, in_channels):
        modules = [
            torch.nn.Conv2d(in_channels, 64, 5, 1, 2, bias=False),
            torch.nn.BatchNorm2d(64),
            torch.nn.ReLU(inplace=True),
            torch.nn.MaxPool2d(5,1,2)
        ]
        return torch.nn.Sequential(*modules)


    def create_mainbuild(self, block_nums, strides=None):
        if strides is None:
            strides = [1 for i in block_nums]
        modules = []
        for i in range(len(block_nums)):
            modules.append(self._make_layer(64*2**i, 64, block_nums[i], strides[i]))

        modules.append(torch.nn.AvgPool2d(2, stride=1))
        return torch.nn.Sequential(*modules)

    def build_finalgarage(self, sample, action_size):
        x = self.mainbuild(self.frontcourt(sample))
        x = x.view(x.size(0), -1)
        latent_dim = x.size(1)
        lin_layer = torch.nn.Linear(latent_dim, action_size)
        self.fc_p = lambda x: torch.nn.functional.log_softmax(lin_layer(x), dim=1)

        lin_layer = torch.nn.Linear(latent_dim, 1)
        self.fc_v = lambda x: torch.nn.functional.tanh(lin_layer(x))


    def _make_layer(self, in_channels, hid_channels, num_blocks, stride=1):
        modules = []
        modules.append(AlphaBlock(in_channels, hid_channels, stride))
        for __ in range(num_blocks - 2):
            modules.append(AlphaBlock(hid_channels, hid_channels, stride))
        modules.append(AlphaBlock(hid_channels, in_channels, stride))

        return torch.nn.Sequential(*modules)

class AlphaBlock(torch.nn.Module):
    def __init__(self, in_channels, hid_channels, stride):
        super(AlphaBlock, self).__init__()

        modules = [
            torch.nn.Conv2d(in_channels, hid_channels, 3, stride, 1, bias=False),
            torch.nn.BatchNorm2d(hid_channels)
            torch.nn.ReLU(inplace=True)
            torch.nn.Conv2d(hid_channels, hid_channels, 3, stride, 1, bias=False),
            torch.nn.BatchNorm2d(hid_channels)
        ]
        self.conv_modules = torch.nn.Sequential(*modules)
        self.relu = torch.nn.ReLU(inplace=True)

    def forward(self, x):
        residual = x
        out = self.conv_modules(x)
        out += residual
        out = self.relu(out)

        return out

