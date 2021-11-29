![GitHub last commit](https://img.shields.io/github/last-commit/Radiation-Transport/SCtools)
![GitHub issues](https://img.shields.io/github/issues/Radiation-Transport/SCtools)
![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/Radiation-Transport/SCtools)
![GitHub top language](https://img.shields.io/github/languages/top/Radiation-Transport/SCtools)
![](https://img.shields.io/badge/license-EU%20PL-blue)

# SCtools
This is a package grouping a set of useful IronPython routines to manipulate/analyse/modify CAD files in SpaceClaim environment.

SCtools contains the following independent tools:
1) Elbow2Cyl
2) CADTree_analyser
3) Various scripts


## Elbow2Cyl
Routine which automatically substitutes the elbow of a pipe or tube into a
simplified geometry made of cylinders as required by the MCNP modelling rules.
Elbow2Cyl has two main branches, each performing a different and independent 
simplification process. The process used will be decided according to a 
parameter provided by the user. The script has been extensively tested 
with SpaceClaim version 19.2 running on the API V17. 


## CADTree_analyser
Tool which exports in a csv file the features of the parts/elements/bodies
contained in the CAD file (e.g. density, volume, mass) as well as the CAD root 
tree. This routine might result very useful for the original/simplified CAD comparison.
The script has been extensively tested with SpaceClaim version 19.2 running on the API V17. 


## Various scripts
A collection of IronPython and CPython scripts that add many new capabilities.

## License
Copyright 2019 F4E | European Joint Undertaking for ITER and the Development of Fusion Energy (‘Fusion for Energy’). Licensed under the EUPL, Version 1.1 or - as soon they will be approved by the European Commission - subsequent versions of the EUPL (the “Licence”). You may not use this work except in compliance with the Licence. You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl.html   
Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the Licence permissions and limitations under the Licence.
