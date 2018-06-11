from __future__ import print_function, absolute_import


def display(args):
    args = (vars(args))

    #  Display information of current training

    print('Learn Rate  \t%.1e' % args['lr'])
    print('Epochs  \t%05d' % args['epochs'])
    print('Log Path \t%s' % args['log_dir'])
    print('Network \t %s' % args['net'])
    print('Data Set \t %s' % args['data'])
    print('Batch Size  \t %d' % args['BatchSize'])
    print('Num-Instance  \t %d' % args['num_instances'])
    print('Embedded Dimension \t %d' % args['dim'])

    print('Loss Function \t%s' % args['loss'])
    # print('Number of Neighbour \t%d' % args.k)
    print('Alpha \t %d' % args['alpha'])

    for key, value in args.items():
        if key in ['beta', 'margin', 'save_step']:
            print("{0} \t {1}".format(key, value))

    print('Begin to fine tune VGG16-BN Network')
    print(40*'#')
