'''
DESCRIPTION:

1) The inputs for all the print functions here coded are variable and can
   go from 1 to 4:
             1st compulsory input    ---->   array to print;
             2nd facultative input   ---->   number of digits;
             3rd facultative input   ---->   'r' to print real numbers, 'c' to print complex;
             4th facultative input   ---->   label that should precede all prints;

   You can use the functions with ordered inputs (variable in number from 1 to 4):
        e.g.:   printArray(array)
                printArray(array,7)
                printArray(array,7,'c')
                printArray(array,7,'c','Column 50')
   Or you can skip the order of the inputs by specifying the fields:
        e.g.:   printArray(array,label='Column 50',var='c',digits=7)
                printArray(array,label='Column 50')

2) printArray: 
   this function prints a 1D array along the same line, e.g., a1 a2 a3 .... aN . 

3) printArrayIndex:
   this function prints a 1D array in 2 columns, specifying on the left the array
   index of each element, e.g. :   0 ---> a1
                                   1 ---> a2
                                   2 ---> a3
                                   ...  ...
                                   N ---> aN

4) printArray2D:
   this function prints a 2D array (matrix) in the classic readable form, with
   array elements organized in rows and columns, e.g.:
                        col0  col1  col2 ... colN
                  
                row0    a00   a01   a02  ...  a0N
                row1    a10   ...   ...  ...  ...
                row2    ...   ...   ...  ...  ...
                ...     ...   ...   ...  ...  ...
                rowN    aN0   ...   ...  ...  aNN

5) printArray2DIndex:
   this function prints a 2D array (matrix) in 2 columns, specifying on the left
   the corresponding row and column number of each element, e.g.:
                                 (0,0) ---> a00
                                 (0,1) ---> a01
                                 (0,2) ---> a02
                                  ...       ...
                                 (N,0) ---> aN0
                                 (N,N) ---> aNN

4) printArray3D:
   this function prints a 3D array slice per slice, that is,
   array is printed as array[i,:,:] with i considered as slice
   index, e.g.:
 
                        Slice 0:
                        a00   a01   a02  ...  a0N
                        a10   ...   ...  ...  ...
                        ...   ...   ...  ...  ...
                        ...   ...   ...  ...  ...
                        aN0   ...   ...  ...  aNN

                        Slice 1:
                        b00   b01   b02  ...  b0N
                        b10   ...   ...  ...  ...
                        ...   ...   ...  ...  ...
                        ...   ...   ...  ...  ...
                        bN0   ...   ...  ...  bNN

                        .........................
                        .........................

                        Slice k:
                        k00   k01   k02  ...  k0N
                        k10   ...   ...  ...  ...
                        ...   ...   ...  ...  ...
                        ...   ...   ...  ...  ...
                        kN0   ...   ...  ...  kNN                        

5) printArray3DIndex:
   this function prints a 3D array in 3 columns, with the first number 
   specifying the slice, the centre numbers specifying row and column of
   the selected slice and the third one representing the array element, e.g.:

                        Slice 0 ---> (0,0) ---> a00
                        Slice 0 ---> (0,1) ---> a01
                        Slice 0 ---> (0,2) ---> a02
                                  ...       ...
                        Slice 0 ---> (N,N) ---> aNN
                        Slice 1 ---> (0,0) ---> b00
                        Slice 1 ---> (0,1) ---> b01
                        Slice 1 ---> (0,2) ---> b02
                                  ...       ...
                        Slice 1 ---> (N,N) ---> bNN                        
                                  ...       ...

6) printVector:
   this function prints only numpy array used as 'proper' vectors to perform
   vector-vector and matrix-vector calculations. For instance, it prints 
   row-vectors, which are of the form 1 x n, and column-vectors, which are of
   form n x 1.
   If the input array is of the form (n,) and not of (n,1) the function will
   give an error. A numpy array of the form (n,) cannot be used to compute the
   following calculation: x.T * A * x  , where A is a matrix.

                F.Arcadu, arcusfil@gmail.com , 23/06/2013                             
'''                                                                                     
from __future__ import print_function
import sys
import numpy as np


# Default number of decimals digits
NUM_DIGITS = 3

