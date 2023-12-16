import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append("..")
from kinetics_interface.query import SabioRKQuery
import requests
import pandas as pd
from kinetics_interface.reaction import EnzymeReaction

# Constants for mocking
FAKE_ENTRYID_QUERY_URL = "http://fake.entryid.query.url"
FAKE_PARAM_QUERY_URL = "http://fake.param.query.url"
MOCK_POST = """
EntryID	Organism	UniprotID	ECNumber	PubMedID	KineticMechanismType	parameter.type	parameter.associatedSpecies	parameter.startValue	parameter.endValue	parameter.standardDeviation	parameter.unit	ReactomeReactionID	HasKineticData	Substrate	Product
12303	Escherichia coli	P08660	2.7.2.4	14623187	Michaelis-Menten	Km	L-Aspartate	6.9E-4		-	M		true	L-Aspartate;ATP	ADP;4-Phospho-L-aspartate
12303	Escherichia coli	P08660	2.7.2.4	14623187	Michaelis-Menten	concentration	L-Aspartate	0.0	0.1	-	M		true	L-Aspartate;ATP	ADP;4-Phospho-L-aspartate
12303	Escherichia coli	P08660	2.7.2.4	14623187	Michaelis-Menten	concentration	ATP	0.016		-	M		true	L-Aspartate;ATP	ADP;4-Phospho-L-aspartate
12303	Escherichia coli	P08660	2.7.2.4	14623187	Michaelis-Menten	Vmax		7.00014E-4		-	katal*g^(-1)		true	L-Aspartate;ATP	ADP;4-Phospho-L-aspartate
"""

class TestSabioRKQuery(unittest.TestCase):

    def setUp(self):
        self.query = SabioRKQuery()

    def test_initialization(self):
        # Test initialization with no parameters
        query = SabioRKQuery()
        self.assertIn('HasKineticData', query.query['q'])

        # Test initialization with parameters
        query = SabioRKQuery(pathway='Glycolysis', organism='E. coli')
        self.assertIn('Pathway:Glycolysis', query.query['q'])
        self.assertIn('Organism:E. coli', query.query['q'])

    @patch('requests.get')
    def test_get_reactions(self, mock_get):
        # Mock the GET request
        mock_get.return_value = MagicMock(status_code=200, text='1\n2\n3')

        # Mock the POST request
        with patch('requests.post') as mock_post:
            mock_post.return_value = MagicMock(status_code=200, text=MOCK_POST)

            _, reactions = self.query.get_reactions()

            # Test if the method returns reactions
            self.assertIsInstance(reactions, list)

    def test_update_query(self):
        # Update query parameters
        self.query.update_query(pathway='TCA Cycle', substrate='Acetyl-CoA')

        # Check if query parameters are updated correctly
        self.assertIn('Pathway:TCA Cycle', self.query.query['q'])
        self.assertIn('Substrate:Acetyl-CoA', self.query.query['q'])


class TestEnzymeReaction(unittest.TestCase):

    def setUp(self):
        # Sample data to initialize EnzymeReaction instances for testing
        data = {
            'parameter.type': ['Km', 'Vmax', 'concentration', 'concentration'],
            'parameter.startValue': [0.5, 100, 10, 20],
            'parameter.endValue': [0, 0, 0, 0],
            'EntryID': [1, 1, 1, 1]
        }
        self.reaction_df = pd.DataFrame(data)
        self.enzyme_reaction = EnzymeReaction(self.reaction_df)

    def test_is_valid(self):
        # Test the is_valid method
        self.assertTrue(self.enzyme_reaction.is_valid())

    def test_initial_values(self):
        # Test if the initial values are correctly set
        self.assertEqual(self.enzyme_reaction.Km, 0.5)
        self.assertEqual(self.enzyme_reaction.Vmax, 100)
        self.assertEqual(self.enzyme_reaction.S_start, 10)
        self.assertEqual(self.enzyme_reaction.E_start, 10)  # Assuming same logic for S_start and E_start

    def test_change_value(self):
        # Test the change_value method
        new_values = {
            'Km': 1.0,
            'Vmax': 200,
            'S_start': 15,
            'E_start': 25,
            'k1': 20
        }
        self.enzyme_reaction.change_value(**new_values)
        
        self.assertEqual(self.enzyme_reaction.Km, 1.0)
        self.assertEqual(self.enzyme_reaction.Vmax, 200)
        self.assertEqual(self.enzyme_reaction.S_start, 15)
        self.assertEqual(self.enzyme_reaction.E_start, 25)
        self.assertEqual(self.enzyme_reaction.k1, 20)

    def test_get_reaction_details(self):
        # Test the get_reaction_details method
        df = self.enzyme_reaction.get_reaction_details()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue('parameter.type' in df.columns)

if __name__ == '__main__':
    unittest.main()
