####################################################################################
####################################################################################
####################################################################################
#######                                                                      #######
#######         FOURIER RING CORRELATION ANALYSIS FOR RESOLUTION             #######
#######                                                                      #######
#######  This routine evaluates the resol by means of the fourier            #######
#######  ring correlation (FRC). The inputs are two reconstructions made     #######
#######  with the same algorithm on a sinogram storing the odd-map_disted    #######
#######  projections and on an other one storing the even-map_disted projec.-#######
#######  tions. The two images are transformed with the FFT and their        #######
#######  transform centered. Then, rings of increasing radius R are selec-   #######
#######  ted, starting from the origin of the Fourier space, and the         #######
#######  Fourier coefficients lying inside the ring are used to calculate    #######
#######  the FRC at R, that is FRC(R), with the following formula:           #######
#######                                                                      #######
####### FRC(R)=(sum_{i in R}I_{1}(r_{i})*I_{2}(r_{i}))/sqrt((sum_{i in R}    #######
#######        ||I_{1}(r_{i})||^{2})*(sum_{i in R}||I_{2}(r_{i})||^{2}))     #######
#######                                                                      #######
#######  At the same time, the so-called '2*sigma' curve is calculated at    #######
#######  each step R:                                                        #######
#######                F_{2*sigma}(R) = 2/sqrt(N_{p}(R)/2)                   #######
#######  where N_{p} is the number of pixels in the ring of radius R.        #######
#######  Then, the crossing point between FRC(R) and 2*sigma(R) is found     #######
#######  as the first zero crossing point with negative slope of the dif-    #######
#######  ference curve:                                                      #######
#######                D(R) = FRC(R) - F_{2*sigma}(R)                        #######
#######  The resol is calculated as real space distance correspon-           #######
#######  to this intersection point.                                         ####### 
#######                                                                      #######
#######  Reference:                                                          #######
#######  "Fourier Ring Correlation as a resol criterion for super-           #######
#######  resol microscopy", N. Banterle et al., 2013, Journal of             #######
#######  Structural Biology, 183  363-367.                                   #######
#######                                                                      #######                                    
#######        Author: Filippo Arcadu, arcusfil@gmail.com, 16/09/2013        #######
#######                                                                      #######
####################################################################################
####################################################################################
####################################################################################




####  PYTHON MODULES
from __future__ import division,print_function
import argparse
import sys
import os
import numpy as np
from scipy import interpolate 
from scipy import optimize
import datetime 
from time import sleep




####  MY MODULES
sys.path.append( '../common/' )
import my_image_io as io
import my_image_display as dis
import my_image_process as proc
import my_print as pp




####  PLOTTING PYTHON MODULES
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties




####  MY VARIABLE TYPE
myint     = np.int
myfloat   = np.float32
myfloat2  = np.float64
mycomplex = np.complex64



####  CONSTANTS
eps = 1e-1




################################################################
################################################################
####                                                        ####
####                   GET INPUT ARGUMENTS                  ####
####                                                        ####
################################################################
################################################################

def getArgs():
    parser = argparse.ArgumentParser( description='Fourier ring correlation analysis' , 
                                      formatter_class=argparse.ArgumentDefaultsHelpFormatter )

    parser.add_argument('-i', dest='images',
                        help='Digit names of each pair of input images; e.g.: -i image1_odd:image1_even,'
                        + 'image2_odd:image2_even, .... ; minimum number of images is 2')
    
    parser.add_argument('-o', dest='pathout',
                        help='Select output folder where to save the log file'
                        + ' and the plots')
    
    parser.add_argument('-r', dest='width_ring', type=myfloat, default=5,
                        help='Set thickness of the ring for FRC calculation') 
    
    parser.add_argument('-n', dest='resol_square', action='store_true',
                        help='Enable analysis only in the resolution square')

    parser.add_argument('-w', dest='hanning', action='store_true',
                        help='Enable multiplication of the images with a hanning window')  

    parser.add_argument('-l', dest='labels',
                        help='Enable specific labels for plots, one for each pair of images;'
                        + ' e.g.: -l EST:GRIDREC:IFBPTV')

    parser.add_argument('-p', dest='plot', action='store_true',
                        help='Display check plot')
    
    parser.add_argument('-d', dest='polynom_degree', type=myint, default=20,
                        help='Set polynomial degree to fit FRC curve')     

    args = parser.parse_args()
    

    ##  Exit in case compulsory inputs are missing
    if args.images is None:
        parser.print_help()
        sys.exit('ERROR: No input image specified!')
    
    return args




