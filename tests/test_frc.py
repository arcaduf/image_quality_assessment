from __future__ import division , print_function
import os

command = 'python -W ignore fourier_ring_correlation.py -i ../data/phantom_01.tif:../data/phantom_01_distorted.tif -p'

os.chdir( '../metrics/' )

print( '\nTEST: Measure spatial resolution through Edge Profile Fitting (EPF)\n' )
print( command )
os.system( command )


