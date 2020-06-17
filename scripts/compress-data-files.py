import os
import gzip
import glob


for path in glob.glob('../data/*'):
    path, ext = os.path.splitext(path)
    if ext in ['.tsv', '.csv', '.txt']:
        with gzip.open('{}.gz'.format( path+ext), 'wt') as f:
            f.write(open(path+ext).read())
