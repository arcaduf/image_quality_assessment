###########################################################
###########################################################
####                                                   ####
####        CALCULATE STRUCTURAL SIMILARITY INDEX      ####
####                                                   ####
#### Adaptation of the python code of Antoine Vacavant ####
#### available at the webpage:                         ####
####   http://isit.u-clermont1.fr/~anvacava/code.html  ####
####                                                   ####  
#### Reference:                                        ####
#### "Image Quality Assessment: From Error Visibility  ####
####  to Structural Similarity", Z.Whang, A.C.Bovik et ####
####  al., IEEE Transactions on image processing, Vol. ####
####  13, No. 4, April 2004.                           ####
####                                                   ####
####    Author: Filippo Arcadu, arcusfil@gmail.com,    ####
####                     11/11/2013                    ####
####                                                   ####
###########################################################
###########################################################




####  PYTHON MODULES
from __future__ import print_function,division
import time
import argparse
import sys
import os
import glob
import datetime
import numpy as np
import scipy.optimize
import scipy.ndimage as scim




####  MY MODULES
sys.path.append( '../common/' )
import my_image_io as io 
import my_image_display as dis
import my_image_process as proc




####  MY VARIABLES
myfloat = np.float64




####  MY CONSTANTS
SIGMA = 1.5




###########################################################
###########################################################
####                                                   ####
####                 GET INPUT ARGUMENTS               ####                 
####                                                   ####
###########################################################
###########################################################  

def getArgs():
    parser = argparse.ArgumentParser(description='Calculates the structure' +
                                    ' similarity index (SSIM) between two images.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i1','--image1',dest='image1',
                        help = 'Select reference image')
    
    parser.add_argument('-i2','--image2',dest='image2',
                        help = 'Select an image / images to analyze; if'
                        + ' more images are selected use a ":" to separate them')
    
    parser.add_argument('-s','--scaling',dest='scaling',action='store_true',
                        help = 'Enable scaling procedure to fit the interval'
                        +'of grey values to the image/s to analyze with that of'
                        +' the reference image')
    
    parser.add_argument('-t','--register',dest='register',action='store_true',
                        help = 'Enable registration of the image to be analized'
                        +' with the oracle')  
    
    parser.add_argument('-c','--resol_circle',dest='resol_circle',action='store_true',
                        help = 'Enable analisys only inside the resolution circle')      

    parser.add_argument('-r','--roi',dest='roi',
                        help = 'Select vertices of the region of interest; e.g. -r x0:y0,x1:y1'
                        + ' or select roi-file: e.g. -r path/file')

    parser.add_argument('-g','--grad',dest='gradient', action='store_true',
                        help = 'Run the analysis on the gradient images of the inputs')  

    parser.add_argument('-w','--window',dest='window',type=int,default=11,
                        help = 'Select size of the computation window')   
    
    parser.add_argument('-p','--plot',dest='plot',action='store_true',
                        help='Enable plots to check whether the orientation'
                        +' of the images is correct')

    parser.add_argument('-i3',dest='logpath',
                        help='Specify path for logfile')  

    parser.add_argument('-l',dest='log',action='store_true',
                        help='Enable extensed logfile')   

    args = parser.parse_args()
    
    if args.image1 is None:
        parser.print_help()
        sys.exit('\nERROR: Reference image not specified!\n')
    
    if args.image2 is None and args.path is None:
        parser.print_help()
        sys.exit('\nERROR: Neither single image nor bunch of images'
                 + ' to analyze specified!\n')     
    
    return args




###########################################################
###########################################################
####                                                   ####
####               COMPUTE GRADIENT IMAGE              ####                 
####                                                   ####
###########################################################
###########################################################

def compute_gradient_image( image ):
    grad_image = np.gradient( image )
    grad_image = np.array( grad_image ).reshape( 2 , image.shape[0] , image.shape[1] )
    sqr_grad_image = np.sqrt( grad_image[0,:,:]**2 + grad_image[1,:,:]**2 )
    return sqr_grad_image




###########################################################
###########################################################
####                                                   ####
####             INITIALIZE GAUSSIAN KERNEL            ####                 
####                                                   ####
###########################################################
########################################################### 

