from __future__ import division , print_function
import os

command1 = 'python rescale_image.py -Di ../data/ -i phantom_01.tif -z 0.7 -p'
command2 = 'python rescale_image.py -Di ../data/ -i phantom_04.tif -n  736 -p'

os.chdir( '../phantom_creation/' )

print( '\nTEST 1: Rescale image with a specified factor\n' )
print( command1 )
os.system( command1 )

print( '\nTEST 2: Rescale image with a specified number of pixels\n' )
print( command2 )
os.system( command2 )

