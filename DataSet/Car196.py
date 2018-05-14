from __future__ import absolute_import, print_function
import os
from DataSet import transforms
import torchvision.datasets as datasets


class Car196:
    def __init__(self, root, train=True, test=True, transform=None):
        # Data loading code
        std_value = 1.0 / 255.0
        mean_values = [104 / 255.0, 117 / 255.0, 128 / 255.0]

        if transform is None:
            transform = [transforms.Compose([
                transforms.CovertBGR(),
                transforms.Resize(256),
                transforms.RandomResizedCrop(size=227, scale=(0.16, 1.4)),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(mean=mean_values,
                                     std=3 * [std_value]),
            ]),
                transforms.Compose([
                    transforms.CovertBGR(),
                    transforms.Resize(256),
                    transforms.CenterCrop(227),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=mean_values,
                                         std=3 * [std_value]),
                ])]

        if root is None:
            root = '/opt/intern/users/xunwang/DataSet/Car196'
        traindir = os.path.join(root, 'train')
        testdir = os.path.join(root, 'test')

        if train:
            self.train = datasets.ImageFolder(traindir, transform[0])
        if test:
            self.test = datasets.ImageFolder(testdir, transform[1])

