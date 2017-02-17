##########################################################
##########################################################
####                                                  ####
####                 ADD NOISE TO IMAGES              ####
####                                                  ####
##########################################################
##########################################################  




####  PYTHON MODULES
from __future__ import division , print_function
import argparse
import sys
import numpy as np
import glob
import os




####  MY I/O MODULES
sys.path.append( '../common/' )
import my_image_io as io
import my_image_display as dis




####  MY FORMAT VARIABLE
myfloat = np.float32




##########################################################
##########################################################
####                                                  ####
####             GET INPUT ARGUMENTS                  ####
####                                                  ####
##########################################################
##########################################################

def getArgs():
    parser = argparse.ArgumentParser(description='Add noise to images',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-Di', '--pathin', dest='pathin', default='./',
                        help='Specify path to input data')
    
    parser.add_argument('-Do', '--pathout', dest='pathout',
                        help='Specify path to output data')  
    
    parser.add_argument('-i', '--image', dest='image',
                        help='Specify name of input image')
    
    parser.add_argument('-l', '--label', dest='label',
                        help='Specify label of the input data')

    parser.add_argument('-n', '--noise', dest='noise', default='gaussian',
                        help='Specify kind of noise')    
    
    parser.add_argument('-s', '--sigma_list', dest='sigma_list',
                        default='60:70:80:90:100',
                        help='Specify number of noisy versions of each input image'
                             + ' and the array of sigma values as percentages of the'
                             + ' sigma of the input image (separated by a ":")')  
    
    parser.add_argument('-p',dest='plot', action='store_true',
                        help='Display check-plots during the run of the code')
    
    args = parser.parse_args()
    
    ##  Exit of the program in case of missing arguments
    if args.image is None and args.label is None:
        parser.print_help()
        sys.exit('ERROR: Input image name not specified!')  
    
    return args




##########################################################
##########################################################
####                                                  ####
####           ADD GAUSSIAN NOISE ROUTINE             ####
####                                                  ####
##########################################################
##########################################################  

def add_gaussian_noise( image , sigma ):
    if image.ndim == 2:
        nrows , ncols = image.shape
        noise = np.random.normal( loc=0 , scale=sigma , size=(nrows,ncols) )
    else:
        nz , nrows , ncols = image.shape
        noise = np.random.normal( loc=0 , scale=sigma , size=(nz,nrows,ncols) )         
    image[:] += noise
    return image




##########################################################
##########################################################
####                                                  ####
####            ADD POISSON NOISE ROUTINE             ####
####                                                  ####
##########################################################
##########################################################  

def add_poisson_noise( image ):
    if image.ndim == 2:
        nrows , ncols = image.shape
        noise = np.random.poisson( lam=image , size=(nrows,ncols) )
    else:
        nz , nrows , ncols = image.shape
        noise = np.random.poisson( lam=image , size=(nz,nrows,ncols) )         
    image[:] += noise
    return image




##########################################################
##########################################################
####                                                  ####
####                  WRITE OUTPUT IMAGE              ####
####                                                  ####
##########################################################
########################################################## 

def write_output_image( pathout , filein , image_noisy , label , sigma=None ):
    ext     = filein[len(filein)-4:] 
    fileout = filein[:len(filein)-4] + '_noise_' + label
                
    if label == 'gaussian':               
        if sigma < 1:
            fileout += '000' + str( int( sigma * 10 ) )  
        elif sigma < 10:
            fileout += '00' + str( int( sigma * 10 ) ) + '0'                
        elif sigma < 100:
            fileout += '0' + str( int( sigma * 10 ) ) + '0' 
        else:
            fileout += str( int( sigma * 10 ) ) + '0'
                                      
    fileout += ext
    fileout  = pathout + fileout
                
    io.writeImage( fileout , image_noisy ) 
    print( '\nOutput image written in:\n' , fileout )    




##########################################################
##########################################################
####                                                  ####
####                         MAIN                     ####
####                                                  ####
##########################################################
########################################################## 

