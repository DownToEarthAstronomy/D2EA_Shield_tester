from __future__ import annotations
import json
import copy
import math
import os
import time
import itertools
import multiprocessing
import queue
import gzip
import base64
import urllib.request
from typing import List, Tuple, Any, Dict, Optional


class ShieldBoosterVariant(object):
    SLOT_TEMPLATE = "tinyhardpoint{}"

    def __init__(self):
        self._engineering = ""
        self._experimental = ""
        self._shield_strength_bonus = ""
        self._exp_res_bonus = ""
        self._kin_res_bonus = ""
        self._therm_res_bonus = ""
        self._can_skip = False
        self._loadout_template = None  # type: Optional[Dict[str, Any]]

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

    def get_loadout_template_slot(self, slot: int) -> Dict[str, Any]:
        """
        Get the loadout dictionary for the provided slot number
        :param slot: int from 1 to 8 (including)
        :return:
        """
        if self._loadout_template:
            loadout = copy.deepcopy(self._loadout_template)
            loadout["Slot"] = self.SLOT_TEMPLATE.format(slot)
            return loadout
        return dict()

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

    # noinspection PyTypeChecker
    @staticmethod
    def calculate_booster_bonuses(shield_boosters: List[ShieldBoosterVariant], booster_loadout: List[int] = None) -> Tuple[float, float, float, float]:
        """
        Calculate the combined bonus of shield boosters. This function has 2 modes: either supply it with a list of all ShieldBoosterVariant and a list of indexes
        for the boosters to use or supply it only with a list of ShieldBoosterVariant.
        :param shield_boosters: list of ShieldBoosterVariant.
        :param booster_loadout: booster loadout as a list of indexes of the booster in shield_boosters
        :return: tuple: exp_modifier, kin_modifier, therm_modifier, hitpoint_bonus
        """
        exp_modifier = 1.0
        kin_modifier = 1.0
        therm_modifier = 1.0
        hitpoint_bonus = 1.0

        if booster_loadout:
            print(booster_loadout)
            boosters = [shield_boosters[x] for x in booster_loadout]
        else:
            boosters = shield_boosters

        for booster in boosters:
            exp_modifier *= (1.0 - booster._exp_res_bonus)
            kin_modifier *= (1.0 - booster._kin_res_bonus)
            therm_modifier *= (1.0 - booster._therm_res_bonus)
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
    SLOT_TEMPLATE = "slot01_size{}"

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
    def module_class(self) -> int:
        return self._class

    @property
    def name(self) -> str:
        return self._name

    @property
    def symbol(self) -> str:
        return self._symbol

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

    def _calculate_and_set_engineering(self, attr: str, key: str, features: Dict[str, Any], calc_type: int, is_percentage: bool = False):
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
        self._calculate_and_set_engineering("_integrity", "integrity", features, self.CALC_NORMAL)
        self._calculate_and_set_engineering("_brokenregen", "brokenregen", features, self.CALC_NORMAL)
        self._calculate_and_set_engineering("_regen", "regen", features, self.CALC_NORMAL)
        self._calculate_and_set_engineering("_distdraw", "distdraw", features, self.CALC_NORMAL)
        self._calculate_and_set_engineering("_power", "power", features, self.CALC_NORMAL)

        self._calculate_and_set_engineering("_optmul", "optmul", features, self.CALC_MASS)
        self._calculate_and_set_engineering("_minmul", "optmul", features, self.CALC_MASS)
        self._calculate_and_set_engineering("_maxmul", "optmul", features, self.CALC_MASS)

        self._calculate_and_set_engineering("_kinres", "kinres", features, self.CALC_RES, is_percentage)
        self._calculate_and_set_engineering("_thermres", "thermres", features, self.CALC_RES, is_percentage)
        self._calculate_and_set_engineering("_explres", "explres", features, self.CALC_RES, is_percentage)

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

    def _create_modifier_templates(self, default_sg: ShieldGenerator):
        modifiers = list()

        def helper(label: str, def_value, value, less_is_good: int = 0):
            return {"Label": label,
                    "Value": value,
                    "OriginalValue": def_value,
                    "LessIsGood": less_is_good}

        if default_sg._integrity != self._integrity:
            modifiers.append(helper("Integrity", default_sg._integrity, self._integrity))
        if default_sg._power != self._power:
            modifiers.append(helper("PowerDraw", default_sg._power, self._power, 1))
        if default_sg._optmul != self._optmul:
            modifiers.append(helper("ShieldGenStrength", default_sg._optmul * 100, self._optmul * 100))
        if default_sg._distdraw != self._distdraw:
            modifiers.append(helper("EnergyPerRegen", default_sg._distdraw, self._distdraw, 1))
        if default_sg._brokenregen != self._brokenregen:
            modifiers.append(helper("BrokenRegenRate", default_sg._brokenregen, self._brokenregen))
        if default_sg._regen != self._regen:
            modifiers.append(helper("RegenRate", default_sg._regen, self._regen))
        if default_sg._kinres != self._kinres:
            modifiers.append(helper("KineticResistance", default_sg._kinres * 100, self._kinres * 100))
        if default_sg._thermres != self._thermres:
            modifiers.append(helper("ThermicResistance", default_sg._thermres * 100, self._thermres * 100))
        if default_sg._explres != self._explres:
            modifiers.append(helper("ExplosiveResistance", default_sg._explres * 100, self._explres * 100))
        return modifiers

    def create_loadout(self, default_sg: ShieldGenerator, slot_class: int) -> Dict[str, Any]:
        """
        Create loadout dictionary for use in Coriolis
        :param default_sg: non engineered ShieldGenerator for comparing values
        :param slot_class: class of shield generator
        :return: dictionary containing module information about the shield generator
        """
        modifiers = self._create_modifier_templates(default_sg)
        engineering = {"BlueprintName": self._engineered_symbol,
                       "Level": 5,
                       "Quality": 1,
                       "Modifiers": modifiers,
                       "ExperimentalEffect": self._experimental_symbol}
        loadout = {"Item": self._symbol,
                   "Slot": self.SLOT_TEMPLATE.format(slot_class),
                   "On": True,
                   "Priority": 0,
                   "Engineering": engineering}
        return loadout


