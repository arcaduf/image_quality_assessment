##########################################################
##########################################################
####                                                  ####
####                ADD BLURRING TO IMAGES            ####
####                                                  ####
##########################################################
##########################################################  



##  PYTHON MODULES
from __future__ import division , print_function
import argparse
import sys
import numpy as np
import glob
import os
from scipy import ndimage as nimg




##  MY I/O MODULES
sys.path.append( '../common/' )
import my_image_io as io
import my_image_display as dis




##  MY FORMAT VARIABLE
myfloat = np.float32




##########################################################
##########################################################
####                                                  ####
####             GET INPUT ARGUMENTS                  ####
####                                                  ####
##########################################################
##########################################################

def getArgs():
    parser = argparse.ArgumentParser(description='Blur images',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-Di', '--pathin', dest='pathin', default='./',
                        help='Specify path to input data')
    
    parser.add_argument('-Do', '--pathout', dest='pathout',
                        help='Specify path to output data')  
    
    parser.add_argument('-i', '--filein', dest='filein',
                        help='Specify name of input image')
    
    parser.add_argument('-s', '--sigma_list', dest='sigma_list',
                        default='60:70:80:90:100',
                        help='Specify number of blurred versions of each input image'
                             + ' and the array of sigma values as percentages of the'
                             + ' sigma of the input image (separated by a ":")')

    parser.add_argument('-sr', '--sigma_range', dest='sigma_range',
                        help='Specify blurring how many radii from min to max: e.g. 10-20-50')   
    
    parser.add_argument('-p',dest='plot', action='store_true',
                        help='Display check-plots during the run of the code')
    
    args = parser.parse_args()
    
    ##  Exit of the program in case of missing arguments
    if args.filein is None:
        parser.print_help()
        sys.exit('ERROR: Input image name not specified!')
    
    return args




##########################################################
##########################################################
####                                                  ####
####           ADD GAUSSIAN BLURRING ROUTINE          ####
####                                                  ####
##########################################################
##########################################################  

def add_gaussian_blurring( image , sigma ):
    nrows,ncols = image.shape
    image_blur = np.zeros( ( nrows , ncols ) , dtype=myfloat )
    image_blur[:,:] = nimg.filters.gaussian_filter( image , [ sigma , sigma ] )
    return image_blur




##########################################################
##########################################################
####                                                  ####
####                  WRITE OUTPUT FILE               ####
####                                                  ####
##########################################################
########################################################## 

def write_output_file( pathout , filein , image_blur , sigma ):
    ext     = filein[len(filein)-4:]
    fileout = filein[:len(filein)-4] + '_blur' 
        
    if sigma < 10:
        fileout += '00' + str( int( sigma ) )
    elif sigma < 100:
        fileout += '0' + str( int( sigma ) ) 
    else:
        fileout += str( int( sigma_arr[im] ) )  
        
    fileout = pathout + fileout + ext
    io.writeImage( fileout , image_blur )
    print( '\nOutput image written in:\n' , fileout,'\n' )
        
        
        

##########################################################
##########################################################
####                                                  ####
####                         MAIN                     ####
####                                                  ####
##########################################################
########################################################## 

def main():
    print('\nADD BLURRING TO IMAGES\n')



    ##  Get input arguments
    args = getArgs()



    ##  Get input and output path
    pathin = args.pathin
    if pathin[len(pathin)-1] != '/':
        pathin += '/'

    if args.pathout is None:
        pathout = pathin
    else:
        pathout = args.pathout
    if pathout[len(pathout)-1] != '/':
        pathout += '/'

    print('\nInput path:\n', pathin)
    print('\nOutput path:\n', pathout)



    ##  Get single image
    filein = args.filein
    imagein = io.readImage( pathin + filein )
    nrows , ncols = imagein.shape
        
    print('\nReading image:\n', filein, '\n')
    print('Image size: ', nrows,' X ', ncols)



    ##  Check plot
    if args.plot is True:
        dis.plot( imagein , 'Input image' )
        

        
    ##  Allocate memory for the noisy temporary image
    image_blur = np.zeros( ( nrows, ncols ) , dtype=myfloat )



    ##  Get blurring radii
    if args.sigma_range is None:
        sigma_list = args.sigma_list
        sigma_arr  = np.array( sigma_list.split(':') , dtype=myfloat )
        nimg = len( sigma_arr )
    else:
        sigma_list = args.sigma_range
        sigma_list = np.array( sigma_list.split('-') , dtype=myfloat )
        sigma_arr  = np.linspace( sigma_list[0] , sigma_list[1] , sigma_list[2] )
        nimg = len( sigma_arr )      



    ##  Loop on each gaussian sigma
    for im in range( nimg ):
        ##  Add gaussian noise
        image_blur[:,:] = add_gaussian_blurring( imagein , sigma_arr[im] )

        ##  Check noisy image
        if args.plot is True:
            dis.plot( image_blur , 'Blurred image -- sigma: ' + str( sigma_arr[im] ) )

        ##  Write noisy image to file
        write_output_file( pathout , filein , image_blur , sigma_arr[im] )




##########################################################
##########################################################
####                                                  ####
####                         MAIN                     ####
####                                                  ####
##########################################################
########################################################## 

if __name__ == '__main__':
	main()
