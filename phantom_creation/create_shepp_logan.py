#####################################################################
#####################################################################
####                                                             ####
####              COMPUTE ANALYTICAL RADON TRANSFORM             ####
####                  OF THE SHEPP-LOGAN PHANTOM                 ####
####                                                             ####
####          24/02/2014   F. Arcadu   arcusfil.gmail.com        ####
####                                                             ####
#####################################################################
#####################################################################




####  PYTHON MODULES
from __future__ import division, print_function
import argparse
import sys
import numpy as np




####  MY PYTHON MODULES
sys.path.append( '../common/' )
import my_image_io as io
import my_image_display as dis




####  VARIABLE FORMAT
myfloat = np.float64




#####################################################################
#####################################################################
####                                                             ####
####                     GET INPUT ARGUMENTS                     ####
####                                                             ####
#####################################################################
#####################################################################

def getArgs():
    parser = argparse.ArgumentParser(description='''Create phantom for analytical
                                     computation of the Radon transform''',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-D', '--path', dest='path', default='./',
                        help = 'Select path to the output folder')  

    parser.add_argument('-n', '--npix', dest='npix', type=np.int16,
                        help = 'Number of pixels of the Shepp-Logan phantom')
    
    parser.add_argument('-a', '--nang', dest='nang', type=np.int16, 
                        help = '''Number of projection angles distributed from 0
                                to pi''')
    
    parser.add_argument('-f', '--filein', dest='filein', 
                        help = '''Input file with the specifics of the ellipses;
                        e.g.: a_{1} , b_{1} , x_{1} , y_{1} , alpha_{1} , value_{1}  , npix_{1}
                              a_{2} , b_{2} , x_{2} , y_{2} , alpha_{2} , value_{2}  , npix_{2} 
                              ... ''')
    
    parser.add_argument('-p', '--plot', dest='plot', action='store_true',
                        help = '''Enable check plots''')

    parser.add_argument('-o',  dest='file_format', default='.tif',
                        help = '''Select type of outout file_format''')   

    args = parser.parse_args() 

    if args.npix is None:
        parser.print_help()
        sys.exit('\nERROR: Number of pixel of the phantom not specified!\n')              

    return args
    
    


#####################################################################  
#####################################################################
####                                                             ####
####                          CLASS ELLIPSE                      ####
####                                                             ####
#####################################################################
#####################################################################

class Ellipse:
    ##  DEFINE THE CLASS FIELDS
    def __init__ ( self , a , b , orig , rotaz , value , npix ):
        ##  Horizontal ( when "rotaz" = 0 ) semi-axis
        self.a = a * 0.5 * npix

        ##  Vertical ( when "rotaz" = 0 ) semi-axis
        self.b = b * 0.5 * npix

        ##  Origin of the ellipse; if no translation, 
        ##  it corresponds to the origin of the image
        if orig[0] >= -1 and orig[0] <= 1 and orig[1] >= -1 and orig[1] <= 1: 
            self.ctr = np.zeros( 2 , dtype=myfloat )
            self.ctr[0] = ( orig[0] + 0.5 ) * npix
            self.ctr[1] = ( orig[1] + 0.5 ) * npix
        else:
            sys.exit('''\nERROR: the ellipse origin should be placed in the square 
                         ( [ -1 , 1 ] , [ -1 , 1 ]  ) and then it gets rescaled
                         with the image size!\n''')

        ##  Rotation angle in radiants
        self.alpha = rotaz * np.pi / 180.0

        ##  Constant gray level inside the ellipse
        self.value = value

        ##  Size of the npix
        self.npix = npix


    ##  EQUATION OF THE ELLIPSE         
    def equation( self , x , y ):
        x0 = self.ctr[0]
        y0 = self.ctr[1]
        alpha = self.alpha
        a = self.a
        b = self.b
        
        return ( \
                 ( ( x - x0 ) * np.cos( alpha ) + ( y - y0 ) * np.sin( alpha ) ) * \
                     ( ( x - x0 ) * np.cos( alpha ) + ( y - y0 ) * np.sin( alpha ) ) / ( a * a ) + \
                 ( ( x - x0 ) * np.sin( alpha ) - ( y - y0 ) * np.cos( alpha )  ) * \
                     ( ( x - x0 ) * np.sin( alpha ) - ( y - y0 ) * np.cos( alpha ) ) / ( b * b ) \
               )           
        

    ##  FUNCTION TO COLOR THE ELLIPSE WITH ITS VALUE
    def color_ellipse( self , image ):
        if self.npix != image.shape[0]:
            sys.exit('''\nERROR: the ellipse does not belong to the selected image!\n''')   

        x = np.arange( self.npix )
        y = np.arange( self.npix )
        x , y = np.meshgrid( x , y )

        ind_ellipse_zero = np.argwhere( ( self.equation( x[:,:] , y[:,:] ) <= 1 ) )
        image[ind_ellipse_zero[:,0],ind_ellipse_zero[:,1]] += self.value




