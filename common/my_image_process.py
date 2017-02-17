###############################################################################
###############################################################################
###############################################################################
######                                                                   ######
######       PRE- AND POST-PROCESSING TOOLS FOR RECONSTRUCTIONS          ######
######                                                                   ######
######       List of functions to run before or after performing         ######
######            a reconstruction with whatever algorithm.              ######
######                                                                   ######
######                        FUNCTION LIST:                             ######
######                   1) sino_correct_rot_axis                        ######
######                   2) sino_edge_padding                            ######
######                   3) sino_zero_padding                            ######
######                   4) diff_sino                                    ######
######                   5) diff_sino_ctr                                ######
######                   6) diff_sino_savitzky_golay                     ######
######                   7) image_zero_padding                           ###### 
######                   8) search_rot_ctr                               ######
######                   9) select_resol_square                          ######
######                  10) linear_regression                            ######
######                  11) crop_image                                   ######
######                  12) image_registration                           ######
######                                                                   ######
######        Author: Filippo Arcadu, arcusfil@gmail.com, 09/07/2013     ######
######                                                                   ######
###############################################################################
###############################################################################
###############################################################################




####  PYTHON LIBRARIES
from __future__ import division,print_function
import sys
import numpy as np
from numpy.fft import *
import math
from math import factorial
import scipy
from scipy import interpolate as interp




####  MY FORMAT VARIABLE
myfloat = np.float32




#######################################################################
#######################################################################
####                                                               ####
####           CORRECT SINOGRAM FOR THE CENTER OF ROTATION         ####
####                                                               ####
#######################################################################
#######################################################################
##
## 1) The inputs:
##    sino ---> a 2D array of floating values, where sino.shape[0] = number of projections
##                  and sino.shape[1] = number of pixels for each projections; 
## 
##    ctr   ---> estimated abscissa coordinate (along the pixel line) of the rotation axis;
##
## 2) How it works.
##
##   EXAMPLE 1 :
##                             1 2 3 4 5
##                 sino =  6 7 8 9 1    ,    ctr = +4   ====>  shift = ctr-npix/2 = 2
##                             1 5 7 5 6
##                                                               3 4 5 5 5 
##     	                        ====>   centrered sino =     8 9 1 1 1
##                                                               7 5 6 6 6
##
##   EXAMPLE 2 :
##                             1 2 3 4 5
##                 sino =  6 7 8 9 1    ,    ctr = 0   ====>  shift = ctr-npix/2 = -2
##                             1 5 7 5 6
##                                                               1 1 1 2 3 
##      	                      ====>   centrered sino =   6 6 6 7 8
##                                                               1 1 1 5 7
##
## 3) Note: since only shifts are essentially performed without any kind of interpolation, one cannot use the 
##          decimal digits of the ctr coordinate to centre more finely the sino.          

def sino_correct_rot_axis( sino , ctr ):
    nang = sino.shape[0]
    npix = sino.shape[1]
    
    shift = ctr - npix * 0.5

    if shift.is_integer() is False:
        npix_pad = npix + 200
        sino_corr = np.zeros( ( nang , npix_pad ) , dtype=myfloat )
        i1 = int( ( npix_pad - npix ) * 0.5 );  i2 = i1 + npix
        sino_corr[:,i1:i2] = sino

        grid_x1 , grid_y1 = np.meshgrid( np.arange( npix_pad ) , np.arange( nang ) )
        z = np.dstack( ( grid_y1 , grid_x1 ) ).reshape( npix_pad * nang , 2 )
        grid_x2 , grid_y2 = np.mgrid[ 0:nang , i1+shift:i2+shift ] 
        sino_corr  = interp.griddata( z , sino_corr.reshape( -1 ) , ( grid_x2 , grid_y2 ) ,
                                     method='cubic' )

    else:
        shift = int( ctr - npix/2 )

        if shift > 0:
            sino_corr = np.roll( sino , -shift , axis=1 )
            block = np.ones( ( 1 , shift ) ) * np.array( sino[:,npix-1] ).reshape( nang , 1 )
            sino_corr = np.concatenate( ( sino_corr[:,:npix-shift] , block ) , axis=1 )
        else:
            sino_corr = np.roll( sino , -shift , axis=1 )
            block = np.ones( ( 1 , -shift ) ) * np.array( sino[:,0] ).reshape( nang , 1 )
            sino_corr = np.concatenate( ( block , sino_corr[:,-shift:] ) , axis=1 )   

    return sino_corr




