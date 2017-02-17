###########################################################
###########################################################
####                                                   ####
####       CALCULATE NORMALIZED MUTUAL INFORMATION     ####
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




####  MY MODULES
sys.path.append( '../common/' )
import my_image_io as io 
import my_image_display as dis
import my_image_process as proc




####  MY VARIABLES
myFloat = np.float64




####  CONSTANTS
eps = 1e-5




###########################################################
###########################################################
####                                                   ####
####                 GET INPUT ARGUMENTS               ####                 
####                                                   ####
###########################################################
###########################################################  

def getArgs():
    parser = argparse.ArgumentParser(description='Calculates the normalized' +
                                    ' mutual information (NMI) between two images.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i1', '--image1', dest='image1',
                        help = 'Select reference image')
    
    parser.add_argument('-i2', '--image2', dest='image2',
                        help = 'Select an image / images to analyze; if'
                        + ' more images are selected use a ":" to separate them')
    
    parser.add_argument('-c', '--resol_circle', dest='resol_circle', action='store_true',
                        help = 'Enable analisys only inside the resolution circle')      

    parser.add_argument('-r', '--roi', dest='roi',
                        help = 'Select vertices of the region of interest; e.g. -r x0:y0,x1:y1'
                        + ' or select roi-file: e.g. -r path/file')  

    parser.add_argument('-b', '--nbins', dest='nbins', type=np.int, default=256,
                        help = 'Enable analisys only inside the resolution circle')  
    
    parser.add_argument('-o', '--fileout', dest='fileout',
                        help='Select an output text file with the'
                        +' outcomes of the SSIM calculation')

    parser.add_argument('-s','--scaling',dest='scaling',action='store_true',
                        help = 'Enable scaling procedure to fit the interval'
                        +'of grey values to the image/s to analyze with that of'
                        +' the reference image')  

    parser.add_argument('-p', '--plot', dest='plot', action='store_true',
                        help='Enable plots to check whether the orientation'
                        +' of the images is correct')

    parser.add_argument('--save', dest='save',
                        help='Specify the name of the plot of the SSIM map')       
                        
    args = parser.parse_args()
    
    if args.image1 is None:
        parser.print_help()
        sys.exit('\nERROR: Reference image not specified!\n')
    
    if args.image2 is None and args.path is None:
        parser.print_help()
        sys.exit('\nERROR: Neither single image nor bunch of images'
                 + ' to analyze specified!\n')     
    
    if args.fileout is None:
        print('\nWarning: no output text file specified\n')

    return args




###########################################################
###########################################################
####                                                   ####
####        COMPUTE NORMALIZED MUTUAL INFORMATION      ####                 
####                                                   ####
###########################################################
########################################################### 

def computeNMI( image1 , image2 , nbins ):
    ##  Allocate memory for the quantized versions of the input images
    nrows , ncols = image1.shape
    imq1 = np.zeros( ( nrows , ncols ) , dtype=np.int )
    imq2 = np.zeros( ( nrows , ncols ) , dtype=np.int )    


    ##  Quantize images  with the given number of bins
    min1 = np.min( image1 );  max1 = np.max( image1 )
    min2 = np.min( image2 );  max2 = np.max( image2 )

    imq1[:,:] = np.array( ( image1 - min1 ) * ( nbins - 1 ) / ( max1 - min1 ) ).astype( np.int )
    imq2[:,:] = np.array( ( image2 - min2 ) * ( nbins - 1 ) / ( max2 - min2 ) ).astype( np.int )


    ##  Create normalized histograms of the quantized images
    histo1 , bin_edges = np.histogram( imq1 , nbins )
    histo2 , bin_edges = np.histogram( imq2 , nbins )

    ind = np.argwhere( histo1 != 0 )
    histo1 = np.array( histo1[ind] ).astype( np.float32 )

    ind = np.argwhere( histo2 != 0 )
    histo2 = np.array( histo2[ind] ).astype( np.float32 )      


    histo1 /= np.float( nrows * ncols )
    histo2 /= np.float( nrows * ncols )


    ##  Compute entropies
    H1 = -np.sum( histo1 * np.log2( histo1 ) )
    H2 = -np.sum( histo2 * np.log2( histo2 ) )


    ##  Compute joint histogram for H(1,2)
    J = np.zeros( ( nbins , nbins ) , dtype=np.float32 )
    
    for i in range( nrows ):
        for j in range( ncols ):
            J[imq1[i,j],imq2[i,j]] += 1
    
    J /= np.float32( nrows * ncols )
    ind = np.argwhere( J > eps )
    J = J[ ind[:,0], ind[:,1] ]

    H12 = -np.sum( J * np.log2( J ) )


    ##  Compute normalized mutual information
    NMI = ( H1 + H2 - H12 ) / np.max( np.abs( H1 ) )


    return NMI




