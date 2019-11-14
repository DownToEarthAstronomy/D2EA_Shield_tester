from __future__ import annotations
import json
import copy
import math
import os
import time
import itertools
import threading
import multiprocessing
import queue
from typing import List, Tuple, Any, Dict, Optional


class ShieldBoosterVariant(object):
    # TODO slot names for loadout event
    def __init__(self):
        self._engineering = ""
        self._experimental = ""
        self._shield_strength_bonus = ""
        self._exp_res_bonus = ""
        self._kin_res_bonus = ""
        self._therm_res_bonus = ""
        self._can_skip = False
        self._loadout_template = ""

    @property
    def engineering(self):
        return self._engineering

    @property
    def experimental(self):
        return self._experimental

    @property
    def shield_strength_bonus(self):
        return self._shield_strength_bonus

    @property
    def exp_res_bonus(self):
        return self._exp_res_bonus

    @property
    def kin_res_bonus(self):
        return self._kin_res_bonus

    @property
    def therm_res_bonus(self):
        return self._therm_res_bonus

    @property
    def can_skip(self):
        return self._can_skip

    @property
    def loadout_template(self):
        return self._loadout_template

    @staticmethod
    def create_from_json(json_booster: json) -> ShieldBoosterVariant:
        """
        Create a ShieldBoosterVariant object from json node
        :param json_booster: json node (or dictionary) in data file
        :return: newly created ShieldBoosterVariant object
        """
        booster = ShieldBoosterVariant()
        booster._engineering = json_booster["engineering"]
        booster._experimental = json_booster["experimental"]
        booster._shield_strength_bonus = json_booster["shield_strength_bonus"]
        booster._exp_res_bonus = json_booster["exp_res_bonus"]
        booster._kin_res_bonus = json_booster["kin_res_bonus"]
        booster._therm_res_bonus = json_booster["therm_res_bonus"]
        booster._can_skip = json_booster["can_skip"]
        booster._loadout_template = json_booster["loadout_template"]
        return booster

    @staticmethod
    def calculate_booster_bonuses(shield_boosters: List[ShieldBoosterVariant], booster_loadout: List[int]) -> Tuple[float, float, float, float]:
        """
        Calculate the combined bonus of shield boosters
        :param shield_boosters: list of ShieldBoosterVariant
        :param booster_loadout: booster loadout as a list of indexes of the booster in shield_boosters
        :return: tuple: exp_modifier, kin_modifier, therm_modifier, hitpoint_bonus
        """
        exp_modifier = 1.0
        kin_modifier = 1.0
        therm_modifier = 1.0
        hitpoint_bonus = 1.0

        for booster_index in booster_loadout:
            booster = shield_boosters[booster_index]
            exp_modifier *= booster._exp_res_bonus
            kin_modifier *= booster._kin_res_bonus
            therm_modifier *= booster._therm_res_bonus
            hitpoint_bonus += booster._shield_strength_bonus

        # Compensate for diminishing returns
        if exp_modifier < 0.7:
            exp_modifier = 0.7 - (0.7 - exp_modifier) / 2
        if kin_modifier < 0.7:
            kin_modifier = 0.7 - (0.7 - kin_modifier) / 2
        if therm_modifier < 0.7:
            therm_modifier = 0.7 - (0.7 - therm_modifier) / 2

        return exp_modifier, kin_modifier, therm_modifier, hitpoint_bonus


