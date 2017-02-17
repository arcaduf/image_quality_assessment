from __future__ import division , print_function
import os

command = 'python calc_mse.py -i1 ../data/phantom_02.tif -i2 ../data/phantom_02_distorted.tif -s -p'

os.chdir( '../metrics/' )

print( '\nTEST: Mean Squared Error (MSE) and Peak Signal to Noise Ratio (PSNR)\n' )
print( command )
os.system( command )


