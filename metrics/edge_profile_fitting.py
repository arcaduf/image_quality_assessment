#################################################################################
#################################################################################
#################################################################################
#######                                                                   #######
#######   CALCULATE RESOLUTION BY FITTING LINE PROFILE WITH ERROR FUNC.   #######
#######                                                                   #######
#######   Routine to evaluate the resolution of images by fitting the     #######
#######   line profile, taken between two (supposed) homogeneuos regions, #######
#######   with the error function and then taking the FWHM of the deriva- #######
#######   tive of this fitting function. The reason to fit the line       #######
#######   profile, before taking the derivative of the same, is that, in  #######
#######   case of noisy images, the characteristic peak in the derivative #######
#######   shape does not come out, because covered by noise.              #######
#######                                                                   #######
#######   Requirements:                                                   ####### 
#######   You need Python Enthought to run this script                    #######
#######   The input text file is provided by Line_Profile_Stack.py, which #######
#######   is a Jython script to run with ImageJ (java repository).        #######
#######                                                                   #######
#######   Usage:                                                          ####### 
#######       python calcResolFEF.py [args]                               ####### 
#######                                                                   ####### 
#######        Author: Filippo Arcadu, arcusfil@gmail.com, 03/08/2013     #######
#######                                                                   #######
#################################################################################
#################################################################################
################################################################################# 




####  GENERIC PYTHON MODULE
from __future__ import division,print_function
import argparse
import sys
import re
import numpy as np
import scipy
from scipy import special
from scipy import optimize
import math
import datetime




####  PLOTTING PYTHON MODULES
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.font_manager import FontProperties
from matplotlib import rc, rcParams




####  MY VARIABLE TYPE
####  This precision for the floating variables is necessary to let
####  scipy.optimize.leastsq work properly, otherwise the Jacobian
####  is a zero matrix and the line profile does not get fitted
myfloat = np.float64




###########################################################
###########################################################
####                                                   ####
####                  GET INPUT ARGUMENTS              ####
####                                                   ####
###########################################################
###########################################################

def getArgs():
    parser = argparse.ArgumentParser(description='Calculate image resolution by'
                                                + ' fitting an edge profile',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--filein', dest='filein',
                        help='The input is a text file printed by Fiji after'
                        + ' having computed the profile of a line')

    parser.add_argument('-o', '--fileout', dest='fileout',
                        help='You can enable an output text file where results are saved')
    
    parser.add_argument('-p', '--plot', dest='plot', action='store_true',
                        help='Enable plot')

    parser.add_argument('-f', '--func', dest='func', default='erf',
                        help='Select fitting funtion: erf or sigmoid')     
    
    parser.add_argument('-c', '--correction', dest='correct',
                        help='Specify a list (placed in the same folder path, if'
                        + ' working with paths, or in the working directory, if working'
                        + ' with single input file) of fitting parameters, 4 for each image in the list,'
                        + ' to correct the the resolution values, that are the'
                        + ' outcome of a first run of the program; e.g.: -c path/list_corrections.txt ;'
                        + ' e.g. of the list:\n3.11728806e-06 -2.26914679e-06 2.86760028e+02 5.30636558e+00\n'
                        + ' -1 -1 -1 -1\n2.83676500e-06 -2.02158491e-06 2.83958500e+02 4.09769484e+00\n. . . . .\n'
                        + ' the four "-1" means no correction for image number 2 (in this case)')  
    
    parser.add_argument('-pr', '--prefilt', dest='prefilt', action='store_true',
                        help='Enable prefiltering of the data')

    parser.add_argument('-k', '--pixdim', dest='pixdim', type=myfloat, 
                        help='Specify pixel size in um')    
    
    parser.add_argument('-w', '--saveplots',dest='saveplots',
                        help='Save the plots in .png format in the specified path;'
                        + ' -e.g.: -w path/')
    
    args = parser.parse_args()
    
    if args.filein is None:
        parser.print_help()
        print("ERROR: Input file not specified!")
        sys.exit()
    
    return args




###########################################################
###########################################################
####                                                   ####
####                     PRE-FILTERING                 ####
####                                                   ####
###########################################################
###########################################################

