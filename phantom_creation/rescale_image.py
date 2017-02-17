##########################################################
##########################################################
####                                                  ####
####                    RESCALE IMAGE                 ####
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
from scipy import ndimage




####  MY I/O MODULES
sys.path.append( '../common/' )
import my_image_io as io
import my_image_display as dis




####  MY FORMAT VARIABLE
myfloat = np.float32
myint = np.int




##########################################################
##########################################################
####                                                  ####
####             GET INPUT ARGUMENTS                  ####
####                                                  ####
##########################################################
##########################################################

def getArgs():
    parser = argparse.ArgumentParser(description='Rescale image',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-Di', '--pathin', dest='pathin', default='./',
                        help='Specify path to input data')
    
    parser.add_argument('-Do', '--pathout', dest='pathout',
                        help='Specify path to output data')  
    
    parser.add_argument('-i', '--image', dest='image',
                        help='Specify name of input image')
    
    parser.add_argument('-l', '--label', dest='label',
                        help='Specify label of the input data')
    
    parser.add_argument('-z', '--rescale', dest='rescale', type=myfloat,
                        help='Specify the rescaleing factor: > 1.0 to enlarge the image,'
                        + ' < 1.0 for the viceversa')

    parser.add_argument('-q', '--square', dest='square', action='store_true',
                        help='Make the image square with side equal to the ' \
                             'smallest one of the original image')   

    parser.add_argument('-n', '--npix', dest='npix', type=myint,
                        help='Specify the number of pixels that the image should have') 
    
    parser.add_argument('-p',dest='plot', action='store_true',
                        help='Display check-plots during the run of the code')
    
    args = parser.parse_args()
    
    if args.image is None and args.label is None:
        parser.print_help()
        sys.exit('ERROR: Input image name not specified!')
  
    if args.rescale is None and args.npix is None:
        parser.print_help()
        sys.exit('ERROR: Neither rescaleing factor nor new number of pixels \
                  were specified!') 
    
    return args




##########################################################
##########################################################
####                                                  ####
####                    ZOOM IMAGE                    ####
####                                                  ####
##########################################################
##########################################################  

def rescale_image( image , rescale ):
    image_rescale = ndimage.zoom( image , rescale )  
    return image_rescale




##########################################################
##########################################################
####                                                  ####
####                         MAIN                     ####
####                                                  ####
##########################################################
########################################################## 

def main():
    print('\nRESCALE IMAGE\n')



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
        filein = args.image
        imagein = io.readImage( pathin + filein )
        nrows , ncols = imagein.shape[0] , imagein.shape[1]
        
        print('\nReading image:', filein)
        print('Image size: ', nrows,' X ', ncols)


        ##  Check plot
        if args.plot is True:
            dis.plot( imagein , 'Input image' )
        

        ##  Make image square
        if args.square is True:
            if nrows < ncols:
                imagein = imagein[:,:nrows]
            else:
                imagein = imagein[:ncols,:]    


        ##  Rescaled image
        if args.rescale is not None:
            rescale = args.rescale
            nrows_new = int( nrows * rescale )
            ncols_new = int( ncols * rescale )

        else:
            nrows_new = ncols_new = args.npix
            rescale = nrows_new / myfloat( nrows )

        image_rescale = rescale_image( imagein , rescale )

        print('\nRescaled factor: ', rescale)
        print('Rescaled-image size: ', image_rescale.shape)


        ##  Check plot
        if args.plot is True:
            dis.plot( image_rescale , 'Rescaled image -- factor = ' 
                                         + str( rescale ) ) 

            
        ##  Write noisy image to file
        fileout = filein[:len(filein)-4] + '_pix' 
        if nrows_new < 100:
            fileout += '00' + str( nrows_new ) + '.DMP'
        elif nrows_new < 1000:
            fileout += '0' + str( nrows_new ) + '.DMP'
        else:
            fileout += str( nrows_new ) + '.DMP' 

        io.writeImage( pathout + fileout , image_rescale )
        print('\nWriting rescaled image:', fileout)          


    
    ##  Get bunch of input images
    elif args.label is not None:
        curr_dir = os.getcwd()

        ##  Reading images
        os.chdir( pathin )
        files = sorted( glob.glob( '*' + args.label + '*' ) )
        os.chdir( curr_dir )

        num_im_input = len( files )

        for i in range( num_im_input ):
            imagein = io.readImage( pathin + files[i] )
            nrows , ncols = imagein.shape[0] , imagein.shape[1]
            
            print('\nReading image:\n', files[i])
            print('\nImage size: ', nrows,' X ', ncols)


            ##  Make image square
            if args.square is True:
                if nrows < ncols:
                    imagein = imagein[:,:nrows]
                else:
                    imagein = imagein[:ncols,:]


            ##  Rescaled image
            if args.rescale is not None:
                rescale = args.rescale
                nrows_new = int( nrows * rescale )
                ncols_new = int( ncols * rescale )

            else:
                nrows_new = ncols_new = args.npix
                rescale = nrows_new / myfloat( nrows )

            image_rescale = rescale_image( imagein , rescale )

            print('\nRescaled factor: ', rescale)
            print('Rescaled-image size: ', image_rescale.shape)                   
                
            
            ##  Write noisy image to file
            fileout = files[i][:len(files[i])-4] + '_pix' 
            if nrows_new < 100:
                fileout += '00' + str( nrows_new ) + '.DMP'
            elif nrows_new < 1000:
                fileout += '0' + str( nrows_new ) + '.DMP'
            else:
                fileout += str( nrows_new ) + '.DMP' 

            io.writeImage( pathout + fileout , image_rescale )
            print('\nWriting rescaled image:', fileout)  
    
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
