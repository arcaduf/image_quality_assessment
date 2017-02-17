from __future__ import division , print_function
import os

command1 = 'python calc_complexity.py -Di ../data/ -i phantom_01.tif -p'
command2 = 'python calc_complexity.py -Di ../data/ -i phantom_02.tif -p'

os.chdir( '../metrics/' )

print( '\nTEST: Compute image complexity\n' )

print( command1 )
os.system( command1 )

print( command2 )
os.system( command2 )


