#!/usr/bin/env python3

"""
All credit for the calculations goes to DownToEarthAstronomy and his PowerShell program
which can be found at https://github.com/DownToEarthAstronomy/D2EA_Shield_tester

This is just an implementation in Python of his program featuring a user interface. Python adaptation and UI by Sebastian Bauer

Build to exe using the command: "pyinstaller --noconsole elite_shield_tester.py"
Don't forget to copy csv files into the exe's directory afterward.
"""

import csv
import os
import locale
import time
import multiprocessing
import threading
import queue
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from typing import List, Dict

# Configuration
FILE_SHIELD_BOOSTER_VARIANTS = os.path.join(os.getcwd(), "ShieldBoosterVariants_short.csv")
FILE_SHIELD_GENERATOR_VARIANTS = os.path.join(os.getcwd(), "ShieldGeneratorVariants.csv")
LOG_DIRECTORY = os.path.join(os.getcwd(), "Logs")


class IntegerEntry(tk.Entry):
    # base class for validating entry widgets
    def __init__(self, master, value="", **kw):
        super().__init__(master, **kw)
        self.__value = value
        self.__variable = tk.StringVar()
        self.__variable.set(value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        if newvalue is None:
            self.__variable.set(self.__value)
        elif newvalue != value:
            self.__value = newvalue
            self.__variable.set(self.newvalue)
        else:
            self.__value = value

    @staticmethod
    def validate(value):
        try:
            if value:
                v = int(value)
                return value
            else:
                return ""
        except ValueError:
            return None


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


class ShieldTesterData:
    def __init__(self):
        self.number_of_boosters = 0
        self.damage_effectiveness = 0
        self.explosive_dps = 0
        self.kinetic_dps = 0
        self.thermal_dps = 0
        self.absolute_dps = 0
        self.cpu_cores = 0
        self.scb_hitpoints = 0
        self.guardian_hitpoints = 0
        self.shield_booster_variants = None
        self.booster_combinations = None


class ShieldTester(tk.Tk):
    EVENT_COMPUTE_OUTPUT = "<<EventComputeOutput>>"
    EVENT_COMPUTE_COMPLETE = "<<EventComputeComplete>>"
    EVENT_PROGRESS_BAR_STEP = "<<EventProgressBarStep>>"
    EVENT_WARNING_WRITE_LOGFILE = "<<EventShowWarningWriteLogfile>>"

    def __init__(self):
        super().__init__()
        self.title("Shield Tester")

        self.bind(self.EVENT_COMPUTE_OUTPUT, lambda e: self._event_process_output(e))
        self.bind(self.EVENT_COMPUTE_COMPLETE, lambda e: self._event_compute_complete(e))
        self.bind(self.EVENT_PROGRESS_BAR_STEP, lambda e: self._event_progress_bar_step(e))
        self.bind(self.EVENT_WARNING_WRITE_LOGFILE, lambda e: self._event_show_warning_logfile(e))
        self.message_queue = queue.SimpleQueue()
        self._shield_booster_variants = None
        self._shield_generator_variants = None

        # add some padding
        tk.Frame(self, width=10, height=10).grid(row=0, column=0, sticky=tk.N)
        tk.Frame(self, width=10, height=10).grid(row=2, column=3, sticky=tk.N)

        self._lockable_ui_elements = list()

        padding = 5
        self._left_frame = tk.Frame(self, borderwidth=1, relief=tk.RIDGE)
        self._left_frame.grid(row=1, column=1, sticky=tk.NS)
        tk.Label(self._left_frame, text="Number of boosters").grid(row=0, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._booster_slider = tk.Scale(self._left_frame, from_=0, to=8, orient=tk.HORIZONTAL, length=175, takefocus=True)
        self._booster_slider.set(2)
        self._booster_slider.grid(row=0, column=1, sticky=tk.E, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._booster_slider)

        row = 1
        tk.Label(self._left_frame, text="Damage effectiveness in %").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._effectiveness_slider = tk.Scale(self._left_frame, from_=1, to=100, orient=tk.HORIZONTAL, length=175, takefocus=True)
        self._effectiveness_slider.set(25)
        self._effectiveness_slider.grid(row=row, column=1, sticky=tk.E, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._effectiveness_slider)

        row += 1
        tk.Label(self._left_frame, text="Shield cell bank hit point pool").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._scb_hitpoints = IntegerEntry(self._left_frame)
        self._scb_hitpoints.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._scb_hitpoints)

        row += 1
        tk.Label(self._left_frame, text="Guardian shield reinforcement hit point pool").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._guardian_hitpoints = IntegerEntry(self._left_frame)
        self._guardian_hitpoints.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._guardian_hitpoints)

        row += 1
        tk.Label(self._left_frame, text="Explosive DPS").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._explosive_dps_entry = IntegerEntry(self._left_frame)
        self._explosive_dps_entry.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._explosive_dps_entry)

        row += 1
        tk.Label(self._left_frame, text="Kinetic DPS").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._kinetic_dps_entry = IntegerEntry(self._left_frame)
        self._kinetic_dps_entry.insert(0, 50)
        self._kinetic_dps_entry.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._kinetic_dps_entry)

        row += 1
        tk.Label(self._left_frame, text="Thermal DPS").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._thermal_dps_entry = IntegerEntry(self._left_frame)
        self._thermal_dps_entry.insert(0, 50)
        self._thermal_dps_entry.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._thermal_dps_entry)

        row += 1
        tk.Label(self._left_frame, text="Absolute DPS (Thargoids)").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._absolute_dps_entry = IntegerEntry(self._left_frame)
        self._absolute_dps_entry.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._absolute_dps_entry)

        # empty row
        row += 1
        tk.Label(self._left_frame, text="").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)

        row += 1
        tk.Label(self._left_frame, text="CPU cores to use").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._cores_slider = tk.Scale(self._left_frame, from_=1, to=os.cpu_count(), orient=tk.HORIZONTAL, length=175, takefocus=True)
        self._cores_slider.set(os.cpu_count())
        self._cores_slider.grid(row=row, column=1, sticky=tk.E, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._cores_slider)

        self._right_frame = tk.Frame(self, borderwidth=1, relief=tk.RIDGE)
        self._right_frame.grid(row=1, column=2, sticky=tk.NS)
        self._text_widget = tk.Text(self._right_frame, height=27, width=75)
        self._text_widget.pack(padx=padding, pady=padding)
        self._text_widget.config(state=tk.DISABLED)

        row += 1
        self._compute_button = tk.Button(self._left_frame, text="Compute best loadout", command=self.compute)
        self._compute_button.grid(row=row, columnspan=2, sticky=tk.S, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._compute_button)

        row += 1
        self._progress_bar = ttk.Progressbar(self._left_frame, orient="horizontal", mode="determinate")
        self._progress_bar.grid(row=row, columnspan=2, sticky=tk.EW, padx=padding, pady=padding)
        self._progress_bar.config(value=0)

        self._lock_ui_elements()
        self.after(100, self._read_csv_files())

    def _read_csv_files(self):
        error_occurred = False
        if os.path.exists(FILE_SHIELD_BOOSTER_VARIANTS) and os.path.exists(FILE_SHIELD_GENERATOR_VARIANTS):
            try:
                self._shield_booster_variants = dict()
                with open(FILE_SHIELD_BOOSTER_VARIANTS, "r") as csv_file:
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        variant = ShieldBoosterVariant(row)
                        self._shield_booster_variants.setdefault(variant.id, variant)

                self._shield_generator_variants = dict()
                with open(FILE_SHIELD_GENERATOR_VARIANTS, "r") as csv_file:
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        variant = ShieldGeneratorVariant(row)
                        self._shield_generator_variants.setdefault(variant.id, variant)
            except Exception as e:
                print("Exception while reading/parsing CSV files: ")  # in case we have a console window
                print(e)
                error_occurred = True
        else:
            error_occurred = True

        if not error_occurred:
            self._progress_bar.config(maximum=len(self._shield_generator_variants))
            self._unlock_ui_elements()
        else:
            if tk.messagebox.askretrycancel("No data", "Could not read CSV files.\nPlease place them in the same directory as this program.\n"
                                                       "Required:\n{generator}\n{booster}".format(generator=os.path.basename(FILE_SHIELD_GENERATOR_VARIANTS),
                                                                                                  booster=os.path.basename(FILE_SHIELD_BOOSTER_VARIANTS))):
                self._read_csv_files()

    def _lock_ui_elements(self):
        for element in self._lockable_ui_elements:
            element.config(state=tk.DISABLED)

    def _unlock_ui_elements(self):
        for element in self._lockable_ui_elements:
            element.config(state=tk.NORMAL)

    def _event_process_output(self, event):
        self._text_widget.config(state=tk.NORMAL)
        position, message = self.message_queue.get_nowait()
        self._text_widget.insert(position, message)
        self._text_widget.config(state=tk.DISABLED)

    def _event_progress_bar_step(self, event):
        if self._progress_bar:
            self._progress_bar.step()

    def _event_compute_complete(self, event):
        self._unlock_ui_elements()

    def _event_show_warning_logfile(self, event):
        messagebox.showwarning("Could not write logfile.", "Could not write logfile.")

    def _generate_booster_variations(self, number_of_boosters: int, variations_list: List[List[int]],
                                     current_booster: int = 1, current_variation: int = 1, variations: List[int] = list()):
        # Generate all possible booster combinations recursively and append them to the given variationsList.
        if current_booster <= number_of_boosters:
            while current_variation <= len(self._shield_booster_variants):
                current_variation_list = variations.copy()
                current_variation_list.append(current_variation)
                self._generate_booster_variations(number_of_boosters, variations_list, current_booster + 1, current_variation, current_variation_list)
                current_variation += 1
        else:
            # Append to list. Variable is a reference and lives in main function. Therefore it is safe to append lists of booster IDs to it.
            variations_list.append(variations)

    def _compute_background(self, test_data: ShieldTesterData):
        output = list()
        output.append("Shield Booster Count: {0}".format(test_data.number_of_boosters))
        output.append("Shield Booster Variants: {0}".format(len(self._shield_booster_variants)))
        output.append("Generating list of booster loadouts")
        output.append("")
        self.message_queue.put((tk.END, "\n".join(output)))
        output = list()
        self.event_generate(self.EVENT_COMPUTE_OUTPUT)  # thread safe communication

        variations_list = list()  # list of all possible booster variations
        self._generate_booster_variations(test_data.number_of_boosters, variations_list)
        test_data.booster_combinations = variations_list
        output.append("Shield loadouts to be tested: [{0:n}]".format(len(variations_list) * len(self._shield_generator_variants)))
        output.append("Running calculations. Please wait...")
        output.append("")
        self.message_queue.put((tk.END, "\n".join(output)))
        output = list()
        self.event_generate(self.EVENT_COMPUTE_OUTPUT)  # thread safe communication

        best_result = {"bestSurvivalTime": -1}

        def apply_async_callback(r: Dict[str, object]):
            nonlocal best_result
            if r["bestSurvivalTime"] > best_result["bestSurvivalTime"]:
                best_result = r
            self.event_generate(self.EVENT_PROGRESS_BAR_STEP)

        if test_data.cpu_cores > 1 and (len(variations_list) * len(self._shield_generator_variants)) > 1000:
            # 1 core is handling UI and this thread, the rest is working on running the calculations
            with multiprocessing.Pool(processes=test_data.cpu_cores - 1) as pool:
                for shield_generator_variant in self._shield_generator_variants.values():
                    pool.apply_async(test_case, args=(test_data, shield_generator_variant), callback=apply_async_callback)
                pool.close()
                pool.join()
        else:
            for shield_generator_variant in self._shield_generator_variants.values():
                result = test_case(test_data, shield_generator_variant)
                if result["bestSurvivalTime"] > best_result["bestSurvivalTime"]:
                    best_result = result
                self.event_generate(self.EVENT_PROGRESS_BAR_STEP)

        output.append("")
        output.append("---- TEST RESULTS ----")
        if best_result["bestSurvivalTime"] > 0:
            # sort by survival time and put highest value to start of the list
            output.append("Survival Time [s]: [{0:.3f}]".format(best_result["bestSurvivalTime"]))

            shield_generator = self._shield_generator_variants.get(best_result["bestShieldGenerator"])
            output.append("Shield Generator: [{type}] - [{eng}] - [{exp}]"
                          .format(type=shield_generator.type, eng=shield_generator.engineering, exp=shield_generator.experimental))
            output.append("Shield Boosters:")
            for bestShieldBoosterLoadout in best_result["bestShieldBoosterLoadout"]:
                shield_booster_variant = self._shield_booster_variants.get(bestShieldBoosterLoadout)
                output.append("  [{eng}] - [{exp}]".format(eng=shield_booster_variant.engineering, exp=shield_booster_variant.experimental))

            output.append("")
            output.append("Shield Hitpoints: [{0:.3f}]".format(best_result["bestLoadoutStats"].hitPoints))
            output.append("Shield Regen: [{0} hp/s]".format(best_result["bestLoadoutStats"].regenRate))
            output.append("Explosive Resistance: [{0:.3f}]".format(best_result["bestLoadoutStats"].explosiveResistance * 100))
            output.append("Kinetic Resistance: [{0:.3f}]".format(best_result["bestLoadoutStats"].kineticResistance * 100))
            output.append("Thermal Resistance: [{0:.3f}]".format(best_result["bestLoadoutStats"].thermalResistance * 100))
        else:
            output.append("Didn't take enough damage. Please increase DPS and/or damage effectiveness.")

        output_string = "\n".join(output)
        self.message_queue.put((tk.END, output_string))
        self.event_generate(self.EVENT_COMPUTE_OUTPUT)  # thread safe communication
        self.event_generate(self.EVENT_COMPUTE_COMPLETE)
        try:
            self._write_log(test_data, output_string)
        except Exception as e:
            print("Error writing logfile")
            print(e)
            self.event_generate(self.EVENT_WARNING_WRITE_LOGFILE)

    def compute(self):
        self._lock_ui_elements()

        # clear text widget
        self._text_widget.config(state=tk.NORMAL)
        self._text_widget.delete("1.0", tk.END)
        self._text_widget.config(state=tk.DISABLED)

        # get data from UI
        ui_data = ShieldTesterData()
        ui_data.number_of_boosters = self._booster_slider.get()
        ui_data.damage_effectiveness = self._effectiveness_slider.get() / 100.0
        ui_data.scb_hitpoints = int(self._scb_hitpoints.get()) if self._scb_hitpoints.get() else 0
        ui_data.guardian_hitpoints = int(self._guardian_hitpoints.get()) if self._guardian_hitpoints.get() else 0
        ui_data.explosive_dps = int(self._explosive_dps_entry.get()) if self._explosive_dps_entry.get() else 0
        ui_data.kinetic_dps = int(self._kinetic_dps_entry.get()) if self._kinetic_dps_entry.get() else 0
        ui_data.thermal_dps = int(self._thermal_dps_entry.get()) if self._thermal_dps_entry.get() else 0
        ui_data.absolute_dps = int(self._absolute_dps_entry.get()) if self._absolute_dps_entry.get() else 0
        ui_data.cpu_cores = self._cores_slider.get()

        ui_data.shield_booster_variants = self._shield_booster_variants

        t = threading.Thread(target=self._compute_background, args=(ui_data,))
        t.start()

    @staticmethod
    def _write_log(data: ShieldTesterData, result: str):
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
        with open(os.path.join(LOG_DIRECTORY, time.strftime("%Y-%m-%d %H.%M.%S") + ".txt"), "a+") as logfile:
            logfile.write("Test run at: {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            logfile.write("\n")
            logfile.write("---- TEST SETUP ----\n")
            logfile.write("Shield Booster Count: [{}]\n".format(data.number_of_boosters))
            logfile.write("Shield Cell Bank Hit Point Pool: [{}]\n".format(data.scb_hitpoints))
            logfile.write("Guardian Shield Reinforcement Hit Point Pool: [{}]\n".format(data.guardian_hitpoints))
            logfile.write("Explosive DPS: [{}]\n".format(data.explosive_dps))
            logfile.write("Kinetic DPS: [{}]\n".format(data.kinetic_dps))
            logfile.write("Thermal DPS: [{}]\n".format(data.thermal_dps))
            logfile.write("Absolute DPS: [{}]\n".format(data.absolute_dps))
            logfile.write("Damage Effectiveness: [{:.0f}%]\n".format(data.damage_effectiveness * 100))
            logfile.write(result)
            logfile.flush()


def test_case(data: ShieldTesterData, shield_generator_variant: ShieldGeneratorVariant) -> Dict:
    best_survival_time = 0
    best_shield_generator = 0
    best_shield_booster_loadout = None
    best_loadout_stats = 0

    for booster_variation in data.booster_combinations:
        # Calculate the resistance, regen-rate and hitpoints of the current loadout
        loadout_stats = calculate_loadout_stats(data, shield_generator_variant, booster_variation)

        actual_dps = data.damage_effectiveness * (
                data.explosive_dps * (1 - loadout_stats.explosiveResistance) +
                data.kinetic_dps * (1 - loadout_stats.kineticResistance) +
                data.thermal_dps * (1 - loadout_stats.thermalResistance) +
                data.absolute_dps) - loadout_stats.regenRate * (1 - data.damage_effectiveness)

        survival_time = (loadout_stats.hitPoints + data.scb_hitpoints) / actual_dps

        if survival_time > best_survival_time:
            best_shield_generator = shield_generator_variant.id
            best_shield_booster_loadout = booster_variation
            best_loadout_stats = loadout_stats
            best_survival_time = survival_time

    return {"bestShieldGenerator": best_shield_generator,
            "bestShieldBoosterLoadout": best_shield_booster_loadout,
            "bestLoadoutStats": best_loadout_stats,
            "bestSurvivalTime": best_survival_time}


def calculate_loadout_stats(data: ShieldTesterData, shield_generator_variant: ShieldGeneratorVariant, shield_booster_loadout: List[int]) -> LoadOutStat:
    exp_modifier = 1
    kin_modifier = 1
    therm_modifier = 1
    hitpoint_bonus = 0

    for booster_id in shield_booster_loadout:
        booster_stats = data.shield_booster_variants.get(booster_id)

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
    hitpoints = (1 + hitpoint_bonus) * shield_generator_variant.shieldStrength + data.guardian_hitpoints

    return LoadOutStat(hitpoints, shield_generator_variant.regenRate, exp_res, kin_res, therm_res)


def main():
    locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
    shield_tester = ShieldTester()
    shield_tester.mainloop()


if __name__ == '__main__':
    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()
    main()