def init_gaussian_kernel( l , sigma ):
    gauss_kernel = np.zeros( ( l,l) , dtype=myfloat )
    c = 0.5 * (l-1)
    for i in range( l ):
        for j in range( l ):
            gauss_kernel[i,j] = ( 1 / ( 2*np.pi*sigma**2 ) ) * \
                               np.exp(-(((i-c)**2)+((j-c)**2)) / (2*sigma**2) )
    
    ##  Normalize coefficients
    totalSum = np.sum( gauss_kernel )
    gauss_kernel *= 1.0 / totalSum

    return gauss_kernel




###########################################################
###########################################################
####                                                   ####
####              COMPUTE MAP OF SSIM VALUES           ####                 
####                                                   ####
###########################################################
########################################################### 

def compute_map_ssim( image1 , image2 , window_size , sigma ):
    ## Initialize normalized circular-symmetric gaussian kernel
    print('\nInitialize gaussian kernel ....')
    gauss_kernel = init_gaussian_kernel( window_size , sigma )


    ## Calculate maps of mean values
    # convolution perform with scipy.ndimage.filters.convolve because
    # numpy.convolve does not support convolutions between matrices;
    # scipy.ndimage.filters.convolve treats, by default, the boundaries
    # with pixel reflection (see reference literature) 
    print('\nCalculating map of mean values ....')
    image_mean1 = scim.filters.convolve( image1 , gauss_kernel )
    image_mean2 = scim.filters.convolve( image2 , gauss_kernel )
    print('Shape of mean values map: ', image_mean1.shape)

    # compute the squares of the maps of mean values
    image_mean_sqr1 = image_mean1 * image_mean1
    image_mean_sqr2 = image_mean2 * image_mean2
    image_mean12 = image_mean1 * image_mean2 


    ## Calculate maps of standard deviations and map of covariances
    # convolution perform with scipy.ndimage.filters.convolve because
    # numpy.convolve does not support convolutions between matrices;
    # scipy.ndimage.filters.convolve treats, by default, the boundaries
    # with pixel reflection (see reference literature)
    print('\nCalculating map of standard deviations values ....')
    image_std1 = scim.filters.convolve( image1 * image1 , gauss_kernel ) - image_mean_sqr1 
    image_std2 = scim.filters.convolve( image2 * image2 , gauss_kernel ) - image_mean_sqr2
    image_cov = scim.filters.convolve( image1 * image2 , gauss_kernel ) - image_mean12
    print('Shape of std values map: ', image_std1.shape)


    ## Calculate map of SSIM indeces
    # Select the parameters C1, C2 to stabilize the calculation
    # of the SSIM indeces
    K = 0.001
    L = 0.5 * ( np.abs(np.max(image1)-np.min(image1)) + \
        np.abs(np.max(image2)-np.min(image2)) )
    C1 = ( K * L ) ** 2
    C2 = ( K * L ) ** 2
    print('\nParameters to calculate the SSIM indeces:')
    print('K = ', K,'   L = ', L,'   C1 = ', C1,'   C2 = ', C2)

    # apply SSIM formula presented
    print('\nCalculating map of SSIM values ....')
    map_ssim = (( 2*image_mean12 + C1 ) * ( 2*image_cov + C2 )) / \
              (( image_mean_sqr1 + image_mean_sqr2 + C1 ) * ( image_std1 + image_std2 + C2 ));
    print('.... calculation done!')

    # calculate the mean value of the SSIM map
    MSSIM = np.average( map_ssim )
    print('\nMSSIM (mean value of the SSIM map) = ', MSSIM)

    return map_ssim , MSSIM




###########################################################
###########################################################
####                                                   ####
####                  WRITE LOG FILE                   ####                 
####                                                   ####
###########################################################
########################################################### 

