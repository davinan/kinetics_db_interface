from typing import List, Dict

class Reaction:

    def __init__(self, queried_reaction):
        self.name_map = {}
        for name in queried_reaction['reactants']:
            self.name_map[name] = name.replace(",", "comma").replace("+", "plus").replace("-", "minus")
        for name in queried_reaction['products']:
            self.name_map[name] = name.replace(",", "comma").replace("+", "plus").replace("-", "minus")
        self._get_concentrations(queried_reaction)
        self._get_Vmax(queried_reaction)
        self._get_Km(queried_reaction)

        self.name = f"Reaction{queried_reaction['name']}"
        self.reaction = queried_reaction

    def _get_value_dict(self, param):
        value_dict = {
            'low': param['low'],
            'high': param['high']
        }
        if str(value_dict['low']) == 'nan':
            if str(value_dict['high']) == 'nan':
                value_dict['using'] = 'nan'
            else:
                value_dict['using'] = value_dict['high']
        else:
            if str(value_dict['high']) == 'nan':
                value_dict['using'] = value_dict['low']
            else:
                value_dict['using'] = (value_dict['high'] + value_dict['low']) / 2
        return value_dict

    def _get_concentrations(self, reaction):
        species = set(reaction['reactants'])
        with_concentration = set()
        conc = {}
        for param in reaction['params']:
            if param['type'] == 'concentration':
                value_dict = self._get_value_dict(param)
                if str(value_dict['using']) != 'nan':
                    if param['associated_species'] in self.name_map.keys():
                        with_concentration.add(self.name_map[param['associated_species']])
                        conc[self.name_map[param['associated_species']]] = value_dict

        self.has_concentrations = len(with_concentration) == len(species)
        self.concentrations = conc

    def _get_Vmax(self, reaction):
        has_Vmax = False
        Vmax = None
        conc = {}
        for param in reaction['params']:
            if param['type'] == 'Vmax':
                value_dict = self._get_value_dict(param)
                if str(value_dict['using']) != 'nan':
                    Vmax = value_dict
        self.Vmax = Vmax

    def _get_Km(self, reaction):
        Km = None
        conc = {}
        for param in reaction['params']:
            if param['type'] == 'Km':
                value_dict = self._get_value_dict(param)
                if str(value_dict['using'] )!= 'nan':
                    Km = value_dict
                    Km['species'] = self.name_map[param['associated_species']]
        self.Km = Km

    def is_valid(self):
        return (
            self.has_concentrations
            and self.Km is not None
            and self.Vmax is not None
        )
    def get_concentrations(self, with_range=True, prefix=""):
        s = ""
        for k, v in self.concentrations.items():
            if with_range:
                s += f"{prefix}{k}: [{v['low'], v['high']}], using {v['using']}"
            else:
                s += f"{prefix}{k} = {v['using']};\n"
        return s
    def get_all_species(self):
        return ', '.join([v for k, v in self.name_map.items()])
    def get_reaction_string(self):
        s = f"\tJ1: {' + '.join([self.name_map[i] for i in self.reaction['reactants']])} -> {' + '.join([self.name_map[i] for i in self.reaction['products']])}; "
        s += f"Vmax*{self.Km['species']}/(Km+{self.Km['species']});"
        return s
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
