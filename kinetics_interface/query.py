import requests
import pandas as pd
import io
from reaction import Reaction

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


    def get_reactions(self):
        # make GET request
        request = requests.get(ENTRYID_QUERY_URL, params=self.query)
        request.raise_for_status() # raise if 404 error


        # each entry is reported on a new line
        entryIDs = [int(x) for x in request.text.strip().split('\n')]
        print('%d matching entries found.' % len(entryIDs))
        # encode next request, for parameter data given entry IDs
        query = {'entryIDs[]':entryIDs, 'format':'tsv', 'fields[]':[
            'EntryID', 
            'Organism', 
            'UniprotID',
            'ECNumber', 
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
            reaction = {'params' :[],}
            for i, row in df[df.EntryID == entry_id].iterrows():
                reaction['reactants'] = row.Substrate.split(";")
                reaction['products'] = row.Product.split(";")
                reaction['name'] = row.EntryID
        
                reaction['params'].append({
                    'type': row['parameter.type'],
                    'associated_species': row['parameter.associatedSpecies'],
                    'low': row['parameter.startValue'],
                    'high': row['parameter.endValue'],
                })
        
            R = Reaction(reaction)
            if R.is_valid():
                valid_reactions.append(R)
        print(f"{len(valid_reactions)} reactions found with valid Km and Vmax")
        return df, valid_reactions

