import requests
import pandas as pd

class GurooClient(object):
    """
    Guroo API client. Queries location-specific costs for healthcare procedures.
    """

    def __init__(self):
        self.api_version = '2016-08-18'
        self.load_bundles()
        self.load_locations()

    def load_bundles(self):
        """Load all Guroo bundle names and codes"""
        payload = {'api-version': self.api_version}
        response = requests.get('https://api.guroo.com/CareBundles/shortcarebundles/', params=payload)
        response.raise_for_status()
        self.bundles = response.json()

    def load_locations(self):
        """Load mapping for CBSA codes and metropolitan area names"""
        df = pd.read_excel('cbsa.xls', skiprows=2, skip_footer=4, dtype={'CBSA Code': str})
        df = df[['CBSA Title', 'CBSA Code']].drop_duplicates()
        self.msa_map = df.set_index('CBSA Title').to_dict()['CBSA Code']

    def set_location(self, location):
        """Choose a metropolitan area to search for costs within"""
        self.msa_code = self.msa_map[location]
        self.location = location

    def search_locations(self, string):
        """Return a list of metropolitan area names that match a substring"""
        locations = [loc for loc in self.msa_map.keys() if string.lower() in loc.lower()]
        for loc in locations:
            print(loc)

    def search_bundles(self, string):
        """Return a list of Guroo care bundles that match a substring"""
        bundles = [b['name'] for b in self.bundles if string.lower() in b['name'].lower()]
        for bundle in bundles:
            print(bundle)

    def get_bundle_code(self, name):
        """Return the Guroo care bundle code for a given care bundle name"""
        return next(b['code'] for b in self.bundles if b['name'] == name)

    def get_bundle_id(self, code):
        """Return the Guroo care bundle id for a given care bundle code"""
        payload = {
            'api-version': self.api_version,
            'code': code
        }
        response = requests.get(url='https://api.guroo.com/CareBundles/', params=payload)
        response.raise_for_status()
        bundle_data = response.json()
        bundle_id = bundle_data['id']
        return bundle_id

    def get_cost(self, bundle_id):
        """Return the cost range for a given care bundle ID using the previously set location"""
        payload = {
            'msa': self.msa_code,
            'api-version': '2016-08-18',
        }
        response = requests.get(
            url='https://api.guroo.com/CareBundles/{}/'.format(bundle_id),
            params=payload)
        response.raise_for_status()
        data = response.json()
        sub_bundles = [s for s in data['costSheets'] if s['geoLevel'] == self.msa_code]
        cost = {}
        cost['lower'] = sum([s['percent25Allowed'] for s in sub_bundles])
        cost['mid'] = sum([s['percent50Allowed'] for s in sub_bundles])
        cost['upper'] = sum([s['percent75Allowed'] for s in sub_bundles])
        return cost

    def search(self, name):
        """Print the cost range for a given care bundle name using the previously set location"""
        code = self.get_bundle_code(name)
        bundle_id = self.get_bundle_id(code)
        cost = self.get_cost(bundle_id)
        print("Cost for '{}' in {} is typically between ${:,} and ${:,}." \
              .format(name, self.location, cost['lower'], cost['upper']))
