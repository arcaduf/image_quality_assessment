IMAGE QUALITY ASSESSMENT
========================



##  Brief description
This repository contains various methods to assess the quality of an image
and to construct simulated dataset to test tomographic reconstruction algorithms.


The following metrics are included:

* Mean-Squared-Error (MSE).

* Peak-Signal-to-Noise-Ratio (PSNR).                       

* Structural Similarity Index (SSIM).

* Normalized Mutual Information (NMI).
                                
* Image Complexity.

* Resolution analysis through Edge-Profile-Fitting (EPF).
                                                     
* Resolution analysis through Fourier Ring Correlation (FRC).
                                                       
                                                       
The following routines to construct simulated datasets are included:

* Create a Shepp-Logan phantom.

* Create generic phantoms with analytical X-ray transform.

* Rescale image.

* Downsample sinogram.

* Add Gaussian or Poisson noise.

* Add Gaussian blurring.



##  Requirements
 scipy, scikit-image, PIL and h5py.



##  Test the package
Go inside the folder "data/" and unzip the test dataset: `unzip dataset.zip`.

Then, inside the folder "tests/" try to run one by one the test scripts.

When a plot is produced during the execution of a test, the script is halted until
the plot window is manually closed.