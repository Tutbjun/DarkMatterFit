# Dark matter fit
Codebase for constraining epsilon given magnetic field data.

Three files are currently in use:

1) np_data_downsampler.py
   
Takes the meassured data and downsamples it to the wished sampling rate
2) dict_file_2_np.py
   
An auxillary file for fieldline data: takes the csv file and converts it inot npy file format.

3) Bayesian pipeline.ipynb
   
This is the main data-processing script, and goes all the way from meassure field strength to a constraint on epsilon. Roughly the following steps are performed:

*) Fourier transformation of data

*) Calculation of noise covariance

*) Numeric calculation of theoretical $\mu$ values

*) Decomposition of data into relevant matricies

*) (Assuming the correct formula for d-marginalization) calculates the integral for the upper bound on $\epsilon$ given a Jeffreys prior.