#####################################################################
#####################################################################
####                                                             ####
####         ELLIPSE LOOK-UP-TABLE FOR SHEPP-LOGAN PHANTOM       ####
####                                                             ####
#####################################################################
#####################################################################

def lut_shepp_logan( npix , nang ):
    ##  LUT is a 10 X 7 list, since the Shepp-Logan phantom consists of
    ##  10 ellipses and each of those ellipses is characterized by 6 numbers:
    ##  horizontal semi-axis , vertical semi-axis , origin abscissa , origin
    ##  ordinate , rotation angle , constant gray level of the ellipse ,
    ##  size of the entire image
    LUT = []

    ##  In order:
    ##  1st number  --->  horizontal ( if rotaz. is zero ) semi-axis
    ##  2nd number  --->  vertical ( if rotaz. is zero ) semi-axis
    ##  3rd number  --->  abscissa of the ellipse origin with respect to the image centre
    ##                    values can go from ( -1 , +1 )
    ##  4th number  --->  ordinate of the ellipse origin with respect to the image centre
    ##                    values can go from ( -1 , +1 ) 
    ##  5th number  --->  rotation angle
    ##  6th number  --->  constant gray level
    ##  7th number  --->  size of the entire image

    ##  Test ellipse   
    #ellipseTest = Ellipse( 0.6 , 0.3 , [ 0.1 , 0.1 ] , 0.0 , 1  , npix )
    #LUT.append( ellipseTest )

    ##  Big white ellipse in the background    
    ellipse1 = Ellipse( 0.92 , 0.69 , [ 0.0 , 0.0 ] , 90.0 , 2  , npix )
    LUT.append( ellipse1 )

    ##  Big gray ellipse in the background
    ellipse2 = Ellipse( 0.874 , 0.6624 , [ 0.0 , -0.0100 ] , 90.0 , -0.98 , npix )
    LUT.append( ellipse2 )     

    ##  Right black eye 
    ellipse3 = Ellipse( 0.31 , 0.11 , [ 0.11 , 0.0 ] , 72.0 , -1.02 , npix )
    LUT.append( ellipse3 )          

    ##  Left black eye 
    ellipse4 = Ellipse( 0.41 , 0.16 , [ -0.11 , 0.0 ] , 108.0 , -1.02 , npix ) 
    LUT.append( ellipse4 ) 
    
    ##  Big quasi-circle on the top
    ellipse5 = Ellipse( 0.25 , 0.21 , [ 0.0 , 0.17 ] , 90.0 , 0.4 , npix )
    LUT.append( ellipse5 )       

    ##   
    ellipse6 = Ellipse( 0.046 , 0.046 , [ 0.0 , 0.05 ] , 0.0 , 0.4 , npix ) 
    LUT.append( ellipse6 )

    ##   
    ellipse7 = Ellipse( 0.046 , 0.046 , [ 0.0 , -0.1 ] , 0.0 , 0.4 , npix ) 
    LUT.append( ellipse7 ) 
    
    ##  
    ellipse8 = Ellipse( 0.046 , 0.023 , [ -0.04 , -0.305 ] , 0.0 , 0.6 , npix )
    LUT.append( ellipse8 )       

    ##   
    ellipse9 = Ellipse( 0.023 , 0.023 , [ 0.0 , -0.305 ] , 0.0 , 0.6 , npix ) 
    LUT.append( ellipse9 )

    ##   
    ellipse10 = Ellipse( 0.046 , 0.023 , [ 0.03 , -0.305 ] , 90.0 , 0.6 , npix ) 
    LUT.append( ellipse10 )      

    return LUT         




