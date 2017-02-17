from __future__ import division , print_function
import os

command = 'python calc_nmi.py -i1 ../data/phantom_02.tif -i2 ../data/phantom_02_distorted.tif -s -p'

os.chdir( '../metrics/' )

print( '\nTEST: Compute Normalized Mutual Information (NMI)\n' )
print( command )
os.system( command )