class ShieldGenerator(object):
    CALC_NORMAL = 1
    CALC_RES = 2
    CALC_MASS = 3

    TYPE_NORMAL = "normal"
    TYPE_BIWEAVE = "bi-weave"
    TYPE_PRISMATIC = "prismatic"

    def __init__(self):
        self._symbol = ""
        self._integrity = 0
        self._power = 0
        self._explres = 0
        self._kinres = 0
        self._thermres = 0
        self._name = ""
        self._class = 0
        self._regen = 0
        self._brokenregen = 0
        self._distdraw = 0
        self._maxmass = 0
        self._maxmul = 0
        self._minmass = 0
        self._minmul = 0
        self._optmass = 0
        self._optmul = 0
        self._engineered_name = "not engineered"
        self._engineered_symbol = ""
        self._experimental_name = "no experimental effect"
        self._experimental_symbol = ""

    @property
    def maxmass(self) -> float:
        return self._maxmass

    @property
    def maxmul(self) -> float:
        return self._maxmul

    @property
    def minmass(self) -> float:
        return self._minmass

    @property
    def minmul(self) -> float:
        return self._minmul

    @property
    def optmass(self) -> float:
        return self._optmass

    @property
    def optmul(self) -> float:
        return self._optmul

    @property
    def module_class(self) -> int:
        return self._class

    @property
    def explres(self) -> float:
        return self._explres

    @property
    def kinres(self) -> float:
        return self._kinres

    @property
    def thermres(self) -> float:
        return self._thermres

    @property
    def name(self) -> str:
        return self._name

    @property
    def regen(self) -> float:
        return self._regen

    @property
    def engineered_name(self) -> str:
        return self._engineered_name

    @property
    def experimental_name(self) -> str:
        return self._experimental_name

    @staticmethod
    def create_from_json(json_generator: json) -> ShieldGenerator:
        """
        Create a ShieldGenerator object from json node
        :param json_generator: json node (or dictionary) in data file
        :return: newly created ShieldGenerator object
        """
        generator = ShieldGenerator()
        generator._symbol = json_generator["symbol"]
        generator._integrity = json_generator["integrity"]
        generator._power = json_generator["power"]
        generator._explres = json_generator["explres"]
        generator._kinres = json_generator["kinres"]
        generator._thermres = json_generator["thermres"]
        generator._name = json_generator["name"]
        generator._class = json_generator["class"]
        generator._regen = json_generator["regen"]
        generator._brokenregen = json_generator["brokenregen"]
        generator._distdraw = json_generator["distdraw"]
        generator._maxmass = json_generator["maxmass"]
        generator._maxmul = json_generator["maxmul"]
        generator._minmass = json_generator["minmass"]
        generator._minmul = json_generator["minmul"]
        generator._optmass = json_generator["optmass"]
        generator._optmul = json_generator["optmul"]
        return generator

    def __calculate_and_set_engineering(self, attr: str, key: str, features: Dict[str, Any], calc_type: int, is_percentage: bool = False):
        """
        Apply engineering changes
        :param attr: class attribute to change.
        :param key: the key in the json feature list
        :param features: dictionary of features
        :param calc_type: how to calculate the new value. Refer to class "constants"
        :param is_percentage: set to true if the value in the features list is a percentage value (0-100) instead of a fraction (0-1)
        :return:
        """
        if key in features:
            r = getattr(self, attr)
            v = features[key]
            if is_percentage:
                v /= 100.0

            if calc_type == self.CALC_RES:
                r = 1.0 - (1.0 - r) * (1.0 - v)
            elif calc_type == self.CALC_MASS:
                r = (r * 100.0) * (1.0 + v) / 100.0
            elif calc_type == self.CALC_NORMAL:
                r = r * (1.0 + v)

            setattr(self, attr, round(r, 4))

    def _apply_engineering(self, features: json, is_percentage: bool = False):
        self.__calculate_and_set_engineering("_integrity", "integrity", features, self.CALC_NORMAL)
        self.__calculate_and_set_engineering("_brokenregen", "brokenregen", features, self.CALC_NORMAL)
        self.__calculate_and_set_engineering("_regen", "regen", features, self.CALC_NORMAL)
        self.__calculate_and_set_engineering("_distdraw", "distdraw", features, self.CALC_NORMAL)
        self.__calculate_and_set_engineering("_power", "power", features, self.CALC_NORMAL)

        self.__calculate_and_set_engineering("_optmul", "optmul", features, self.CALC_MASS)
        self.__calculate_and_set_engineering("_minmul", "optmul", features, self.CALC_MASS)
        self.__calculate_and_set_engineering("_maxmul", "optmul", features, self.CALC_MASS)

        self.__calculate_and_set_engineering("_kinres", "kinres", features, self.CALC_RES, is_percentage)
        self.__calculate_and_set_engineering("_thermres", "thermres", features, self.CALC_RES, is_percentage)
        self.__calculate_and_set_engineering("_explres", "explres", features, self.CALC_RES, is_percentage)

    @staticmethod
    def create_engineered_shield_generators(prototype: ShieldGenerator, blueprints: json, experimentals: json) -> List[ShieldGenerator]:
        """
        Use a non engineered shield generator as prototype to generate a list of possible engineered shield generators.
        :param prototype: non engineered shield generator
        :param blueprints: blueprints from data.json containing only recipes for shield generators
        :param experimentals: experimental effects from data.json containing only recipes for shield generators
        :return: list of all combinations of shield generators from given blueprints and experimental effects
        """
        variations = list()

        for blueprint in blueprints:
            engineered_sg = copy.deepcopy(prototype)
            engineered_sg._engineered_symbol = blueprint["symbol"]
            engineered_sg._engineered_name = blueprint["name"]
            engineered_sg._apply_engineering(blueprint["features"])
            for experimental in experimentals:
                exp_eng_sg = copy.deepcopy(engineered_sg)
                exp_eng_sg._experimental_symbol = experimental["symbol"]
                exp_eng_sg._experimental_name = experimental["name"]
                exp_eng_sg._apply_engineering(experimental["features"], is_percentage=True)
                variations.append(exp_eng_sg)

        return variations


