#######################################################################
#######################################################################
####                                                               ####
####                      DOWNSAMPLE SINOGRAM                      ####
####                                                               ####
####           Written by F. Arcadu  on the 06/02/2014             ####
####                                                               ####
#######################################################################
#######################################################################




####  PYTHON MODULES
from __future__ import print_function , division
import argparse
import sys
import numpy as np
import bisect




####  MY PYTHON MODULES
sys.path.append( '../common/' )
import my_image_io as io
import my_image_display as dis




####  MY FORMAT VARIABLE
myfloat = np.float32




################################################################
################################################################
####                                                        ####
####                   GET INPUT ARGUMENTS                  ####
####                                                        ####
################################################################
################################################################

def getArgs():
    parser = argparse.ArgumentParser(description='''Downsample sinogram''',
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-Di','--pathin', dest='pathin', default='./',
                        help = 'Path to input sinogram')
    
    parser.add_argument('-Do','--pathout', dest='pathout',
                        help = 'Path to the output folder')   
    
    parser.add_argument('-i','--sino', dest='sino',
                        help = 'Input sinogram name')
    
    parser.add_argument('-g', '--geometry', dest='geometry',default='0',
                        help='Specify projection geometry;'
                             +' -g 0 --> equiangular projections between 0 and 180 degrees (default);'
                             +' -g angles.txt use a list of angles (in degrees) saved in a text file')          
    
    parser.add_argument('-f', '--factor', dest='factor', type=int,
                        help='Downsampling factor along the pixel direction')

    parser.add_argument('-n', '--nproj', dest='nproj', type=int,
                        help='Specify how many projections to consider')      
    
    parser.add_argument('-p', '--plot', dest='plot', action='store_true',
                        help='Display input and output images')      

    args = parser.parse_args()

    if args.sino is None:
        parser.print_help()
        sys.exit('\nERROR: Input sinogram name not specified!\n')
        
    if args.factor is None and args.nproj is None:
        parser.print_help()
        sys.exit('\nERROR: Neither number of projections nor factor along the pixel' + \
                 ' has been specified!\n')       

    return args




################################################################
################################################################
####                                                        ####
####                   PROJECTION GEOMETRY                  ####
####                                                        ####
################################################################
################################################################

def create_projection_angles( args , nang ):
    if args.geometry == '0':
        print('\nDealing with equiangular projections distributed between 0 and'
                +' 180 degrees ---> [0,180)')
        angles = np.arange( nang ).astype( myfloat )
        angles[:] = ( angles * 180.0 )/myfloat( nang )

    else:
        geometryfile = pathin + args.geometry
        print('\nReading list of projection angles: ', geometryfile)
        angles = np.fromfile( geometryfile , sep="\t" )
        nang = len( angles )

    return angles




################################################################
################################################################
####                                                        ####
####                      BINARY SEARCH                     ####
####                                                        ####
################################################################
################################################################ 
    
def binary_search( array , el ):
    ind  = bisect.bisect_left( array , el )

    if array[ind] > el:
        ind_left  = ind - 1
        ind_right = ind
    else:
        ind_left  = ind
        ind_right = ind + 1  
    
    al = array[ind_left];  ar = array[ind_right]

    if np.abs( al - el ) < np.abs( ar - el ):
        return ind_left
    else:
        return ind_right




################################################################
################################################################
####                                                        ####
####      DOWNSAMPLE SINOGRAM ALONG THE ANGLE DIRECTION     ####
####                                                        ####
################################################################
################################################################

def downsample_sinogram_angles( sino , angles , args ):
    nang = len( angles )
    nproj = args.nproj
        
    angles_aux = np.arange( nproj ).astype( myfloat ) 
    angles_aux[:] = ( angles_aux * 180.0 )/myfloat( nproj )
        
    ii = np.zeros( nproj , dtype=int )
    for i in range( nproj ):
        ii[i] = binary_search( angles , angles_aux[i] )
    
    sino_down   = sino[ii,:]
    angles_down = angles[ii]
    
    print('\nDownsampling sinogram to ', nproj,' projections')

    return sino_down , angles_down




################################################################
################################################################
####                                                        ####
####      DOWNSAMPLE SINOGRAM ALONG THE PIXEL DIRECTION     ####
####                                                        ####
################################################################
################################################################

def downsample_sinogram_pixels( sino , args ):
    nang , npix = sino.shape
    
    fac = args.factor
    if fac < 2:
        fac = 2
    
    sino_down   = sino[:,::fac]
    
    print('\nDownsampling sinogram by ', fac,' in number of pixels')

    return sino_down
    
    
    
    
################################################################
################################################################
####                                                        ####
####             DOWNSAMPLE SINOGRAM IN ANGLES              ####
####                                                        ####
################################################################
################################################################

def write_output_files( sino , angles , args , pathin , filename ):
    nang , npix = sino.shape

    if args.pathout is None:
        pathout = pathin
    else:
        pathout = args.pathout

    extension = filename[len(filename)-4:]
    name_base = filename[:len(filename)-4] + '_'
    
    if args.nproj is not None:
        fileout = name_base + 'ang'
        num     = nang
    elif args.factor is not None:
        fileout = name_base + 'pix'
        num     = npix        

    if num < 10:
        string = '000' + str( num )
    elif num < 100:
        string = '00' + str( num )
    elif num < 1000:
        string = '0' + str( num )
    else:
        string = str( num )  

    fileout = pathout + fileout + string + extension
    io.writeImage( fileout , sino )
    print('\nWritten downsampled sinogram:\n', fileout)

    if args.nproj is not None:
        fileout = pathout + name_base + string + '_angle_list.txt'   
        np.savetxt( fileout , angles , delimiter='\n' )
        print('\nWritten corresponding list of angles:\n', fileout)     




################################################################
################################################################
####                                                        ####
####                      MAIN PROGRAM                      ####
####                                                        ####
################################################################
################################################################ 

def main():
    print('\n')
    print('##############################################')
    print('##############################################')
    print('####                                      ####')
    print('####         DOWNSAMPLE SINOGRAM          ####')
    print('####                                      ####')      
    print('##############################################')
    print('##############################################')  
    print('\n') 


    ##  Get input arguments
    args = getArgs()


    
    ##  Read input sinogram
    pathin = args.pathin
    if pathin[len(pathin)-1] != '/':
        pathin += '/'

    filename = args.sino
    sino = io.readImage( pathin + filename )
    nang , npix = sino.shape

    print('\nInput path:\n', pathin)
    print('\nInput sinogram:\n', filename)
    print('Sinogram size: ', nang,' ang  X  ', npix,' pixels')


    
    ##  Getting projection geometry  
    angles = create_projection_angles( args , nang )



    ##  Downsample sinogram
    angles_down = None
    
    if args.nproj is not None:
        sino_down , angles_down = downsample_sinogram_angles( sino , angles , args )
        
    elif args.factor is not None:
        sino_down = downsample_sinogram_pixels( sino , args )        


    
    ##  Display check plot
    if args.plot is True:
        sino_list = [ sino , sino_down ]
        title_list = [ 'Original sinogram' , 'Undersampled sinogram' ]
        dis.plot_multi( sino_list , title_list )



    ##  Write image & angle list
    write_output_files( sino_down , angles_down , args , pathin , filename )
                 
    print('\n')




################################################################
################################################################
####                                                        ####
####                 CALL TO MAIN PROGRAM                   ####
####                                                        ####
################################################################
################################################################

if __name__ == '__main__':
    main()  
