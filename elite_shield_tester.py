#!/usr/bin/env python3

"""
All credit goes to DownToEarthAstronomy for his PowerShell program which can be found at https://github.com/DownToEarthAstronomy/D2EA_Shield_tester
This is just an implementation in Python of his program.
"""

import csv
import os
import locale
import multiprocessing
from functools import partial
from typing import List, Dict


# Configuration
SHIELD_BOOSTER_COUNT = 8

EXPLOSIVE_DPS = 0
KINETIC_DPS = 50
THERMAL_DPS = 50
ABSOLUTE_DPS = 0

DAMAGE_EFFECTIVENESS = 0.33  # 1 = always taking damage; 0.5 = Taking damage 50% of the time

NUMBER_OF_PROCESSES = os.cpu_count()  # change to any positive integer value or use os.cpu_count()
FILE_SHIELD_BOOSTER_VARIANTS = os.path.join(os.getcwd(), "ShieldBoosterVariants_short.csv")
FILE_SHIELD_GENERATOR_VARIANTS = os.path.join(os.getcwd(), "ShieldGeneratorVariants.csv")


class ShieldBoosterVariant:
    def __init__(self, csv_row):
        self.id = int(csv_row["ID"])
        self.engineering = csv_row["Engineering"]
        self.experimental = csv_row["Experimental"]
        self.shieldStrengthBonus = float(csv_row["ShieldStrengthBonus"])
        self.expResBonus = float(csv_row["ExpResBonus"])
        self.kinResBonus = float(csv_row["KinResBonus"])
        self.thermResBonus = float(csv_row["ThermResBonus"])


class ShieldGeneratorVariant:
    def __init__(self, csv_row):
        self.id = int(csv_row["ID"])
        self.type = csv_row["Type"]
        self.engineering = csv_row["Engineering"]
        self.experimental = csv_row["Experimental"]
        self.shieldStrength = int(csv_row["ShieldStrength"])
        self.regenRate = float(csv_row["RegenRate"])
        self.expRes = float(csv_row["ExpRes"])
        self.kinRes = float(csv_row["KinRes"])
        self.thermRes = float(csv_row["ThermRes"])


class LoadOutStat:
    def __init__(self, hitpoints, regen_rate, explosive_resistance, kinetic_resistance, thermal_resistance):
        self.hitPoints = hitpoints
        self.regenRate = regen_rate
        self.explosiveResistance = explosive_resistance
        self.kineticResistance = kinetic_resistance
        self.thermalResistance = thermal_resistance


def calculate_loadout_stats(shield_generator_variant: ShieldGeneratorVariant,
                            shield_booster_loadout: List[int],
                            shield_booster_variants: Dict[int, ShieldBoosterVariant]) -> LoadOutStat:
    exp_modifier = 1
    kin_modifier = 1
    therm_modifier = 1
    hitpoint_bonus = 0

    for booster_id in shield_booster_loadout:
        booster_stats = shield_booster_variants.get(booster_id)

        exp_modifier = exp_modifier * (1 - booster_stats.expResBonus)
        kin_modifier = kin_modifier * (1 - booster_stats.kinResBonus)
        therm_modifier = therm_modifier * (1 - booster_stats.thermResBonus)
        hitpoint_bonus = hitpoint_bonus + booster_stats.shieldStrengthBonus

    # Compensate for diminishing returns
    if exp_modifier < 0.7:
        exp_modifier = 0.7 - (0.7 - exp_modifier) / 2
    if kin_modifier < 0.7:
        kin_modifier = 0.7 - (0.7 - kin_modifier) / 2
    if therm_modifier < 0.7:
        therm_modifier = 0.7 - (0.7 - therm_modifier) / 2

    # Compute final resistance
    exp_res = 1 - ((1 - shield_generator_variant.expRes) * exp_modifier)
    kin_res = 1 - ((1 - shield_generator_variant.kinRes) * kin_modifier)
    therm_res = 1 - ((1 - shield_generator_variant.thermRes) * therm_modifier)

    # Compute final hitpoints
    hitpoints = (1 + hitpoint_bonus) * shield_generator_variant.shieldStrength

    return LoadOutStat(hitpoints, shield_generator_variant.regenRate, exp_res, kin_res, therm_res)


def generate_booster_variations(number_of_shield_variants: int, number_of_boosters: int, variations_list: List[List[int]],
                                current_booster: int=1, current_variation: int=1, variations: List[int]=list()):
    # Generate all possible booster combinations recursively and append them to the given variationsList.
    if current_booster <= number_of_boosters:
        while current_variation <= number_of_shield_variants:
            current_variation_list = variations.copy()
            current_variation_list.append(current_variation)
            generate_booster_variations(number_of_shield_variants, number_of_boosters, variations_list, current_booster + 1, current_variation, current_variation_list)
            current_variation += 1
    else:
        # Append to list. Variable is a reference and lives in main function. Therefore it is safe to append lists of booster IDs to it.
        variations_list.append(variations)


