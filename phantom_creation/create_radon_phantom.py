#####################################################################
#####################################################################
####                                                             ####
####              COMPUTE ANALYTICAL RADON TRANSFORM             ####
####             RADIALLY SYMMETRIC FUNCTIONS CIRCLES            ####
####                                                             ####
####          24/02/2014   F. Arcadu   arcusfil.gmail.com        ####
####                                                             ####
#####################################################################
#####################################################################

##  The routine creates radially symmetric phantoms of the form:
##  f(x,y) = ( a^{2} - x^{2} - y^{2} )^{n}  for x^{2} + y^{2} <= a^{2}
##
##  The formula for the Radon transform, R{f}(t) and (d/dt)R{f}(t) (not dependent on theta), is:
##  R{f}(t)       = c * (2n)!! / (2n+1)!! * ( a^{2} - t^{2} )^{n+1/2} 
##  (d/dt)R{f}(t) = -c * t * (2n)!! / (2n-1)!! * ( a^{2} - t^{2} )^{n-1/2}
##  c =| 2  , if n=2k 
##     | pi , if n=2k+1




####  PYTHON MODULES
from __future__ import division, print_function
import argparse
import sys
import numpy as np
from scipy import ndimage as ndi
from scipy.misc import factorial2 as fac2




####  MY PYTHON MODULES
sys.path.append( '../common/' )
import my_image_io as io
import my_image_display as dis




####  VARIABLE FORMAT
myfloat = np.float64
myint   = np.int



####  CONSTANT
eps = 1e-5




#####################################################################
#####################################################################
####                                                             ####
####                     GET INPUT ARGUMENTS                     ####
####                                                             ####
#####################################################################
#####################################################################

def getArgs():
    parser = argparse.ArgumentParser(description='''Create radially symmetric functions''',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-D', '--path', dest='path', default='./',
                        help = 'Select path to the output folder')

    parser.add_argument('-o', dest='fileout',
                        help = 'Select output name')  

    parser.add_argument('-n', '--npix', dest='npix', type=myint,
                        help = 'Number of pixels of the Shepp-Logan phantom')
    
    parser.add_argument('-a', '--nang', dest='nang', type=myint, 
                        help = '''Number of projection angles distributed from 0
                                to pi''')

    parser.add_argument('-d', dest='degree', type=myint, default='2', 
                        help = '''Select degree of the function''')  
    
    parser.add_argument('-dpc', dest='dpc', action='store_true',
                        help = '''Enable dpc phantom''') 
    
    parser.add_argument('-p', '--plot', dest='plot', action='store_true',
                        help = '''Enable check plots''')

    parser.add_argument('-f',  dest='file_format', default='.DMP',
                        help = '''Select type of outout file_format''')   

    args = parser.parse_args() 

    if args.npix is None:
        parser.print_help()
        sys.exit('\nERROR: Number of pixel of the phantom not specified!\n')              

    return args
    
    


#####################################################################
#####################################################################
####                                                             ####
####                 CREATE LOOK-UP-TABLE FOR FUNCTIONS          ####
####                                                             ####
#####################################################################
#####################################################################

def create_lut( npix ):
    lut = []

    ##  In order:
    ##  1st number  --->  x0 
    ##  2nd number  --->  y0
    ##  3rd number  --->  r
    ##  x0 , y0, r in [0.0,1.0]; e.g.: x0 = 0.35  --->  x0 = round( n/2 * ( 1 + 0.35 ) )
    ##                           e.g.: r  = 0.35  --->  r  = round( n/2 * 0.35 )
    
    ##  n.1
    f1 = np.array( [ -0.2 , 0.2 , 0.6 ] )
    lut.append( f1 )
    
    ##  n.2
    f2 = np.array( [ 0.35 , 0.35 , 0.4 ] )
    lut.append( f2 )
    
    ##  n.3
    f3 = np.array( [ 0.4 , -0.3 , 0.5 ] )
    lut.append( f3 )
    
    ##  n.4
    f4 = np.array( [ -0.45 , -0.45 , 0.35 ] )
    lut.append( f4 )     
    
    ##  n.5
    f5 = np.array( [ +0.2 , -0.55 , 0.3 ] )
    lut.append( f5 )  
    
    return lut         




#####################################################################
#####################################################################
####                                                             ####
####                 CREATE SHEPP-LOGAN PHANTOM                  ####
####                                                             ####
#####################################################################
#####################################################################

def create_phantom( npix , deg , lut ):
    ##  Allocate memory for the phantom
    image = np.zeros( ( npix , npix ) , dtype=myfloat )
    nh    = 0.5 * npix
    d     = deg

    ##  Draw phantom
    num   = len( lut )
    x     = np.arange( npix )
    x , y = np.meshgrid( x , x )

    for i in range( num ):
        x0 =  myint( nh * ( 1 + lut[i][0] ) )
        y0 =  myint( nh * ( 1 + lut[i][1] ) )  
        r  =  nh * lut[i][2]

        ii = np.argwhere( np.sqrt( ( x - x0 )**2 + ( y - y0 )**2 ) <= r )
        image[ii[:,0],ii[:,1]] += ( r**2 - ( x0 - x[ii[:,0],ii[:,1]] )**2 - \
                                           ( y0 - y[ii[:,0],ii[:,1]] )**2 )**d

    return image
             



#####################################################################
#####################################################################
####                                                             ####
####             CALCULATE PROJECTION OF A SNGLE FUNCTION        ####
####                                                             ####
#####################################################################
#####################################################################   

