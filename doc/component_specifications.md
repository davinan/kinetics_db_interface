# Component Specification


## Software Components

#### **Objects**

**Query**
This object will be used to both build queries to the NIST Database and to check for errors in the search parameters input by the user

Fields:
- query_string: a string representing the query 

*__init__*(self, reactants: List[str], products: List[str], constraints: Dict[str, str]):
- inputs: list of reactant and product species names and the constraints for the search
- initializes the query using build_query

*check_for_errors*(self, reactants, products, constraints):
- throws an error if the inputs are badly formed

*build_query*(self, reactants: List[str], products: List[str], constraints: List[Dict[str: str]]) -> str:
- Inputs: a list of reactant names, product names, and other constraints for the reactions that are searchable on the NIST Database
- Outputs: a query string that can be sent to the NIST Database API


**Reactions**
This object will be used to represent a reaction and will have variables for the reactants, products, and reaction rates. This object will also hold helper functions for running Tellurium simulations

Fields:
- reactants List[str]: the names of the reactants
- products List[str]: the names of the products
- stoichiometry Dict[str, float]: holds a mapping from the name of a reactant/product to its stoichiometry value
- reaction_rates Dict[str, float]: holds a mapping from a rate constant name and its value

*__init__*(self, query_result): 
- sets up an object
- Inputs: the result returned by the NIST Database API. 

*change_rate*(self, rate_name: str, rate: float): 
- enables adjusting the rate for any step of the reaction
- Inputs: the rate_constant name and its new value

*get_tellurium_string*(self) -> str: 
- Outputs: a string that can be used to run a Tellurium simulation

*get_description*(self) -> str:
- Outputs: get a description of the reaction in text that is user friendly


#### **Functions**

*execute_query*(self, query: Query) -> List[Reactions]:
- This method will be the main code-level entrypoint for the NIST Database API and will be used to access it. 
- Inputs: a query object created by build_query
- Outputs: a list of reactions returned by the NIST Database

## **Interactions to Accomplish Use Case**

Use Case: find reactions with O2 as a reactant

The user will first build a query using the Query object. Then the user will check for errors in the query, and if no errors are found, they can execute the query using the ```execute_query``` method. The user will then run a tellurium simulation and save the results of the simulation for each reaction returned by the query. A pseudocode of this can be seen below: 
```python
reactants = ['O2']
products = []
constraints = {'max_reactions_to_return': 1}
query = Query(reactants, products, constraints)

reactions = execute_query(query)

for reaction in reactions:
    simulate_and_save(reaction.get_tellurium_string)
```

## **Preliminary Plan**

1. Figure out format for querying the NIST database
2. Figure out return format from the NIST database
3. Implement the Query Object and test querying for some reactions
4. Understand the format of Tellurium simulation strings
5. Implement the Reaction Object



