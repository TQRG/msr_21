import sys
import argparse
from os import listdir
from os.path import isfile, join

import pandas as pd
import numpy as np
from tqdm import tqdm
import re

LINE = "---------------------------"

def get_source(x):
    if 'github' in x:
        return 'github'
    elif 'bitbucket' in x:
        return 'bitbucket'
    elif 'gitlab' in x:
        return 'gitlab'

def get_patches(fin, fout):
    # read the csv
    df = pd.read_csv(fin)

    # get references to source code hosting websites 
    for idx, row in tqdm(df.iterrows()):
        refs = eval(row['refs'])
        patch_refs = set()
        for ref in refs:
            found = re.search(r'(github|bitbucket|gitlab).*(/commit/|/commits/)', ref)
            if found: 
                patch_refs.add(ref)
        df.at[idx, 'code_refs'] = str(patch_refs)
    
    # filter cases without any references to source code hosting websites
    df_code_ref = df[df['code_refs'] != 'set()']

    # save data
    df_code_ref.to_csv(fout, index=False)
    print(f"{len(df_code_ref)} patches were saved to {fout}")

def patches_stats(fin):
    def set_len(x):
        return len(eval(x))

    # read the csv
    df = pd.read_csv(fin)

    # get number of commits involved in each patch
    df['n_commits'] = df['code_refs'].transform(set_len)

    print(f"{LINE}\ncommits (#)\tpatches (#)\n{LINE}")
    # iterate over the stats
    for n in np.sort(df['n_commits'].unique()):
        print(f"{n}\t\t{len(df[df['n_commits'] == n])}")
    print(f"{LINE}\n👀 n security patches where\nperformed using y commits\n{LINE}\n")
    
    # get commits source
    df['source'] = df['code_refs'].transform(get_source)

    print(f"{LINE}{LINE}\nSOURCE\t\tpatches (#)\tpatches (%)\n{LINE}{LINE}")
    # iterate over the different sources 
    for source in df['source'].unique():
        n_source = len(df[df['source'] == source])
        if source == 'bitbucket':
            print(f"{source}\t{n_source}\t\t{(n_source/len(df))*100:.2f}%")
        else:
            print(f"{source}\t\t{n_source}\t\t{(n_source/len(df))*100:.2f}%")
    print(f"{LINE}{LINE}\n")

def get_source_patches(fin, source):

    # read csv
    df = pd.read_csv(fin)

    # get commits source
    df['source'] = df['code_refs'].transform(get_source)
    
    # # get patches from github 
    df_source = df[df['source'] == source]

    # save patches
    fout = f'../dataset/{source}_cve_details_patches.csv'
    df_source.to_csv(fout, index=False)
    print(f"{len(df_source)} patches were saved to {fout}")

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Get patches data from cve-details data:')
    parser.add_argument('--task', dest='format', choices=['filter', 'stats', 'source'])
    parser.add_argument('-fin', type=str, metavar='file', help='cve details file')
    parser.add_argument('-fout', type=str, metavar='file', help='new file')
    parser.add_argument('-source', type=str, metavar='str', help='name of the source')
    
    args = parser.parse_args()

    if args.format == 'filter':
        if args.fin and args.fout:
            get_patches(args.fin, args.fout)
    elif args.format == 'stats':
        if args.fin:
            patches_stats(args.fin)
    elif args.format == 'source':
        if args.fin and args.source in {'github', 'bitbucket', 'gitlab'}:
            get_source_patches(args.fin, args.source)
    else:
        print('Something wrong with the input file name or year.')

        