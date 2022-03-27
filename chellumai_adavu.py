# -*- coding: utf-8 -*-
from pprint import pprint, pformat
import pdb
from tqdm import tqdm
from tamil.utf8 import get_letters
import tamil
from collections import defaultdict, Counter

import sys
import string
import utils
from resources import DEFAULT_DICTIONARY_FILES


import argparse

def read_tokens(filepath):
    print('reading tokens from {}'.format(filepath))
    with utils.openfile(filepath) as f:
        for line in tqdm(f, desc='reading...'):
            try:
                token, count = line.split(',')
                yield token
            except:
                print(line)
                continue
            
def chellumai_eenu(tokens):
    arichuvadi = Counter()
    chellumai = defaultdict(Counter)

    for token in tqdm(tokens, 'chellumai samaippil...'):
        token = '^' + list(token) + '$'
        arichuvadi.update(token)
        for a, b in zip(token, token[1:]):
            chellumai[a][b] += 1

    return arichuvadi, chellumai

def write_chellumai(ofilepath, arichuvadi, chellumai) :
    with open(ofilepath, 'w') as ofile:
        print(','.join( [' '] + sorted(arichuvadi.keys())), file=ofile)
        for i in sorted(arichuvadi.keys()):
            print('{}, '.format(i), end='', file=ofile)

            print(
                ','.join(
                    [ str(chellumai[i][j]) for j in sorted(arichuvadi.keys())]
                ),
                file=ofile)

            
def read_chellumai(ifilepath):
    chellumai = defaultdict(Counter)
    with open(ifilepath) as ifile:

        varigal = ifile.readlines()
        arichuvadi = { i:1 for i in varigal[0].strip().split(',')[1:] }
        print(varigal[0])
        for vari in varigal[1:]:
            print(vari)
            vari = vari.strip()
            muthal, meethi = vari.split(',', 1)
            j, count = muthal.strip('"'), meethi.split(',')
            #pdb.set_trace()
            print(count)
            if j == '^':
                pdb.set_trace()
            count = [int(i.strip()) for i in count]
            for idx, i in enumerate(sorted(arichuvadi.keys())):
                i = i.strip(' "\t\n')
                chellumai[j][i] = count[idx]

    return arichuvadi, chellumai

def narrukku(arichuvadi, chellumai):
    for i in chellumai.keys():
        for j in chellumai.keys():
            if chellumai[i][j] < 1:
                del chellumai[i][j]

    return arichuvadi, chellumai
    
def chellumai_eeniyeluthu(args):
    ifilepath = args.input.split(',') 
    ofilepath = args.output

    tokens = []
    for filepath in ifilepath:
        tokens.extend(read_tokens(filepath))

    arichuvadi, chellumai = chellumai_eenu(tokens)
    write_chellumai(ofilepath, arichuvadi, chellumai)
    
    
def saripaar(chellumai, thodar):
    thodar = ['^'] + list(thodar) + ['$']
    for idx, (i, j) in enumerate(zip(thodar, thodar[1:])):
        print(idx, i, j, chellumai[i][j])
        if chellumai[i][j] <= 0:
            break

    #print(idx, len(thodar))
    return idx >= len(thodar) - 2 
        

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='types of A')
    
    eenu_parser = subparsers.add_parser(
        'eenu',
        help='subcommand to generate chellumaia adavu (transition table)')

    eenu_parser.add_argument('--task',
                             help="task",
                             default='eenu')

    eenu_parser.add_argument("-i", '--input',
                             help="frequency dictionary of words",
                             default=','.join(DEFAULT_DICTIONARY_FILES))
    
    eenu_parser.add_argument("-o", '--output',
                             help="output file to write chellumai adaivu",
                             default='data/chellumai.csv')
    
    saripaar_parser = subparsers.add_parser(
        'saripaar',
        help='subcommand to check words')

    
    saripaar_parser.add_argument('--task',
                                 help="task",
                                 default='saripaar')
    
    saripaar_parser.add_argument('-c', '--chellumai',
                                 help='path to file chellumai adavu',
                                 default='data/orungurri-chellumai-cholloadai.csv')
    
    saripaar_parser.add_argument('-i', '--input',
                                 help='path to file read and flag text from',
                                 type=argparse.FileType('rt'),
                                 default='-')
    
    saripaar_parser.add_argument('-o', '--output',
                                 help='path to file to write the output to',
                                 type=argparse.FileType('wt'),
                                 default='-')    

    args = parser.parse_args()
    pprint(args)

    if args.task == 'eenu':
        chellumai_eeniyeluthu(args)
    elif args.task == 'saripaar':
        arichuvadi, chellumai = read_chellumai(args.chellumai)
        for vari in args.input:
            for thundu in vari.split():
                thundu = thundu.strip(string.punctuation)
                print( '{} {} {}'.format(
                    thundu,
                    saripaar(chellumai, thundu),
                    [i for i in thundu]
                ),
                       file=args.output)

        thundu = input('> ')
        while thundu:
            print(saripaar(chellumai, thundu))
            thundu = input('> ')
            
                
