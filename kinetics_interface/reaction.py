from typing import List, Dict
import tellurium as te

class EnzymeReaction:
    """
    A class representing an enzyme reaction, defined by kinetic parameters and initial conditions.

    Attributes:
        df (DataFrame): A pandas DataFrame containing the reaction parameters.
        S_start (float): The starting concentration of the substrate.
        E_start (float): The starting concentration of the enzyme.
        Km (float): The Michaelis constant of the reaction.
        Vmax (float): The maximum velocity of the reaction.
        k1 (float): The rate constant for the formation of the enzyme-substrate complex.
        name (str): A unique identifier for the reaction.
        _is_valid (bool): Indicates whether the reaction parameters are valid and complete.

    Methods:
        change_value: Update reaction parameters.
        get_reaction_details: Return the reaction parameters DataFrame.
        is_valid: Check if the reaction parameters are valid and complete.
        get_model: Generate a textual representation of the reaction model.
        plot_tellurium: Simulate and plot the reaction using Tellurium.
    """

    def __init__(self, reaction_df):
        """
        Initialize the EnzymeReaction object with a DataFrame containing reaction parameters.

        Args:
            reaction_df (DataFrame): A DataFrame containing parameters like Km, Vmax,
                                     and concentrations with columns 'parameter.type', 
                                     'parameter.startValue', and 'parameter.endValue'.

        The initialization process extracts necessary parameters (Km, Vmax, starting concentrations)
        from the DataFrame and checks for the presence of essential data to determine if the reaction
        is valid.
        """
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
        """
        Update reaction parameters like Km, Vmax, starting concentrations, and rate constant.

        Args:
            Km (float, optional): New Michaelis constant.
            Vmax (float, optional): New maximum velocity.
            S_start (float, optional): New starting substrate concentration.
            E_start (float, optional): New starting enzyme concentration.
            k1 (float, optional): New rate constant for the formation of the enzyme-substrate complex.

        Returns:
            DataFrame: The updated DataFrame containing the reaction parameters.
        """
        if Km is not None: self.Km = Km
        if k1 is not None: self.k1 = k1
        if Vmax is not None: self.Vmax = Vmax
        if E_start is not None: self.E_start = E_start
        if S_start is not None: self.S_start = S_start
        return self.get_reaction_details()

    def get_reaction_details(self):
        """
        Return the DataFrame containing reaction parameters.

        Returns:
            DataFrame: The DataFrame representing the reaction parameters.
        """
        return self.df

    def is_valid(self):
        """
        Check if the reaction parameters are valid and complete

        Returns:
            bool: True if the reaction parameters are valid and complete, False otherwise.
        """
        return self._is_valid

    def get_model(self):
        """
        Generate a Antimony representation of the reaction model.

        Returns:
            str: A string representation of the reaction model using kinetic parameters.
        """
        model = f"model {self.name}\n"
        model += f"\n\tspecies E, S, ES, P;\n"
        model += f"\n\tVmax = {self.Vmax};"
        model += f"\n\tKm = {self.Km};"
        model += f"\n\tE = {self.E_start};"
        model += f"\n\tS = {self.S_start};\n"
        model += f"\n\tJ0: E + S -> ES; k1*E*S"
        model += f"\n\tJ1: ES -> E + S; (1/k1)*ES"
        model += f"\n\tJ2: ES -> E + P; Vmax * ES / (Km + S)\n"
        model += f"\n\tk1 = {self.k1};"
        model += f"\nend"
        return model

    def plot_tellurium(self, range=(0, 100), num_timesteps=1000):
        """
        Simulate and plot the reaction using Tellurium.

        Args:
            range (tuple, optional): The time range for the simulation (start, end).
            num_timesteps (int, optional): The number of timesteps in the simulation.

        Returns:
            numpy.ndarray: The simulation data as an array.
        """
        te.setDefaultPlottingEngine('matplotlib')
        r = te.loada(self.get_model())
        data = r.simulate(range[0], range[1], num_timesteps)
        r.plot(xtitle='Time', ytitle='Concentration', title=self.name)
        return data