def prefiltering( y ):
    print('\n')
    x1 = int( raw_input('Input extent x1 of the left step: ') )
    x2 = int( raw_input('Input extent x2 of the right step: ') )
    
    mean_1 = np.mean( y[:x1] )
    y[:x1] = mean_1
    mean_2 = np.mean( y[x2:] )
    y[x2:] = mean_2

    return y




###########################################################
###########################################################
####                                                   ####
####                   ERROR FUNCTION                  ####
####                                                   ####
###########################################################
###########################################################

def error_func( p , x ):
    return p[0] + p[1] * special.erf( ( x - p[2] ) / p[3] ) 

def error_func_fit( p , x , y ): 
    return p[0] + p[1] * special.erf( ( x - p[2] ) / p[3] ) - y




###########################################################
###########################################################
####                                                   ####
####                   SIGMOID FUNCTION                ####
####                                                   ####
###########################################################
########################################################### 

def sigmoid_func( p , x ):
    return p[0] + p[1] / ( 1 + p[2] * np.exp( -p[3] * x ) ) 

def sigmoid_func_fit( p , x , y ): 
    return p[0] + p[1] / ( 1 + p[2] * np.exp( -p[3] * x ) ) - y  




###########################################################
###########################################################
####                                                   ####
####                     PLOT FUNCTION                 ####
####                                                   ####
###########################################################
########################################################### 

def plot_function( curves , n , args ):
    ##  Common plot settings
    if n == 1:
        y = curves.copy()
    if n == 2:
        y = curves[0]
        yfit = curves[1]
    npix = len( y )
    y = y.astype( myfloat )
    x = np.arange(npix).astype(myfloat) 
    fig = plt.figure(1)
    rect = fig.patch
    rect.set_facecolor('white')
    axescolor  = '#f6f6f6'
    ax = plt.subplot(111,axisbg=axescolor)  
    font0 = FontProperties()
    font1 = font0.copy()
    font1.set_size('large')
    font = font1.copy()
    font.set_family('serif')
    rc('text',usetex=True)  
    gridLineWidth = 0.2
    ax.yaxis.grid(True, linewidth=gridLineWidth, linestyle='-', color='0.05')  
    fig.autofmt_xdate(bottom=0.18)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)  
    plt.xlabel('Pixel index', fontsize=12,position=(0.5,-0.2))
    plt.ylabel( 'Grey value' , fontsize=12,position=(0.5,0.5))

    if n == 1:
        plt.title('Input line profile', fontsize=12, fontweight='bold')
        plt.plot( x , y , linewidth=2 , color='b' ) 
    elif n == 2:
        plt.title('Line profile fitted with ERF', fontsize=12, fontweight='bold')
        plt.plot( x , y , linewidth=2 , color='blue' , label='Line profile' )
        plt.hold( True )
        plt.plot( x , yfit , linewidth=3 , color='r' , label='Erf fit function' )
        plt.legend(loc='upper right', shadow=True)
    
    if n == 2 and args.saveplots is not None:
        fileout = args.saveplots
        plt.savefig( fileout , facecolor=fig.get_facecolor() , edgecolor='black' ,
                     format='eps', dpi=1000) 

    if args.plot is True:
        plt.show() 



###########################################################
###########################################################
####                                                   ####
####     FITTING LINE PROFILE WITH ERROR FUNCTION      ####
####                                                   ####
###########################################################
###########################################################   

def fit_line_profile( y , args ):
    ##  Initialize input arrays for fit
    npix = len( y )
    y = y.astype( myfloat )
    x = np.arange(npix).astype(myfloat)


    ##  Calculate starting values of the parameters
    p0 = np.zeros( 4 , dtype=myfloat )
    p0[0] = y.min()
    p0[1] = y[npix-1] - y[0]
    p0[2] = ( x.max() - x.min() ) * 0.5
    p0[3] = 1.0


    ##  Fitting by means of least square method
    if args.func == 'erf':
        ##  Fitting function: a + b * erf( ( x - c ) / d )
        param , success = scipy.optimize.leastsq( error_func_fit , p0 , args=(x,y) )
        print('\nFit performed with function:  a + b * erf( ( x - c ) / d')
    elif args.func == 'sigmoid':
        ##  Fitting function: a + b / ( c + exp( -d ) )
        param , success = scipy.optimize.leastsq( sigmoid_func_fit , p0 , args=(x,y) ) 
        print('\nFit performed with function:  a + b / ( c + exp( -d ) )')

    print('a = ', param[0],'  b = ', param[1],'  c = ', param[2],'  d = ', param[3])


    ##  Plot line profile with ERF fitting function
    if args.func == 'erf':
        yfit = error_func( param , x )
    elif args.func == 'sigmoid':
        yfit = sigmoid_func( param , x ) 
    
    plot_function( [ y , yfit ] , 2 , args )

    return param , yfit




