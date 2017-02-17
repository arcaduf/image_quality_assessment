#################################################################################
#################################################################################
################################################################################# 
#######                                                                   #######
#######              SET OF ROUTINES TO TRASFORM IMAGES                   #######
#######                                                                   #######
#######      List of functions to trasform images of specific types:      #######
#######                       .DMP , .h5 , .tif                           #######
#######                                                                   #######
#######                        FUNCTION LIST:                             #######
#######                   1) rotate90Clockwise                            #######
#######                   2) rotate90Counterclockwise                     #######
#######                   3) flipVertically                               #######
#######                   4) flipHorizontally                             #######
#######                   5) transpose image                              #######
#######                   6) change dynamic range                         #######
#######                   7) crop region of interest                      #######
#######                                                                   #######
#######        Author: Filippo Arcadu, arcusfil@gmail.com, 09/07/2013     #######
#######                                                                   #######
#################################################################################
#################################################################################
#################################################################################  




####  PYTHON MODULES
from __future__ import print_function
import argparse
import sys
import os,os.path
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm




####  MY PYTHON MODULES
sys.path.append('/home/arcusfil/tomcat/Programs/python_ambient/Common/')
import myImageIO as io



####  MY VARIABLE TYPE
myFloat = np.float32




####  LIST OF KEYWORDS RELATED TO THE AVAILABLE TRANSFORMATIONS
availActionArr = ['rc','ra','fv','fh','tr']




####  HANDLING INPUT ARGUMENTS
def getArgs():
    parser = argparse.ArgumentParser(description='Transform dump images ( .DMP).',
                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-Di','--pathin',dest='pathin',default='./',
                        help = 'Specify input folder')
    parser.add_argument('-Do','--pathout',dest='pathout',
                        help = 'Specify output folder') 
    parser.add_argument('-i','--input',dest='input',
                        help = 'Specify a single image .DMP to be transformed')
    parser.add_argument('-l','--label',dest='label',
                        help = 'Specify common label of the input .DMP images')
    parser.add_argument('-a','--action',dest='action',
                        help = 'Specify actions to be performed on the input \
                        images; operations must be separated by a "+";'+
                        ' --------------------------------- ----------- LIST OF AVAILABLE OPERATIONS'+
                        '------------- --- clockwise rotation of 90 degrees: ------------- rc'+
                        ' --- counter-clockwise rotation of 90 degrees: ----- ra'+
                        ' --- flip vertically (around horiz. median axis): -- fv'+
                        ' --- flip horizontally (around vert. median axis): - fh'+
                        ' --- transpose image : ----------------------------- tr')
    parser.add_argument('-d','--dynRange',dest='dynRange',
                        help = 'Change dynamic range of the grey levels to fit' +
                        ' inside the specified interval; e.g.: -r minValue:maxValue')
    parser.add_argument('-c','--crop',dest='crop',
                        help = 'Crop rectangular ROI of the original image; -c value'
                        + ' to crop the inner square of side = value; -c x0:y0:value'
                        + ' to crop the square having vertex in (x0,y0) and side = value;'
                        +' -c x0:y0:x1:y1 to crop the rectangle with opposite verteces'
                        + ' (x0,y0) and (x1,y1)')
    parser.add_argument('-r', '--overwrite', dest='overwrite', action='store_true',
                        help = 'Force overwriting of hte old images with the new ones') 
    
    args = parser.parse_args()

    
    if args.input is None and args.label is None:
        parser.print_help()
        sys.exit('\nERROR: neither the input image nor a group of images'
                  + ' has been specified!')
    
    if args.action is None and args.dynRange is None and args.crop is None:
        parser.print_help() 
        sys.exit('ERROR: neither transformation to apply'
                 + ' nor to change the dynamic range'
                 + ' nor to crop the image has been selected')
 
    
    return args