def calc_proj( n , lut , deg , theta , dpc ):
    ##  Function to compute the projection
    if dpc is False:
        p = lambda r , t , d , c : c * fac2( 2 * d ) / fac2( 2*d + 1 ) * \
                                   np.power( r**2 - t**2 , d + 0.5 )
    else:
        p = lambda r , t , d , c : - t * c * fac2( 2 * d ) / fac2( 2*d - 1 ) * \
                                   np.power( r**2 - t**2 , d - 0.5 )


    ##  Allocate memory for projection
    proj = np.zeros( n , dtype=np.float64 )


    ##  Center and radius of the radially symmetric function
    nh = 0.5 * n
    x0 = -lut[0] * nh 
    y0 = lut[1] * nh
    r  = lut[2] * nh

    
    ##  Constant c
    if deg % 2 == 0:
        c = 2.0
    else:
        c = np.pi


    ##  Compute projection
    for j in range( n ):
        t = ( j - nh ) - ( x0 * np.cos( theta ) + y0 * np.sin( theta ) )
        #print( '\n\nr = ', r,'  t = ' , t )
        if np.abs( t ) <= np.abs( r ):
            proj[j] = p( r , t , deg , c )

    return proj            

    


#####################################################################
#####################################################################
####                                                             ####
####         ANALYTICAL RADON TRANSFORM OF THE PHANTOM           ####
####                                                             ####
#####################################################################
#####################################################################

def radon_transform_analytical( lut , npix , nang , deg , dpc ):
    ##  Allocate memory for the sinogram
    sinogram = np.zeros( ( nang , npix ) , dtype=np.float64 )


    ##  Create projection angles
    theta = np.arange( nang ) * np. pi / myfloat( nang )


    ##  Loop on each projection angle
    for i in range( len( lut ) ):
        for j in range( nang ):
            sinogram[j,:] += calc_proj( npix , lut[i] , deg , theta[j] , dpc )

    return sinogram

        


#####################################################################
#####################################################################
####                                                             ####
####                        WRITE OUTPUT FILE                    ####
####                                                             ####
#####################################################################
#####################################################################

def write_output_file( array , mode , args ):
    ##  Get path
    path = args.path
    if path[len(path)-1] != '/':
        path += '/'     


    ##  Get degree
    deg = args.degree
    str_deg = '_deg' + str( deg )


    ##  String for number of pixels
    npix = args.npix

    if npix < 10:
        common = '000' + str( npix )    
    elif npix < 100:
        common = '00' + str( npix )
    elif npix < 1000:
        common = '0' + str( npix )
    else:
        common = str( npix )         


    ##  Save phantom
    if mode == 'image':
        if args.fileout is None:
            filename = path + 'radial_phantom'
        else:
            name = args.fileout
            filename = path + name + '_pix'

        filename += common + str_deg + args.file_format
        io.writeImage( filename , array )   
        print('\nWriting sinogram in:\n', filename)


    ##  Save sinogram
    elif mode == 'sinogram':
        nang = args.nang

        if args.fileout is None:
            filename = path + 'radial_phantom' + common + '_ang'
        else:
            name = args.fileout
            filename = path + name + '_pix' + common + '_ang'

        string = '_rt_anal_sino' 
        if args.dpc is True:
            string += '_dpc'

        if nang < 10:
            filename += '000' + str( nang )
        elif nang < 100:
            filename += '00' + str( nang ) 
        elif nang < 1000:
            filename += '0' + str( nang ) 
        else:
            filename += str( nang )  

        filename += string + str_deg + args.file_format 
        
        io.writeImage( filename , array )   
        print('\nWriting sinogram in:\n', filename)  




#####################################################################
#####################################################################
####                                                             ####
####                         MAIN PROGRAM                        ####
####                                                             ####
#####################################################################
#####################################################################

def main():
    print('\n')
    print('#########################################################')
    print('#########################################################')
    print('###                                                   ###')
    print('###             ANALYTICAL RADON TRANSFORM OF         ###')
    print('###             RADIALLY SYMMETRIC FUNCTIONS          ###')  
    print('###                                                   ###')     
    print('#########################################################')
    print('#########################################################') 
    print('\n')


    ##  Get arguments
    args = getArgs()


    ##  Get input parameters
    npix = args.npix
    nang = args.nang
    deg  = args.degree
    dpc  = args.dpc
    
    print('\nNumber of pixels: ', npix)
    print('Number of views: ', nang)
    print('Function degree: ', deg)
    print('Option DPC: ', dpc)


    ##  Create LUT for the radially symmetric functions
    lut = create_lut( npix )


    ##  Create Shepp-Logan phantom
    phantom = create_phantom( npix , deg , lut )

    
    ##  Write phantom
    write_output_file( phantom , 'image' , args )


    ##  Plot phantom
    if args.plot is True:
        dis.plot( phantom , 'Radon phantom  with ' + str( npix ) + ' X ' +  str( npix ) + ' pixels')

    

    ##  Compute analitically radon transform of the phantom
    if args.nang is not None:
        print('\nCalculating analytical radon transform of the phantom ....')

        sinogram = radon_transform_analytical( lut , npix , nang , deg , dpc )
        if args.dpc is False:
            sinogram[:,:] = sinogram[:,::-1]
        sinogram[:,:] = np.roll( sinogram , 1 , axis=1 )


        ##  Write sinogram
        write_output_file( sinogram , 'sinogram' , args )


        ##  Plot Shepp-Logan phantom
        if args.plot is True:
            dis.plot( sinogram , 'Sinogram  ' + str( nang ) + ' views X ' + str( npix ) + ' pixels' )
    
    print('\n\n')




#####################################################################
#####################################################################
####                                                             ####
####                     CALL TO MAIN PROGRAM                    ####
####                                                             ####
#####################################################################
#####################################################################

if __name__ == '__main__':
    main() 
