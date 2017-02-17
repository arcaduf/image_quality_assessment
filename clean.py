###########################################################################
###########################################################################
####                                                                   ####
####                  COMPILE ALL SUBROUTINES IN C                     ####
####                                                                   ####
###########################################################################
###########################################################################

##  Usage:
##    MODE-1:     python setup.py   --> install all subroutines in C
##    MODE-2:     python setup.py 1 --> delete all compiles files '.o', '.so' and all
##                                      folders 'debug/', 'build/' and '__pycache__' 




##  Python packages
from __future__ import division , print_function
import os
import sys
import shutil


list_img = [ 'phantom_01.tif' , 'phantom_02.tif' , 'phantom_03.tif' ,
             'phantom_04.tif' , 'sl_pix0512_ang0364_sino.tif' ]


##  Choose whether to use the script in MODE-1 or in MODE-2
if len( sys.argv ) == 1:
    clean = True
else:
    clean = False


##  Remove all compile files and related folders
curr_dir = os.getcwd()

for path , subdirs , files in os.walk( './' ):
    for i in range( len( subdirs ) ):
        folderin = subdirs[i]
        if folderin == 'build' or folderin == 'debug':
            shutil.rmtree( os.path.join( path , folderin ) )
        if folderin == '__pycache__':
            shutil.rmtree( os.path.join( path , folderin ) )
    
    for i in range( len( files ) ):
        filein = files[i]

        if filein.endswith( '.pyc' ) is True or \
           filein.endswith( '.pyo' ) is True or \
           filein.endswith( '.o' )   is True or \
           filein.endswith( '.so' )  is True or \
           filein.endswith( '.swp' )  is True or \
           filein.endswith( '.swo' )  is True or \
           filein.endswith( '.swn' )  is True or \
           filein.endswith( '~' )  is True:
            os.remove( os.path.join( path , filein ) ) 


##  Zip / Unzip data
string = ''
for i in range( len( list_img ) ):
    string += list_img[i]

if clean is False:   
    os.chdir( 'data/' )
    os.system( 'unzip dataset.zip' )
    os.system( 'rm dataset.zip' ) 


else:
    os.chdir( curr_dir ) 
    os.chdir( 'data/' )
    os.system( 'zip -r dataset.zip ' + string )
    shutil.rmtree( '*.tif' )
