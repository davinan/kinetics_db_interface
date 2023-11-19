# Functional Specifications for Rate Constant API
### Author: Davi Nakajima An
### BIOEN 537 Computational Systems Biology

## Background

There are several chemical kinetics databases available that gather reported kinetic measurements for ready access, such as the NIST Chemical Kinetics Database and the Chemkin Thermodynamic database. The former (NIST Database) contains kinetics measurements of more than 38,000 gas-phase chemical reactions, of which there are 11,700 different reactant pairs [1]. The latter (Chemkin) contains thermodynamic properties for various chemical specias, which prove to be essential for basing simulations involving chemical reactions [2]. 

Kinetic and thermodynamics data from these datasets have been extensively used to study chemical reactions. For example, *Ravindran et al.* model gasoline spark-ignited engine combustion reactions using liquid thermochemistry data from NIST and modeling software from the Chemkin group [3]. Furthermore, *Chen et al.* simulate reaction mechanisms of silicon production using thermodynamic data from the Chemkin database [4]. 

Data scientists must efficiently leverage interfaces such as the ones described to conduct their research. They do so by using APIs that match nicely and are intuitive to use. This project aims to create an interface for accessing the NIST Chemical Kinetics Database for kinetic data ready to run simulations in Tellurium. The interface will also be designed to be scalable to incorporate new repositories of kinetic constants such as BioModels. In each database search method there will be an option to choose which database or repository to use, a flexibility which will be handled in the backend.


## User Profile 

Users will include the user base of Tellurium as well as people seeking a python interface to the NIST Chemical Kinetics Database. In essence, anyone using python to run kinetics simulations can find it useful to use the tool. 


## Use Cases

There are many hypothetical use cases for this tool. Here is a short non-exhaustive list of them: 

1. Researchers who want to screen reactions that exhibit certain phenomina kinetically (e.g. those that reach a stable equilibrium) can use this tool to rapidly search the NIST Chemical Kinetics Database for such reactions.

Example code:

```python
import kinetics_db_interface as kdi

reactions = kdi.search_reactions(reactants=['H2O'], database="NIST")

viable_reactions = []
for reaction in reactions:
    results = run_tellurium(reaction.get_tellurium_string())
    if reaches_equilibrium(results):
        viable_reactions.append(reaction)
```

Note that the above use case can also be used in a Jupyter Notebook environment


2. This tool can be used to search for reactions that students might be more familiar with, which in turn could be used as tangible use cases for using Tellurium as a modeling tool. 

Example code in a Jupyter Environment
Cell 1:
```python
import kinetics_db_interface as kdi

reactions = kdi.search_reactions(reactants=['H2O'], products=['H+', 'OH-'], database='NIST')

print(reactions)

```
Cell 2:
```python
chosen_reaction = reactions[chosen_index]

print(chosen_reaction.get_rate_info())
print(chosen_reaction.get_tellurium_string())

results = run_tellurium(chosen_reaction.get_tellurium_string())

```

3. Researcher wants to train a ML model for a chemical kinetics task. The tool can be used to access the NIST Chemical Kinetics Database efficiently on the same popular programming language for ML (python).

Example code
```python
import kinetics_db_interface as kdi

# First search for reactions you want to train your model on
reactions = kdi.search_reactions(reactants=['H2O', 'O2', ...], database='NIST')

# Train your model
model, optimizer, loss = initialize_ML_objects()

for reaction in reactions:
    results = run_tellurium(reaction.get_tellurium_string())

    prediction_results = model(reaction.get_tellurium_string())

    l = loss(results, prediction_results)

    optimizer(l)

```


## Citations

[1] J. A. Manion, R. E. Huie, R. D. Levin, D. R. Burgess Jr., V. L. Orkin, W. Tsang, W. S. McGivern, J. W. Hudgens, V. D. Knyazev, D. B. Atkinson, E. Chai, A. M. Tereza, C.-Y. Lin, T. C. Allison, W. G. Mallard, F. Westley, J. T. Herron, R. F. Hampson, and D. H. Frizzell, NIST Chemical Kinetics Database, NIST Standard Reference Database 17, Version 7.0 (Web Version), Release 1.6.8, Data version 2015.09, National Institute of Standards and Technology, Gaithersburg, Maryland, 20899-8320.  Web address:  https://kinetics.nist.gov/

[2] Kee, R. J., Rupley, F. M., and Miller, J. A.. The Chemkin Thermodynamic Data Base. United States: N. p., 1990. Web. doi:10.2172/7073290.

[3] Ravindran AC, Kokjohn SL. The challenges of using detailed chemistry model for simulating direct injection spark ignition engine combustion during cold-start. International Journal of Engine Research. 2023;24(1):161-177. doi:10.1177/14680874211045968

[4] Chen, H., Jie, Y., Yan, H., Wu, W., & Xiang, Y. (2023). Numerical simulation and validation of reaction mechanism for the Siemens process in silicon production. Journal of Crystal Growth, 618, 127314. doi:10.1016/j.jcrysgro.2023.127314