class StarShip(object):
    def __init__(self):
        self._name = ""
        self._symbol = ""
        self._loadout_template = dict()
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
    def loadout_template(self) -> Dict[str, Any]:
        return copy.deepcopy(self._loadout_template)

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
        self._shield_generator = shield_generator
        self._ship = ship
        self.boosters = None  # type: List[ShieldBoosterVariant]
        self._shield_strength = self.__calculate_shield_strength()

    @property
    def ship_name(self):
        if self._ship:
            return self._ship.name
        else:
            return "ship not set"

    @property
    def shield_strength(self) -> float:
        return self._shield_strength

    @property
    def shield_generator(self) -> ShieldGenerator:
        return self._shield_generator

    # noinspection PyProtectedMember
    def __calculate_shield_strength(self):
        # formula taken from https://github.com/EDCD/coriolis/blob/master/src/app/shipyard/Calculations.js
        if self._shield_generator and self._ship:
            min_mass = self._shield_generator._minmass
            opt_mass = self._shield_generator._optmass
            max_mass = self._shield_generator._maxmass
            min_mul = self._shield_generator._minmul
            opt_mul = self._shield_generator._optmul
            max_mul = self._shield_generator._maxmul
            hull_mass = self._ship.hull_mass

            xnorm = min(1.0, (max_mass - hull_mass) / (max_mass - min_mass))
            exponent = math.log((opt_mul - min_mul) / (max_mul - min_mul)) / math.log(min(1.0, (max_mass - opt_mass) / (max_mass - min_mass)))
            ynorm = math.pow(xnorm, exponent)
            mul = min_mul + ynorm * (max_mul - min_mul)
            return round(self._ship.base_shield_strength * mul, 4)
        else:
            return 0

    def get_total_values(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Calculate total shield values for the loadout (boosters + shield). Returns None if boosters are not set
        :return: exp_res, kin_res, therm_res, hp
        """
        if self.boosters and len(self.boosters) > 0:
            return self.calculate_total_values(*ShieldBoosterVariant.calculate_booster_bonuses(self.boosters))
        return None

    # noinspection PyProtectedMember
    def calculate_total_values(self, exp_modifier, kin_modifier, therm_modifier, hitpoint_bonus) -> Tuple[float, float, float, float]:
        """
        Provide booster bonuses to calculate total shield values for the loadout
        :param exp_modifier: booster explosive modifier
        :param kin_modifier: booster kinetic modifier
        :param therm_modifier: booster thermal modifier
        :param hitpoint_bonus:  booster hitpoint modifier
        :return: exp_res, kin_res, therm_res, hp
        """
        exp_res = (1 - self._shield_generator._explres) * exp_modifier
        kin_res = (1 - self._shield_generator._kinres) * kin_modifier
        therm_res = (1 - self._shield_generator._thermres) * therm_modifier
        hp = self._shield_strength * hitpoint_bonus
        return exp_res, kin_res, therm_res, hp

    def generate_loadout_event(self, default_sg: ShieldGenerator) -> Dict[str, Any]:
        """
        Generate loadout "event" to import into Coriolis
        :param default_sg: default ShieldGenerator to compare changes
        :return: loadout "event" as dictionary
        """
        if not self._ship:
            return dict()

        loadout_json = self._ship.loadout_template
        modules = loadout_json["Modules"]
        modules.append(self._shield_generator.create_loadout(default_sg, self._ship.highest_internal))

        for i, booster in enumerate(self.boosters):
            modules.append(booster.get_loadout_template_slot(i + 1))
        return loadout_json


class TestResult:
    def __init__(self, best_loadout: LoadOut = None, best_survival_time: int = 0):
        self.best_loadout = best_loadout
        self.best_survival_time = best_survival_time  # if negative, the ship didn't die

    def get_output_string(self, guardian_hitpoints: int = 0):
        """
        Get output string for console output, text output or a logfile of the test result
        :param guardian_hitpoints: Guardian Shield Reinforcement to add to shield hitpoints
        :return: string
        """
        output = list()
        output.append("------------ TEST RESULTS ------------")
        if self.best_survival_time != 0:
            # sort by survival time and put highest value to start of the list
            if self.best_survival_time > 0:
                output.append("    Survival Time [s]: [{0:.3f}]".format(self.best_survival_time))
            else:
                output.append("    Survival Time [s]: [Didn't die]")
            shield_generator = self.best_loadout.shield_generator
            output.append("     Shield Generator: [{type}] - [{eng}] - [{exp}]".format(type=shield_generator.name,
                                                                                       eng=shield_generator.engineered_name,
                                                                                       exp=shield_generator.experimental_name))
            for i, shield_booster_variant in enumerate(self.best_loadout.boosters):
                if i == 0:
                    output.append("     Shield Booster {i}: [{eng}] - [{exp}]".format(i=i + 1,
                                                                                      eng=shield_booster_variant.engineering,
                                                                                      exp=shield_booster_variant.experimental))
                else:
                    output.append("                    {i}: [{eng}] - [{exp}]".format(i=i + 1,
                                                                                      eng=shield_booster_variant.engineering,
                                                                                      exp=shield_booster_variant.experimental))

            output.append("")
            exp_res, kin_res, therm_res, hp = self.best_loadout.get_total_values()
            output.append("Shield Hitpoints [MJ]: [{0:.3f}]".format(hp + guardian_hitpoints))
            regen = self.best_loadout.shield_generator.regen
            regen_time = (hp + guardian_hitpoints) / (2 * self.best_loadout.shield_generator.regen)
            output.append("  Shield Regen [MJ/s]: [{regen}] ({time:.2f}s from 50%)".format(regen=regen, time=regen_time))
            output.append(" Explosive Resistance: [{0:.3f}]".format((1.0 - exp_res) * 100))
            output.append("   Kinetic Resistance: [{0:.3f}]".format((1.0 - kin_res) * 100))
            output.append("   Thermal Resistance: [{0:.3f}]".format((1.0 - therm_res) * 100))
        else:
            output.append("No test results. Please change DPS and/or damage effectiveness.")
        return "\n".join(output)


class TestCase(object):
    def __init__(self, ship: StarShip):
        self.ship = ship
        self.damage_effectiveness = 0
        self.explosive_dps = 0
        self.kinetic_dps = 0
        self.thermal_dps = 0
        self.absolute_dps = 0
        self.scb_hitpoints = 0
        self.guardian_hitpoints = 0
        self.shield_booster_variants = None  # type: List[ShieldBoosterVariant]
        self.loadout_list = None  # type: List[LoadOut]
        self.number_of_boosters_to_test = 0
        self.use_prismatics = True

    def get_output_string(self) -> str:
        """
        Get output string for console output, text output or a logfile of the test result
        :return: string
        """
        output = list()
        output.append("------------ TEST SETUP ------------")
        if self.loadout_list:
            output.append("                    Ship Type: [{}]".format(self.loadout_list[0].ship_name))
            output.append("        Shield Generator Size: [{}]".format(self.loadout_list[0].shield_generator.module_class))
        else:
            output.append("                    Ship Type: [NOT SET]")
            output.append("        Shield Generator Size: [SHIP NOT SET]")
        output.append("         Shield Booster Count: [{0}]".format(self.number_of_boosters_to_test))
        output.append("             Shield Cell Bank: [{}]".format(self.scb_hitpoints))
        output.append("Guardian Shield Reinforcement: [{}]".format(self.guardian_hitpoints))
        output.append("  Access to Prismatic Shields: [{}]".format("Yes" if self.use_prismatics else "No"))
        output.append("                Explosive DPS: [{}]".format(self.explosive_dps))
        output.append("                  Kinetic DPS: [{}]".format(self.kinetic_dps))
        output.append("                  Thermal DPS: [{}]".format(self.thermal_dps))
        output.append("                 Absolute DPS: [{}]".format(self.absolute_dps))
        output.append("         Damage Effectiveness: [{:.0f}%]".format(self.damage_effectiveness * 100))
        output.append("")
        return "\n".join(output)

    # noinspection PyProtectedMember
    @staticmethod
    def test_case(test_case: TestCase, booster_variations: List[List[int]]) -> TestResult:
        """
        Run a particular test based on provided TestCase and booster variations.
        :param test_case: TestCase containing test setup
        :param booster_variations: list of lists of indexes of ShieldBoosterVariant
        :return: best result as TestResult
        """
        best_survival_time = 0
        best_loadout = 0
        best_shield_booster_loadout = None

        # reduce calls -> speed up program, this should speed up the program by a couple hundred ms when using 8 boosters and the short list
        damage_effectiveness = test_case.damage_effectiveness
        explosive_dps = test_case.explosive_dps
        kinetic_dps = test_case.kinetic_dps
        thermal_dps = test_case.thermal_dps
        absolute_dps = test_case.absolute_dps
        scb_hitpoints = test_case.scb_hitpoints
        guardian_hitpoints = test_case.guardian_hitpoints

        for booster_variation in booster_variations:
            boosters = [test_case.shield_booster_variants[x] for x in booster_variation]
            # Do this here instead of for each loadout to save some time.
            exp_modifier, kin_modifier, therm_modifier, hitpoint_bonus = ShieldBoosterVariant.calculate_booster_bonuses(boosters)

            for loadout in test_case.loadout_list:
                loadout.boosters = boosters

                # can't use same function in LoadOut because of speed
                exp_res = (1 - loadout._shield_generator._explres) * exp_modifier
                kin_res = (1 - loadout._shield_generator._kinres) * kin_modifier
                therm_res = (1 - loadout._shield_generator._thermres) * therm_modifier
                hp = loadout._shield_strength * hitpoint_bonus

                actual_dps = damage_effectiveness * (
                        explosive_dps * exp_res +
                        kinetic_dps * kin_res +
                        thermal_dps * therm_res +
                        absolute_dps) - loadout._shield_generator._regen * (1.0 - damage_effectiveness)

                survival_time = (hp + scb_hitpoints + guardian_hitpoints) / actual_dps

                if actual_dps > 0 and best_survival_time >= 0:
                    # if another run set best_survival_time to a negative value, then the ship didn't die, therefore the other result is better
                    if survival_time > best_survival_time:
                        best_loadout = loadout
                        best_shield_booster_loadout = boosters
                        best_survival_time = survival_time
                elif actual_dps < 0:
                    if survival_time < best_survival_time:
                        best_loadout = loadout
                        best_shield_booster_loadout = boosters
                        best_survival_time = survival_time

        best_loadout = copy.deepcopy(best_loadout)
        best_loadout.boosters = best_shield_booster_loadout
        return TestResult(best_loadout, best_survival_time)


class ShieldTester(object):
    MP_CHUNK_SIZE = 10000
    LOG_DIRECTORY = os.path.join(os.getcwd(), "Logs")
    CORIOLIS_URL = "https://coriolis.io/import?data={}"

    def __init__(self):
        self.__ships = dict()
        self.__booster_variants = list()
        # key of outer dictionary is the type, key for inner dictionary is the class
        # and the value is a list of all engineered shield generator combinations of that class and type
        self.__shield_generators = dict()  # type: Dict[str, Dict[int, List[ShieldGenerator]]]
        self.__unengineered_shield_generators = dict()

        self.__test_case = None  # type: Optional[TestCase]
        self.__use_short_list = True

        self.__runtime = 0
        self.__cpu_cores = os.cpu_count()

    @property
    def use_short_list(self) -> bool:
        return self.__use_short_list

    @use_short_list.setter
    def use_short_list(self, value: bool):
        if self.__test_case and self.__use_short_list != value:
            self.__use_short_list = value
            self.__test_case.shield_booster_variants = copy.deepcopy(self.__find_boosters_to_test())

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
    def use_prismatics(self) -> bool:
        if self.__test_case:
            return self.__test_case.use_prismatics
        else:
            return True

    @use_prismatics.setter
    def use_prismatics(self, value: bool):
        if self.__test_case and self.__test_case.use_prismatics != value:
            self.__test_case.use_prismatics = value
            self.__test_case.loadout_list = copy.deepcopy(self.__create_loadouts())

    @property
    def number_of_tests(self) -> int:
        """
        Calculate number of tests based on shield booster variants and shield generator variants
        :return: number of tests
        """
        if self.__test_case and self.__test_case.shield_booster_variants:
            result = math.factorial(len(self.__test_case.shield_booster_variants) + self.__test_case.number_of_boosters_to_test - 1)
            result = result / math.factorial(len(self.__test_case.shield_booster_variants) - 1) / math.factorial(self.__test_case.number_of_boosters_to_test)
            return int(result * len(self.__test_case.loadout_list))
        return 0

    @staticmethod
    def write_log(test_case: TestCase, result: TestResult, filename=None, coriolis_url: str = None):
        """
        Write a log file with the test setup from a TestCase and the results from a TestResult.
        :param test_case: TestCase for information about setup
        :param result: TestResult for information about results
        :param filename: optional filename to append new log (omit file ending)
        :param coriolis_url: optional link to Coriolis
        """
        os.makedirs(ShieldTester.LOG_DIRECTORY, exist_ok=True)
        if not filename:
            filename = time.strftime("%Y-%m-%d %H.%M.%S")
        with open(os.path.join(ShieldTester.LOG_DIRECTORY, filename + ".txt"), "a+") as logfile:
            logfile.write("Test run at: {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            logfile.write(test_case.get_output_string())
            logfile.write("\n")
            logfile.write(result.get_output_string(test_case.guardian_hitpoints))
            if coriolis_url:
                logfile.write("\n")
                logfile.write(coriolis_url)
                logfile.write("\n")

            logfile.write("\n\n\n")
            logfile.flush()

    def __find_boosters_to_test(self) -> List[ShieldBoosterVariant]:
        return list(filter(lambda x: not (x.can_skip and self.__use_short_list), self.__booster_variants))

    def __create_loadouts(self) -> List[LoadOut]:
        """
        Create a list containing all relevant shield generators but no boosters
        """
        loadouts_to_test = list()

        if self.__test_case:
            module_class = self.__test_case.ship.highest_internal

            shield_generators = list()
            shield_generators += self.__shield_generators.get(ShieldGenerator.TYPE_BIWEAVE).get(module_class)
            shield_generators += self.__shield_generators.get(ShieldGenerator.TYPE_NORMAL).get(module_class)
            if self.__test_case.use_prismatics:
                shield_generators += self.__shield_generators.get(ShieldGenerator.TYPE_PRISMATIC).get(module_class)

            for sg in shield_generators:
                loadouts_to_test.append(LoadOut(sg, self.__test_case.ship))
        return loadouts_to_test

    def get_default_shield_generator_of_variant(self, sg_variant: ShieldGenerator) -> Optional[ShieldGenerator]:
        """
        Provide a (engineered) shield generator to get a copy of the same type but as non-engineered version.
        :param sg_variant: the (engineered) shield generator
        :return: ShieldGenerator or None
        """
        if sg_variant:
            return copy.deepcopy(self.__unengineered_shield_generators.get(sg_variant.symbol))
        return None

    def compute(self, test_settings: TestCase, callback: function = None, message_queue: queue.Queue = None) -> Optional[TestResult]:
        """
        Compute best loadout. Best to call this in an extra thread. It might take a while to complete.
        :param test_settings: settings of test case
        :param callback: optional callback. Will be called [<number of tests> / MP_CHUNK_SIZE] times if more than 1 core is used.
                         Will be called only once when only 1 core is used
        :param message_queue: message queue containing some output messages
        """
        if not test_settings or not test_settings.shield_booster_variants or not test_settings.loadout_list:
            # nothing to test
            # TODO maybe raise exception
            print("Can't test nothing")
            return

        print(test_settings.get_output_string())

        self.__runtime = time.time()
        output = list()

        # use built in itertools and assume booster ids are starting at 1 and that there are no gaps
        booster_combinations = list(itertools.combinations_with_replacement(range(0, len(test_settings.shield_booster_variants)), test_settings.number_of_boosters_to_test))
        output.append("------------ TEST RUN ------------")
        output.append("        Shield Booster Count: [{0}]".format(test_settings.number_of_boosters_to_test))
        output.append("   Shield Generator Variants: [{0}]".format(len(test_settings.loadout_list)))
        output.append("     Shield Booster Variants: [{0}]".format(len(self.__booster_variants)))
        output.append("Shield loadouts to be tested: [{0:n}]".format(len(booster_combinations) * len(test_settings.loadout_list)))
        output.append("Running calculations. Please wait...")
        output.append("")
        if message_queue:
            message_queue.put("\n".join(output))
        print("\n".join(output))  # in case there is a console
        output = list()

        best_result = TestResult(best_survival_time=0)

        def apply_async_callback(r: TestResult):
            nonlocal best_result
            if best_result.best_survival_time < 0:
                if r.best_survival_time < best_result.best_survival_time:
                    best_result = r
            else:
                if r.best_survival_time < 0:
                    best_result = r
                elif r.best_survival_time > best_result.best_survival_time:
                    best_result = r
            if callback:
                callback()

        if self.__cpu_cores > 1 and (len(booster_combinations) * len(test_settings.loadout_list)) > self.MP_CHUNK_SIZE:
            # 1 core is handling UI and this thread, the rest is working on running the calculations
            with multiprocessing.Pool(processes=self.__cpu_cores - 1) as pool:
                last_i = 0
                for i in range(self.MP_CHUNK_SIZE, len(booster_combinations), self.MP_CHUNK_SIZE):
                    pool.apply_async(TestCase.test_case, args=(test_settings, booster_combinations[last_i:i]), callback=apply_async_callback)
                    last_i = i + 1
                if last_i < len(booster_combinations):
                    pool.apply_async(TestCase.test_case, args=(test_settings, booster_combinations[last_i:]), callback=apply_async_callback)
                pool.close()
                pool.join()
        else:
            result = TestCase.test_case(test_settings, booster_combinations)
            apply_async_callback(result)  # can use the same function here as mp.Pool would

        output.append("Calculations took {:.2f} seconds".format(time.time() - self.__runtime))
        output.append("")
        if message_queue:
            message_queue.put("\n".join(output))
        print("\n".join(output))  # in case there is a console

        print(best_result.get_output_string(test_settings.guardian_hitpoints))

        return best_result

    def get_coriolis_link(self, loadout: LoadOut) -> str:
        """
        Generate a link to coriolis to import the current shield build.
        :param loadout: loadout containing the build (e.g. get from results)
        :return:
        """
        if loadout and loadout.shield_generator:
            loadout_str = loadout.generate_loadout_event(self.get_default_shield_generator_of_variant(loadout.shield_generator))
            loadout_json = json.dumps(loadout_str).encode("utf-8")
            loadout_gzip = gzip.compress(loadout_json)
            loadout_b64 = base64.b64encode(loadout_gzip)
            loadout_url = urllib.request.quote(loadout_b64)
            return ShieldTester.CORIOLIS_URL.format(loadout_url)
        return ""

    def get_test_case(self) -> Optional[TestCase]:
        """
        Get a the test case containing some settings already.
        Don't forget to add additional attributes like incoming DPS.
        :return: TestCase or None if no ship was selected
        """
        if self.__test_case:
            return self.__test_case
        return None

    def select_ship(self, name: str):
        if name in self.__ships:
            self.__test_case = TestCase(copy.deepcopy(self.__ships.get(name)))
            self.__test_case.loadout_list = copy.deepcopy(self.__create_loadouts())
            self.__test_case.number_of_boosters_to_test = self.__test_case.ship.utility_slots
            self.__test_case.shield_booster_variants = copy.deepcopy(self.__find_boosters_to_test())

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

            # load shield generators
            sg_node = j_data["shield_generators"]
            for sg_type, sg_list in sg_node["modules"].items():
                sg_type_dict = self.__shield_generators.setdefault(sg_type, dict())
                for j_generator in sg_list:
                    generator = ShieldGenerator.create_from_json(j_generator)
                    self.__unengineered_shield_generators.setdefault(generator.symbol, generator)
                    generator_variants = ShieldGenerator.create_engineered_shield_generators(generator,
                                                                                             sg_node["engineering"]["blueprints"],
                                                                                             sg_node["engineering"]["experimental_effects"])
                    sg_type_dict.setdefault(generator.module_class, generator_variants)
