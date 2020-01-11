import numpy as np
import torch.utils.model_zoo as model_zoo
import torch
import torchvision as tv
import torch.nn as nn
#from torch.nn.functional import Variable
from scipy import misc
import math
import torch.nn.functional as F

from torchvision.models.resnet import ResNet


class AlphaNet(ResNet):
    def __init__(self, args, game, layers):
        block=AlphaBlock
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args
        outputShift=1 if self.board_x in [6,7,11] else 4
        self.inplanes = 64

        super(ResNet, self).__init__()

        self.conv1 = nn.Conv2d(1, 64, kernel_size=5, stride=1, padding=2,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=5, stride=1, padding=2)

        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        
        self.avgpool = nn.AvgPool2d(2, stride=1)
        self.fc_p= nn.Linear(512 * block.expansion*outputShift,self.action_size)
        self.fc_v=nn.Linear(512* block.expansion*outputShift,1)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)


    def forward(self, x):
        # print("input x shape:{}".format(x.shape))
        x= x.view(-1, 1, self.board_x, self.board_y)
        # x=x.view(1,*x.shape)

        # print("view output:{}".format(x.shape))

        x = self.conv1(x)
        # print("conv1 output:{}".format(x.shape))
        x = self.bn1(x)
        # print("bn1 output:{}".format(x.shape))
        x = self.relu(x)
        # print("relu output:{}".format(x.shape))
        x = self.maxpool(x)
        # print("maxpool output:{}".format(x.shape))

        x = self.layer1(x)
        # print("layer1 output:{}".format(x.shape))
        x = self.layer2(x)
        # print("layer2 output:{}".format(x.shape))
        x = self.layer3(x)
        # print("layer3 output:{}".format(x.shape))
        x = self.layer4(x)
        # print("layer4 output:{}".format(x.shape))

        try:
            x = self.avgpool(x)
        except:
            pass
        # print("avgpool output:{}".format(x.shape))
        x = x.view(x.size(0), -1)
        p = self.fc_p(x)
        # print("p output:{}".format(p.shape))
        v = self.fc_v(x)
        # print("v output:{}".format(p.shape))
        return F.log_softmax(p,dim=1),F.tanh(v)


def conv3x3(in_planes, out_planes, stride=1):
    "3x3 convolution with padding"
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)



class AlphaBottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(AlphaBottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride,
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out




class AlphaBlock(nn.Module):
    expansion = 1
    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(AlphaBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out