def main():
    print('\nADD NOISE TO IMAGES\n')



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
    if args.image is not None:
        ##  Reading image
        filein  = args.image
        imagein = io.readImage( pathin + filein ).astype( myfloat )
        shape   = np.array( imagein.shape )
        print('\nReading image:\n', filein, '\n')  

        if len( shape ) == 2:
            dim = 2
            nrows , ncols = shape
            print('Image size: ', nrows,' X ', ncols)
            if args.plot is True:
                dis.plot( imagein , 'Input image' )
        else:
            dim = 3
            nz , nrows , ncols = shape
            print('Image size: ', nz , ' X ' , nrows,' X ', ncols)
            if args.plot is True:
                dis.plot( imagein[0,:,:] , 'Input image' ) 
        

        ##  Compute standard deviation of the image
        ##  and, subsequently, the gaussian sigmas
        if args.noise == 'gaussian':
            sigma = 0.5 * np.max( imagein )
        
            sigma_list = args.sigma_list
            sigma_list = np.array( sigma_list.split(':') , dtype=myfloat )
            nimg = len( sigma_list )

            sigma_arr = sigma * sigma_list / 100.0

            print('\nSigma of the input image: ', sigma)
            print('Sigma percentages: ', sigma_list)
            
        elif args.noise == 'poisson':
            nimg = 1
            
        else:
            sys.exit( '\nERROR: Noise type "' + args.noise +'" is not an option available with this routine!\n' )


        ##  Loop on each gaussian sigma
        for im in range( nimg ):
            ##  Add noise
            if args.noise == 'gaussian':
                image_noisy = add_gaussian_noise( imagein , sigma_arr[im] )
                label = 'gauss'
                write_output_image( pathout , filein , image_noisy , label , sigma=sigma_list[im] )
                
            elif args.noise == 'poisson':
                image_noisy = add_poisson_noise( imagein )
                label = 'poiss'
                write_output_image( pathout , filein , image_noisy , label )    


            ##  Check noisy image
            if args.plot is True:
                if dim == 2:
                    if args.noise == 'gaussian':
                        dis.plot( image_noisy , 'Gaussian noisy image -- sigma: ' + str( sigma_list[im] ) )
                    elif args.noise == 'poisson':
                        dis.plot( image_noisy , 'Poisson noisy image' ) 
                else:
                    if args.noise == 'gaussian':
                        dis.plot( image_noisy[0,:,:] , 'Gaussian noisy image -- sigma: ' + str( sigma_list[im] ) )
                    elif args.noise == 'poisson':
                        dis.plot( image_noisy[0,:,:] , 'Poisson noisy image' )      

    
    ##  Get bunch of input images
    elif args.label is not None:
        curr_dir = os.getcwd()

        ##  Reading images
        os.chdir( pathin )
        files = sorted( glob.glob( '*' + args.label + '*' ) )
        os.chdir( curr_dir )

        num_im_input = len( files )

        for i in range( num_im_input ):
            imagein = io.readImage( pathin + files[i] ).astype( myfloat )
            nrows , ncols = imagein.shape
            
            print('\nReading image:\n', files[i])
            print('Image size: ', nrows,' X ', ncols)  
                
                
            ##  Compute standard deviation of the image
            ##  and, subsequently, the gaussian sigmas
            sigma = np.mean( imagein )
            if sigma == 0:
                sigma = 1.0
        
            sigma_list = args.sigma_list
            sigma_list = np.array( sigma_list.split(':') , dtype=myfloat )
            nimg = len( sigma_list )

            sigma_arr = sigma * sigma_list / 100.0

            print('\nSigma of the input image: ', sigma)
            print('Sigma percentages: ', sigma_list)
            print('Gaussian sigma values: ', sigma_arr)


            ##  Add noise ##  Loop on each gaussian sigma
            if args.noise == 'gaussian':
                for im in range( nimg ):
                    ##  Loop on each gaussian sigma
                    image_noisy = add_gaussian_noise( imagein , sigma_arr[im] )
                    label = 'gauss'
                    write_output_file( pathout , files[i] , image_noisy , label , sigma=sigma_arr[im] )
                    
                    
            elif args.noise == 'poisson':
                image_noisy = add_poisson_noise( imagein )
                label = 'poiss'
                write_output_file( pathout , files[i] , image_noisy , label )

    print('\n\n')




##########################################################
##########################################################
####                                                  ####
####                    CALL TO MAIN                  ####
####                                                  ####
##########################################################
########################################################## 

if __name__ == '__main__':
	main()