#######################################################################
#######################################################################
####                                                               ####
####                          EDGE PADDING                         ####
####                                                               ####
#######################################################################
#######################################################################  
##
## 1) The inputs:
##    sino ---> a 2D array of floating values, where sino.shape[0] = number of projections
##                  and sino.shape[1] = number of pixels for each projections; 
##
##    padding  ---> a floating value used to set how much the input sino should be edge-padded;
##                  the pixels that are added to the input sino are 2*padding*number_pixel_sino.
##
## 2) This functions takes the first column of the sino (pixel 0 of all the angles), repeat
##    it column padding*number_pixel_sino times all of them are placed at the beginning of the new
##    sino; the same occurs with the last column whose repetitions are added at the end of the 
##    new sino.

def sino_edge_padding( sino , padding ):
    nang = sino.shape[0]
    npix_old = sino.shape[1]    
    npad = int( padding * npix_old )
        
    print("Padded pixels on one side = ", npad)

    col0 = np.array( sino[:,0] ).reshape( nang , 1 )
    col1 = np.array( sino[:,npix_old-1] ).reshape( nang , 1 )

    edge_left = np.ones( ( 1 , npad ) ) * col0
    edge_right = np.ones( ( 1 , npad ) ) * col1
        
    sino_pad = np.concatenate( ( edge_left , sino , edge_right ) , axis=1 )
        
    return sino_pad




#######################################################################
#######################################################################
####                                                               ####
####                    ZERO PADDING OF SINOGRAMS                  ####
####                                                               ####
#######################################################################
#######################################################################  
##
## 1) The inputs:
##    sino ---> a 2D array of floating values, where sino.shape[0] = number of projections
##                  and sino.shape[1] = number of pixels for each projections; 
##
##    factor   ---> integer value that multiplies the minimum zero padding
##
## 2) The functions calculates the lowest power of 2 which is bigger than the number of pixels of
##    the input sino and this power is multiplied by factor. The old sino is, then, copied
##    in an other one having that power of two as number of pixels.

def sino_zero_padding( sino , factor ):
    nang = sino.shape[0]
    npix = sino.shape[1]
    npix_pad = int( math.pow( 2.0 , math.ceil( math.log( npix , 2 ) ) ) ) * factor 
    
    sino_pad = np.zeros( ( nang , npix_pad ) , dtype=myfloat )
    i = int( ( npix_pad - npix ) * 0.5 )
    sino_pad[:,i:i+npix] = sino

    return sino_pad




#######################################################################
#######################################################################
####                                                               ####
####     DIFFERENTIAL SINOGRAM dS/dr WITH SAVITZKY-GOLAY METHOD    ####
####                                                               ####
#######################################################################
#######################################################################

##  Simple finite differences 
def diff_sino( sino ):
    sino_diff = sino.copy();  sino_diff[:] = 0.0
    sino_diff[:,1:] = np.diff( sino , axis=1 )
    return sino_diff 



##  Central finite differences
def diff_sino_ctr( sino ):
    nr , nc = sino.shape
    D = np.zeros( ( nc , nc ) , dtype=myfloat )
    D[0,0] = -1.0;  D[1,0] = 1.0;  D[nc-2,nc-1] = -1.0;  D[nc-1,nc-1] = 1.0
    aux = np.zeros( nc , dtype=myfloat );  aux[0] = -0.5;  aux[2] = 0.5
    
    for i in range( 1 , nc-1 ):
        D[:,i] = aux
        aux[:] = np.roll( aux , 1 )

    sino_diff = np.dot( sino , D )

    return sino_diff 



