# coding=utf-8
from __future__ import absolute_import

import torch
from torch import nn
from torch.autograd import Variable
import numpy as np


"""
To Implement the Triplet Loss in paper :
Generalization in Metric Learning: Should the Embedding Layer be the Embedding Layer?
https://arxiv.org/pdf/1803.03310.pdf
"""


class Triplet(nn.Module):
    def __init__(self, alpha=4):
        super(Triplet, self).__init__()
        self.alpha = alpha

    def forward(self, inputs, targets):
        n = inputs.size(0)
        inputs = self.alpha * normalize(inputs)
        # Compute pairwise distance
        dist_mat = euclidean_dist(inputs)
        targets = targets.cuda()
        # split the positive and negative pairs
        eyes_ = Variable(torch.eye(n, n)).cuda()
        # eyes_ = Variable(torch.eye(n, n))
        pos_mask = targets.expand(n, n).eq(targets.expand(n, n).t())
        neg_mask = eyes_.eq(eyes_) - pos_mask
        pos_mask = pos_mask - eyes_.eq(1)

        pos_dist = torch.masked_select(dist_mat, pos_mask)
        neg_dist = torch.masked_select(dist_mat, neg_mask)

        num_instances = len(pos_dist)//n + 1
        num_neg_instances = n - num_instances

        pos_dist = pos_dist.resize(len(pos_dist)//(num_instances-1), num_instances-1)
        neg_dist = neg_dist.resize(
            len(neg_dist) // num_neg_instances, num_neg_instances)

        loss = 0
        acc_num = 0
        num_valid_triplets = 0

        # 遍历Anchor, 每个样本都作为Anchor,来计算损失
        for i, pos_pair in enumerate(pos_dist):
            # pos_pair是以第i个样本为Anchor的所有正样本的距离
            pos_pair = pos_dist[i]
            # neg_pair是以第i个样本为Anchor的所有负样本的距离
            neg_pair = neg_dist[i]

            pos_pair = pos_pair.repeat(num_neg_instances, 1)
            neg_pair = neg_pair.repeat((num_instances-1), 1).t()

            triplet_mat = torch.log(torch.exp(pos_pair - neg_pair) + 1)
            triplet_mask = triplet_mat > 0.693
            valid_triplets = torch.masked_select(triplet_mat, triplet_mask)
            if len(valid_triplets) == 0:
                acc_num += 1
                continue

            num_valid_triplets += torch.sum(triplet_mask).item()
            loss += torch.mean(valid_triplets)

        # transverse all the valid triplets then average
        if num_valid_triplets == 0:
            loss = 0*torch.sum(pos_pair)
        else:
            loss = loss/num_valid_triplets

        accuracy = float(acc_num)/n
        neg_d = torch.mean(neg_dist).item()
        pos_d = torch.mean(pos_dist).item()

        return loss, accuracy, pos_d, neg_d


def euclidean_dist(inputs_):
    n = inputs_.size(0)
    dist = torch.pow(inputs_, 2).sum(dim=1, keepdim=True).expand(n, n)
    dist = dist + dist.t()
    dist.addmm_(1, -2, inputs_, inputs_.t())
    # for numerical stability
    # dist = dist.clamp(min=1e-12).sqrt()
    return dist


def normalize(x):
    norm = x.norm(dim=1, p=2, keepdim=True)
    x = x.div(norm.expand_as(x))
    return x


def main():
    data_size = 32
    input_dim = 3
    output_dim = 2
    num_class = 4
    # margin = 0.5
    x = Variable(torch.rand(data_size, input_dim), requires_grad=False)
    w = Variable(torch.rand(input_dim, output_dim), requires_grad=True)
    inputs = x.mm(w).cuda()
    y_ = 8*list(range(num_class))
    targets = Variable(torch.IntTensor(y_)).cuda()

    loss, accuracy, pos_d, neg_d = Triplet(alpha=3)(inputs, targets)
    loss.backward()

if __name__ == '__main__':
    main()
    print('Congratulations to you!')
