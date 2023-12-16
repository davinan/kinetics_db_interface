# Kinetics Database Interface
A python API to find kinetics information and reactions from Kinetics databases + an intuitive interface to Tellurium

## Datasets Currently Supported

* [SabioRK](http://sabio.h-its.org/) enzyme dataset. 

Dataset of Enzyme kinetics data. Has parameters for Km, Vmax, kcat, and Ki (sometimes not all at once)
## Model Enzyme Kinetics using the Rapid Equilibrium Approximation and experimentally determined Km and Vmax values!
Note: We assume a 1 substrate Michaelis-Menten reaction where all the other possible substrates are kept constant. 

$$E + S \rightleftharpoons ES \rightarrow E + P$$

Assumption: $E + S \rightleftharpoons ES$ is much faster than $ES \rightarrow E + P$. Therefore we can assume that the binding of the substrate to the enzyme is in equilibrium. Practically this can be modeled by using a high rate constant for the forward reaction $ E + S \rightarrow ES$

We model the $ES \rightarrow E + P$ kinetics using:
$$v = \frac{V_{max} \times [ES]}{K_m + [S]}$$

### TODO:

* Model enzyme kinetics during Steady State
* Model enzyme kinetics with inhibitor (Ki values are currently ignored)
* Include the brenda database (has kinetic parameters 

Check out the demo [here](https://colab.research.google.com/drive/1gA5_tvYiiMMuHw1AEEUqvIlYUbBfT3Md?usp=sharing)


# Pip install our package!

You can pip install the package using the following command: ```pip install git+https://github.com/davinan/kinetics_db_interface.git```

# Contribute to the package:

When developing for kinetics_db_interface, please add unittests to ```unit_tests/tests.py``` and run them using: ```python tests.py```

As of Dec 15 2023, here are the results when running ```tests.py```:


```
....3 matching entries found.
1 reactions found with valid Km and Vmax
...
----------------------------------------------------------------------
Ran 7 tests in 0.022s

OK
```


