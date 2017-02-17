#################################################################################
#################################################################################
#################################################################################
#######                                                                   #######
#######                  MY IMAGE INPUT INPUT-OUTPUT                      #######
#######                                                                   #######
#######  Collection of functions to read and write images for different   #######
#######  formats or to convert a format to an other one.                  #######
#######  Currently implemented formats:                                   #######
#######                 1) Dump  --->  .DMP                               #######
#######                 2) TIF   --->  .tif                               #######
#######                 3) JPEG  --->  .jpg                               #######
#######  Available conversions:                                           #######
#######                 1) DMP   --->  tif                                #######
#######                 2) tif   --->  DMP                                #######
#######                                                                   #######
#######        Author: Filippo Arcadu, arcusfil@gmail.com, 13/08/2013     #######
#######                                                                   #######
#################################################################################
#################################################################################
#################################################################################    




####  PYTHON PACKAGES
import numpy as np
import scipy
from scipy import misc as misc
import skimage.io as skio
from PIL import Image




####  PYTHON PLOTTING MODULES
import matplotlib.pyplot as plt
import matplotlib.cm as cm




####  EQUIVALENT EXTENSION
ext_dmp = [ 'dmp' , 'DMP' ]
ext_tif = [ 'tif' , 'tiff' , 'TIF' , 'TIFF' ]
ext_jpg = [ 'jpg' , 'jpeg' , 'JPG' , 'JPEG' ]
ext_png = [ 'png' , 'PNG' ]
ext_raw = [ 'raw' , '.RAW' ]




####################################################
#############                          #############
#############    PARAMETERS FOR I/O    #############
#############                          #############
####################################################
##
##  Class which contains some useful parameters to either
##  read or write images of different formats

class paramIO:
    def __init__ ( self ):
        ##  Name of the file to read/write
        self.filename = None

        ##  File extension
        self.extension = None

        ##  Dimensions ( for raw headerless file )
        self.dims = None

        ##  Type ( for raw headerless file )
        self.type = None  

        ##  Array to write
        self.imarray = None

        ##  Depth of TIFF images: it can be 8 or 16 bits
        self.tifDepth = 8

        ##  Compression level for JPEG: it can range from 0 to 100
        self.jpegCompr = 0

    def getImageType( self ):
        chunks = self.filename.split('.')
        self.extension = chunks[len( chunks )-1]  




####################################################
#############                          #############
#############         CHECK ARGS       #############
#############                          #############
####################################################
##
##  Check input arguments for reading operations

def checkArgsRead( args , obj ):
    ##  Get name of the file
    obj.filename = args[0]

    ##  Get file extension
    obj.getImageType()

    ##  If it a raw headerless file get sizes
    if obj.extension in ext_raw:
        if len( args ) < 3:
            raise ValueError( 'Not specified dimensions and type \
                               of RAW file to read !!' )
        obj.dims = np.array( args[1] ).astype( np.int )
        obj.type = args[2]



##  Check input arguments for writing operations 

def checkArgsWrite( args , obj ):
    ##  Get name of the file
    obj.filename = args[0]

    ##  Get file extension
    obj.getImageType()

    ##  Get array to be written
    obj.imarray = args[1]

    ##  Get other parameters for writing    
    if len( args ) == 3:
        ##  get the depth if it is a TIFF image 
        if obj.extension in ext_tif:
            obj.tifDepth = int( args[2] )

        ##  get level of jpeg compression
        elif obj.extension in ext_jpg:
            obj.jpegCompr = int( args[2] )

    elif len( args ) == 4:
        obj.dims = args[2]
        obj.type = args[3]  




####################################################
#############                          #############
#############   GENERAL I/O ROUTINES   #############
#############                          #############
####################################################
##
##  READ IMAGE
##  This routine automatically recognizes the image format and opens it

def readImage( *args ):
    ##  Initialize class I/O
    obj = paramIO()

    ##  Check input arguments
    checkArgsRead( args , obj )

    ##  Select which image format you have to deal with
    if obj.extension in ext_dmp:
        return readImageDmp( obj )

    elif obj.extension in ext_tif:
        return readImageTif( obj )
    
    elif obj.extension in ext_jpg:
        return readImageJpeg( obj )

    elif obj.extension in ext_png:
        return readImagePng( obj )

    elif obj.extension in ext_raw:
        return readImageRaw( obj )

    else:
        raise Exception('\nI/O of files ' + obj.extension + ' not supported yet!\n')


##  WRITE IMAGE
##  This routine automatically recognizes the image format and writes it   

