#!/usr/bin/env python3

"""
All credit for the calculations goes to DownToEarthAstronomy and his PowerShell program
which can be found at https://github.com/DownToEarthAstronomy/D2EA_Shield_tester

This is just an implementation in Python of his program featuring a user interface. Python adaptation and UI by Sebastian Bauer (https://github.com/Thurion)

Build to exe using the command: "pyinstaller --noconsole elite_shield_tester.py"
Don't forget to copy csv files into the exe's directory afterwards.
"""

import csv
import os
import sys
import re
import locale
import time
import itertools
import multiprocessing
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Dict, Tuple

# Configuration
VERSION = "0.4"

path = os.pardir
if re.match(".*elite_shield_tester\.exe", sys.executable):
    path = os.getcwd()
FILE_SHIELD_BOOSTER_VARIANTS = os.path.join(path, "ShieldBoosterVariants_short.csv")
FILE_SHIELD_GENERATOR_VARIANTS = os.path.join(path, "ShieldGeneratorVariants.csv")
LOG_DIRECTORY = os.path.join(os.getcwd(), "Logs")


class CustomEntry(tk.Entry):
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
            self.__variable.set(newvalue)
        else:
            self.__value = value

    def validate(self, value):
        return True


class IntegerEntry(CustomEntry):
    def validate(self, value):
        try:
            if value:
                v = int(value)
                return value
            else:
                return ""
        except ValueError:
            return None


class TextEntry(CustomEntry):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._regex = re.compile("^([A-Za-z0-9,._-]*|[A-Za-z0-9,.-_]+[A-Za-z0-9,._ -]*)$")

    def validate(self, value):
        if value:
            if self._regex.match(value):
                return value
            else:
                return None
        else:
            return ""


class ShieldBoosterVariant:
    def __init__(self, csv_row):
        self.id = int(csv_row["ID"])
        self.engineering = csv_row["Engineering"]
        self.experimental = csv_row["Experimental"]
        self.shieldStrengthBonus = float(csv_row["ShieldStrengthBonus"])
        self.expResBonus = 1.0 - float(csv_row["ExpResBonus"])
        self.kinResBonus = 1.0 - float(csv_row["KinResBonus"])
        self.thermResBonus = 1.0 - float(csv_row["ThermResBonus"])


class ShieldGeneratorVariant:
    def __init__(self, csv_row):
        self.id = int(csv_row["ID"])
        self.type = csv_row["Type"]
        self.engineering = csv_row["Engineering"]
        self.experimental = csv_row["Experimental"]
        self.shieldStrength = int(csv_row["ShieldStrength"])
        self.regenRate = float(csv_row["RegenRate"])
        self.expRes = 1.0 - float(csv_row["ExpRes"])
        self.kinRes = 1.0 - float(csv_row["KinRes"])
        self.thermRes = 1.0 - float(csv_row["ThermRes"])


class LoadOutStat:
    def __init__(self, hitpoints: float=0.0, regen_rate: float=0.0, explosive_resistance: float=0.0, kinetic_resistance: float=0.0, thermal_resistance: float=0.0):
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
        self.booster_combination_bonuses = None
        self.shield_generator_variants = None
        self.booster_combinations = None
        self.usePrismatic = False


class TestResult:
    def __init__(self, best_shield_generator: int=0, best_shield_booster_loadout: List[int]=None,
                 best_loadout_stats: LoadOutStat=None, best_survival_time: int=0):
        self.best_shield_generator = best_shield_generator
        self.best_shield_booster_loadout = best_shield_booster_loadout
        self.best_loadout_stats = best_loadout_stats
        self.best_survival_time = best_survival_time  # if negative, the ship didn't die