#####################################################################
#####################################################################
####                                                             ####
####           ELLIPSE LOOK-UP-TABLE FOR GENERIC PHANTOM         ####
####                                                             ####
#####################################################################
#####################################################################

def lut_generic_phantom( lut_file , npix , nang ):
    LUT = []
    num_ellipses = lut_file.shape[0]
    
    
    for i in range( num_ellipses ):

        ellipse = Ellipse( lut_file[i,0] , lut_file[i,1] , [ lut_file[i,2] , lut_file[i,3] ] , 
                           lut_file[i,4] , lut_file[i,5] , npix )
        LUT.append( ellipse )

    return LUT




#####################################################################
#####################################################################
####                                                             ####
####                 CREATE SHEPP-LOGAN PHANTOM                  ####
####                                                             ####
#####################################################################
#####################################################################

def create_phantom( LUT , npix ):
    ##  Allocate memory for the phantom
    phantom = np.zeros( ( npix , npix ) , dtype=myfloat )

    ##  Draw Shepp-Logan
    num_ellipse = len( LUT )

    for i in range( num_ellipse ):
        LUT[i].color_ellipse( phantom )

    return phantom
             



#####################################################################
#####################################################################
####                                                             ####
####             CALCULATE PROJECTION OF AN ELLIPSE              ####
####                                                             ####
#####################################################################
#####################################################################   

def calc_proj_ellipse( ellipse , angle ):
    ##  Analytical formula for the projection
    ##     a  --->  horizontal semi-axis
    ##     b  --->  vertical semi-axis
    ##     alpha  --->  rotation angle of the ellipse
    ##     value  --->  constant value inside the ellipse
    ##     c  --->  function to compute factor constant for fixed ellipse and angle
    ##     c_ --->  calculated value of c for fixed ellipse and angle
    ##     p  --->  function to compute factor constant for fixed ellipse, angle and
    ##              ray-parameter
    ##     t  --->  ray-parameter         
    c = lambda a , b , ang : ( a * np.cos( ang ) )**2 + ( b * np.sin( ang ) )**2
    p = lambda a , b , v , c , t : 2 * v * a * b * np.sqrt( c - t**2 ) / c


    ##  Allocate memory for projection
    npix = ellipse.npix
    proj = np.zeros( npix , dtype=np.float64 )


    a = ellipse.a
    b = ellipse.b
    x0 = ellipse.ctr[0] - npix * 0.5 
    y0 = -( ellipse.ctr[1] - npix * 0.5 ) 

    alpha = ellipse.alpha
    v = ellipse.value

    new_ang = angle + alpha
    c_ = c( a , b , new_ang )

    for j in range( npix ):
        t = ( j - npix * 0.5 ) - ( x0 * np.cos( angle ) + y0 * np.sin( angle ) )
        if c_ - t**2 >= 0:
            proj[j] = p( a , b , v , c_ , t )

    return proj            

    


#####################################################################
#####################################################################
####                                                             ####
####         ANALYTICAL RADON TRANSFORM OF SHEPP-LOGAN           ####
####                                                             ####
#####################################################################
#####################################################################

