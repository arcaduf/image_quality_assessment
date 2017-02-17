###########################################################
###########################################################
####                                                   ####
####                  MY IMAGE DISPLAY                 ####                 
####                                                   ####
####      Collection of functions to display images    ####      
####                                                   ####
####               Author: Filippo Arcadu              ####
####           arcusfil@gmail.com, 15/05/2013          ####
####                                                   ####
###########################################################
###########################################################



####  PYTHON MODULES
from __future__ import print_function,division
import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm




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

def plot( img , title=None , colorbar=False , axis=True ):
    
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

    if colorbar is True:
        plt.colorbar()

    if axis is False:
        plt.axis( 'off' )

    if title is not None:
        plt.suptitle( title , fontsize=20 )

    plt.show()  



def plot_multi( img_list , title_list=None , title=None , colorbar=False , axis=True ):
    
    ##  Get number of image arrays
    n = len( img_list )


    ##  Check if you have enough titles for the subplots
    if title_list is not None and len( title_list ) != n:
        sys.exit('\nERROR in myImageDisplay.plot: '
                 + 'number of image array does not match '
                 + 'with the number of subplot titles')

    if n == 2:
        num = [ 121 , 122 ]
    elif n == 3:
        num = [ 131 , 132 , 133 ]
    elif n == 4:
        num = [ 241 , 242 , 243 , 244 ]
    elif n == 5:
        num = [ 251 , 252 , 253 , 254 , 255 ]
    elif n == 6:
        num = [ 261 , 262 , 263 , 264 , 265 , 266 ]
    elif n == 7:
        num = [ 261 , 262 , 263 , 264 , 265 , 266 , 267 ]
    elif n == 8:
        num = [ 261 , 262 , 263 , 264 , 265 , 266 , 267 , 268 ]
    elif n == 9:
        num = [ 261 , 262 , 263 , 264 , 265 , 266 , 267 , 268 , 269 ]  
    elif n == 10:
        num = [ 261 , 262 , 263 , 264 , 265 , 266 , 267 , 268 , 269 , 270]


    ##  Initialize figure enviroment
    fig = plt.figure()

    for im in range( n ):
        ax = fig.add_subplot( num[im] )
        
        if title_list is not None:
            subtitle = title_list[im]
            ax.set_title( title_list[im] , fontsize=15 ) 

        ax.imshow(  img_list[im] , origin="lower" ,
                    cmap = cm.Greys_r ,
                    interpolation='nearest' )
    
        def format_coord( x , y):
            nrows, ncols = img_list[im].shape
            col = int(x+0.5)
            row = int(y+0.5)
    
            if col>=0 and col<ncols and row>=0 and row<nrows:
                z = img_list[im][row,col]
                return 'x=%d, y=%d, value=%1.4e'%(x, y, z)
            else:
                return 'x=%d, y=%d'%(x, y)   

        ax.format_coord = format_coord

        if colorbar is True:
            PCM = ax.get_children()[2]
            plt.colorbar( PCM , ax=ax )


    if title is not None:
        plt.suptitle( title , fontsize=20 )


    plt.show()
