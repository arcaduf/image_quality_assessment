from __future__ import division , print_function
import os

command = 'python add_blur.py -Di ../data/ -i phantom_04.tif -s 4 -p'

os.chdir( '../phantom_creation/' )

print( '\nTEST: Add Gaussian blurring to phantom\n' )
print( command )
os.system( command )