# Function to check variable number of inputs
def checkArgs( functionName , args ):
    array = args[0]
    numberDigits = args[1]
    varType = args[2]
    label = args[3]

    if varType != 'r' and varType != 'c':
        print("\n\tERROR: The variable type input (var) is wrong!")
        print("\n\t        It can be 'r' ---> for real numbers or 'c' ---> for complex ones")
        print("\n\tUsage:\n\t",functionName,"(array)\n\t",functionName,"(array,numberDigits)\n\t",
              functionName,"(array,numberDigits,varType)\n\t",
              functionName,"(array,numberDigits,varType,label)\n\t",
              functionName,"(array,digits=numberDigits,var=varType,label=mylabel)\n\t")
        sys.exit()
    if len(args)==0 or len(args)>4:
        if len(args) == 0:
            problem = 'few'
        elif len(args)>4:
            problem = 'many'
        print("\n\tERROR: Too ",problem," inputs for myPrint.",functionName,"!")
        print("\n\tUsage: ",functionName,"(array)\n\t",functionName,"(array,numberDigits)\n\t",
              functionName,"(array,numberDigits,varType)\n\t",
              functionName,"(array,numberDigits,varType,label)\n\t")
        sys.exit()

    if functionName == 'printArray' or functionName == 'printArrayIndex':
        if array.ndim != 1:
            problem = str(array.ndim)+'D'
            print("\n\tERROR: Input selected for",functionName,
                  "is not a 1D array, but rather a",problem,"one!\n")
            sys.exit()
    elif functionName == 'printArray2D' or functionName == 'printArray2DIndex':
        if array.ndim != 2:
            problem = str(array.ndim)+'D'
            print("\n\tERROR: Input selected for",functionName,
                  "is not a 2D array, but rather a",problem,"one!\n")
            sys.exit()
    elif functionName == 'printArray3D' or functionName == 'printArray3DIndex':
        if array.ndim != 3:
            problem = str(array.ndim)+'D'
            print("\n\tERROR: Input selected for",functionName,
                  "is not a 3D array, but rather a",problem,"one!\n")
            sys.exit()    
    elif functionName == 'printVector':
        height,width = array.shape
        if height!=1 and width!=1:
            print("\n\tERROR: Input selected for",functionName,
                  "is neither a row-vector ( 1 X n ) nor a column-vector ( n x 1 )\n")
            sys.exit()   

    return array,numberDigits,varType,label



def printArray( array , digits=3 , var='r' , label=None ):
    args = [array,digits,var,label]
    array,numberDigits,varType,label = checkArgs('printArray',args)
    sys.stdout.write('\n')
    for i in range(len(array)):
        if label is None:
            if varType == 'r':
                if array[i] >= 0:
                    sys.stdout.write("+{0:.{1}f}  ".format(array[i],numberDigits))
                else:
                    sys.stdout.write("-{0:.{1}f}  ".format(np.abs(array[i]),numberDigits)) 
            elif varType == 'c':
                if array[i].real >= 0: 
                    sys.stdout.write("+{0:.{1}f}".format(array[i].real,numberDigits))
                else:
                    sys.stdout.write("-{0:.{1}f}".format(np.abs(array[i].real),numberDigits))
                if array[i].imag >= 0: 
                    sys.stdout.write("+{0:.{1}f}j  ".format(array[i].imag,numberDigits))
                else:
                    sys.stdout.write("-{0:.{1}f}j  ".format(np.abs(array[i].imag),numberDigits))    
        elif label is not(None):
            print(label,end=" ")
            if varType == 'r':               
                if array[i] >= 0:
                    sys.stdout.write("+{0:.{1}f}  ".format(array[i],numberDigits))
                else:
                    sys.stdout.write("-{0:.{1}f}  ".format(np.abs(array[i]),numberDigits)) 
            elif varType == 'c':
                if array[i].real >= 0: 
                    sys.stdout.write("+{0:.{1}f}".format(array[i].real,numberDigits))
                else:
                    sys.stdout.write("-{0:.{1}f}".format(np.abs(array[i].real),numberDigits))
                if array[i].imag >= 0: 
                    sys.stdout.write("+{0:.{1}f}j  ".format(array[i].imag,numberDigits))
                else:
                    sys.stdout.write("-{0:.{1}f}j  ".format(np.abs(array[i].imag),numberDigits))
    sys.stdout.write("\n")		



def printArrayIndex( array , digits=3 , var='r' , label=None):
    args = [array,digits,var,label]
    array,numberDigits,varType,label = checkArgs('printArrayIndex',args) 
    sys.stdout.write('\n')
    for i in range(len(array)):
        if label is None:
            if varType == 'r': 
                sys.stdout.write("k = {0}  --->  {1:.{2}f}\n".format(i,array[i],numberDigits))
            elif varType == 'c':
                sys.stdout.write("k = {0}  --->  {1:.{3}f} {2:.{3}f}j\n".format(i,array[i].real,array[i].imag,numberDigits))
        elif label is not(None):
            print(label,end=" ")
            if varType == 'r': 
                sys.stdout.write("---> k = {0} ---> {1:.{2}f}\n".format(i,array[i],numberDigits))
            elif varType == 'c':
                sys.stdout.write("---> k = {0} ---> {1:.{3}f}  {2:.{3}f}j\n".format(i,array[i].real,array[i].imag,numberDigits))



