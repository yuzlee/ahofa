#!/usr/bin/env python3

import sys
import tempfile
import argparse
import multiprocessing

from nfa import Nfa
from reduction_eval import reduce_nfa, armc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r','--ratio', metavar='N', type=float,
        default=.2, help='reduction ratio')
    parser.add_argument('input', type=str, help='NFA to reduce')
    parser.add_argument('-n','--nw', type=int,
        default=multiprocessing.cpu_count() - 1,
        help='number of workers to run in parallel')
    parser.add_argument('--test', type=str, help='test pcap files')
    parser.add_argument('--train', type=str, help='train pcap file')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m','--merge', action='store_true',
        help='merging reduction')
    group.add_argument('-a','--armc', action='store_true',
        help='merging reduction ala abstract regular model checking')

    parser.add_argument('-th','--thresh', type=float,
        help='threshold for merging', default=.995)
    parser.add_argument('-mf','--maxfr', type=float, default=.1,
        help='max frequency of a state allowed to be merged')
    parser.add_argument('-o','--output', type=str,default='output.fa')
    args = parser.parse_args()

    if (args.merge or args.armc) and not args.train:
        raise SystemError('--train option is required when merging')

    aut = Nfa.parse(args.input)

    if args.armc:
        m = armc(aut, args.train, ratio=args.ratio, th=args.thresh,
            prune_empty=0)
        sys.stderr.write('Merged: ' + str(m) + '\n')
    else:
        sys.stderr.write('Reduction ratio: ' + str(args.ratio) + '\n')
        freq = aut.get_freq(args.train)
        aut, m = reduce_nfa(aut, freq, args.ratio, args.merge, args.thresh,
            args.maxfr)
        if args.merge:
            sys.stderr.write('Merged: ' + str(m) + '\n')

    with open(args.output,'w') as f:
        sys.stderr.write('Saved as ' + args.output + '\n')
        aut.print(f)

    if args.test:
        reduced = args.output
        r = Nfa.eval_accuracy(args.input, args.output, args.test, nw=args.nw)
        _,_,total, _, _, fp, tp = r.split(',')
        total, fp, tp = int(total), int(fp), int(tp)
        print('error:', round(fp/total,4))
        if tp + fp > 0:
            print('precision:', round(tp/(fp+tp),4))

if __name__ == '__main__':
    main()