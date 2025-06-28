"""
Class for importing and sampling the RASMI dataset and linking it with
A1-A3 LCA factors to estimate embodied emissions of building construction.
"""

import numpy as np
import pandas as pd


class RasmiLCA:
    
    def __init__(self, rasmi_path='', factors_path=''):
        if rasmi_path == '':
            self.rasmi_path = 'data/RASMI/RASMI_MI_data_20230905.xlsx'
        else:
            self.rasmi_path = rasmi_path

        if factors_path == '':
            self.factors_path = 'data/lca_factors/compiled_ecoinvent_lca_factors.xlsx'
        else:
            self.factors_path = factors_path
        
        #self.factors_path = 'data/lca_factors/compiled_ecoinvent_lca_factors.xlsx'

        # set datasets
        self.rasmi = self.import_rasmi()
        self.efacs = self.import_lcafacs()

        # set sampling parameters
        self.n = 10000
        self.seed = 100
        self.xps_prod = 0


    def import_rasmi(self):
        """returns rasmi as a dictionary containing a dataframe for each material."""

        print('importing RASMI dataset...')
        mats = ['concrete','brick','wood','steel','glass','plastics','aluminum','copper']
        ras = {}

        # get excel data
        for m in mats:
            print('  ', m,'...')
            ras[m] = pd.read_excel(self.rasmi_path, sheet_name=m, index_col=[0,1,2])

        # get unique queries
        ras['functions'] = ras['concrete'].index.get_level_values(0).unique()
        ras['structures'] = ras['concrete'].index.get_level_values(1).unique()
        ras['geos'] = ras['concrete'].index.get_level_values(2).unique()
        ras['mats'] = mats

        return ras
    
    def import_lcafacs(self):
        """returns lca/emission factors as a dictionary containing a dataframe for each material."""

        print('importing lca factor dataset...')
        mats = ['concrete','brick','wood','steel','glass','plastics','aluminum','copper']
        facs = {}
        for m in mats:
            print('  ', m,'...')
            facs[m] = pd.read_excel(self.factors_path, sheet_name=m, usecols='A:I')

        return facs


    def query_rasmi(self, function_, structure, geo):
        """
        return query for all materials
        inputs = function_, structure, and geography as strings corresponding to RASMI dataset, respectively.
        output = dictionary of data for each material.
        """
        rasmi_q = self.rasmi.copy()
        mats = ['concrete','brick','wood','steel','glass','plastics','aluminum','copper']

        for m in mats:
            rasmi_q[m] = rasmi_q[m].loc[function_, structure, geo]

        return rasmi_q

    def query_lcafacs(self, geo):
        """
        Queries lca/emission factors for each material to get specific country code from RASMI requested.
        c_code = desired country code
        output = dictionary of lca/emission factors for each material.
        """
        efacs_c = self.efacs.copy()
        mats = ['concrete','brick','wood','steel','glass','plastics','aluminum','copper']
        for m in mats:
            # get indexes of country
            c_quer = efacs_c[m]['geos'].str.replace(' ','').str.split(',')
            c_quer = c_quer.apply(lambda x: x).apply(lambda x: True if geo in x else False)

            # limit to countries
            efacs_c[m] = efacs_c[m].loc[c_quer[c_quer == True].index]

        return efacs_c
    

    def sample_rasmi(self, rasmi_q):
        """
        samples values for each material
        rasmi_q = queried RASMI dataset
        n = number of samples
        seed = common random numbers seed
        """
        mats = ['concrete','brick','wood','steel','glass','plastics','aluminum','copper']
        ras_s = []
        for m in mats:
            # append samples with replacement
            ras_s.append(rasmi_q[m][m].sample(n=self.n, random_state=self.seed, replace=True).values)

        # return combined in array
        return np.array(ras_s).T

    def sample_efacs(self, efacs_q):
        """
        samples emission factor values
        efacs_q = queried emission factor dataset
        xps_prod = 0 uses CO2 blowing, 1 uses HFC blowing (for plastics with Ecoinvent dataset)
        n = number of samples
        seed = common random numbers seed
        """
        mats = ['concrete','brick','wood','steel','glass','plastics','aluminum','copper']
        efacs_s = []
        for m in mats:
            # if plastics, choose xps production pathway
            if m == 'plastics':
                if self.xps_prod == 0:
                    efacs_q[m] = efacs_q[m][efacs_q[m]['note'] != 'XPS-HFC']
                if self.xps_prod == 1:
                    efacs_q[m] = efacs_q[m][efacs_q[m]['note'] != 'XPS-CO2']

            # sample
            efacs_s.append(efacs_q[m]['kgco2e/kg'].sample(n=self.n, random_state=self.seed, replace=True).values)

        return np.array(efacs_s).T
    
    
    def sample_and_calc(self, function_, structure, geo):
        """
        Given function, structure, geo, sample and calculate impact (emissions) per m2.
        """
        # get samples
        rasmi_s = self.sample_rasmi(self.query_rasmi(function_, structure, geo))
        efacs_s = self.sample_efacs(self.query_lcafacs(geo))
        
        # return diagonal einstein summation
        return np.einsum('ij,ji->i', rasmi_s, efacs_s.T)