def radon_transform_analytical( phantom , LUT , npix , nang ):
    ##  Allocate memory for the sinogram
    sinogram = np.zeros( ( nang , npix ) , dtype=np.float64 )

    ##  Create array of projection angles
    angles = np.arange( nang ) * np.pi / myfloat( nang )

    ##  Loop on each projection angle
    for i in range( len( LUT ) ): 
        for j in range( nang ):
            angle = angles[j]
            sinogram[j,:] += calc_proj_ellipse( LUT[i] , angle )

    return sinogram

        


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
    print('###  CREATE SHEPP-LOGAN AND ITS ANALYTICAL SINOGRAM   ###')        
    print('###                                                   ###')     
    print('#########################################################')
    print('#########################################################') 
    print('\n')


    
    ##  Get arguments
    args = getArgs()


    
    ##  Get number of pixels
    npix = args.npix
    nang = args.nang
    
    print('\nNumber of pixels: ', npix)
    print('Number of views: ', nang)   

    
    
    ##  Create look-up-table of Shepp-Logan ellipses or read specifics from file
    if args.filein is None:
        LUT = lut_shepp_logan( npix , nang ) 
        print('\nCreated LUT for Shepp-Logan phantom')

    else:
        lut_file = np.loadtxt( args.filein )
        LUT = lut_generic_phantom( lut_file , npix , nang )
        
        if args.filein.find( '/' ) == -1:
            name = args.filein.split( '.' )[0]
        else:
            tokens = args.filein.split( '/' )
            name = tokens[len(tokens)-1].split('.')[0]  

        print('\nReading LUT for phantom from file:\n', args.filein)
        print('Label selected for the putput files: ', name)
        


    ##  Create Shepp-Logan phantom
    phantom = create_phantom( LUT , npix )

    

    ##  Write phantom
    path = args.path
    if path[len(path)-1] != '/':
        path += '/'

    if args.filein is None:
        filename = path + 'shepp_logan_pix'
    else:
        filename = path + name + '_pix'

    if npix < 10:
        common = '000' + str( npix )    
    elif npix < 100:
        common = '00' + str( npix )
    elif npix < 1000:
        common = '0' + str( npix )
    else:
        common = str( npix )

    filename += common + args.file_format

    io.writeImage( filename , phantom )   
    
    print('\nWriting sinogram in:\n', filename)     


    
    ##  Plot phantom
    if args.plot is True:
        dis.plot( phantom , 'Shepp-Logan ' + str( npix ) + ' X ' + str( npix ) + ' pixels' )

    

    ##  Compute analitically radon transform of the phantom
    if args.nang is not None:
        print('\nCalculating analytical radon transform of the phantom ....')
        
        sinogram = radon_transform_analytical( phantom , LUT , npix , nang )
        sinogram[:,:] = sinogram[:,::-1]
        sinogram[:,:] = np.roll( sinogram , 1 , axis=1 )


        ##  Plot Shepp-Logan phantom
        if args.plot is True:
            dis.plot( sinogram , 'Sinogram  ' + str( nang ) + ' views X ' + str( npix ) + ' pixels' )


        ##  Write sinogram
        if args.filein is None:
            filename = path + 'shepp_logan_pix' + common + '_ang'
        else:
            filename = path + name + '_pix' + common + '_ang'

        if nang < 10:
            filename += '000' + str( nang ) + '_rt_anal_sino' + args.file_format
        elif nang < 100:
            filename += '00' + str( nang ) + '_rt_anal_sino' + args.file_format
        elif nang < 1000:
            filename += '0' + str( nang ) + '_rt_anal_sino' + args.file_format
        else:
            filename += str( nang ) + '_rt_anal_sino' + args.file_format  
        
        io.writeImage( filename , sinogram )
   
        print('\nWriting sinogram in:\n', filename)      
    
    
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
