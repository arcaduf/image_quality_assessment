from __future__ import division , print_function
import os

filein = 'sl_pix0512_ang0364_sino.tif'

command1 = 'python downsample_sinogram.py -Di ../data/ -i ' + filein + ' -n 150 -p'
command2 = 'python downsample_sinogram.py -Di ../data/ -i ' + filein + ' -f 2 -p'

os.chdir( '../phantom_creation/' )

print( '\nTEST 1: Downsample sinogram to 150 views\n' )
print( command1 )
os.system( command1 )

print( '\nTEST 2: Downsample sinogram by a factor of 2 along the pixel direction\n' )
print( command2 )
os.system( command2 )

