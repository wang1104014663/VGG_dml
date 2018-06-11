from __future__ import absolute_importimport torchfrom torch import nnfrom torch.autograd import Variableimport numpy as npfrom utils import normalize"""HDC methodHard-Aware Deeply Cascaded Embedding"""def similarity(inputs_):    # Compute similarity mat of deep feature    # n = inputs_.size(0)    sim = torch.matmul(inputs_, inputs_.t())    return simclass HDCLoss(nn.Module):    def __init__(self, margin=0.5):        super(HDCLoss, self).__init__()        self.margin = margin        # self.alpha = alpha    def forward(self, inputs, targets):        n = inputs.size(0)        targets = targets.cuda()        # split the positive and negative pairs        eyes_ = Variable(torch.eye(n, n)).cuda()        # eyes_ = Variable(torch.eye(n, n))        pos_mask = targets.expand(n, n).eq(targets.expand(n, n).t())        neg_mask = eyes_.eq(eyes_) - pos_mask        pos_mask = pos_mask - eyes_.eq(1)        # split inputs        inputs = [inputs[:, :128], inputs[:, 128:256], inputs[:, 256:]]        # print('shape is : ', [i.shape for i in inputs])        # Compute similarity matrix        sim_mats = [similarity(f_) for f_ in inputs]        pos_sims = [torch.masked_select(sim_mat, pos_mask) for sim_mat in sim_mats]        neg_sims = [torch.masked_select(sim_mat, neg_mask) for sim_mat in sim_mats]        prec = 0        neg_d = torch.mean(neg_sims[0]).item()        pos_d = torch.mean(pos_sims[0]).item()        # Hard aware process        ratio = [0.9, 0.6, 0.3]        loss = 0        k = np.random.randint(64)        for i in range(3):            pos_sim, neg_sim = pos_sims[i], neg_sims[i]            pos_sim, pos_idx = pos_sim.sort()            neg_sim, neg_idx = neg_sim.sort()            if k == 1:                print("Model-{0} \t P {1} \t Q {2}".format(                    i, torch.mean(pos_sim).item(), torch.mean(neg_sim).item()))            pos_sim = torch.masked_select\                (pos_sim, pos_sim < torch.clamp(neg_sim[-1]+0.05, min=0.99))            pos_sim = pos_sim[:int(ratio[i]*len(pos_sim))]            if k == 1:                print('Model-{0} \t number of Selected Positive pair is \t {1}'.format(i, len(pos_sim)))            if len(pos_sim) > 0:                loss += 0.9 - torch.mean(pos_sim)            neg_sim = torch.masked_select(neg_sim, neg_sim > pos_sim[0] - 0.1)            neg_sim = torch.masked_select(neg_sim, neg_sim > self.margin)            neg_sim = neg_sim[-int(ratio[i] * len(neg_sim)):]            if k == 1:                print('Model-{0} \t number of Selected Negative pair is \t {1}'.format(i, len(neg_sim)))            if len(neg_sim) > 0:                loss += torch.mean(neg_sim) - self.margin        print('\n')        return loss, prec, pos_d, neg_ddef main():    data_size = 32    input_dim = 3    output_dim = 2    num_class = 4    # margin = 0.5    x = Variable(torch.rand(data_size, input_dim), requires_grad=False)    w = Variable(torch.rand(input_dim, output_dim), requires_grad=True)    inputs = x.mm(w).cuda()    y_ = 8*list(range(num_class))    targets = Variable(torch.IntTensor(y_)).cuda()    print(HDCLoss()(inputs, targets))if __name__ == '__main__':    main()    print('Congratulations to you!')