def writeImage( *args ):
    ##  Initialize class I/O
    obj = paramIO()

    ##  Check input arguments
    checkArgsWrite( args , obj )   

    ##  Select which image format you have to deal with 
    if obj.extension in ext_dmp:
        writeImageDmp( obj )
    
    elif obj.extension in ext_tif:
        writeImageTif( obj ) 

    elif obj.extension in ext_jpg:
        writeImageJpeg( obj )

    elif obj.extension in ext_png:
        writeImagePng( obj )

    elif obj.extension in ext_raw:
        writeImageRaw( obj )

    else:
        raise Exception('\nI/O of files ' + obj.extension + ' not supported yet!\n')   




#################################################
#############                       #############
#############   DMP I/O FUNCTIONS   #############
#############                       #############
################################################# 
##
##  DUMP IMAGE READER

def readImageDmp( obj ):
    fd = open( obj.filename , 'rb' )
    datatype = 'h'
    numberOfHeaderValues = 3
    headerData = np.zeros(numberOfHeaderValues)
    headerData = np.fromfile(fd, datatype, numberOfHeaderValues)
    imageShape = (headerData[1], headerData[0])
    imageData = np.fromfile(fd, np.float32, -1)
    imageData = imageData.reshape(imageShape)

    return imageData.astype(np.float32)


##  DUMP IMAGE WRITER

def writeImageDmp( obj ):
    fd = open( obj.filename , 'wb')
    np_array = obj.imarray
    width = np.array(np_array.shape[1])
    height = np.array(np_array.shape[0])
    header = np.array([width, height, 0], np.uint16)
    header.tofile(fd)
    if np_array.dtype != 'float32':
        np_array = np_array.astype(np.float32)
    np_array.tofile(fd)




#################################################
#############                       #############
#############   TIF I/O FUNCTIONS   #############
#############                       #############
#################################################       
##
##  TIF IMAGE READER

def readImageTif( obj ):
    image = skio.imread( obj.filename )
    return image


##  8 BIT TIF IMAGE WRITER

def writeImageTif( obj ):
    skio.imsave( obj.filename , obj.imarray )




#################################################
#############                       #############
#############   JPEG I/O FUNCTIONS  #############
#############                       #############
#################################################       
##
##  JPEG IMAGE READER

def readImageJpeg( obj ):
    fileName = obj.filename
    return misc.imread( fileName )


##  JPEG IMAGE WRITER
def writeImageJpeg( obj ):
    fileName = obj.filename
    comprss = obj.jpegCompr
    visual = obj.imarray
    visual = ( visual - visual.min() ) / ( visual.max() - visual.min() )
    imageAs2DArray = ( visual * 255 ).astype( np.uint8 )
    image = Image.fromarray( imageAs2DArray )
    q = obj.jpegCompr
    image.save( fileName , quality=q )




#################################################
#############                       #############
#############   PNG I/O FUNCTIONS   #############
#############                       #############
#################################################       
##
##  PNG IMAGE READER

def readImagePng( obj ):
    fileName = obj.filename
    return misc.imread( fileName )


##  PNG IMAGE WRITER
def writeImagePng( obj ):
    fileName = obj.filename
    imageAs2DArray = obj.imarray
    misc.imsave( fileName , imageAs2DArray )  




#################################################
#############                       #############
#############   RAW I/O FUNCTIONS   #############
#############                       #############
#################################################       
##
##  RAW IMAGE READER

def readImageRaw( obj ):
    fp = open( obj.filename , 'rb' )
    image = np.fromfile( fp , obj.type ).reshape( obj.dims )
    fp.close()
    return image


##  RAW IMAGE WRITER

def writeImageRaw( obj ):
    fp = open( obj.filename , 'wb' )
    fp.write( obj.imarray )
    fp.close()

    


###########################################
#############                 #############
#############   CONVERSIONS   #############
#############                 #############
########################################### 

def convert( file1 , file2 ):
    imageData = readImage( file1 )

    if imageData.ndim == 3 and file2[len(file2)-4:] == '.DMP':
        imageData = imageData.astype( np.float32 )
        imageData = 0.2126 * imageData[:,:,0] + 0.7152 * imageData[:,:,1] \
                    + 0.0722 * imageData[:,:,2]

    writeImage( file2 , imageData )




##################################################
#############                        #############
#############   PLOTTING FUNCTIONS   #############
#############                        #############
##################################################

##  GRAY SCALE PLOT OF DMP IMAGE

def plotImageDmp( filename ):
    imageDmp = readImageDmp( filename )
    plt.imshow( imageDmp , cmap = cm.Greys_r )
    plt.show()    