class StarShip(object):
    def __init__(self):
        self._name = ""
        self._symbol = ""
        self._loadout_template = ""
        self._base_shield_strength = 0
        self._hull_mass = 0
        self._utility_slots = 0
        self._highest_internal = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def loadout_template(self):
        return self._loadout_template

    @property
    def base_shield_strength(self) -> int:
        return self._base_shield_strength

    @property
    def hull_mass(self) -> int:
        return self._hull_mass

    @property
    def utility_slots(self) -> int:
        return self._utility_slots

    @property
    def highest_internal(self) -> int:
        return self._highest_internal

    @staticmethod
    def create_from_json(json_ship: json) -> StarShip:
        """
        Create a Ship object from json node
        :param json_ship: json node (or dictionary) in data file
        :return: newly created Ship object
        """
        ship = StarShip()
        ship._name = json_ship["ship"]
        ship._symbol = json_ship["symbol"]
        ship._loadout_template = json_ship["loadout_template"]
        ship._base_shield_strength = json_ship["baseShieldStrength"]
        ship._hull_mass = json_ship["hullMass"]
        ship._utility_slots = json_ship["utility_slots"]
        ship._highest_internal = json_ship["highest_internal"]
        return ship


class LoadOut(object):
    def __init__(self, shield_generator: ShieldGenerator, ship: StarShip):
        self.__shield_generator = shield_generator
        self.__ship = ship
        self.boosters = list()
        self.__shield_strength = self.__calculate_shield_strength()

    @property
    def shield_strength(self):
        return self.__shield_strength

    def __calculate_shield_strength(self):
        # formula taken from https://github.com/EDCD/coriolis/blob/master/src/app/shipyard/Calculations.js
        if self.__shield_generator and self.__ship:
            min_mass = self.__shield_generator.minmass
            opt_mass = self.__shield_generator.optmass
            max_mass = self.__shield_generator.maxmass
            min_mul = self.__shield_generator.minmul
            opt_mul = self.__shield_generator.optmul
            max_mul = self.__shield_generator.maxmul
            hull_mass = self.__ship.hull_mass

            xnorm = min(1.0, (max_mass - hull_mass) / (max_mass - min_mass))
            exponent = math.log((opt_mul - min_mul) / (max_mul - min_mul)) / math.log(min(1.0, (max_mass - opt_mass) / (max_mass - min_mass)))
            ynorm = math.pow(xnorm, exponent)
            mul = min_mul + ynorm * (max_mul - min_mul)
            return round(self.__ship.base_shield_strength * mul, 4)
        else:
            return 0

    def generate_loadout_event(self):
        # TODO
        pass


class TestCase(object):
    def __init__(self):
        self.damage_effectiveness = 0
        self.explosive_dps = 0
        self.kinetic_dps = 0
        self.thermal_dps = 0
        self.absolute_dps = 0
        self.scb_hitpoints = 0
        self.guardian_hitpoints = 0


