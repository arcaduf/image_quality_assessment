from __future__ import division , print_function
import os

command = 'python -W ignore edge_profile_fitting.py -i ../data/phantom_01_distorted_line_profile.txt -p'

os.chdir( '../metrics/' )

print( '\nTEST: Measure spatial resolution through Edge Profile Fitting (EPF)\n' )
print( command )
os.system( command )