################################################################
################################################################
####                                                        ####
####                 FIND LONGEST COMMON ARRAY              ####
####                                                        ####
################################################################
################################################################

def common_string( strings ):
    prefix1 = strings[0]
    prefix2 = strings[1] 

    if prefix1.find( '/' ) != -1:
        prefix1 = prefix1.split( '/' )
        prefix1 = prefix1[len(prefix1)-1]

    if prefix2.find( '/' ) != -1:
        prefix2 = prefix2.split( '/' )
        prefix2 = prefix2[len(prefix2)-1]

    strings = [ prefix1 , prefix2 ]
    prefix = prefix1

    for s in strings:
        if len(s) < len(prefix):
            prefix = prefix[:len(s)]
        if not prefix:
            return ''
        for i in range(len(prefix)):
            if prefix[i] != s[i]:
                prefix = prefix[:i]
                break

    return prefix




################################################################
################################################################
####                                                        ####
####        FIND ARRAY VALUES INSIDE VALUE INTERVAL         ####
####                                                        ####
################################################################
################################################################

def find_points_interval( array, inf, sup ):
    arr_inf = array >= inf
    arr_sup = array <= sup
    ind = np.argwhere( arr_inf * arr_sup)
    return ind




################################################################
################################################################
####                                                        ####
####        CHECK WHETHER ARRAY IS MULTIDIMENSIONAL         ####
####                                                        ####
################################################################
################################################################  

def isMultidimArray( array ):
    if len(array.shape) == 1:
        return False
    elif len(array.shape) == 2 and array.shape[1] == 1:
        return False
    else:
        return True




################################################################
################################################################
####                                                        ####
####                       PLOT FRC CURVES                  ####
####                                                        ####
################################################################
################################################################   

def plot_frc_curves( curve_list , x , args , pathout , prefix , title ,
                     labels=None , prefix_add=None , mode='single' , point=None ):
    ##  Define figure enviroment
    #fig = plt.figure(figsize=(80,80))
    fig = plt.figure( 1 ) 
    rect = fig.patch
    rect.set_facecolor( 'white' )
    axescolor  = '#f6f6f6'
    ax = plt.subplot( 111 , axisbg=axescolor )
    

    
    ##  Font setting
    font0 = FontProperties()
    font1 = font0.copy()
    font1.set_size( 'large' )
    font = font1.copy()
    font.set_family( 'serif' )


    
    ##  Enable grid
    gridLineWidth = 0.2
    ax.yaxis.grid( True , linewidth=gridLineWidth , linestyle='-' , color='0.05' )


    
    ##  Marker setup
    colorArray = ['blue','red','red','orange','brown','black','violet','pink']
    marker_array = ['o','d','^','s','o','d','1','v','*','p']

    
    
    ##  Axis limits
    plt.ylim( [ 0 , 1.2 ] )

    
    
    ##  Axis labelling
    fig.autofmt_xdate(bottom=0.18)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    xlabel = 'Radius'
    ylabel = 'FRC'
    plt.xlabel( xlabel , fontsize=12 , position=(0.5,-0.2) )
    plt.ylabel( ylabel , fontsize=12 , position=(0.5,0.5) )


    
    ##  Title
    #plt.text( 0.5 , 1.06 , title , horizontalalignment='center' ,
    #          fontsize=22 , transform = ax.transAxes )


    
    ##  Plottting modalities
    curve_list = np.array( curve_list )

    ##  1) Modality single: only 1 FRC curve
    if mode == 'single':
        y = curve_list
        #plt.plot( x , y , marker_array[0] , markersize=9 , color=colorArray[0] )
        plt.plot( x , y , '-' , linewidth=3 , color='blue' ) 


    ##  2) Modality resol: FRC curve + fit of the curve + criterion curve +
    ##     resol. point
    elif mode == 'resol':
        y = curve_list[0]
        #plt.plot( x , y , marker_array[0] , markersize=9 , color=colorArray[0] ,
        #          label='FRC curve')
        plt.plot( x , y , '-' , linewidth=2 , color='blue' , label='FRC curve' )

        plt.hold( 'True' )

        y = curve_list[1]
        plt.plot( x , y , '-' , linewidth=3 , color='red' , 
                  label='Polynomial fit degree ' + str( args.polynom_degree ) )

        plt.hold( 'True' )  

        y = curve_list[2]
        if prefix_add == '_onebit':
            label = 'One-bit curve'
        elif prefix_add == '_halfbit':
            label = 'Half-bit curve'     
        elif prefix_add == '_halfheight':
            label = 'y = 0.5'     
        plt.plot( x , y , color=colorArray[3] , linewidth=2 , 
                  label=label )

        plt.hold( 'True' )


        if point is not None:
            x0 = point[0]
            y0 = point[1]
            plt.plot( x0 , y0 , 'ro' , markersize=3 , color='black' , label='Resolution point' )

            verts = [ ( x0 , 0 ) , ( x0 , y0 ) ]
            xs, ys = zip( *verts )
        
            ax.plot( xs , ys , 'x--' , lw=2 , color='blue' , ms=2 )
            ax.text( x0 , y0+0.05 , 'RES-FREQ' , color='black', fontsize=12 )    


    ##  3) Modality multi: 
    elif mode == 'multi':
        num_curves = len( curve_list )
        for i in range(num_curves):
            y = curve_list[i]
            if labels is not None:  
                plt.plot( x , y , color=colorArray[i] , label=labels[i] ,
                          linewidth=3 )
            else:
                plt.plot( x , y , color=colorArray[i] , linewidth=5 )    
            plt.hold( 'True' )   


    
    ##  Add legend
    plt.legend( loc='best' )



    ##  Save plot
    if pathout is not None:
        if prefix_add is None:
            fileout = pathout + prefix + '_frc' + '.eps' 
        else:
            fileout = pathout + prefix + '_frc' + prefix_add + '.eps'
        plt.savefig( fileout , facecolor=fig.get_facecolor() ,
                     edgecolor='black' , format='eps', dpi=1000 )
        


    ##  Show plot
    if args.plot is True:
        plt.show()

    plt.clf()