##  Savitzky-Golay method: least-square polynomial fit
def diff_sino_savitzky_golay( sino , window_size=11 , order=3 , deriv=1 , rate=1 ):
    ##  Do some checks
    window_size = np.abs( np.int( window_size ) )
    order = np.abs( np.int( order ) )
    

    ##  Finite differences
    if window_size % 2 != 1 or window_size < order + 2:
        sino[:,:] = diff_sino( sino )
        ctr = sino.shape[1] * 0.5
        sino[:,:] = sino_correct_rot_axis( sino , ctr + 0.5 )


    ##  Savitky-Golay
    else:
        ##  Precompute coefficients
        nang , npix = sino.shape
        order_range = range( order + 1 )
        half_window = ( window_size -1 ) // 2
        b = np.mat( [ [ k**i for i in order_range ] for k in range( -half_window , half_window + 1 ) ] )
        m = np.linalg.pinv( b ).A[deriv] * rate**deriv * factorial( deriv )


        ##  Apply filter to each projection
        for i in range( nang ):
            ##  Copy projection in auxiliary array
            y = sino[i,:].copy()

            ##  Edge-padding of the signal
            firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
            lastvals = y[-1] + np.abs( y[-half_window-1:-1][::-1] - y[-1] )
            y = np.concatenate( ( firstvals , y , lastvals ) )

            ##  1D convolution
            sino[i,:] = np.convolve( m[::-1] , y , mode='valid' )

    return sino




#######################################################################
#######################################################################
####                                                               ####
####                    ZERO PADDING FOR IMAGES                    ####
####                                                               ####
#######################################################################
#######################################################################  
##
## 1) The inputs:
##    image    ---> a 2D array of floating values; 
##
##    factor   ---> integer value that multiplies the minimum zero padding
##
## 2) The functions calculates the lowest power of 2 which is bigger than the number of pixels of
##    the input image and this power is multiplied by factor. The old image is, then, copied
##    in an other one having that power of two as number of pixels along the rows and the columns.

def image_zero_padding( image , factor ):
    width = image.shape[0]
    height = image.shape[1]
    
    if width < height:
        npix = height
    else:
        npix = width
    
    npix_pad = int( math.pow( 2.0 , math.ceil( math.log( npix , 2 ) ) ) ) * factor 
    
    image_zero_padding = np.zeros( ( npix_pad , npix_pad ) )
    i = int( (npix_pad - npix) * 0.5 )
    image_zero_padding[i:i+npix,i:i+npix] = image
    
    return image_zero_padding




#######################################################################
#######################################################################
####                                                               ####
####            FIND CENTER OF ROTATION AXIS FOR SINOGRAMS         ####
####                                                               ####
#######################################################################
#######################################################################
##
## Usage: search_rot_ctr( sino , None , 'a' )        --->  for absorption sinos
##       search_rot_ctr( proj_deg0 , proj_deg180 , 'a' )  --->  for absorption projections
##       search_rot_ctr( sino , None , 'd' )        --->  for dpc sinos
##       search_rot_ctr( proj_deg0 , proj_deg180 , 'd' )  --->  for dpc projections
##
## Implementation in Python of "findRA.m" of P. Modregger ( 2010 )

