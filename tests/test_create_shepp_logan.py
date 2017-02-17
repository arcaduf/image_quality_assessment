from __future__ import division , print_function
import os

command = 'python create_shepp_logan.py -D ../data/ -n 512 -a 364 -p -o .tif'

os.chdir( '../phantom_creation/' )

print( '\nTEST: Create Modified Shepp-Logan phantom with 512 X 512 pixels and its \
                analytical forward projection with 364 views\n' )
print( command )
os.system( command )

