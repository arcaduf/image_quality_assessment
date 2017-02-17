from __future__ import division , print_function
import os

command1 = 'python add_noise.py -Di ../data/ -i phantom_02.tif -n gaussian -s 20 -p'
command2 = 'python add_noise.py -Di ../data/ -i phantom_03.tif -n poisson -p'

os.chdir( '../phantom_creation/' )

print( '\nTEST 1: Add Gaussian noise to phantom\n' )
print( command1 )
os.system( command1 )

print( '\nTEST 2: Add Poisson noise to phantom\n' )
print( command2 )
os.system( command2 )

