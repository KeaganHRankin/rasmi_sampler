# RASMI LCA sampler
This repository contains a compact, object-oriented, easy to use monte carlo sampler for connecting the RASMI building use material dataset with LCA factors.

### RASMI
RASMI is a global dataset of building material intensities. The dataset can be used for material flow and emission applications. More information on RASMI can be found in Fishman et al. (2024) at the following [link](https://doi.org/10.1038/s41597-024-03190-7)

### Sampler
The package contains `rasmi_lca_v1.py`, a python program that links RASMI to LCA factors in a standard excel format. The program can quickly query the RASMI dataset and emission factors. The program also supports bootstrapped sampling of RASMI and LCA factors together, and will return these samples for any combination of structures, materials, and countries in the world.

### Emission factors
LCA factors can be found in the `rasmi_sampler/data/lca_factors/compiled_ecoinvent_lca_factors.xlsx` file. As an example for this package, we compile global IPCC2021 GWP100 factors to link to the RASMI dataset. Theoretically, and LCA factors could be inserted into this file or compiled in a seperate excel file in the same format in order to perform analysis of other environmental impacts (e.g. biodiversity, water scarcity).

### Questions and comments
Please contact keagan.rankin@mail.utoronto.ca