################################################################
################################################################
####                                                        ####
####                    RESOLUTION CRITERIA                 ####
####                                                        ####
################################################################
################################################################ 

def resolution_criterion( y1 , x , n , ff , crit , pd ):
    ##  Create either one-bit or half-bit curve
    if crit == 'one-bit':
        y2 = ( 0.5 + 2.4142 / np.sqrt( n ) ) / ( 1.5 + 1.4142 / np.sqrt( n ) )
    elif crit == 'half-bit':
        y2 = ( 0.2071 + 1.9102 / np.sqrt( n ) ) / ( 1.2071 + 0.9102 / np.sqrt( n ) )
    elif crit == 'half-height':
        y2 = 0.5 * np.ones( len( n ) )

    
    
    ##  Find piecewise polynomial to approximate the FRC curves
    #p1 = interpolate.PiecewisePolynomial( x , y1[:,np.newaxis] )
    coeff = np.polyfit( x , y1 , pd )
    p1 = np.poly1d( coeff )



    ##  Get criterion curve
    if crit == 'one-bit' or crit == 'half-bit':
        p2 = interpolate.interp1d( x , y2 , bounds_error=False )      
        
    def pdiff1(x):
        return  p1( x ) - p2( x )

    def pdiff2(x):
        return  p1( x ) - 0.5          


    ##  Find intersection of the difference with the axis y == 0
    roots = set()
    x_max = x[ len( x ) - 1 ]

    if crit == 'one-bit' or crit == 'half-bit': 
        for i in x: 
            root , infodict , ier , mesg = optimize.fsolve( pdiff1 , i ,
                                                            full_output=True )
            if ( ier == 1 ) and ( 0 < root < x_max):
                root = root[0]
                break
        
        if np.abs( p1( root ) - p2( root ) ) > eps:
            success = 0
        else:
            success = 1

    else:
        if pdiff2( 0.0 ) * pdiff2( x[len(x)-1] ) < 0:
            root = optimize.bisect( pdiff2 , 0.0 , x[len(x)-1] )
            success = 1
        else:
            success = 0

    #if success:
    point = [ root , p1( root ) ]
    root *= ff          
    #else:
    #root = None
    #point = None

    return point , root , p1( x ) , y2    




################################################################
################################################################
####                                                        ####
####                      WRITE LOG FILE                    ####
####                                                        ####
################################################################
################################################################

def write_log_file( resol , args , pathout , prefix , image_name ):
    print( 'pathout:\n', pathout )
    print( 'prefix:\n', prefix )
    file_log = prefix + 'frc_log.txt'
    fp = open( pathout + file_log , 'w' )
    fp.write('FRC analysis log file')
    today = datetime.datetime.today()
    fp.write('\n\nCaculation done on the ' + str( today ))
    fp.write('\n\nInput images:\n1) ' + image_name[0] + '\n2) ' + image_name[1])
    if args.resol_square is True:
        fp.write('\nComputation done inside the resolution circle')
    if args.hanning is True:
        fp.write('\nHanning pre-filter activated')       
    fp.write('\nRing thickness: ' + str( args.width_ring ))

    fp.write('\n\n\nResolution results:')
    fp.write('\n1) Criterion one-bit: ' + str( resol[0] ) + ' pixels')
    fp.write('\n2) Criterion half-bit: ' + str( resol[1] ) + ' pixels') 
    fp.write('\n3) Criterion half-height: ' + str( resol[2] ) + ' pixels')

    fp.close()  