###########################################################
###########################################################
####                                                   ####
####                  WRITE LOG FILE                   ####                 
####                                                   ####
###########################################################
########################################################### 

def writeLogFile( args , image_list , results ):
    ##  Open the file
    fp = open( args.fileout , 'w' ) 


    ##  Initial logo
    fp.write('\n')
    fp.write('\n##########################################')
    fp.write('\n##########################################') 
    fp.write('\n###                                    ###')
    fp.write('\n###   NORMALIZED MUTUAL INFORMATION    ###')
    fp.write('\n###                                    ###')
    fp.write('\n##########################################')
    fp.write('\n##########################################') 
    fp.write('\n')


    ##  Date
    today = datetime.datetime.now()
    fp.write('\nNMI calculation performed on the '
                  + str(today))   


    ##  Print oracle image file
    fp.write('\n\nReading reference image:\n' + args.image1)


    ##  Select resolution circle
    if args.resol_circle is True:
        fp.write('\n\nSelecting the resolution circle')

    
    ##  Summary of the results
    num_img = len( image_list )
    for i in range( num_img ):
        fp.write('\n\nTest image number ' + str( i ) + '\n' + image_list[i])
        fp.write('\nNMI = ' + str( results[i] ) )

    fp.write('\n')


    ##  Close the file
    fp.close()




###########################################################
###########################################################
####                                                   ####
####                         MAIN                      ####                 
####                                                   ####
###########################################################
###########################################################