def test_case(shield_generator_variants: List[ShieldGeneratorVariant],
              shield_booster_variants: Dict[int, ShieldBoosterVariant],
              shield_booster_loadout: List[int]) -> Dict:
    best_survival_time = 0
    best_shield_generator = 0
    best_shield_booster_loadout = None
    best_loadout_stats = 0

    for shield_generator_variant in shield_generator_variants:
        # Calculate the resistance, regen-rate and hitpoints of the current loadout
        loadout_stats = calculate_loadout_stats(shield_generator_variant, shield_booster_loadout, shield_booster_variants)

        actual_dps = DAMAGE_EFFECTIVENESS * (
            EXPLOSIVE_DPS * (1 - loadout_stats.explosiveResistance) +
            KINETIC_DPS * (1 - loadout_stats.kineticResistance) +
            THERMAL_DPS * (1 - loadout_stats.thermalResistance) +
            ABSOLUTE_DPS) - loadout_stats.regenRate * (1 - DAMAGE_EFFECTIVENESS)

        survival_time = loadout_stats.hitPoints / actual_dps

        if survival_time > best_survival_time:
            best_shield_generator = shield_generator_variant.id
            best_shield_booster_loadout = shield_booster_loadout
            best_loadout_stats = loadout_stats
            best_survival_time = survival_time

    return {"bestShieldGenerator": best_shield_generator,
            "bestShieldBoosterLoadout": best_shield_booster_loadout,
            "bestLoadoutStats": best_loadout_stats,
            "bestSurvivalTime": best_survival_time}


def main():
    locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
    shield_booster_variants = dict()
    with open(FILE_SHIELD_BOOSTER_VARIANTS, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            variant = ShieldBoosterVariant(row)
            shield_booster_variants.setdefault(variant.id, variant)

    shield_generator_variants = dict()
    with open(FILE_SHIELD_GENERATOR_VARIANTS, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            variant = ShieldGeneratorVariant(row)
            shield_generator_variants.setdefault(variant.id, variant)

    print("Shield Booster Count: {0}".format(SHIELD_BOOSTER_COUNT))
    print("Shield Booster Variants: {0}".format(len(shield_booster_variants)))
    print("Generating list of booster loadouts...")

    variations_list = list()  # list of all possible booster variations
    generate_booster_variations(len(shield_booster_variants), SHIELD_BOOSTER_COUNT, variations_list)
    print("Shield loadouts to be tested: [{0:n}]".format(len(variations_list) * len(shield_generator_variants)))

    best_result = {"bestSurvivalTime": -1}
    print("Running calculations. Please wait...")

    with multiprocessing.Pool(processes=NUMBER_OF_PROCESSES) as pool:
        func = partial(test_case, list(shield_generator_variants.values()), shield_booster_variants)
        results = pool.imap_unordered(func, variations_list, chunksize=1000)
        for result in results:
            if result["bestSurvivalTime"] > best_result["bestSurvivalTime"]:
                best_result = result

    print("")
    if best_result["bestSurvivalTime"] > 0:
        # sort by survival time and put highest value to start of the list
        print("---- TEST RESULTS ----")
        print("Survival Time [s]: [{0:.3f}]".format(best_result["bestSurvivalTime"]))

        shield_generator = shield_generator_variants.get(best_result["bestShieldGenerator"])
        print("Shield Generator: [{type}] - [{eng}] - [{exp}]".format(type=shield_generator.type, eng=shield_generator.engineering, exp=shield_generator.experimental))
        print("Shield Boosters:")
        for bestShieldBoosterLoadout in best_result["bestShieldBoosterLoadout"]:
            shield_booster_variant = shield_booster_variants.get(bestShieldBoosterLoadout)
            print("    [{eng}] - [{exp}]".format(eng=shield_booster_variant.engineering, exp=shield_booster_variant.experimental))

        print("")
        print("Shield Hitpoints: [{0:.3f}]".format(best_result["bestLoadoutStats"].hitPoints))
        print("Shield Regen: [{0} hp/s]".format(best_result["bestLoadoutStats"].regenRate))
        print("ExplosivecResistance: [{0:.3f}]".format(best_result["bestLoadoutStats"].explosiveResistance * 100))
        print("Kinetic Resistance: [{0:.3f}]".format(best_result["bestLoadoutStats"].kineticResistance * 100))
        print("Thermal Resistance: [{0:.3f}]".format(best_result["bestLoadoutStats"].thermalResistance * 100))


if __name__ == '__main__':
    main()
