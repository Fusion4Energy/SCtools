# SCtools
This is a package grouping a set of useful routines to manipulate/analyse/modify CAD files in SpaceClaim environment.

Detailed information and documentation is available on request contacting marco.fabbri@f4e.europa.eu

SCtools contains the following independent tools:
1) Elbow2Cyl
2) CADTree_analyser


# Elbow2Cyl
Routine which automatically substitutes the elbow of a pipe or tube into a
simplified geometry made of cylinders as required by the MCNP modelling rules.
Elbow2Cyl has two main branches, each performing a different and independent 
simplification process. The process used will be decided according to a 
parameter provided by the user. The script has been extensively tested 
with SpaceClaim version 19.2 running on the API V17. 


# CADTree_analyser
Tool which exports in a csv file the features of the parts/elements/bodies
contained in the CAD file (e.g. density, volume, mass) as well as the CAD root 
tree. This routine might result very useful for the original/simplified CAD comparison.
The script has been extensively tested with SpaceClaim version 19.2 running on the API V17. 