###########################################################
###########################################################
####                                                   ####
####               CALCULATE RESOLUTION                ####
####                                                   ####
###########################################################
###########################################################   

def calc_resol( y , args ):
    ##  Pre-treatment of the data
    if args.prefilt is True:
        y[:] = prefiltering( y )

        if args.plot is True:
            plt.title('Filtered line profile')
            x = np.arange( len( y ) )
            plt.plot( x , y )
            plt.show()


    ##  Fitting with error function
    param , yfit = fit_line_profile( y , args )
    slope = param[3]

    
    ##  Calculate resolution
    dy = yfit[1:] - yfit[:len(yfit)-1]
    x1 = np.min( np.argwhere( dy != 0 ) ) - 1
    x2 = np.max( np.argwhere( dy != 0 ) ) + 1
    resol = ( np.max( yfit ) - np.min( yfit ) ) / myfloat( x2 - x1 )

    print('\nResolution (pixels): ', resol )

    if args.pixdim is not None:
        resol *= args.pixdim 
        print('Resolution (um): ', resol )

    return resol




###########################################################
###########################################################
####                                                   ####
####                    WRITE LOG FILE                 ####
####                                                   ####
###########################################################
########################################################### 

def write_log_file( resol , args ):
    fp = open( args.fileout , 'w' ) 


    ##  Initial logo
    fp.write('\n')
    fp.write('\n##################################################')
    fp.write('\n##################################################') 
    fp.write('\n###                                            ###')
    fp.write('\n###    RESOLUTION BY FITTING AN EDGE PROFILE   ###')
    fp.write('\n###                                            ###')
    fp.write('\n##################################################')
    fp.write('\n##################################################') 
    fp.write('\n')


    ##  Date
    today = datetime.datetime.now()
    fp.write('\nResolution calculation performed on the '
                  + str(today))   


    ##  Print oracle image file
    fp.write('\n\nReading line profile file:\n' + args.filein)


    
    ##  Print oracle image file
    fp.write('\n\nProfile fitting with function::\n' + args.func)  



    ##  Summary of the results
    if args.pixdim is None:
        fp.write('\nRESOLUTION = ' + str( resol ) + ' pixels' )
    else:
        fp.write('\nRESOLUTION = ' + str( resol ) + ' um' )    

    fp.write('\n')


    ##  Close the file
    fp.close()   




###########################################################
###########################################################
####                                                   ####
####                          MAIN                     ####
####                                                   ####
###########################################################
###########################################################

def main():
    print('\n')
    print('############################################################')  
    print('############################################################')
    print('####                                                    ####')
    print('####       RESOLUTION BY FITTING AN EDGE PROFILE        ####')
    print('####                                                    ####')  
    print('############################################################')  
    print('############################################################')



    ##  GET INPUT ARGUMENTS
    args = getArgs()



    ##  READ LINE PROFILE FILE
    line_profile = np.loadtxt( args.filein )
    print('\nInput line profile file:\n', args.filein)

    if args.plot is True:
        plot_function( line_profile[:,1] , 1 , args )

   
    ##  GET SELECTION OF FITTING FUNCTION
    print('\nSelected fitting function: ', args.func)


    ##  CALCULATE RESOLUTION WITH ERROR FUNCTION FITTING METHOD
    resol = calc_resol( line_profile[:,1] , args )



    ##  WRITE OUTPUT LOG FILE
    if args.fileout is not None:
        write_log_file( resol , args )


    print('\n')


    

###########################################################
###########################################################
####                                                   ####
####                   CALL TO  MAIN                   ####
####                                                   ####
###########################################################
###########################################################  

if __name__ == '__main__':
    main()
