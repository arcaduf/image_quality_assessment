#########################################################
#########################################################
####                                                 ####
####         CALCULATE IMAGE COMPLEXITY INDEX        ####
####                                                 ####
####        based on JPEG standard compression       ####
####       and spatial information (SI) calculus     ####
####                                                 ####
#########################################################
#########################################################




##  PYTHON MODULES
from __future__ import division, print_function
import argparse
import sys
import os
import numpy as np
import scipy
from scipy import ndimage




##  MY PYTHON MODULES
sys.path.append('../common/')
import my_image_io as io
import my_image_display as dis




##  MY FORMAT VARIABLE
myfloat = np.float32




#######################################################################
#######################################################################
####                                                               ####
####                         GET ARGUMENTS                         ####
####                                                               ####
#######################################################################
#######################################################################

def getArgs():
    parser = argparse.ArgumentParser(description='Calculate image complexity')
       
    parser.add_argument('-Di','--pathin', dest='pathin', default='./',
                  help='Path to the folder containing the image to analyze')
    
    parser.add_argument('-i','--filein', dest='filein',
                  help='Select the image to analyze')
    
    parser.add_argument('-j','--jpeg_compr', dest='jpeg_compr', type=np.int32 , default=75,
                  help='Select the quality of the jpeg compression, ranging from'
                  +' 0 to 100 ( default: 75 )')
    
    parser.add_argument('-p','--plot', dest='plot', action='store_true' ,
                  help='Display check plots')   

    args = parser.parse_args()

    if args.filein is None:
        parser.print_help()
        sys.exit('\nERROR: input image not specified!\n')

    return args




#######################################################################
#######################################################################
####                                                               ####
####   IMAGE COMPLEXITY INDEX BASED ON STANDARD JPEG COMPRESSION   ####
####                                                               ####
#######################################################################
####################################################################### 

def complexity_jpeg( image , args ):
    print('\n1) Calculate image complexity index based on JPEG compression ....')

    ##  Save converted file to temporary file
    compr_ratio   = 100     
    tmp_file_orig = args.pathin + 'tmp_gray.jpg'
    io.writeImage( tmp_file_orig , image , compr_ratio )

    ##  JPEG compression
    compr_ratio    = 75  
    tmp_file_compr = args.pathin + 'tmp_comprss' + str( compr_ratio ) + '.jpg'
    io.writeImage( tmp_file_compr , image , compr_ratio )

    ##  Evaluate ratio of the file sizes
    size_orig  = myfloat( os.stat( tmp_file_orig ).st_size )
    size_compr = myfloat( os.stat( tmp_file_compr ).st_size )

    complexity = size_compr / size_orig 

    print('Original file size: ', size_orig)
    print('Compressed file size: ', size_compr)
    print('JPEG compression factor: ', complexity)

    ##  Close compressed image and delete temporary compressed file
    os.remove( tmp_file_orig )
    os.remove( tmp_file_compr ) 




#######################################################################
#######################################################################
####                                                               ####
####      IMAGE COMPLEXITY INDEX BASED ON SPATIAL INFORMATION      ####
####                                                               ####
#######################################################################
#######################################################################  

def complexity_struct_info( image ):
    print('\n2) Calculate image complexity index based on spatial information ....')  
    
    ##  Applying vertical and horizontal Sobel filter
    print('Applying vertical and horizontal Sobel filter')    
    dy = ndimage.filters.sobel( image , 1 )
    dx = ndimage.filters.sobel( image , 0 ) 

    ##  Calculate the map of the spatial information (SI) or,
    ##  in other words, the map of magnitudes of the edge images
    npix   = image.shape[0] * image.shape[1] 
    map_si =  dx*dx + dy*dy

    si_mean = np.mean( map_si )
    si_rms  = np.sqrt( 1.0/npix * np.sum( map_si * map_si )  )
    si_std  = np.std( map_si )

    print('\nSI -- mean: ', si_mean )
    print('SI -- rms: ', si_rms ) 
    print('SI -- std: ', si_std )     

    ##  Calculate the gradient sparsity index ( GSI )
    map_si = map_si != 0
    complexity = np.count_nonzero( map_si ) / myfloat( npix ) 
    
    print('\n3) Calculate image complexity index based on gradient sparsity index ....')     
    print('\nGradient sparsity index: ', complexity)
    print('\n')




#######################################################################
#######################################################################
####                                                               ####
####                           MAIN PROGRAM                        ####
####                                                               ####
#######################################################################
#######################################################################

def main():

    print('')
    print('######################################') 
    print('######################################')
    print('####                              ####')
    print('####  CALCULATE IMAGE COMPLEXITY  ####')
    print('####                              ####')   
    print('######################################')
    print('######################################') 


    ##  Get input arguments
    args = getArgs()


    ##  Read input image
    filein  = args.pathin + args.filein 
    image   = io.readImage( filein )
    nx , ny = image.shape
    
    print('\nReading input image:\n', filein)     
    print('Image size: ', nx, '  X  ', ny)
    
    if args.jpeg_compr <= 0 and args.jpeg_compr >= 100:
        args.jpeg_compr = 75    

    if args.plot is True:
        dis.plot( image , 'Input image' )


    ##  Calculate image complexity index based on JPEG compression
    complexity_jpeg( image , args )


    ##  Calculate image complexity index based on spatial information (SI)
    complexity_struct_info( image )




#######################################################################
#######################################################################
####                                                               ####
####                           CALL TO MAIN                        ####
####                                                               ####
#######################################################################
#######################################################################

if __name__ == '__main__':
    main()
