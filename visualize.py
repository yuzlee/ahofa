#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import re
import os

def main():
    error = 'experiments/error.csv'
    reduction = 'experiments/reduction.csv'

    df1 = pd.read_csv(error).drop_duplicates()
    dfe = df1.groupby('reduced').sum()

    dfe['ce'] = (dfe['fp_c'] / dfe['total'])
    dfe['ppr'] = (dfe['pp_c'] / (dfe['pp_c'] + dfe['fp_c']))
    dfe = dfe[['ce', 'ppr']]

    df2 = pd.read_csv(reduction, index_col='reduced').drop_duplicates()
    dfr = df2[['ratio','iter']]
    comb = pd.concat([dfr, dfe],axis=1, join='inner')
    comb = comb.reset_index()
    comb['reduced'] = comb['reduced'].apply(lambda x: re.sub('\..*$','',x))
    comb = comb.set_index(['reduced','ratio','iter'])

    # plot backdoor
    bd = comb.unstack(level=[0,2])
    plt.style.use('ggplot')
    
    ax = bd['ce','backdoor'].plot(title='backdoor.rules ppr',marker='o')
    ax.set_ylabel('classification error')
    ax.get_figure().savefig('backdoor-ce.png')
    #plt.show()

    ax = bd['ppr','backdoor'].plot(title='backdoor.rules ppr',marker='o')
    ax.set_ylabel('positive positive rate')
    ax.get_figure().savefig('backdoor-ppr.png')
    #plt.show()

    # plot sprobe
    comb = comb.loc[(['sprobe'], slice(None), [0])]
    comb = comb.unstack(level=[0,2])
    comb.columns = ['ce','ppr']

    ax = comb.plot(title='sprobe pruning',marker='o')
    #plt.show()
    ax.get_figure().savefig('sprobe-pruning.png')
    print(comb)


def pcap_analysis(fname='mc.txt'):
    # read with mixed data type, numpy stores result in 1d structured array
    data = np.log10(np.loadtxt(open(fname,'r'), delimiter=' '))
    close(filename)
    plt.imshow(data, cmap='jet', interpolation='nearest')
    plt.colorbar()
    plt.show()

if __name__ == "__main__":
    main()