def search_rot_ctr( data1 , data2 , flag ):
    ##  Check whether flag is available
    if ( flag in ['a','d'] ) is False:
        flag = 'a'
        raise Exception('''\nWarning: the search of the rotation center requires
                         either the flag 'a' for absorption data or 'd' for dpc
                         data. Data considered by default of absorption''')
        

    
    ##  Case 1: search for the best rotation center given a sino
    if data2 is None:
        nang = data1.shape[0]
        npix = data1.shape[1] 
        proj_deg0 = data1[0,:]
        proj_deg180 = data1[nang-1,:]

        
        ##  Preprocess data if they are dpc data
        if flag == 'd':
            proj_deg0 = np.abs( proj_deg0 - np.mean( proj_deg0 ) )
            proj_deg180 = np.abs( proj_deg180 - np.mean( proj_deg180 ) )

        
        ##  Calculate cross-correlation map
        aux_deg0 = np.fft.fftshift( np.fft.fft( proj_deg0 ) )
        aux_deg180 = np.conj( np.fft.fftshift( np.fft.fft(  proj_deg180[::-1] ) ) )
        map_auto_corr = np.abs( np.fft.ifftshift( np.fft.ifft( aux_deg0 * aux_deg180 ) ) )
        max_corr = np.max( map_auto_corr )
        ind_max_corr = np.argwhere( map_auto_corr == max_corr )          
        max_corr = np.max( map_auto_corr )
        ind_max_corr = np.argwhere( map_auto_corr == max_corr )


    
    
    ##  Case 2: search for the best rotation center given 2 projections 
    else:
        npix = len( data1 )
        proj_deg0 = data1
        proj_deg180 = data2

        
        ##  Preprocess data if they are dpc data
        if flag == 'd':
            proj_deg0 = np.abs( proj_deg0 - np.mean( proj_deg0 ) )
            proj_deg180 = np.abs( proj_deg180 - np.mean( proj_deg180 ) )

        
        ##  Calculate cross-correlation map
        aux_deg0 = np.fft.fftshift( np.fft.fft2( proj_deg0 ) )
        aux_deg180 = np.conj( np.fft.fftshift( np.fft.fft2(  np.fliplr( proj_deg180 ) ) ) )
        map_auto_corr = np.abs( np.fft.ifftshift( np.fft.ifft2( aux_deg0 * aux_deg180 ) ) )  
        
        max_corr = np.max( map_auto_corr )
        ind_max_corr = np.array( np.argwhere( map_auto_corr == max_corr ) ).reshape(2,1)
        ind_max_corr = ind_max_corr[1]

 
    ctr = ( ( ind_max_corr + 1 + npix*0.5 )*0.5 - 1.25 ).astype( np.float32 )

    return ctr




#######################################################################
#######################################################################
####                                                               ####
####  CROP SQUARE INSCRIBED IN THE RESOLUTION CIRCLE OF THE IMAGE  ####
####                                                               ####
#######################################################################
#######################################################################  

def select_resol_square( image ):
    width,height = image.shape
    radius = 0.5 * np.min( [ width , height ] )
    l = radius * np.sqrt( 2.0 ) * 0.5
    
    edges = [ int( np.ceil( width * 0.5 - l ) )  , int( np.ceil( height * 0.5 - l ) ),
              int( np.floor( width * 0.5 + l ) ) , int( np.floor( height * 0.5 + l ) ) ]
    
    image = image[edges[0]:edges[2],edges[1]:edges[3]]

    return image




#######################################################################
#######################################################################
####                                                               ####
####                         LINEAR REGRESSION                     ####
####                                                               ####
#######################################################################
#######################################################################   

##  Usage:
##  x = oracle image  ,  y = image to analyze
##  you want to find the  yr |  yr = a*y + b  which minimizes  || a*y + b - x ||**2
##  the least square method is applied to solve it:
##      a = covariance( x , y ) / variance( y )
##      b = mean( x ) - a * mean( y )
##      yr = a * y + b

def linear_regression( x , y ):
    print('\nComputing linear regressed version of the image to analyze ....')

    ##  Take care that you are working with double precision
    x = x.astype(myfloat)  # oracle image
    y = y.astype(myfloat)  # image to be regressed

    
    ##  Calculate the mean values for both images
    mean_x = np.average(x)
    mean_y = np.average(y)

    
    ##  Calculate a,b that minimize || a*x + b - y ||**2
    ##  which is just a manual version of the least square method
    ##     a = covariance( x , y ) / variance( x ) 
    a = np.cov(x.reshape(-1),y.reshape(-1))[0,1]/(np.std(y))**2
    b = mean_x - a*mean_y
    print('yr = a*y + b  which minimizes  || a*y + b - x ||**2 ,'
          +' x = oracle image  ,  y = image to analyze')
    print('a = ', a,'   b = ', b)

    
    ##  Calculate predictor
    y = a*y + b 

    return y




#######################################################################
#######################################################################
####                                                               ####
####                    CROP REGION OF INTEREST                    ####
####                                                               ####
#######################################################################
#######################################################################

def crop_image( image , p0 , p1 ):
    x0 = np.min( [ p0[0] , p1[0] ] )
    x1 = np.max( [ p0[0] , p1[0] ] )
    
    y0 = np.min( [ p0[1] , p1[1] ] )
    y1 = np.max( [ p0[1] , p1[1] ] )
    
    return image[x0:x1,y0:y1]