class ShieldTester(tk.Tk):
    EVENT_COMPUTE_OUTPUT = "<<EventComputeOutput>>"
    EVENT_COMPUTE_COMPLETE = "<<EventComputeComplete>>"
    EVENT_PROGRESS_BAR_STEP = "<<EventProgressBarStep>>"
    EVENT_WARNING_WRITE_LOGFILE = "<<EventShowWarningWriteLogfile>>"

    def __init__(self):
        super().__init__()
        self.title("Shield Tester v{}".format(VERSION))
        self._runtime = 0

        self.bind(self.EVENT_COMPUTE_OUTPUT, lambda e: self._event_process_output(e))
        self.bind(self.EVENT_COMPUTE_COMPLETE, lambda e: self._event_compute_complete(e))
        self.bind(self.EVENT_PROGRESS_BAR_STEP, lambda e: self._event_progress_bar_step(e))
        self.bind(self.EVENT_WARNING_WRITE_LOGFILE, lambda e: self._event_show_warning_logfile(e))
        self._message_queue = queue.SimpleQueue()
        self._shield_booster_variants = None
        self._shield_generator_variants = None

        # add some padding
        tk.Frame(self, width=10, height=10).grid(row=0, column=0, sticky=tk.N)
        tk.Frame(self, width=10, height=10).grid(row=2, column=3, sticky=tk.N)

        self._lockable_ui_elements = list()

        padding = 5
        # ---------------------------------------------------------------------------------------------------
        # left frame
        self._left_frame = tk.LabelFrame(self, borderwidth=1, relief=tk.RIDGE, text="Config")
        self._left_frame.grid(row=1, column=1, sticky=tk.NSEW)

        row = 0
        tk.Label(self._left_frame, text="Name of test (optional)").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._test_name = TextEntry(self._left_frame)
        self._test_name.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._test_name)

        row += 1
        tk.Label(self._left_frame, text="Number of boosters").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._booster_slider = tk.Scale(self._left_frame, from_=0, to=8, orient=tk.HORIZONTAL, length=175, takefocus=True)
        self._booster_slider.set(2)
        self._booster_slider.grid(row=row, column=1, sticky=tk.E, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._booster_slider)

        row += 1
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

        row += 1
        tk.Label(self._left_frame, text="Access to prismatic shields").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._usePrismatic = tk.IntVar()
        self._usePrismatic.set(1)
        self._prismatic_check_button = tk.Checkbutton(self._left_frame, variable=self._usePrismatic)
        self._prismatic_check_button.grid(row=row, column=1, sticky=tk.W, pady=padding)
        self._lockable_ui_elements.append(self._prismatic_check_button)

        # empty row
        row += 1
        tk.Label(self._left_frame, text="").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)

        row += 1
        tk.Label(self._left_frame, text="CPU cores to use").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._cores_slider = tk.Scale(self._left_frame, from_=1, to=os.cpu_count(), orient=tk.HORIZONTAL, length=175, takefocus=True)
        self._cores_slider.set(1)
        if sys.version_info >= (3, 8):
            self._cores_slider.grid(row=row, column=1, sticky=tk.E, padx=padding, pady=padding)
            self._lockable_ui_elements.append(self._cores_slider)
        else:
            tk.Label(self._left_frame, text="Upgrade to Python 3.8+ to unlock multiple cores").grid(row=row, column=1, sticky=tk.SW, padx=padding, pady=padding)

        row += 1
        self._compute_button = tk.Button(self._left_frame, text="Compute best loadout", command=self.compute)
        self._compute_button.grid(row=row, columnspan=2, sticky=tk.S, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._compute_button)

        row += 1
        self._progress_bar = ttk.Progressbar(self._left_frame, orient="horizontal", mode="determinate")
        self._progress_bar.grid(row=row, columnspan=2, sticky=tk.EW, padx=padding, pady=padding)
        self._progress_bar.config(value=0)

        # ---------------------------------------------------------------------------------------------------
        # right frame
        self._right_frame = tk.LabelFrame(self, borderwidth=1, relief=tk.RIDGE, text="Output")
        self._right_frame.grid(row=1, column=2, sticky=tk.NSEW)
        self._text_widget = scrolledtext.ScrolledText(self._right_frame, height=27, width=75)
        self._text_widget.grid(row=0, column=0, padx=padding, pady=padding, sticky=tk.NSEW)
        self._text_widget.config(state=tk.DISABLED)

        # set behaviour for resizing
        self.rowconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self._right_frame.rowconfigure(0, weight=1)
        self._right_frame.columnconfigure(0, weight=1)

        self._lock_ui_elements()
        self.after(100, self._read_csv_files)

        def set_window_size():
            self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())
        self.after(200, set_window_size)

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
        if not self._message_queue.empty():
            self._text_widget.config(state=tk.NORMAL)
            position, message = self._message_queue.get_nowait()
            self._text_widget.insert(position, message)
            self._text_widget.config(state=tk.DISABLED)

    def _event_progress_bar_step(self, event):
        if self._progress_bar:
            self._progress_bar.step()

    def _event_compute_complete(self, event):
        self._unlock_ui_elements()

    def _event_show_warning_logfile(self, event):
        messagebox.showwarning("Could not write logfile.", "Could not write logfile.")

    def _compute_background(self, test_data: ShieldTesterData):
        self._runtime = time.time()
        output = list()
        output.append("Shield Booster Count: {0}".format(test_data.number_of_boosters))
        output.append("Shield Booster Variants: {0}".format(len(self._shield_booster_variants)))
        output.append("Generating booster loadouts")
        output.append("")
        self._message_queue.put((tk.END, "\n".join(output)))
        output = list()
        self.event_generate(self.EVENT_COMPUTE_OUTPUT, when="tail")  # thread safe communication

        # use built in itertools and assume booster ids are starting at 1 and that there are no gaps
        test_data.booster_combinations = list(itertools.combinations_with_replacement(range(1, len(self._shield_booster_variants) + 1), test_data.number_of_boosters))
        test_data.booster_combination_bonuses = list(map(self._calculate_booster_bonuses, test_data.booster_combinations))

        output.append("Shield loadouts to be tested: [{0:n}]".format(len(test_data.booster_combinations) * len(test_data.shield_generator_variants)))
        output.append("Running calculations. Please wait...")
        output.append("")
        self._message_queue.put((tk.END, "\n".join(output)))
        output = list()
        self.event_generate(self.EVENT_COMPUTE_OUTPUT, when="tail")  # thread safe communication

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
            self.event_generate(self.EVENT_PROGRESS_BAR_STEP, when="tail")

        if test_data.cpu_cores > 1 and (len(test_data.booster_combinations) * len(test_data.shield_generator_variants)) > 1000:
            # 1 core is handling UI and this thread, the rest is working on running the calculations
            with multiprocessing.Pool(processes=test_data.cpu_cores - 1) as pool:
                for shield_generator_variant in test_data.shield_generator_variants.values():
                    pool.apply_async(test_case, args=(test_data, shield_generator_variant), callback=apply_async_callback)
                pool.close()
                pool.join()
        else:
            for shield_generator_variant in test_data.shield_generator_variants.values():
                result = test_case(test_data, shield_generator_variant)
                apply_async_callback(result)  # can use the same function here as mp.Pool would

        output.append("Calculations took {:.2f} seconds".format(time.time() - self._runtime))
        output.append("")
        output.append("---- TEST RESULTS ----")
        if best_result.best_survival_time != 0:
            # sort by survival time and put highest value to start of the list
            if best_result.best_survival_time > 0:
                output.append("Survival Time [s]: [{0:.3f}]".format(best_result.best_survival_time))
            else:
                output.append("Survival Time [s]: [Didn't die]")
            shield_generator = self._shield_generator_variants.get(best_result.best_shield_generator)
            output.append("Shield Generator: [{type}] - [{eng}] - [{exp}]"
                          .format(type=shield_generator.type, eng=shield_generator.engineering, exp=shield_generator.experimental))
            output.append("Shield Boosters:")
            for bestShieldBoosterLoadout in best_result.best_shield_booster_loadout:
                shield_booster_variant = self._shield_booster_variants.get(bestShieldBoosterLoadout)
                output.append("  [{eng}] - [{exp}]".format(eng=shield_booster_variant.engineering, exp=shield_booster_variant.experimental))

            output.append("")
            output.append("Shield Hitpoints: [{0:.3f}]".format(best_result.best_loadout_stats.hitPoints))
            output.append("Shield Regen: [{0} hp/s]".format(best_result.best_loadout_stats.regenRate))
            output.append("Explosive Resistance: [{0:.3f}]".format((1.0 - best_result.best_loadout_stats.explosiveResistance) * 100))
            output.append("Kinetic Resistance: [{0:.3f}]".format((1.0 - best_result.best_loadout_stats.kineticResistance) * 100))
            output.append("Thermal Resistance: [{0:.3f}]".format((1.0 - best_result.best_loadout_stats.thermalResistance) * 100))
        else:
            output.append("No test results. Please change DPS and/or damage effectiveness.")

        output_string = "\n".join(output)
        self._message_queue.put((tk.END, output_string))
        self.event_generate(self.EVENT_COMPUTE_OUTPUT, when="tail")  # thread safe communication
        self.event_generate(self.EVENT_COMPUTE_COMPLETE, when="tail")
        try:
            self._write_log(test_data, output_string, self._test_name.get())
        except Exception as e:
            print("Error writing logfile")
            print(e)
            self.event_generate(self.EVENT_WARNING_WRITE_LOGFILE, when="tail")

    def _calculate_booster_bonuses(self, booster_loadout: Tuple[int]):
        exp_modifier = 1.0
        kin_modifier = 1.0
        therm_modifier = 1.0
        hitpoint_bonus = 1.0

        for booster_id in booster_loadout:
            booster_stats = self._shield_booster_variants.get(booster_id)

            exp_modifier *= booster_stats.expResBonus
            kin_modifier *= booster_stats.kinResBonus
            therm_modifier *= booster_stats.thermResBonus
            hitpoint_bonus += booster_stats.shieldStrengthBonus

        # Compensate for diminishing returns
        if exp_modifier < 0.7:
            exp_modifier = 0.7 - (0.7 - exp_modifier) / 2
        if kin_modifier < 0.7:
            kin_modifier = 0.7 - (0.7 - kin_modifier) / 2
        if therm_modifier < 0.7:
            therm_modifier = 0.7 - (0.7 - therm_modifier) / 2

        return exp_modifier, kin_modifier, therm_modifier, hitpoint_bonus

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
        ui_data.usePrismatic = True if self._usePrismatic.get() else False

        if ui_data.usePrismatic:
            ui_data.shield_generator_variants = self._shield_generator_variants
        else:
            ui_data.shield_generator_variants = {k: v for k, v in self._shield_generator_variants.items() if v.type != "Prismatic"}
        ui_data.shield_booster_variants = self._shield_booster_variants

        self._progress_bar.config(maximum=len(ui_data.shield_generator_variants))

        t = threading.Thread(target=self._compute_background, args=(ui_data,))
        t.start()

    @staticmethod
    def _write_log(data: ShieldTesterData, result: str, filename=None):
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
        if not filename:
            filename = time.strftime("%Y-%m-%d %H.%M.%S")
        with open(os.path.join(LOG_DIRECTORY, filename + ".txt"), "a+") as logfile:
            logfile.write("Test run at: {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            logfile.write("---- TEST SETUP ----\n")
            logfile.write("Shield Booster Count: [{}]\n".format(data.number_of_boosters))
            logfile.write("Shield Cell Bank Hit Point Pool: [{}]\n".format(data.scb_hitpoints))
            logfile.write("Guardian Shield Reinforcement Hit Point Pool: [{}]\n".format(data.guardian_hitpoints))
            logfile.write("Access to Prismatic Shields: [{}]\n".format("Yes" if data.usePrismatic else "No"))
            logfile.write("Explosive DPS: [{}]\n".format(data.explosive_dps))
            logfile.write("Kinetic DPS: [{}]\n".format(data.kinetic_dps))
            logfile.write("Thermal DPS: [{}]\n".format(data.thermal_dps))
            logfile.write("Absolute DPS: [{}]\n".format(data.absolute_dps))
            logfile.write("Damage Effectiveness: [{:.0f}%]\n".format(data.damage_effectiveness * 100))
            logfile.write(result)
            logfile.write("\n\n\n")
            logfile.flush()


def test_case(data: ShieldTesterData, shield_generator_variant: ShieldGeneratorVariant) -> TestResult:
    best_survival_time = 0
    best_shield_generator = 0
    best_shield_booster_loadout = None
    best_loadout_stats = 0

    for i in range(0, len(data.booster_combinations)):
        booster_variation = data.booster_combinations[i]
        exp_modifier, kin_modifier, therm_modifier, hitpoint_bonus = data.booster_combination_bonuses[i]
        # Calculate the resistance, regen-rate and hitpoints of the current loadout
        explosive_resistance = shield_generator_variant.expRes * exp_modifier
        kinetic_resistance = shield_generator_variant.kinRes * kin_modifier
        thermal_resistance = shield_generator_variant.thermRes * therm_modifier

        # Compute final hitpoints
        hitpoints = hitpoint_bonus * shield_generator_variant.shieldStrength + data.guardian_hitpoints

        actual_dps = data.damage_effectiveness * (
                data.explosive_dps * explosive_resistance +
                data.kinetic_dps * kinetic_resistance +
                data.thermal_dps * thermal_resistance +
                data.absolute_dps) - shield_generator_variant.regenRate * (1.0 - data.damage_effectiveness)

        survival_time = (hitpoints + data.scb_hitpoints) / actual_dps

        if actual_dps > 0 and best_survival_time >= 0:
            # if another run set best_survival_time to a negative value, then the ship didn't die, therefore the other result is better
            if survival_time > best_survival_time:
                best_shield_generator = shield_generator_variant.id
                best_shield_booster_loadout = booster_variation
                best_loadout_stats = LoadOutStat(hitpoints=hitpoints,
                                                 regen_rate=shield_generator_variant.regenRate,
                                                 explosive_resistance=explosive_resistance,
                                                 kinetic_resistance=kinetic_resistance,
                                                 thermal_resistance=thermal_resistance)
                best_survival_time = survival_time
        elif actual_dps < 0:
            if survival_time < best_survival_time:
                best_shield_generator = shield_generator_variant.id
                best_shield_booster_loadout = booster_variation
                best_loadout_stats = LoadOutStat(hitpoints=hitpoints,
                                                 regen_rate=shield_generator_variant.regenRate,
                                                 explosive_resistance=explosive_resistance,
                                                 kinetic_resistance=kinetic_resistance,
                                                 thermal_resistance=thermal_resistance)
                best_survival_time = survival_time

    return TestResult(best_shield_generator, best_shield_booster_loadout, best_loadout_stats, best_survival_time)


def main():
    locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
    shield_tester = ShieldTester()
    shield_tester.mainloop()


if __name__ == '__main__':
    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()
    main()