def main():
    print('\n')
    print('#########################################')
    print('#########################################') 
    print('###                                   ###')
    print('###   NORMALIZED MUTUAL INFORMATION   ###')
    print('###                                   ###')
    print('#########################################')
    print('#########################################') 
    print('\n')

    
    
    ##  Get input arguments
    args = getArgs()



    ## Get oracle image
    currDir = os.getcwd()
    image1 = io.readImage( args.image1 )
    image1 = image1.astype(myFloat)

    print('\nReading reference image:\n', args.image1)
    print('Image shape: ', image1.shape)


    image_list = []
    results = []

    
    
    ##  CASE OF SINGLE IMAGE TO ANALYZE
    if args.image2 is not None:
        if args.image2.find( ':' ) == -1:
            image_list.append( args.image2 )
            image2 = io.readImage( args.image2 )  # image2 --> image to analyze
            image2 = image2.astype(myFloat)
            num_img = 1

            print('\nReading image to analyze:\n', args.image2)
            print('Image shape: ', image2.shape)


            ## Get time in which the prgram starts to run
            time1 = time.time()      


            ##  Scale image to analyze with respect to the reference one
            if args.scaling is True:
                print('\nPerforming linear regression ....')
                image2 =  proc.linear_regression( image1 , image2 )  
            
            
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
                
                    image1 = proc.cropImage( image1 , p0 , p1 )
                    image2 = proc.cropImage( image2 , p0 , p1 )

                    dis.plot( image1 )

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

                    dis.plot( image1 )


            ##  Check whether the 2 images have the same shape
            if image1.shape != image2.shape:
                sys.error('\nERROR: The input images have different shapes!\n')


            ##  Plot to check whether the images have the same orientation
            if args.plot is True:
                print('\nPlotting images to check orientation ....')
                img_list = [ image1 , image2 ]
                title_list = [ 'Oracle image' , 'Image to analyze' ]
                dis.plot_multi( img_list , title_list , 'Check plot' )        


            ##  Get number of bins
            nbins = args.nbins
            print('Number of bins: ', nbins)


            ## Calculate map of SSIM values
            NMI = computeNMI( image1 , image2 , nbins )
            results.append( NMI )


        
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
                image2 = image2.astype(myFloat)
                print('\nReading image to analyze:\n', args.image2)
                print('Image shape: ', image2.shape)


                ##  Get time in which the prgram starts to run
                time1 = time.time()      


                ##  Scale image to analyze with respect to the reference one
                if args.scaling is True:
                    print('\nPerforming linear regression ....')
                    image2 =  proc.linear_regression( image1 , image2 ) 
                
                
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
                
                        image1 = proc.cropImage( image1 , p0 , p1 )
                        image2 = proc.cropImage( image2 , p0 , p1 )

                    else:
                        print('\nUsing pixels specified in file:\n', roi) 
                        pixels = np.loadtxt( roi )
                        pixels = pixels.astype( int )
                        p0 = np.array([pixels[0,0],pixels[0,1]])
                        p1 = np.array([pixels[len(pixels)-1,0],pixels[len(pixels)-1,1]])       
                        
                        print('Cropping rectangular ROI with vertices:  ( ', \
                                p0[0],' , ', p0[1], ')   ( ', p1[0],' , ',p1[1], ')')
                
                        image1 = proc.cropImage( image1 , p0 , p1 )
                        image2 = proc.cropImage( image2 , p0 , p1 )     


                ##  Check whether the 2 images have the same shape
                if image1.shape != image2.shape:
                    sys.exit('\nERROR: The input images have different shapes!\n')


                ##  Plot to check whether the images have the same orientation
                if args.plot is True:
                    print('\nPlotting images to check orientation ....')
                    img_list2 = [ image1 , image2 ]
                    title_list2 = [ 'Oracle image' , 'Image to analyze' ]
                    dis.plot_multi( img_list2 , title_list2 , 'Check plot' )   

                
                ##  Get number of bins
                nbins = args.nbins
                print('Number of bins: ', nbins)           


                ##  Calculate map of SSIM values
                NMI = computeNMI( image1 , image2 , nbins )
                results.append( NMI )




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
            image2 = image2.astype(myFloat)
            
            print('\n\n\nIMAGE TO ANALYZE NUMBER: ', i)
            print('\nReading image to analyze:\n', fileIn[i])
            print('Image shape: ', image2.shape)

            
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
                
                    image1 = proc.cropImage( image1 , p0 , p1 )
                    image2 = proc.cropImage( image2 , p0 , p1 )

                else:
                    print('\nUsing pixels specified in file:\n', roi) 
                    pixels = np.loadtxt( roi )
                    pixels = pixels.astype( int )
                    p0 = np.array([pixels[0,0],pixels[0,1]])
                    p1 = np.array([pixels[len(pixels)-1,0],pixels[len(pixels)-1,1]])       
                        
                    print('Cropping rectangular ROI with vertices:  ( ', \
                            p0[0],' , ', p0[1], ')   ( ', p1[0],' , ',p1[1], ')')
                
                    image1 = proc.cropImage( image1 , p0 , p1 )
                    image2 = proc.cropImage( image2 , p0 , p1 )    


            ##  Check whether the 2 images have the same shape
            if image1.shape != image2.shape and args.roi is None:
                sys.error('\nERROR: The input images have different shapes!\n')


            ##  Plot to check whether the images have the same orientation
            if args.plot is True:
                print('\nPlotting images to check orientation ....')
                img_list = [ image1 , image2 ]
                title_list = [ 'Oracle image' , 'Image to analyze' ]
                dis.plot_multi( img_list , title_list , 'Check plot' )    


            ##  Get number of bins
            nbins = args.nbins
            print('Number of bins: ', nbins)           


            ##  Calculate map of SSIM values
            NMI = computeNMI( image1 , image2 , nbins )
            results.append( NMI ) 


        os.chdir(currDir)



    ##  Summary print of the results
    print('\n\nSUMMARY OF THE RESULTS:\n')
    print('\nReference image:\n', args.image1)

    for i in range( num_img ):
        print('\n\nTest image number ', i,'\n', image_list[i],'\n')
        print('NMI = ' , results[i])



    ##  Get time elapsed for the run of the program
    time2 = time.time() - time1
    print('\n\nTime elapsed for the calculation: ', time2)



    ##  Write log file
    if args.fileout is not None:
        if os.path.isfile( args.fileout ) is True:
            print('\nWarning: file ', args.fileout, ' has not been written ',
                    ' because it already exists; delete the file and re-run ',
                    ' the program')
        else:
            writeLogFile( args , image_list , results )


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
