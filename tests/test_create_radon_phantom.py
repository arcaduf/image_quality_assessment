from __future__ import division , print_function
import os

command = 'python create_radon_phantom.py -D ../data/ -n 256 -a 402 -d 3 -p -f .tif'

os.chdir( '../phantom_creation/' )

print( '\nTEST: Create Radon phantom of degree 3 with 256 X 256 pixels and its \
         analytical forward projection with 402 views\n' )
print( command )
os.system( command )