def printArray2D( array , digits=3 , var='r' , label=None ):
    args = [array,digits,var,label]
    array,numberDigits,varType,label = checkArgs('printArray2D',args) 
    sys.stdout.write('\n')
    for i in range(array.shape[0]):
        for j in range(array.shape[1]): 
            if label is None:
                if varType == 'r': 
                    if array[i,j] >= 0:
                        sys.stdout.write("+{0:.{1}f}  ".format(array[i,j],numberDigits))
                    else:
                        sys.stdout.write("-{0:.{1}f}  ".format(np.abs(array[i,j]),numberDigits))      
                elif varType == 'c':
                    if array[i,j].real >= 0: 
                        sys.stdout.write("+{0:.{1}f}".format(array[i,j].real,numberDigits))
                    else:
                        sys.stdout.write("-{0:.{1}f}".format(np.abs(array[i,j].real),numberDigits))
                    if array[i,j].imag >= 0: 
                        sys.stdout.write("+{0:.{1}f}j  ".format(array[i,j].imag,numberDigits))
                    else:
                        sys.stdout.write("-{0:.{1}f}j  ".format(np.abs(array[i,j].imag),numberDigits))
            elif label is not(None):
                print(label,end=" ")
                if varType == 'r': 
                    if array[i,j] >= 0:
                        sys.stdout.write("+{0:.{1}f}  ".format(array[i,j],numberDigits))
                    else:
                        sys.stdout.write("-{0:.{1}f}  ".format(np.abs(array[i,j]),numberDigits))      
                elif varType == 'c':
                    if array[i,j].real >= 0: 
                        sys.stdout.write("+{0:.{1}f}".format(array[i,j].real,numberDigits))
                    else:
                        sys.stdout.write("-{0:.{1}f}".format(np.abs(array[i,j].real),numberDigits))
                    if array[i,j].imag >= 0: 
                        sys.stdout.write("+{0:.{1}f}j  ".format(array[i,j].imag,numberDigits))
                    else:
                        sys.stdout.write("-{0:.{1}f}j  ".format(np.abs(array[i,j].imag),numberDigits))      	
        sys.stdout.write('\n')
    sys.stdout.write('\n')



def printArray2DIndex( array , digits=3 , var='r' , label=None ):
    args = [array,digits,var,label]
    array,numberDigits,varType,label = checkArgs('printArray2DIndex',args) 
    sys.stdout.write('\n')
    for i in range(array.shape[0]):
        for j in range(array.shape[1]): 
            if label is None:
                if varType == 'r': 
                    sys.stdout.write("( {0} , {1} )  --->  {2:.{3}f}\n".format(i,j,array[i,j],numberDigits))
                elif varType == 'c':
                    sys.stdout.write("( {0} , {1} )  --->  {2:.{4}f} {3:.{4}f}j\n".format(i,j,array[i,j].real,array[i,j].imag,numberDigits))  
            elif label is not(None):
                print(label,end=" ")
                if varType == 'r': 
                    sys.stdout.write("---> ( {0} , {1} ) ---> {2:.{3}f}\n".format(i,j,array[i,j],numberDigits))
                elif varType == 'c':
                    sys.stdout.write("---> ( {0} , {1} )  --->  {2:.{4}f}  {3:.{4}f}j\n".format(i,j,array[i,j].real,array[i,j].imag,numberDigits))              
    sys.stdout.write('\n')