#######################################################################
#######################################################################
####                                                               ####
####                        REGISTER 2 IMAGES                      ####
####                                                               ####
#######################################################################
#######################################################################

def local_sum( matrix , shape ):
    p1 = shape[0];  p2 = shape[1]
    p3 = matrix.shape[0] + 2 * p1;  p4 = matrix.shape[1] + 2 * p2
    matrix_pad = np.zeros( ( p3 , p4  ) )
    matrix_pad[ p1:p3-p1 , p2:p4-p2 ] = matrix
    s = np.cumsum( matrix_pad , axis=0 )
    c = s[p1:p3-1,:] - s[:p3-p1-1,:]
    s = np.cumsum( c , axis=1 )
    local_sum = s[:,p2:p4-1] - s[:,:p4-p2-1]
    return local_sum


def template_matching( img , oracle ):
    shape1 = np.array( img.shape ); shape2 = np.array( oracle.shape )
    shape3 = shape1 + shape2 - 1
    i1 = ( ( shape3 - shape1 ) * 0.5 ).astype( np.int )
    i2 = i1 + shape1 
   

    ##  Compute correlation in the frequency domain
    f_oracle = np.fft.fft2( np.rot90( oracle , 2 ) , shape3 )
    f_img = np.fft.fft2( img , shape3 )
    corr_map = np.real( np.fft.ifft2( f_oracle * f_img ) )


    ##  Compute local quadratic sum of image and template
    local_sum_img1 = local_sum( img * img , shape2 )
    local_sum_oracle = np.sum( oracle * oracle )

    
    ##  SSD map
    SSD_map = local_sum_img1 + local_sum_oracle - 2 * corr_map


    ##  Normalize SSD_map between 0 and 1
    SSD_map = SSD_map - np.min( SSD_map )
    SSD_map = 1 - ( SSD_map / np.max( SSD_map ) )


    ##  Unpad array
    SSD_map = SSD_map[i1[0]:i2[0],i1[1]:i2[1]]


    ##  Normalized cross correlation STD
    local_sum_img2 = local_sum( img , shape2 )
    aux = local_sum_img1 - local_sum_img2 * local_sum_img2 / \
                               np.float32( shape2[0] * shape2[1] ) 
    std_img = np.sqrt( np.clip( aux , 0 , np.max(aux) ) )
    std = np.sqrt(np.sum(np.abs(oracle - oracle.mean())**2)/(shape2[0]*shape2[1]-1)) 
    std_oracle = np.sqrt( shape2[0] * shape2[1] - 1 ) * std
    mean_img = local_sum_img2 * np.sum( oracle ) / ( shape2[0]*shape2[1] )
    NCC_map = 0.5 + ( corr_map - mean_img ) / \
              ( 2 * std_oracle * np.clip( std_img , std_oracle/1e5 , np.max( std_img ) ) )
    NCC_map = NCC_map[i1[0]:i2[0],i1[1]:i2[1]]

    return SSD_map , NCC_map



def align_image( image , vector ):
    image_new = np.roll( np.roll( image , vector[0] , axis=0 ) , vector[1] , axis=1 )
    
    if vector[0] > 0:
        image_new[:vector[0],:] = 0.0
    elif vector[0] < 0:
        image_new[image.shape[0]-np.abs(vector[0]):,:] = 0.0

    if vector[1] > 0:
        image_new[:,:vector[1]] = 0.0
    elif vector[1] < 0:
        image_new[:,image.shape[1]-np.abs(vector[1]):] = 0.0

    return image_new



def image_registration( imreg , imtempl , method ):
    nrows_h = int( imreg.shape[0] * 0.5 )
    ncols_h = int( imreg.shape[1] * 0.5 )   

    SSD_map , NCC_map = template_matching( imreg , imtempl ) 
    
    if method == 'ssd':
        pixel = np.argwhere( SSD_map == np.max( SSD_map ) )
    elif method == 'ncc':
        pixel = np.argwhere( NCC_map == np.max( NCC_map ) )  

    vector = pixel - np.array([ nrows_h , ncols_h ])
    vector = -vector          
    
    imreg_correct = align_image( imreg , vector[0] )

    return imreg_correct