class ShieldTester(object):
    MP_CHUNK_SIZE = 10000

    def __init__(self):
        self.__ships = dict()
        self.__booster_variants = list()
        # key of outer dictionary is the type, key for inner dictionary is the class
        # and the value is a list of all engineered shield generator combinations of that class and type
        self.__shield_generators = dict()  # type: Dict[str, Dict[int, List[ShieldGenerator]]]

        self.__selected_ship = None
        self.__use_prismatics = True
        self.__use_short_list = True
        self.__loadouts_to_test = list()
        self.__booster_variants_to_test = list()
        self.__number_of_boosters_to_test = 0

        self.__cpu_cores = os.cpu_count()

    @property
    def use_short_list(self) -> bool:
        return self.__use_short_list

    @use_short_list.setter
    def use_short_list(self, value: bool):
        if self.__use_short_list != value:
            self.__use_short_list = value
            self.__booster_variants_to_test = self.__find_boosters_to_test()

    @property
    def cpu_cores(self) -> int:
        return self.__cpu_cores

    @cpu_cores.setter
    def cpu_cores(self, value: int):
        self.__cpu_cores = max(1, min(os.cpu_count(), abs(value)))

    @property
    def ship_names(self):
        return [ship for ship in self.__ships.keys()]

    @property
    def selected_ship(self) -> Optional[StarShip]:
        if self.__selected_ship:
            return copy.deepcopy(self.__selected_ship)
        else:
            return None

    @property
    def use_prismatics(self) -> bool:
        return self.__use_prismatics

    @use_prismatics.setter
    def use_prismatics(self, value: bool):
        if self.__use_prismatics != value:
            self.__use_prismatics = value
            if self.__selected_ship:
                self.__loadouts_to_test = self.__create_loadouts()

    @property
    def number_of_boosters_to_test(self):
        return self.__number_of_boosters_to_test

    @number_of_boosters_to_test.setter
    def number_of_boosters_to_test(self, value: int):
        if self.__selected_ship:
            min(self.__selected_ship.utility_slots, abs(value))
        else:
            self.__number_of_boosters_to_test = 0

    @property
    def number_of_tests(self):
        result = math.factorial(len(self.__booster_variants_to_test) + self.__number_of_boosters_to_test - 1)
        result = result / math.factorial(len(self.__booster_variants_to_test) - 1) / math.factorial(self.__number_of_boosters_to_test)
        return int(result * len(self.__loadouts_to_test))

    def __find_boosters_to_test(self) -> List[ShieldBoosterVariant]:
        return list(filter(lambda x: not (x.can_skip and self.__use_short_list), self.__booster_variants))

    def __create_loadouts(self) -> List[LoadOut]:
        """
        Create a list containing all relevant shield generators but no boosters
        """
        loadouts_to_test = list()

        if self.__selected_ship:
            module_class = self.__selected_ship.highest_internal

            shield_generators = list()
            shield_generators += self.__shield_generators.get(ShieldGenerator.TYPE_BIWEAVE).get(module_class)
            shield_generators += self.__shield_generators.get(ShieldGenerator.TYPE_NORMAL).get(module_class)
            if self.__use_prismatics:
                shield_generators += self.__shield_generators.get(ShieldGenerator.TYPE_PRISMATIC).get(module_class)

            for sg in shield_generators:
                loadouts_to_test.append(LoadOut(sg, self.__selected_ship))
        return loadouts_to_test

    def select_ship(self, name: str):
        if name in self.__ships:
            self.__selected_ship = self.__ships.get(name)
            self.__loadouts_to_test = self.__create_loadouts()
            self.__number_of_boosters_to_test = self.__selected_ship.utility_slots

    def load_data(self, file: str):
        """
        Load data.
        :param file: Path to json file
        """
        with open(file) as json_file:
            j_data = json.load(json_file)

            # load ships
            for j_ship in j_data["ships"]:
                ship = StarShip.create_from_json(j_ship)
                self.__ships.setdefault(ship.name, ship)

            # load shield booster variants
            for booster_variant in j_data["shield_booster_variants"]:
                self.__booster_variants.append(ShieldBoosterVariant.create_from_json(booster_variant))
            self.__booster_variants_to_test = self.__find_boosters_to_test()

            # load shield generators
            sg_node = j_data["shield_generators"]
            for sg_type, sg_list in sg_node["modules"].items():
                sg_type_dict = self.__shield_generators.setdefault(sg_type, dict())
                for j_generator in sg_list:
                    generator = ShieldGenerator.create_from_json(j_generator)
                    generator_variants = ShieldGenerator.create_engineered_shield_generators(generator,
                                                                                             sg_node["engineering"]["blueprints"],
                                                                                             sg_node["engineering"]["experimental_effects"])
                    sg_type_dict.setdefault(generator.module_class, generator_variants)
