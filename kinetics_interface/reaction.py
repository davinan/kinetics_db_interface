from typing import List, Dict
import tellurium as te

class EnzymeReaction:

    def __init__(self, reaction_df):

        self.df = reaction_df
        Km_rows = self.df[self.df['parameter.type'] == 'Km']
        Ki_rows = self.df[self.df['parameter.type'] == 'Ki']
        Vmax_rows = self.df[self.df['parameter.type'] == 'Vmax']
        c_rows = self.df[self.df['parameter.type'] == 'concentration']

        if len(Km_rows) == 0 or len(Vmax_rows) == 0 or len(c_rows) == 0 or len(Ki_rows)==0:
            self._is_valid = False

        self.conc 

        self.S_start = min(
            [x['parameter.startValue'] for i, x in self.conc.dropna().iterrows() if x['parameter.startValue'] != 0]
            + [x['parameter.endValue'] for i, x in self.conc.dropna().iterrows() if x['parameter.endValue'] != 0]
        )
        self.E_start = min(
            [x['parameter.startValue'] for i, x in self.conc.dropna().iterrows() if x['parameter.startValue'] != 0]
            + [x['parameter.endValue'] for i, x in self.conc.dropna().iterrows() if x['parameter.endValue'] != 0]
        )
        self.Km = Km_rows.iloc[0]['parameter.startValue']
        self.Vmax = Vmax_rows.iloc[0]['parameter.startValue']
        self.Ki = Ki_rows.iloc[0]['parameter.startValue']

        self.name = f"SabioRKID{self.df.iloc[0].EntryID}"

    def change_value(self, Km=None, Vmax=None, S_start=None, E_start=None, Ki=None):
        if Km is not None: self.Km = Km
        if Ki is not None: self.Ki = Ki
        if Vmax is not None: self.Vmax = Vmax
        if E_start is not None: self.E_start = E_start
        if S_start is not None: self.S_start = S_start
        return self.get_reaction_details()

    def get_reaction_details(self):
        return self.df

    def is_valid(self):
        return self._is_valid

    def get_model(self):
        model = ""
        model += f"\nmodel {self.name}\n"
        model += self.get_concentrations(with_range=False, prefix  = "\t")
        model += f"\tspecies {self.get_all_species()};\n"
        model += self.get_reaction_string()
        model += f"\n\tVmax={self.Vmax['using']}"
        model += f"\n\tKm={self.Km['using']}"
        model += f"\nend"
        return model

    def get_model(self):
        model = f"model {self.name}\n"
        model += f"\nspecies E, S, ES, P;"
        model += f"\nVmax = {self.Vmax};"
        model += f"\nKm = {self.Km};"
        model += f"\nE = {self.E_start};"
        model += f"\nS = {self.S_start};"

        model += f"\nJ0: E + S -> ES; k1*E*S"
        model += f"\nJ1: ES -> E + P; Vmax * S / (Km + S)"
        model += f"\nk1 = {1/self.Ki};"
        model += f"\nend"
        return model

    def plot_tellurium(self, range=(0, 100), num_timesteps=1000):
        te.setDefaultPlottingEngine('matplotlib')
        # load models
        r = te.loada(self.get_model())
        r.simulate(range[0], range[1], num_timesteps)
        # plot the simulation
        # plt.title(R.get_reaction_string())
        # r.plot()
        r.plot(xtitle='Time', ytitle='Concentration', title=self.get_reaction_string()[1:])
