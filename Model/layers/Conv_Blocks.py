import torch
import torch.nn as nn

class Inception_Block_V1(nn.Module):
    def __init__(self, in_channels, out_channels, num_kernels=6, init_weight=True):
        super(Inception_Block_V1, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.num_kernels = num_kernels
        kernels = []
        for i in range(self.num_kernels):
            kernels.append(nn.Conv2d(in_channels, out_channels, kernel_size=2 * i + 1, padding=i))
        self.kernels = nn.ModuleList(kernels)
        if init_weight:
            self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        # [1, 128, 1, 96]
        res_list = []
        """
        ModuleList(
          (0): Conv2d(128, 2048, kernel_size=(1, 1), stride=(1, 1))
          (1): Conv2d(128, 2048, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
          (2): Conv2d(128, 2048, kernel_size=(5, 5), stride=(1, 1), padding=(2, 2))
          (3): Conv2d(128, 2048, kernel_size=(7, 7), stride=(1, 1), padding=(3, 3))
          (4): Conv2d(128, 2048, kernel_size=(9, 9), stride=(1, 1), padding=(4, 4))
          (5): Conv2d(128, 2048, kernel_size=(11, 11), stride=(1, 1), padding=(5, 5))
        )
        """
        # [1, out_channels=2048, 1, 96]
        for i in range(self.num_kernels):
            res_list.append(self.kernels[i](x))
        # [1, 128, 1, 96, num_kernels=6] -> [1, 128, 1, 96]
        res = torch.stack(res_list, dim=-1).mean(-1)
        return res


class Inception_Block_V2(nn.Module):
    def __init__(self, in_channels, out_channels, num_kernels=6, init_weight=True):
        super(Inception_Block_V2, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.num_kernels = num_kernels
        kernels = []
        for i in range(self.num_kernels // 2):
            kernels.append(nn.Conv2d(in_channels, out_channels, kernel_size=[1, 2 * i + 3], padding=[0, i + 1]))
            kernels.append(nn.Conv2d(in_channels, out_channels, kernel_size=[2 * i + 3, 1], padding=[i + 1, 0]))
        kernels.append(nn.Conv2d(in_channels, out_channels, kernel_size=1))
        self.kernels = nn.ModuleList(kernels)
        if init_weight:
            self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        res_list = []
        for i in range(self.num_kernels + 1):
            res_list.append(self.kernels[i](x))
        res = torch.stack(res_list, dim=-1).mean(-1)
        return res
