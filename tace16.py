# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format="%(levelname)-8s:%(filename)s.%(funcName)20s >>   %(message)s")
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


from pprint import pprint, pformat
from collections import namedtuple
import csv
CsvRecord = namedtuple('CsvRecord', ['letter', 'valid', 'tace16',
                                     'unicode11', 'unicode12', 'unicode13',
                                     'unicode21', 'unicode22', 'unicode23',
                                     'utf8_tace16_addend'])

def read_csv(filename='data_new.csv'):
    records = [i for i in csv.reader(open(filename), delimiter='|')]
    conversion_map = {}
    tace16_letter_map,  letter_tace16_map = {}, {}
    utf8_letter_map, letter_utf8_map = {}, {}
    vowel_ops = {}
    unicode_list = set()


    for record in records[1:]:
        print(record)
        record = CsvRecord._make(record)
        tace16 = int(record.tace16, base=16)

        tace16_letter_map[tace16] = record.letter
        letter_tace16_map[record.letter] = tace16
        
        if record.valid:
            unicode1 = [record.unicode11, record.unicode12, record.unicode13]
            unicode1 = [int(i, 16) for i in unicode1]
            if record.unicode21:
                unicode2 = [record.unicode21, record.unicode22, record.unicode23]
                unicode2 = [int(i, 16) for i in unicode2]
                
                conversion_map[tace16] = (unicode1, unicode2)

                utf8 = (tuple(unicode1), tuple(unicode2))
                utf8_letter_map[utf8] = record.letter
                letter_utf8_map[record.letter] = utf8

                unicode_list.add(tuple(unicode1))
                unicode_list.add(tuple(unicode2))
                vowel_ops[tuple(unicode2)] = int(record.utf8_tace16_addend)
                print(vowel_ops)
            else:
                conversion_map[tace16] = (unicode1,)
                unicode_list.add(tuple(unicode1))

                utf8 = (tuple(unicode1),)
                utf8_letter_map[utf8] = record.letter
                letter_utf8_map[record.letter] = utf8


    return (conversion_map,
            tace16_letter_map, letter_tace16_map,
            utf8_letter_map, letter_utf8_map,
            list(unicode_list), vowel_ops)

(conversion_map,
 tace16_letter_map, letter_tace16_map,
 utf8_letter_map, letter_utf8_map,
 unicode_list, vowel_ops)                =    read_csv()


def tace16_to_utf8(string):
    return [uc for i in string for c in conversion_map[i] for uc in c]

def utf8_to_tace16(string):
    log.debug('input:{}'.format(string))
    letters = []
    string = string.encode()
    for i in range(len(string)//3):
        triplet = tuple(string[3*i:3*(i+1)])
        if triplet in vowel_ops.keys():
            letters[-1] += vowel_ops[triplet]
        else:
            letter = utf8_letter_map[(triplet,)]
            tace = letter_tace16_map[letter]
            letters.append(tace)

    return letters
                
def utf8_to_utf32(utf8_points):
    smask = int('0b00111111', 2)
    pmask = int('0b00001111', 2)
    utf32_points = []
    for point in utf8_points:
        utf32 = 0
        utf32 = utf32 | point[0] & pmask
        utf32 = utf32 << 4 | point[1] & smask
        utf32 = utf32 << 6 | point[2] & smask
        utf32_points.append(utf32)
    return utf32_points

def utf32_to_utf8(utf32_points):
    smask = int('0b00111111', 2)
    pmask = int('0b00001111', 2)
    utf8_points = []
    for point in utf32_points:
        utf8 = [int('0b11100000', 2), int('0b10000000', 2), int('0b10000000', 2)]
        print('{:032b}'.format(point))
        utf8[2] = utf8[2] | (point & smask)
        utf8[1] = utf8[1] | ((point >> 6) & smask)
        utf8[0] = utf8[0] | ((point >> 12) & pmask)
        utf8_points.append(utf8)
    return utf8_points

        
def test1():
    (conversion_map,
     tace16_letter_map, letter_tace16_map,
     utf8_letter_map, letter_utf8_map,
     unicode_list, vowel_ops)  = read_csv()
    print('========conversionm_map============')
    pprint(conversion_map)
    pprint(len(conversion_map))
    pprint('======tace16_letter_map=======')
    pprint(tace16_letter_map)
    pprint('=========letter_tace16_map============')
    pprint(letter_tace16_map)
    pprint('==============utf8_letter_map=========')
    pprint(utf8_letter_map)
    pprint('=========letter_utf8_map===========')
    pprint(letter_utf8_map)
    pprint('==========unicode_list=============')
    pprint(unicode_list)
    pprint('==========vowel_ops============')
    pprint(vowel_ops)


def test2(string='அம்மா'):
    utf_version = tace16_to_utf8([letter_tace16_map[i] for i in string])
    print('orig:{}'.format(string))
    print('orig bytes: {}'.format(string.encode()))
    print('orig numbers: {}'.format([i for i in string.encode()]))
    print('utf_version: {}'.format(utf_version))
    print('utf_version bytes: {}'.format((bytes(utf_version))))
    print('utf_version bytes: {}'.format(bytes(utf_version).decode()))

    
def print_bytes(b):
    return ' '.join(['{:02X}'.format(i) for i in b])

        
def test3():
    for i, j in utf8_letter_map.items():
        utf32 = utf8_to_utf32(i)
        utf8 = utf32_to_utf8(utf32)
        print('{}\t{:18}\t{:18}\t{:18}'.format(j,
                                      print_bytes([c for x in i for c in x]),
                                      print_bytes(utf32),
                                      print_bytes([c for x in utf8 for c in x])))


def test4(string='அப்பா'):
    print(string, end=' ')
    tace = utf8_to_tace16(string)
    print(print_bytes(tace), end=' ')
    utf =  tace16_to_utf8(tace)
    print(bytes(utf).decode())
    
if __name__ == '__main__':
    test1()
    test4('சிந்தனை')
    #test2('சிந்தனை')
    
