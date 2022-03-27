# -*- coding: utf-8 -*-
from pprint import pprint, pformat
import pdb
from tqdm import tqdm
from tamil.utf8 import get_letters
import tamil
from collections import defaultdict, Counter

import sys
import csv
import string
import utils
from resources import DEFAULT_DICTIONARY_FILES, XSV_DELIMITER


import argparse

def read_tokens(filepath):
    print('reading tokens from {}'.format(filepath))
    with utils.openfile(filepath) as f:
        csvf = csv.reader(f, delimiter=XSV_DELIMITER)
        for line in tqdm(csvf, desc='reading...'):
            try:
                token, count = line
                yield token
            except:
                print(line)
                continue
            
def chellumai_eenu(tokens):
    arichuvadi = Counter()
    chellumai = defaultdict(Counter)

    for token in tqdm(tokens, 'chellumai samaippil...'):
        token = ['^'] + list(token) + ['$']
        arichuvadi.update(token)
        for a, b in zip(token, token[1:]):
            chellumai[a][b] += 1

    return arichuvadi, chellumai

def write_chellumai(ofilepath, arichuvadi, chellumai) :
    with open(ofilepath, 'w') as ofile:
        print(XSV_DELIMITER.join( [' '] + sorted(arichuvadi.keys())), file=ofile)
        for i in sorted(arichuvadi.keys()):
            print('{}{} '.format(i, XSV_DELIMITER), end='', file=ofile)

            print(
                XSV_DELIMITER.join(
                    [ str(chellumai[i][j]) for j in sorted(arichuvadi.keys())]
                ),
                file=ofile)

            
def read_chellumai(ifilepath):
    chellumai = defaultdict(Counter)
    with open(ifilepath) as ifile:
        ifile = csv.reader(ifile, delimiter=XSV_DELIMITER)
        muthal_vari = next(ifile) #read first line
        arichuvadi = { i:1 for i in muthal_vari[1:] } #[1:] - table, hence top left most is empty
        print(muthal_vari)
        for vari in ifile:
            print(vari)
            j, count = vari[0], vari[1:]
            #pdb.set_trace()
            #print(count)
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
    ofilepath = args.output

    tokens = []
    for filepath in args.input:
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
        args.input = args.input.split(',')
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
            
                
