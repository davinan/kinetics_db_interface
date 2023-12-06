import requests
import pandas as pd
import io
from kinetics_interface.reaction import EnzymeReaction

ENTRYID_QUERY_URL = 'http://sabiork.h-its.org/sabioRestWebServices/searchKineticLaws/entryIDs'
PARAM_QUERY_URL = 'http://sabiork.h-its.org/entry/exportToExcelCustomizable'


class SabioRKQuery():
    
    def __init__(self, pathway=None, organism=None, ecnumber=None, substrate=None, product=None):
        entryIDs = []
        # ask SABIO-RK for all EntryIDs matching a query

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


    def get_reactions(self, max_search=500):
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
        query = {'entryIDs[]':entryIDs, 'format':'tsv', 'fields[]':[
            'EntryID', 
            'Organism', 
            'UniprotID',
            'ECNumber', 
            'PubMedID',
            'TemperatureRange',
            'pHValueRange',
            'Parameter',
            'ReactomeReactionID', 
            'HasKineticData', 
            'Substrate', 
            'Product',
            ]}

        # make POST request (to get actual data)
        request = requests.post(PARAM_QUERY_URL, params=query)
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