####  CREATE NAME FOR THE OUTPUT IMAGES
def createOutputName( filename , operation ):
    extension = filename.split('.')
    extension = extension[len(extension)-1]
    newfilename = filename[:len(filename)-len(extension)]
    if operation == 'rc':
        newfilename += 'clockwise_rot_90'
    elif operation == 'ra':
        newfilename += 'counter_clockwise_rot_90'
    elif operation == 'fv':
        newfilename += 'vert_flip'
    elif operation == 'fh':
        newfilename += 'horz_flip'
    elif operation == 'tr':
        newfilename += 'transposed'
    elif operation == 'dr':
        newfilename += 'dyn_range_mod'
    elif operation == 'cr':
        newfilename += 'crop_roi'
    newfilename += '.'+extension
    return newfilename




####  GET LIST OF ACTIONS TO PERFORM ON THE INPUT/INPUTS
def getListOfActions( string ):
    actionArray = string.split('+')
    if len(actionArray) == 0:
        print('ERROR: No actions found! Did you separate actions with a + in the line command?')
        sys.exit()
    else:
        print('\nYou have choosen to perform ',len(actionArray),' transformations:\n')
        for index1 in range(len(actionArray)):
            insideList = 0
            for index2 in range(len(availActionArr)):
                if actionArray[index1] == availActionArr[index2]:
                    insideList = 1
                    break
            if insideList:
                print("  ",actionArray[index1],end=" ")
            else:
                print('Error the keyword: ',actionArray[index1],'does not correspond to any available'+
                      ' transformation!!\n  '+
                       'List of available operations:'+
                        '\n\tclockwise rotation of 90 degrees          --->  keyword: rc'+
                        '\n\tcounter-clockwise rotation of 90 degrees  --->  keyword: ra'+
                        '\n\tflip vertically                           --->  keyword: fv'+
                        '\n\tflip horizontally                         --->  keyword: fh'+
                        '\n\ttranspose image                           --->  keyword: tr'+ 
                        '\n\n Example:  ./myImageTransform -i image.DMP -a rc+fv+ra')
                sys.exit()
        print("\n")            
        return actionArray         




####  ROTATION OF 90 DEGREES CLOCKWISE
def rotate90Clockwise( imageArray ):
    newImageArray = np.rot90(imageArray.copy(),-1)
    return newImageArray




####  ROTATION OF 90 DEGREES COUNTER-CLOCKWISE
def rotate90Counterclockwise( imageArray ):
    newImageArray = np.rot90(imageArray.copy())
    return newImageArray




####  FLIP VERTICALLY
# it means around the horizontal centered axis
def flipVertically( imageArray ):
    newImageArray = np.zeros((imageArray.shape[0],imageArray.shape[1]),dtype=np.float128)
    newImageArray[:,:] = imageArray[::-1,:]
    return newImageArray




####  FLIP HORIZONTALLY
# it means around the vertical centered axis
def flipHorizontally( imageArray ):
    newImageArray = np.zeros((imageArray.shape[0],imageArray.shape[1]),dtype=np.float128)
    newImageArray[:,:] = imageArray[:,::-1]
    return newImageArray




####  TRANSPOSE IMAGE
def transposeImage( imageArray ):
    return np.transpose(imageArray)




####  CHANGE DYNAMIC RANGE
# it means that the grey levels of the image are rescaled to the same interval
def changeDynamicRange( imageArray , min1 , max1 ):
    min2 = np.min(imageArray)
    max2 = np.max(imageArray)
    print('\tmin value = ',min2,'  max value = ',max2)
    imageArray *= myFloat((max1-min1)/(max2-min2)) 
    return imageArray




####  CROP REGION OF INTEREST
def cropROI( imageArray , edge1 , edge2 ):
    x1 = min(edge1[0],edge2[0])
    x2 = max(edge1[0],edge2[0])
    y1 = min(edge1[1],edge2[1])
    y2 = max(edge1[1],edge2[1])
    return imageArray[x1:x2,y1:y2]