def printArray3D(array,digits=3,var='r',label=None):
    args = [array,digits,var,label]
    array,numberDigits,varType,label = checkArgs('printArray3D',args) 
    sys.stdout.write('\n')
    for i in range(array.shape[0]):
        sys.stdout.write("Slice {0}:\n".format(i))        
        for j in range(array.shape[1]):
            for k in range(array.shape[2]): 
                if label is None:
                    if varType == 'r': 
                        if array[i,j,k] >= 0:
                            sys.stdout.write("+{0:.{1}f}  ".format(array[i,j,k],numberDigits))
                        else:
                            sys.stdout.write("-{0:.{1}f}  ".format(np.abs(array[i,j,k]),numberDigits))      
                    elif varType == 'c':
                        if array[i].real >= 0: 
                            sys.stdout.write("+{0:.{1}f}".format(array[i,j,k].real,numberDigits))
                        else:
                            sys.stdout.write("-{0:.{1}f}".format(np.abs(array[i,j,k].real),numberDigits))
                        if array[i].imag >= 0: 
                            sys.stdout.write("+{0:.{1}f}j  ".format(array[i,j,k].imag,numberDigits))
                        else:
                            sys.stdout.write("-{0:.{1}f}j  ".format(np.abs(array[i,j,k].imag),numberDigits))
                elif label is not(None):
                    print(label,end=" ")
                    if varType == 'r':   
                        if array[i,j,k] >= 0:
                            sys.stdout.write("+{0:.{1}f}  ".format(array[i,j,k],numberDigits))
                        else:
                            sys.stdout.write("-{0:.{1}f}  ".format(np.abs(array[i,j,k]),numberDigits))      
                    elif varType == 'c':
                        if array[i].real >= 0: 
                            sys.stdout.write("+{0:.{1}f}".format(array[i,j,k].real,numberDigits))
                        else:
                            sys.stdout.write("-{0:.{1}f}".format(np.abs(array[i,j,k].real),numberDigits))
                        if array[i].imag >= 0: 
                            sys.stdout.write("+{0:.{1}f}j  ".format(array[i,j,k].imag,numberDigits))
                        else:
                            sys.stdout.write("-{0:.{1}f}j  ".format(np.abs(array[i,j,k].imag),numberDigits))
            sys.stdout.write('\n')           
        sys.stdout.write('\n')
    sys.stdout.write('\n')


def printArray3DIndex( array , digits=3 , var='r' , label=None ):
    args = [array,digits,var,label]
    array,numberDigits,varType,label = checkArgs('printArray3DIndex',args)
    sys.stdout.write('\n')
    for i in range(array.shape[0]):
        for j in range(array.shape[1]): 
            for k in range(array.shape[2]): 
                if label is None:
                    if varType == 'r':
                        sys.stdout.write("Slice {0} ---> ( {1} , {2} )  --->  {3:.{4}f}\n"
                                         .format(i,j,k,float(array[i,j,k]),numberDigits))
                    elif varType == 'c':
                        sys.stdout.write("Slice {0} ---> ( {1} , {2} )  --->  {3:.{5}f}  {4:.{5}f}j\n"
                                         .format(i,j,k,float(array[i,j,k].real),float(array[i,j,k].imag),numberDigits))
                if label is not(None):
                    print(label,end=" ")
                    if varType == 'r':
                        sys.stdout.write("---> Slice {0} ---> ( {1} , {2} )  --->  {3:.{4}f}\n"
                                         .format(i,j,k,float(array[i,j,k]),numberDigits))
                    elif varType == 'c':
                        sys.stdout.write("---> Slice {0} ---> ( {1} , {2} )  --->  {3:.{5}f}  {4:.{5}f}j\n"
                                         .format(i,j,k,float(array[i,j,k].real),float(array[i,j,k].imag),numberDigits))                    
        sys.stdout.write('\n')



def printVector( array , digits=3 , var='r' , label=None ):
    args = [array,digits,var,label]
    array,numberDigits,varType,label = checkArgs('printVector',args)
    dims = array.shape
    sys.stdout.write('\n')    
    # print as column vector
    if dims[1] == 1:
        for i in range(dims[0]): 
            if label is None:
                if varType == 'r':
                    sys.stdout.write("{0:.{1}f}\n"
                                     .format(float(array[i]),numberDigits))
                elif varType == 'c':
                    sys.stdout.write("{0:.{2}f}  {1:.{2}f}j\n"
                                     .format(float(array[i].real),float(array[i].imag),numberDigits))
            if label is not(None):
                print(label,end=" ")
                if varType == 'r':
                    sys.stdout.write("{0:.{1}f}\n"
                                     .format(float(array[i]),numberDigits))
                elif varType == 'c':
                    sys.stdout.write("{0:.{2}f}  {1:.{2}f}j\n"
                                     .format(float(array[i].real),float(array[i].imag),numberDigits))
    # print as row vector
    if dims[0] == 1:
        for i in range(dims[1]): 
            if label is None:
                if varType == 'r':
                    sys.stdout.write("{0:.{1}f}  "
                                     .format(float(array[i,j,k]),numberDigits))
                elif varType == 'c':
                    sys.stdout.write("{0:.{1}f}  {0:.{2}f}j   "
                                     .format(float(array[i,j,k].real),float(array[i,j,k].imag),numberDigits))
            if label is not(None):
                print(label,end=" ")
                if varType == 'r':
                    sys.stdout.write("{0:.{1}f}  "
                                     .format(float(array[i,j,k]),numberDigits))
                elif varType == 'c':
                    sys.stdout.write("{0:.{2}f}  {1:.{2}f}j   "
                                     .format(float(array[i,j,k].real),float(array[i,j,k].imag),numberDigits))
    sys.stdout.write('\n')       