def write_log_file( args , image_list , results ):
    ##  Open the file
    if args.logpath is None:
        fileout = args.image2[:len(args.image2)-4] + '_ssim_analysis.txt'
    else:
        logpath = args.logpath
        if logpath[len(logpath)-1] != '/':
            logpath += '/'
        chunks = args.image2[:len(args.image2)-4].split( '/' )
        name   = chunks[len(chunks)-1]
        fileout = logpath + name + '_snr.txt'          
    fp = open( fileout , 'w' )  


    if args.log is True:
        ##  Initial logo
        fp.write('\n')
        fp.write('\n#######################################')
        fp.write('\n#######################################') 
        fp.write('\n###                                 ###')
        fp.write('\n###   STRUCTURE SIMILARITY INDEX    ###')
        fp.write('\n###                                 ###')
        fp.write('\n#######################################')
        fp.write('\n#######################################') 
        fp.write('\n')


        ##  Date
        today = datetime.datetime.now()
        fp.write('\nSSIM calculation performed on the '
                      + str(today))   


        ##  Print oracle image file
        fp.write('\n\nReading reference image:\n' + args.image1)


        ##  Linear regression
        if args.scaling is True:
            fp.write('\n\nLinear regression option enabled')


        ##  Image registration
        if args.register is True:
            fp.write('\n\nImage registration option enabled')


        ##  Select resolution circle
        if args.resol_circle is True:
            fp.write('\n\nSelecting the resolution circle')

    
    ##  Summary of the results
    num_img = len( image_list )
    for i in range( num_img ):
        if args.log is True:
            fp.write('\n\nTest image number ' + str( i ) + '\n' + image_list[i])
        fp.write('\nSSIM = ' + str( results[i] ) )

    fp.write('\n')


    ##  Close the file
    fp.close()




###########################################################
###########################################################
####                                                   ####
####                      CHECK PLOT                   ####
####                                                   ####
###########################################################
###########################################################

##  Routine to display 1 or more images in gray scale with
##  the origin placed at the left bottom corner and with the
##  possibility to display the pixel value by moving the cursor;
##  in input, you can give a list of image arrays , a list of
##  titles for the subplots and one title for the entire plot

def plot( img , title=None , colorbar=True , axis=True ):
    
    ##  Initialize figure enviroment
    fig = plt.figure()

    ax = fig.add_subplot( 111 )
        
    ax.imshow(  img , origin="lower" ,
                cmap = cm.Greys_r ,
                interpolation='nearest' )
    
    def format_coord( x , y):
        nrows, ncols = img.shape
        col = int(x+0.5)
        row = int(y+0.5)
    
        if col>=0 and col<ncols and row>=0 and row<nrows:
            z = img[row,col]
            return 'x=%d, y=%d, value=%1.4e'%(x, y, z)
        else:
            return 'x=%d, y=%d'%(x, y)   

    ax.format_coord = format_coord

    plt.ylim([0.0,1.0])

    #if colorbar is True:
    #    plt.colorbar()

    if axis is False:
        plt.axis( 'off' )

    if title is not None:
        plt.suptitle( title , fontsize=20 )

    plt.show()




###########################################################
###########################################################
####                                                   ####
####                         MAIN                      ####                 
####                                                   ####
###########################################################
###########################################################