####  MAIN
def main():
    print('\n')
    print('################################################')
    print('################################################')
    print('############                        ############')
    print('############   MY IMAGE TRANSFORM   ############')
    print('############                        ############') 
    print('################################################')
    print('################################################') 
    print('\n')

    
    
    ##  Get arguments
    args = getArgs()

    
    
    ##  Get input path
    pathin = args.pathin

    if pathin[len(pathin)-1] != '/':
        pathin += '/'

    print('\nInput path:\n', pathin)



    ##  Get output path
    if args.pathout is None:
        pathout = pathin
        flag_rename = 1
    else:
        pathout = args.pathout
        if pathout == pathin:
            flag_rename = 1
        else:
            flag_rename = 0

    if pathout[len(pathout)-1] != '/':
        pathout += '/' 

    print('\nOutput path:\n', pathout)



    ##  Get single input image and apply array of actions
    if args.input is not(None):
        fileinput = args.input
        flag_single = 1



    ##  Get group of images and apply array of actions

    elif args.label is not(None):
        curr_dir = os.getcwd()
        os.chdir( pathin ) 

        label = args.label
        fileinput = sorted( glob.glob( '*' + label + '*' ) )
        flag_single = 0

        os.chdir( curr_dir )



    ##  Get list of actions to be performed
    if args.action is not(None):
        actionArray = getListOfActions( args.action )

        
        ##  Loop on all the listed actions and the listed inputs
        if flag_single:
            print('\nReading image: ', fileinput)
            imageArray = io.readImage( pathin + fileinput )
            
            for action in actionArray:
                if action == 'rc':
                    print('Applying clockwise rotation of 90 degrees')
                    imageArray = rotate90Clockwise( imageArray )
                
                if action == 'ra':
                    print('Applying counter-clockwise rotation of 90 degrees') 										
                    imageArray = rotate90Counterclockwise( imageArray )
                
                if action == 'fv':
                    print('Applying vertical flip') 										
                    imageArray = flipVertically( imageArray )
                
                if action == 'fh':
                    print('Applying horizontal flip') 
                    imageArray = flipHorizontally( imageArray )
                
                if action == 'tr':
                    print('Applying transpose') 
                    imageArray = transposeImage( imageArray )
                
                
                if flag_rename and args.overwrite is False:
                    newFileName = createOutputName( fileinput , action )
                else:
                    newFileName = fileinput

                
                print('Output file = ', newFileName)

            io.writeImage( pathout + newFileName , imageArray )



        else:
            for index in range( len( fileinput ) ):
                print('Reading image: ', fileinput[index])
                imageArray = io.readImage( pathin + fileinput[index] )
                
                for action in actionArray:
                    if action == 'rc':
                        print('Applying clockwise rotation of 90 degrees') 
                        imageArray = rotate90Clockwise( imageArray )
                    
                    if action == 'ra':
                        print('Applying counter-clockwise rotation of 90 degrees') 
                        imageArray = rotate90Counterclockwise( imageArray )
                    
                    if action == 'fv':
                        print('Applying vertical flip') 
                        imageArray = flipVertically( imageArray )
                    
                    if action == 'fh':
                        print('Applying horizontal flip') 
                        imageArray = flipHorizontally( imageArray )
                    
                    if action == 'tr':
                        print('Applying transpose')
                        imageArray = transposeImage( imageArray )

                    
                    if flag_rename and args.overwrite is False:
                        newFileName = createOutputName( fileinput[index] , action )
                    else:
                        newFileName = fileinput[index]
                    print('Output file = ', newFileName)


                io.writeImage( pathout + newFileName , imageArray )


        print('\n')
    


    ##  Change dynamic range of grey levels
    elif args.dynRange is not(None):
        dynRange = args.dynRange
        [minValue,maxValue] = [myFloat(dynRange.split(':')[0]),
                               myFloat(dynRange.split(':')[1])]
        print('Selected dynamic range interval: [',minValue,',',maxValue,']')
        # loop on all the listed actions and the listed inputs
        
        if flag_single:
            print('\nReading image: ', fileinput)
            imageArray = io.readImage( pathin + fileinput )
            
            print('Changing dynamic range')
            imageArray = changeDynamicRange( imageArray , minValue , maxValue )

            if flag_rename and args.overwrite is False:
                newFileName = createOutputName( fileinput , 'dr' )
            else:
                newFileName = fileinput  

            io.writeImage( pathout + newfileName , imageArray )        

        
        else:
            for index in range(len(fileinput)):
                print('\nReading image: ', fileinput[index])
                imageArray = io.readImage( pathin + fileinput[index] )
                
                print('Changing dynamic range') 
                imageArray = changeDynamicRange( imageArray , minValue , maxValue )

                if flag_rename and args.overwrite:
                    newFileName = createOutputName( fileinput[index] , 'dr' )
                else:
                    newFileName = fileinput[index]

                io.writeImage( pathout + newFileName , imageArray )
        
        
        print('\n')



    ##  Change dynamic range of grey levels
    elif args.crop is not(None):
        roiEdges = args.crop

        if roiEdges.find(':') == -1:
            roiEdges = int( roiEdges )
            flag_square = 1
            print('\nCrop center square of side: ', roiEdges)

        else:
            roiEdges = roiEdges.split(':')
            flag_square = 0

            if len( roiEdges ) == 4:                
                edge1 = np.array( [ int( roiEdges[0] ) , int( roiEdges[1] ) ] )
                edge2 = np.array( [ int( roiEdges[2] ) , int( roiEdges[3] ) ] )

            elif len( roiEdges ) == 3:
                edge1 = np.array( [ int( roiEdges[0] ) , int( roiEdges[1] ) ] )
                width_x = int( roiEdges[2] )
                width_y = int( roiEdges[3] )
                edge2 = np.array( [ edge1[0] + width_x , edge1[1] + width_y ] )
        
            print('\nEdges of the ROI to crop:  edge1 = ( ', edge1[0] , ' , ', edge1[1] ,
                  ')   edge2 = ( ', edge2[0] ,' , ', edge2[1] ,' )')


        ##  Loop on all the listed actions and the listed inputs
        if flag_single:
            print('\nReading image: ', fileinput)
            imageArray = io.readImage( pathin + fileinput )

            if flag_square:
                nrows , ncols = imageArray.shape
                edge1 = np.array( [ int( ( nrows - roiEdges ) * 0.5 ) , 
                                    int( ( nrows - roiEdges ) * 0.5 ) ] ,
                                    dtype=int )
                edge2 = np.array( [ edge1[0] + roiEdges , edge1[0] + roiEdges ] ,
                                    dtype=int )
            
            print('\nCropping selected ROI')
            imageArray = cropROI( imageArray , edge1 , edge2 )
            
            plt.imshow( imageArray , cmap=cm.Greys_r )
            plt.show()

            if flag_rename and args.overwrite is False:
                newFileName = createOutputName( fileinput[index] , 'cr' )
            else:
                newFileName = fileinput[index]

            io.writeImage( pathout + newFileName , imageArray ) 


        else:
            for index in range(len(fileinput)):
                print('\nReading image: ', fileinput[index])
                imageArray = io.readImage( pathin + fileinput[index] )

                if flag_square:
                    nrows , ncols = imageArray.shape
                    edge1 = np.array( [ int( ( nrows - roiEdges ) * 0.5 ) , 
                                        int( ( nrows - roiEdges ) * 0.5 ) ] ,
                                        dtype=int )
                    edge2 = np.array( [ edge1[0] + roiEdges , edge1[0] + roiEdges ] ,
                                        dtype=int ) 

                print('\nCropping selecting ROI') 
                imageArray = cropROI( imageArray , edge1 , edge2 )
                
                if flag_rename and args.overwrite is False:
                    newFileName = createOutputName( fileinput[index] , 'cr' )
                else:
                    newFileName = fileinput[index]

                io.writeImage( pathout + newFileName , imageArray )

        
        print('\n')                



    print('\n')
    print('################################################')
    print('################################################')
    print('############                        ############')
    print('############   MY IMAGE TRANSFORM   ############')
    print('############                        ############') 
    print('################################################')
    print('################################################') 
    print('\n') 
    



####  CALL TO THE MAIN
if __name__ == '__main__':
    main()
