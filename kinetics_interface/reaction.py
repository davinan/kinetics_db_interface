from typing import List, Dict
import tellurium as te

class EnzymeReaction:

    def __init__(self, reaction_df):

        self.df = reaction_df
        Km_rows = self.df[self.df['parameter.type'] == 'Km']
        Vmax_rows = self.df[self.df['parameter.type'] == 'Vmax']
        c_rows = self.df[self.df['parameter.type'] == 'concentration']

        if len(Km_rows) == 0 or len(Vmax_rows) == 0 or len(c_rows) == 0:
            self._is_valid = False
            return
        self._is_valid = True

        self.S_start = min(
            [x['parameter.startValue'] for i, x in c_rows.iterrows() if x['parameter.startValue'] != 0]
            + [x['parameter.endValue'] for i, x in c_rows.iterrows() if x['parameter.endValue'] != 0]
        )
        self.E_start = min(
            [x['parameter.startValue'] for i, x in c_rows.iterrows() if x['parameter.startValue'] != 0]
            + [x['parameter.endValue'] for i, x in c_rows.iterrows() if x['parameter.endValue'] != 0]
        )
        self.Km = Km_rows.iloc[0]['parameter.startValue']
        self.Vmax = Vmax_rows.iloc[0]['parameter.startValue']
        self.k1 = 10.0

        self.name = f"SabioRKID{self.df.iloc[0].EntryID}"

    def change_value(self, Km=None, Vmax=None, S_start=None, E_start=None, k1=None):
        if Km is not None: self.Km = Km
        if k1 is not None: self.k1 = k1
        if Vmax is not None: self.Vmax = Vmax
        if E_start is not None: self.E_start = E_start
        if S_start is not None: self.S_start = S_start
        return self.get_reaction_details()

    def get_reaction_details(self):
        return self.df

    def is_valid(self):
        return self._is_valid

    def get_model(self):
        model = f"model {self.name}\n"
        model += f"\n\tspecies E, S, ES, P;\n"
        model += f"\n\tVmax = {self.Vmax};"
        model += f"\n\tKm = {self.Km};"
        model += f"\n\tE = {self.E_start};"
        model += f"\n\tS = {self.S_start};\n"
        model += f"\n\tJ0: E + S -> ES; k1*E*S"
        model += f"\n\tJ1: ES -> E + S; (1/k1)*ES"
        model += f"\n\tJ2: ES -> E + P; Vmax * S / (Km + S)\n"
        model += f"\n\tk1 = {self.k1};"
        model += f"\nend"
        return model

    def plot_tellurium(self, range=(0, 100), num_timesteps=1000):
        te.setDefaultPlottingEngine('matplotlib')
        # load models
        r = te.loada(self.get_model())
        data = r.simulate(range[0], range[1], num_timesteps)
        # plot the simulation
        # plt.title(R.get_reaction_string())
        # r.plot()
        r.plot(xtitle='Time', ytitle='Concentration', title=self.name)
        return data