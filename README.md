![GitHub last commit](https://img.shields.io/github/last-commit/Radiation-Transport/SCtools)
![GitHub issues](https://img.shields.io/github/issues/Radiation-Transport/SCtools)
![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/Radiation-Transport/SCtools)
![GitHub top language](https://img.shields.io/github/languages/top/Radiation-Transport/SCtools)
![](https://img.shields.io/badge/license-EU%20PL-blue)

# SCtools
This is a package grouping a set of useful IronPython routines to manipulate/analyse/modify CAD files in SpaceClaim environment.

SCtools contains many independent tools.

## Index of scripts
- [`adjust_by_material.py`](sctools/adjust_by_material.py) automatic CAD operations that modify a component to mantain its original volume
- [`cad_to_mcnp_comparison`](sctools/cad_to_mcnp_comparison/) automtizes the generation of reports which compare slice plots from both SpaceClaim and the MCNP plotter.
- [`csv_generator.py`](sctools/csv_generator.py) generates or updates a CSV file that tracks important information like original and simplified volume of every component of a CAD file. It is the basis for many other SCtools scripts.
- [`detect_torus.py`](sctools/detect_torus.py) paints in a shining and opaque red color all the bodies that contain toroidal surfaces for easy identification
- [`detect_volumes_to_adjust.py`](sctools/detect_volumes_to_adjust.py) paints in a shining and opaque red all the components with a volume deviation from the original one higher than a limit while painting all the other components in a transparent blue. This allows easy identification of components that require extra work, they are easily fixed with the use of [`adjust_by_material.py`](sctools/adjust_by_material.py).
- [`load_csv_points.py`](sctools/load_csv_points.py) is a simple script that allows to read a .csv file containing points coordinates and render them as spheres in SpaceClaim.
- [`mcnp_materials_from_csv.py`](sctools/mcnp_materials_from_csv.py) automatically updates a MCNP input file with the material, density, DCF, comments and naming found in the CSV file generated with [`csv_generator.py`](sctools/csv_generator.py).
- [`report_generation`](sctools/report_generation/) generates reports that show CAD comparisons between original and simplified components. 
- [`save_step.py`](sctools/save_step.py) automatically exports a SpaceClaim CAD document into STEP format in a way that will maintain the component hierachy order after MCNP conversion via SuperMC.
- [`show_by_material.py`](sctools/show_by_material.py) select a material as found in the CSV file and only the components that make use of that material will be visible


## License
Copyright 2019 F4E | European Joint Undertaking for ITER and the Development of Fusion Energy (‘Fusion for Energy’). Licensed under the EUPL, Version 1.1 or - as soon they will be approved by the European Commission - subsequent versions of the EUPL (the “Licence”). You may not use this work except in compliance with the Licence. You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl.html   
Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the Licence permissions and limitations under the Licence.
