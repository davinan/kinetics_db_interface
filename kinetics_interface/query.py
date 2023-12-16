import requests
import pandas as pd
import io
from kinetics_interface.reaction import EnzymeReaction

ENTRYID_QUERY_URL = 'http://sabiork.h-its.org/sabioRestWebServices/searchKineticLaws/entryIDs'
PARAM_QUERY_URL = 'http://sabiork.h-its.org/entry/exportToExcelCustomizable'


class SabioRKQuery():
    """
    A class for querying the SABIO-RK database for reaction kinetics information.

    This class allows for the construction of a query based on specific biochemical parameters
    such as pathway, organism, enzyme commission (EC) number, substrate, and product. The query
    can be used to retrieve reaction data, including kinetic parameters, from the SABIO-RK database.

    Attributes:
        query (dict): A dictionary representing the query parameters to be sent to the SABIO-RK API.

    Methods:
        get_reactions: Retrieve reactions from SABIO-RK based on the query parameters.
    """
    
    def __init__(self, pathway=None, organism=None, ecnumber=None, substrate=None, product=None):
        """
        Initialize the SabioRKQuery object with optional search parameters.

        Args:
            pathway (str, optional): The biochemical pathway to filter reactions.
            organism (str, optional): The organism to filter reactions.
            ecnumber (str, optional): The enzyme commission (EC) number to filter reactions.
            substrate (str, optional): The substrate to filter reactions.
            product (str, optional): The product to filter reactions.

        The constructor builds a query string that can be used to search the SABIO-RK database
        for reactions that match the given criteria.
        """
        query_dict = {}
        if pathway is not None:
            query_dict['Pathway'] = pathway
        if organism is not None:
            query_dict['Organism'] = organism
        if ecnumber is not None:
            query_dict['ECNumber'] = ecnumber
        if substrate is not None:
            query_dict['Substrate'] = substrate
        if product is not None:
            query_dict['Product'] = product
        
        query_dict['HasKineticData'] = True

        query_string = ' AND '.join(['%s:%s' % (k,v) for k,v in query_dict.items()])
        self.query = {'format':'txt', 'q':query_string}
    
    def update_query(self, pathway=None, organism=None, ecnumber=None, substrate=None, product=None):
        """
        Update the existing query parameters for the SABIO-RK database search.

        This method allows modifying the query parameters like pathway, organism, EC number, 
        substrate, and product after the SabioRKQuery object has been initialized.

        Args:
            pathway (str, optional): The biochemical pathway to filter reactions.
            organism (str, optional): The organism to filter reactions.
            ecnumber (str, optional): The enzyme commission (EC) number to filter reactions.
            substrate (str, optional): The substrate to filter reactions.
            product (str, optional): The product to filter reactions.

        The method updates the query dictionary and then reconstructs the query string based on 
        the updated parameters. This new query string is used for subsequent searches.
        """

        if pathway is not None:
            self.query['Pathway'] = pathway
        if organism is not None:
            self.query['Organism'] = organism
        if ecnumber is not None:
            self.query['ECNumber'] = ecnumber
        if substrate is not None:
            self.query['Substrate'] = substrate
        if product is not None:
            self.query['Product'] = product

        # Reconstruct the query string based on the updated query dictionary
        query_string = ' AND '.join(['%s:%s' % (k,v) for k,v in self.query.items() if k != 'format' and k != 'q'])
        self.query['q'] = query_string

    def get_reactions(self, max_search=500):
        """
        Retrieve reaction data from the SABIO-RK database based on the query parameters.

        This method performs a GET request to obtain entry IDs based on the query, and then
        a POST request to retrieve detailed reaction data for those entries. It filters and
        processes this data to return valid enzyme reactions.

        Args:
            max_search (int, optional): The maximum number of search results to process. Defaults to 500.

        Returns:
            tuple: A tuple containing two elements:
                - DataFrame: A pandas DataFrame containing detailed reaction data.
                - list: A list of EnzymeReaction objects that have valid Km and Vmax parameters.

        Raises:
            HTTPError: If the request to the SABIO-RK database fails.

        The method first performs a GET request to obtain a list of entry IDs matching the query.
        It then constructs a new query to get detailed parameters for these entries and makes a POST request.
        Finally, it processes the data to filter out valid enzyme reactions based on kinetic parameters.
        """
        # make GET request
        request = requests.get(ENTRYID_QUERY_URL, params=self.query)
        request.raise_for_status() # raise if 404 error


        # each entry is reported on a new line
        entryIDs = [int(x) for x in request.text.strip().split('\n')]
        print('%d matching entries found.' % len(entryIDs))
        if len(entryIDs) > max_search:
            print(f"Reducing search to first {max_search}")
            entryIDs = entryIDs[:max_search]

        # encode next request, for parameter data given entry IDs
        self.query = {'entryIDs[]':entryIDs, 'format':'tsv', 'fields[]':[
            'EntryID', 
            'Organism', 
            'UniprotID',
            'ECNumber', 
            'PubMedID',
            'Parameter',
            'ReactomeReactionID', 
            'HasKineticData', 
            'Substrate', 
            'Product',
            ]}

        # make POST request (to get actual data)
        request = requests.post(PARAM_QUERY_URL, params=self.query)
        request.raise_for_status()

        df = pd.read_csv(io.StringIO(request.text), sep="\t")

        # for each reaction ID with enough information to carry out Tellurium add it to a list
        valid_reactions = []
        for entry_id in df.EntryID.unique():

            R = EnzymeReaction(df[df.EntryID == entry_id])
            if R.is_valid():
                valid_reactions.append(R)
        print(f"{len(valid_reactions)} reactions found with valid Km and Vmax")
        return df, valid_reactions