################################################################
################################################################
####                                                        ####
####            FOURIER RING CORRELATION ANALYSIS           ####
####                                                        ####
################################################################
################################################################

def analysis_frc( image1 , image2 , args , pathout , prefix , image_name , labels=None ):   
    ##  Check whether images have the same height  
    if image1.shape != image2.shape:
        sys.exit('ERROR: Image 1 & 2 have different sizes!')


    ##  Get the Nyquist frequency
    nx,ny = image1.shape
    
    if nx == ny:
        nmax = nx
    elif nx < ny:
        nmax = ny
    else:
        nmax = nx
    
    freq_nyq = int( np.floor( nmax/2.0 ) )

   
    ##  Initialize progress bar
    #bar = progressbar.ProgressBar( maxval=freq_nyq , \
    #                               widgets=[progressbar.Bar('=', '[', ']') , 
    #                               ' ' , progressbar.Percentage()] )


    ##  Create Fourier grid
    x = np.arange( -np.floor( ny/2.0 ) , np.ceil( ny/2.0 ) )
    y = np.arange( -np.floor( ny/2.0 ) , np.ceil( ny/2.0 ) )
    x,y = np.meshgrid( x , y )
    map_dist = np.sqrt( x*x + y*y )


    ##  FFT transforms of the input images
    fft_image1 = np.fft.fftshift( np.fft.fft2( image1 ) )
    fft_image2 = np.fft.fftshift( np.fft.fft2( image2 ) )

    
    ##  Get thickness of the rings
    width_ring = args.width_ring
    print('\nRing width: ', width_ring)


    ##  Get polynomial degree to fit the FRC curve
    pd = args.polynom_degree
    print( '\nPolynomial degree to fit FRC curve: ' , pd )
    
    ##  Calculate FRC and 2*sigma curve
    C1 = [];  C2 = [];  C3 = [];  n = []
    
    r = 0.0
    l = 0

    radii = []

    while r + width_ring < freq_nyq :
        #bar.update(r+1)
        sleep(0.1)
        
        ind_ring = find_points_interval( map_dist , r , r + width_ring )
        
        aux1 = fft_image1[ind_ring[:,0],ind_ring[:,1]]
        aux2 = fft_image2[ind_ring[:,0],ind_ring[:,1]]

        C1.append( np.sum( aux1 * np.conjugate(aux2) ) )
        C2.append( np.sum( np.abs( aux1 )**2 ) )
        C3.append( np.sum( np.abs( aux2 )**2 ) )

        n.append( len( aux1 ) )
        
        radii.append( r )
        r += width_ring
        l += 1

    radii = np.array( radii );  n = np.array( n )
    FRC = np.abs( np.array( C1 ) )/ np.sqrt( np.array( C2 ) * np.array( C3 ) )

    print( '\n\nFRC:' )
    pp.printArray( FRC )
    print('\n')


    
    ##  Plot FRC curve (alone)
    spatial_freq = radii / myfloat( freq_nyq )     
    
    title = 'FRC'
    if args.resol_square is True:
        title += ' inside resolution circle'

    plot_frc_curves( FRC , spatial_freq , args , pathout , prefix , 
                     title , mode='single' )


    
    ##  Get resol point by means of the one-bit, half-bit and half-height criterion
    point1 , index1 , p1 , y1 = resolution_criterion( FRC , spatial_freq , n , freq_nyq , 'one-bit' , pd ) 
    point2 , index2 , p2 , y2 = resolution_criterion( FRC , spatial_freq , n , freq_nyq , 'half-bit' , pd )
    point3 , index3 , p3 , y3 = resolution_criterion( FRC , spatial_freq , n , freq_nyq , 'half-height' , pd )  

    
    
    ##  Plot FRC with resolution points
    plot_frc_curves( [ FRC , p1 , y1 ] , spatial_freq , args ,
                     pathout , prefix , prefix_add='_onebit' , 
                     title='Resolution with one-bit curve',
                     point=point1 , mode='resol' )

    plot_frc_curves( [ FRC , p2 , y2 ] , spatial_freq , args ,
                     pathout , prefix , prefix_add='_halfbit' , 
                     title='Resolution with half-bit curve',
                     point=point2 , mode='resol' ) 

    plot_frc_curves( [ FRC , p2 , y3 ] , spatial_freq , args ,  
                      pathout , prefix , prefix_add='_halfheight' , 
                      title='Resolution with half-height curve' ,
                      point=point3 , mode='resol' ) 



    ##  Compute resolution point
    resol1 = freq_nyq / myfloat( index1 )
    resol2 = freq_nyq / myfloat( index2 )
    resol3 = freq_nyq / myfloat( index3 )
    resol = [ resol1 , resol2 , resol3 ]
    
    print( '\nResolution with one-bit curve: ' , resol1,' pixels' )
    print( '\nResolution with half-bit curve: ' , resol2,' pixels' )
    print( '\nResolution with half-height curve: ' , resol3,' pixels' )    



    ##  Write log file
    if pathout is not None:
        write_log_file( resol , args , pathout , prefix  , image_name )   


    
    return FRC , spatial_freq




