# Statistics of Variability in Main-Sequence Stars

=== Requirements ===

The scripts were written in Ubuntu (Debian-based) Linux. They should work for any UNIX system that uses the Bash shell.


Python 3.x, along with the follwoing libraries:
- Matplotlib
- Numpy
- Scipy
- Astropy
- Tkinter
- PyPDF2

The best option is to download the Anaconda Python distribution: https://www.anaconda.com/download/#linux
- This distribution will contain most of the necessary libraries, with only PyPDF2 missing.
  Simply run the following command to download:  "sudo pip install pypdf2"

----------------------------------------------------------------------------------------------------------------------------

Only two python scripts have to be run in order to work with the data, in the following order:

== obj_id.py ==

This script is what manages the K2 data. It will ensure the necesary directories and files are present in order to function properly during initialization.

The main 2 commands are:

= Download =

Allows the user to download the FITS files for the targets of each campaign.

= Process =

Manipulates the previously downloaded files by:
- Exctracts lightcurves and times of observation, as well as some observational metadata from the FITS file.
- Searches for physical metadata on the target in the EPIC catalog.
- Performs calculations such as putting the lightcurve in ppm and calculating the amplitude spectrum.
- Saves everything into a new FITS file for convenience.

== data_visualpy ==

This script launches the GUI interface used to view/flag data. Some notes about its functionality:

= Flagging =

In order to flag the currently selected dataset, pressing the corresping key on the keyboard will flag it appropriately:
- d : Delta Scuti Candidate
- g : Gamma Dor Candidate
- h : Delta Sct/Gamma Dor Hybrid
- b : Binary
- s : Low Frequency Other Star
- f : High Frequency Other Star
- j : Unprocessed Data/Noise

= File Menu =

- Save As PDF -
This will save everything in the filelist (The box where the target file is selected). Not recommended to use when an entire campaign is displayed. Recommended to refine the box listing with Search parameters.

After creating the PDF, it will be saved in the main directory as 'k2mission.pdf'. Say if this file contained only Delta Scuti stars, it's recommended to rename it and save it elsewhere, since the app creates and appends to the 'k2mission.pdf' file by default.

= Histograms & Plots =

The options in these menus will open a new menu, showing the selected graph for the currently selected campaign in a new window

= Mission =

This menu contains the same options as Histograms & Plots, but these are for the entire mission (includes all processed campaigns)

= Searching =

After inputting the desired search parameters, pressing the Search button will update the filelist box with targets that fulfill the requirements.

Some details to keep in mind:
- Currently, searching for more than two flags is not functional. Only searching for both Temperature and Surface Gravity ranges are allowed.
- In order to refresh the list of targets from the established filters, reselection of the Campaign is needed.

