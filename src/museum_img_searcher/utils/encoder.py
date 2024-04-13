import torch
from torch import nn, cosine_similarity
import torch.nn.functional as F


class ImageEncoder(nn.Module):
    def init(self):
        super(ImageEncoder, self).init()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.relu1 = nn.ReLU(inplace=True)
        self.pulling = nn.AdaptiveAvgPool2d(4)

        self.conv2 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1)
        self.relu2 = nn.ReLU(inplace=True)
        self.linear = nn.Linear(2048, 128)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pulling(x)
        x = F.relu(self.conv2(x))
        x = torch.flatten(x, start_dim=1)
        #print(x.shape)
        x = self.linear(x)
        return x


class ContrastiveLoss(nn.Module):
    def init(self, margin=2.0):
        super(ContrastiveLoss, self).init()
        self.margin = margin

    def forward(self, output1, output2, target):
        cosine_distance = cosine_similarity(output1, output2)

        loss_contrastive = torch.mean((1 - target) * torch.pow(cosine_distance, 2) +
                                      (target) * torch.pow(torch.clamp(self.margin - cosine_distance, min=0.0), 2))
        return loss_contrastive
