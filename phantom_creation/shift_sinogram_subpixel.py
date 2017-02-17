#####################################################################
#####################################################################
####                                                             ####
####              CORRECT SINOGRAM CENTRE OF ROTATION            ####
####                     TO SUBPIXEL PRECISION                   ####
####                                                             ####
####          24/02/2014   F. Arcadu   arcusfil.gmail.com        ####
####                                                             ####
#####################################################################
#####################################################################




##  PYTHON MODULES
from __future__ import print_function , division
import sys
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline




##  MY MODULES
sys.path.append( '../common/' )
import my_image_io as io
import my_image_process as proc




##  MAIN
def main():
    sino = io.readImage( sys.argv[1] )
    ctr = np.float32( sys.argv[2] )

    sino_new = proc.sino_correct_rot_axis( sino , ctr )

    filename = sys.argv[1][:len(sys.argv[1])-4] + '_interp.DMP'
    io.writeImage( filename , sino_new )




##  CALL TO MAIN
if __name__ == '__main__':
    main()