def main():
    print('\n')
    print('#######################################')
    print('#######################################') 
    print('###                                 ###')
    print('###   STRUCTURAL SIMILARITY INDEX   ###')
    print('###                                 ###')
    print('#######################################')
    print('#######################################') 
    print('\n')

    
    
    ##  Get input arguments
    args = getArgs()



    ## Get oracle image
    currDir = os.getcwd()
    image1 = io.readImage( args.image1 )
    image1 = image1.astype( myfloat )

    print('\nReading reference image:\n', args.image1)
    print('Image shape: ', image1.shape)


    image_list = []
    results = []

    
    
    ##  CASE OF SINGLE IMAGE TO ANALYZE
    if args.image2 is not None:
        if args.image2.find( ':' ) == -1:
            image_list.append( args.image2 )
            image2 = io.readImage( args.image2 )  # image2 --> image to analyze
            image2 = image2.astype(myfloat)
            num_img = 1

            print('\nReading image to analyze:\n', args.image2)
            print('Image shape: ', image2.shape)


            ## Get time in which the prgram starts to run
            time1 = time.time()      


            ##  Scale image to analyze with respect to the reference one
            if args.scaling is True:
                print('\nPerforming linear regression ....')
                image2 =  proc.linear_regression( image1 , image2 )


            ##  Register images
            if args.register is True:
                print('\nPerforming registration of the image to analize ....')
                image2 = proc.image_registration( image2 , image1 , 'ssd' )


            ##  Crop resolution circle of the images
            if args.resol_circle is True:
                print('\nSelecting the resolution circle')
                image1 = proc.select_resol_square( image1 )
                image2 = proc.select_resol_square( image2 )                

            ##  Crop images if enabled
            if args.roi is not None:
                roi = args.roi

                if roi.find( ':' ) != -1:
                    roi = roi.split(',')
                    p0 = [int(roi[0].split(':')[1]),int(roi[0].split(':')[0])]
                    p1 = [int(roi[1].split(':')[1]),int(roi[1].split(':')[0])]
                
                    print('Cropping rectangular ROI with vertices:  ( ', \
                            p0[0],' , ', p0[1], ')   ( ', p1[0],' , ',p1[1], ')')
                
                    image1 = proc.crop_image( image1 , p0 , p1 )
                    image2 = proc.crop_image( image2 , p0 , p1 )

                else:
                    print('\nUsing pixels specified in file:\n', roi) 
                    pixels = np.loadtxt( roi )
                    pixels = pixels.astype( int )
                    p0 = np.array([pixels[0,0],pixels[0,1]])
                    p1 = np.array([pixels[len(pixels)-1,0],pixels[len(pixels)-1,1]])       
                        
                    print('Cropping rectangular ROI with vertices:  ( ', \
                            p0[0],' , ', p0[1], ')   ( ', p1[0],' , ',p1[1], ')')
                
                    image1 = proc.crop_image( image1 , p0 , p1 )
                    image2 = proc.crop_image( image2 , p0 , p1 )


            ##  Compute the gradient of the images, if enabled
            if args.gradient is True:
                image1 = compute_gradient_image( image1 )
                image2 = compute_gradient_image( image2 )


            ##  Check whether the 2 images have the same shape
            if image1.shape != image2.shape:
                sys.error('\nERROR: The input images have different shapes!\n')


            ##  Plot to check whether the images have the same orientation
            if args.plot is True:
                print('\nPlotting images to check orientation ....')
                img_list = [ image1 , image2 ]
                title_list = [ 'Oracle image' , 'Image to analyze' ]
                dis.plot_multi( img_list , title_list , 'Check plot' )        


            ##  Get window size
            window_size = args.window
            print('\nSize of the computation window: ', window_size)
            
            if window_size % 2 != 0:
                window_size += 1
                print('Window size is even: window size changed to ', window_size)
            
            
            ##  Get sigma of the gaussian kernel
            sigma = SIGMA
            print('Sigma of the gaussian kernel: ', sigma)


            ## Calculate map of SSIM values
            map_ssim , MSSIM = compute_map_ssim( image1 , image2 , window_size , sigma )
            results.append( MSSIM )

            if args.plot is True:
                print('\nPlotting images + map of ssim ....')
                img_list = [ image1 , image2 , map_ssim ]
                title_list = [ 'Oracle image' , 'Image to analyze' , 'Map of SSIM' ]
                dis.plot_multi( img_list , title_list , 'Images and map of SSIM'  )

            
            ##  Save SSIM map 
            filename = args.image2[:len(args.image2)-4] + '_ssim_map.png'
            io.writeImage( filename , map_ssim )


        
        ##  CASE OF MULTIPLE SPECIFIC IMAGES
        else:
            image_list = args.image2.split(':')
            img_list = [ ]
            title_list = [ ]
            num_img = len( image_list )

            for im in range( num_img ):
                img_file = image_list[im]
                image1 = io.readImage( args.image1 )
                image2 = io.readImage( img_file )  # image2 --> image to analyze
                image2 = image2.astype(myfloat)
                print('\nReading image to analyze:\n', args.image2)
                print('Image shape: ', image2.shape)

                
                ##  Get time in which the prgram starts to run
                time1 = time.time()      


                ##  Scale image to analyze with respect to the reference one
                if args.scaling is True:
                    print('\nPerforming linear regression ....')
                    image2 =  proc.linearRegression( image1 , image2 )


                ##  Register images
                if args.register is True:
                    print('\nPerforming registration of the image to analize ....') 
                    image2 = proc.image_registration( image2 , image1 , 'ssd' ) 


                ##  Crop resolution circle of the images
                if args.resol_circle is True:
                    print('\nSelecting the resolution circle')
                    image1 = proc.selectResolutionSquare( image1 )
                    image2 = proc.selectResolutionSquare( image2 )

                
                ##  Crop images if enabled
                if args.roi is not None:
                    roi = args.roi

                    if args.roi.find(',') != -1:
                        roi = roi.split(',')
                        p0 = [int(roi[0].split(':')[1]),int(roi[0].split(':')[0])]
                        p1 = [int(roi[1].split(':')[1]),int(roi[1].split(':')[0])]
                
                        print('Cropping rectangular ROI with vertices:  ( ', \
                                p0[0],' , ', p0[1], ')   ( ', p1[0],' , ',p1[1], ')')
                
                        image1 = proc.crop_image( image1 , p0 , p1 )
                        image2 = proc.crop_image( image2 , p0 , p1 )

                    else:
                        print('\nUsing pixels specified in file:\n', roi) 
                        pixels = np.loadtxt( roi )
                        pixels = pixels.astype( int )
                        p0 = np.array([pixels[0,0],pixels[0,1]])
                        p1 = np.array([pixels[len(pixels)-1,0],pixels[len(pixels)-1,1]])       
                        
                        print('Cropping rectangular ROI with vertices:  ( ', \
                                p0[0],' , ', p0[1], ')   ( ', p1[0],' , ',p1[1], ')')
                
                        image1 = proc.crop_image( image1 , p0 , p1 )
                        image2 = proc.crop_image( image2 , p0 , p1 )     
                

                ##  Compute the gradient of the images, if enabled
                if args.gradient is True:
                    image1 = compute_gradient_image( image1 )
                    image2 = compute_gradient_image( image2 )


                ##  Check whether the 2 images have the same shape
                if image1.shape != image2.shape:
                    sys.exit('\nERROR: The input images have different shapes!\n')


                ##  Plot to check whether the images have the same orientation
                if args.plot is True:
                    print('\nPlotting images to check orientation ....')
                    img_list2 = [ image1 , image2 ]
                    title_list2 = [ 'Oracle image' , 'Image to analyze' ]
                    dis.plot_multi( img_list2 , title_list2 , 'Check plot' )   

                
                ##  Get window size
                window_size = args.window
                print('\nSize of the computation window: ', window_size)
                
                if window_size % 2 != 0:
                    window_size += 1
                    print('Window size is even: window size changed to ', window_size)
                
                
                ##  Get sigma of the gaussian kernel
                sigma = SIGMA
                print('Sigma of the gaussian kernel: ', sigma)


                ##  Calculate map of SSIM values
                map_ssim , MSSIM = compute_map_ssim( image1 , image2 , window_size , sigma )
                results.append( MSSIM )

                map_ssim[ map_ssim < 0 ] = 0.0

                if args.plot is True:
                    img_list.append( map_ssim )
                    title_list.append( 'SSIM map n.' + str( im + 1 ) )

                
                ##  Save SSIM map 
                filename = img_file[:len(img_file)-4] + '_ssim_map.png'
                io.writeImage( filename , map_ssim )
                
            if args.plot is True:
                print('\nPlotting images + map of ssim ....')
                dis.plot( img_list[0] )
                dis.plot( img_list[1] )
                dis.plot_multi_colorbar( img_list , title_list , 'Maps of SSIM' ) 



    ##  CASE OF BUNCH OF IMAGES TO ANALYZE 
    else:
        os.chdir(args.path)
        image_list = sorted( glob.glob('*') )
        num_images = len( image_list )
        img_list.append( image1 )
        title_list.append('Oracle image') 

        
        ##  Get time in which the prgram starts to run
        time1 = time.time()


        ##  Loop on all the images to analyze
        for i in range( num_img ):
            image1 = io.readImage( args.image1 ) 
            image2 = io.readImage( image_list[i] )
            image2 = image2.astype(myfloat)

            print('\n\n\nIMAGE TO ANALYZE NUMBER: ', i)
            print('\nReading image to analyze:\n', fileIn[i])
            print('Image shape: ', image2.shape)

            
            ##  Scale image to analyze with respect to the reference one
            if args.scaling is True:
                print('\nPerforming linear regression ....')  
                image2 = proc.linearRegression( image1 , image2 )


            ##  Register images
            if args.register is True:
                print('\nPerforming registration of the image to analize ....') 
                image2 = proc.image_registration( image2 , image1 , 'ssd' )


            ##  Crop resolution circle of the images
            if args.resol_circle is True:
                print('\nSelecting the resolution circle')
                image1 = proc.selectResolutionSquare( image1 )
                image2 = proc.selectResolutionSquare( image2 ) 


            ##  Crop images if enabled
            if args.roi is not None:
                roi = args.roi

                if args.roi.find(',') != -1:
                    roi = roi.split(',')
                    p0 = [int(roi[0].split(':')[1]),int(roi[0].split(':')[0])]
                    p1 = [int(roi[1].split(':')[1]),int(roi[1].split(':')[0])]
                
                    print('Cropping rectangular ROI with vertices:  ( ', \
                            p0[0],' , ', p0[1], ')   ( ', p1[0],' , ',p1[1], ')')
                
                    image1 = proc.crop_image( image1 , p0 , p1 )
                    image2 = proc.crop_image( image2 , p0 , p1 )

                else:
                    print('\nUsing pixels specified in file:\n', roi) 
                    pixels = np.loadtxt( roi )
                    pixels = pixels.astype( int )
                    p0 = np.array([pixels[0,0],pixels[0,1]])
                    p1 = np.array([pixels[len(pixels)-1,0],pixels[len(pixels)-1,1]])       
                        
                    print('Cropping rectangular ROI with vertices:  ( ', \
                            p0[0],' , ', p0[1], ')   ( ', p1[0],' , ',p1[1], ')')
                
                    image1 = proc.crop_image( image1 , p0 , p1 )
                    image2 = proc.crop_image( image2 , p0 , p1 )    


            ##  Compute the gradient of the images, if enabled
            if args.gradient is True:
                image1 = compute_gradient_image( image1 )
                image2 = compute_gradient_image( image2 )


            ##  Check whether the 2 images have the same shape
            if image1.shape != image2.shape and args.roi is None:
                sys.error('\nERROR: The input images have different shapes!\n')


            ##  Plot to check whether the images have the same orientation
            if args.plot is True:
                print('\nPlotting images to check orientation ....')
                img_list = [ image1 , image2 ]
                title_list = [ 'Oracle image' , 'Image to analyze' ]
                dis.plot_multi( img_list , title_list , 'Check plot' )    


            ##  Get window size
            window_size = args.window
            print('\nSize of the computation window: ', window_size)
            
            if window_size % 2 != 0:
                window_size += 1
                print('Window size is even: window size changed to ', window_size)
            
            
            ##  Get sigma of the gaussian kernel
            sigma = SIGMA
            print('Sigma of the gaussian kernel: ', sigma)


            ##  Calculate map of SSIM values
            map_ssim,MSSIM = compute_map_ssim( image1 , image2 , window_size , sigma )
            results.append( MSSIM )


            ##  Diplay map of SSIM
            if args.plot is True:
                fig = plt.figure()
                plt.title('Map of SSIM indeces')
                plt.imshow(map_ssim,cmap = cm.Greys_r)
                #plt.colorbar()
                plt.show()


            ##  Save SSIM map
            filename = image_list[i][:len(image_list[i])-4] + '_ssim_map.png'
            io.writeImage( filename , map_ssim )
        os.chdir(currDir)



    ##  Summary print of the results
    print('\n\nSUMMARY OF THE RESULTS:\n')
    print('\nReference image:\n', args.image1)

    for i in range( num_img ):
        print('\n\nTest image number ', i,'\n', image_list[i],'\n')
        print('SSIM = ' , results[i])



    ##  Get time elapsed for the run of the program
    time2 = time.time() - time1
    print('\n\nTime elapsed for the calculation: ', time2)



    ##  Write log file
    write_log_file( args , image_list , results )


    print('\n\n')




###########################################################
###########################################################
####                                                   ####
####                    CALL TO MAIN                   ####                 
####                                                   ####
###########################################################
###########################################################   

if __name__ == '__main__':
    main()