################################################################
################################################################
####                                                        ####
####                             MAIN                       ####
####                                                        ####
################################################################
################################################################

def main():
    
    print('\n')
    print('#############################################################')
    print('############  FOURIER RING CORRELATION ANALYSIS  ############')
    print('#############################################################')
    print('\n')

    

    ##  Get input arguments
    args = getArgs()


    
    ##  Get output folder
    if args.pathout is not None:
        pathout = args.pathout
        if pathout[len(pathout)-1] != '/':
            pathout += '/'
        if os.path.exists( pathout ) is False:
            os.mkdir( pathout )
    else:
        pathout = None




    ##  Get number of pair of images
    image_string = args.images
    file_list = []
    
    if image_string.find(',') != -1:
        image_string = image_string.split(',')
        num_img_pair = len( image_string )

        for i in range( num_img_pair ):
            file_list.append( image_string[i].split(':') )
    
    else:
        file_list.append( image_string.split(':') )
        num_img_pair = 1
    
    num_img = num_img_pair * 2

    print('Number of images to analyze: ', num_img)


    
    ##  Read input images and display them as check
    images = []
    prefix = []

    
    for i in range(num_img_pair):
        for j in range(2):
            ##  Read single image
            image_name = file_list[i][j]
            image = io.readImage( image_name )
            m , n = image.shape


            ##  Crop it as a square image
            npix = np.min( ( m , n ) )
            i1 = int( 0.5 * ( m - npix ) )
            i2 = int( 0.5 * ( n - npix ) )
            image = image[i1:i1+npix,i2:i2+npix]

            print('Reading image: ', image_name)


            ##  Select resolution square
            if args.resol_square is True:
                print('Calculation enabled in the resol square')
                image = proc.select_resol_square( image )            


            ##  Apply hanning window
            if args.hanning is True:
                window = np.hanning( npix )
                window = np.outer( window , window )
                image *= window

            images.append( image )


        ##  Get common prefix
        prefix.append( common_string( [ file_list[i][0] , file_list[i][1] ] ) )    


        
        ##  Check plot
        if args.plot is True:
            dis.plot_multi( [ images[2*i] , images[2*i+1] ] , 
                            [ 'Input image ' + str( 2*i ) , 'Input image ' + str( 2*i + 1 ) ] ) 
    


    ##  Get labels for plots
    labels = None
    if args.labels is not(None):
        labels = args.labels
        labels = labels.split(':')

        if ( 2 * len(labels) ) != num_img:
            sys.exit('\nERROR: Number of labels is not half number of input images!\n')

    
    
    ##  Fourier ring correlation analysis
    frc_curves = []

    for i in range(num_img_pair):
        print('\nCalculating FRC between:\n1)', file_list[i][0],'\n2)',\
                file_list[i][1])
        
        FRC , spatial_freq = analysis_frc( images[2*i] , images[2*i+1] , args , pathout ,
                                           prefix[i] , file_list[i] , labels=None )
        frc_curves.append( FRC )
    frc_curves = np.array( frc_curves ).reshape( num_img_pair , len( spatial_freq ) )



    ##  Plot FRC curves
    if num_img_pair > 1:
        title = 'FRC - Comparison'
        prefix = 'comparison_curves'
        plot_frc_curves( frc_curves , spatial_freq , args , pathout , prefix , 
                         title , labels , mode='multi' ) 


    print('\n##########  FOURIER RING CORRELATION ANALYSIS END  ##########\n')




################################################################
################################################################
####                                                        ####
####                         CALL TO MAIN                   ####
####                                                        ####
################################################################
################################################################    

if __name__ == '__main__':
    main()
