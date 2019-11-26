#!/usr/bin/env python3

"""
All credit for the calculations goes to DownToEarthAstronomy and his PowerShell program
which can be found at https://github.com/DownToEarthAstronomy/D2EA_Shield_tester

This is just an implementation in Python of his program featuring a user interface. Python adaptation and UI by Sebastian Bauer (https://github.com/Thurion)

Build to exe using the command: "pyinstaller --noconsole elite_shield_tester.py"
Don't forget to copy csv files into the exe's directory afterwards.
"""

import os
import re
import locale
import multiprocessing
import sys
import threading
import queue
import copy
import webbrowser
import tkinter as tk
from typing import Dict, List, Optional
from tkinter import ttk, messagebox, scrolledtext
import shield_tester as st

# Configuration
VERSION = "1.1 beta"
DATA_FILE = os.path.join(os.getcwd(), "data.json")
QUICK_GUIDE_FILE = os.path.join(os.getcwd(), "quick_guide.txt")


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


class TabData(object):
    def __init__(self, tab: scrolledtext.ScrolledText = None, test_result: st.TestResult = None):
        self.tab = tab
        self.test_result = test_result


class ShieldTesterUi(tk.Tk):
    EVENT_COMPUTE_OUTPUT = "<<EventComputeOutput>>"
    EVENT_COMPUTE_COMPLETE = "<<EventComputeComplete>>"
    EVENT_COMPUTE_CANCELLED = "<<EventComputeCancelled>>"
    EVENT_PROGRESS_BAR_STEP = "<<EventProgressBarStep>>"
    EVENT_WARNING_WRITE_LOGFILE = "<<EventShowWarningWriteLogfile>>"
    EVENT_TAB_CHANGED = "<<NotebookTabChanged>>"

    PRELIMINARY_FILTERING = 10  # set preliminary filtering to 10 which should find almost always the same result

    KEY_QUICK_GUIDE = "Quick Guide"

    def __init__(self):
        super().__init__()
        self.title("Shield Tester v{}".format(VERSION))
        self._runtime = 0

        self._shield_tester = st.ShieldTester()
        self._test_case = None  # type: st.TestCase
        self._lockable_ui_elements = list()

        # tab_name used as key for tabs
        self._active_tab_name = ""
        self._tabs = dict()  # type: Dict[str, TabData]

        self.bind(ShieldTesterUi.EVENT_COMPUTE_OUTPUT, lambda e: self._event_process_output(e))
        self.bind(ShieldTesterUi.EVENT_COMPUTE_COMPLETE, lambda e: self._event_compute_complete(e))
        self.bind(ShieldTesterUi.EVENT_COMPUTE_CANCELLED, lambda e: self._event_compute_cancelled(e))
        self.bind(ShieldTesterUi.EVENT_PROGRESS_BAR_STEP, lambda e: self._event_progress_bar_step(e))
        self.bind(ShieldTesterUi.EVENT_WARNING_WRITE_LOGFILE, lambda e: self._event_show_warning_logfile(e))
        self._message_queue = queue.SimpleQueue()

        # add some padding
        tk.Frame(self, width=10, height=10).grid(row=0, column=0, sticky=tk.N)
        tk.Frame(self, width=10, height=10).grid(row=2, column=3, sticky=tk.N)

        def headline(frame, title, h_row):
            # headline, use this instead of LabelFrame to keep using the same grid
            ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=h_row, columnspan=2, sticky=tk.EW, pady=(3*padding, 0))
            h_row += 1
            tk.Label(frame, text=title, justify=tk.CENTER).grid(row=h_row, columnspan=2, sticky=tk.EW)
            h_row += 1
            ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=h_row, columnspan=2, sticky=tk.EW)
            return h_row

        padding = 3
        # ---------------------------------------------------------------------------------------------------
        # left frame
        left_frame = tk.LabelFrame(self, borderwidth=1, text="Config")
        left_frame.grid(row=1, column=1, sticky=tk.NSEW)

        row = 0
        tk.Label(left_frame, text="Name of test (optional)").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._test_name = TextEntry(left_frame)
        self._test_name.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._test_name)

        row += 1
        row = headline(left_frame, "[Defender]", row)

        row += 1
        tk.Label(left_frame, text="Choose a ship").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._ship_select_var = tk.StringVar(self)
        self._ship_select_var.set("no data yet")
        self._ship_select = tk.OptionMenu(left_frame, self._ship_select_var, "", command=self._ship_select_command)
        self._ship_select.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)

        row += 1
        tk.Label(left_frame, text="Class of shield generator").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._sg_class_slider = tk.Scale(left_frame, from_=1, to=8, orient=tk.HORIZONTAL, length=175, takefocus=True,
                                         command=self._set_shield_class_command)
        self._sg_class_slider.config(state=tk.DISABLED)
        self._sg_class_slider.grid(row=row, column=1, sticky=tk.E, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._sg_class_slider)

        row += 1
        tk.Label(left_frame, text="Number of boosters").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._booster_slider = tk.Scale(left_frame, from_=0, to=8, orient=tk.HORIZONTAL, length=175, takefocus=True,
                                        command=self._set_number_of_boosters_command)
        self._booster_slider.set(7)
        self._booster_slider.grid(row=row, column=1, sticky=tk.E, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._booster_slider)

        row += 1
        tk.Label(left_frame, text="Shield cell bank hit point pool").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._scb_hitpoints = IntegerEntry(left_frame)
        self._scb_hitpoints.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._scb_hitpoints)

        row += 1
        tk.Label(left_frame, text="Guardian shield reinforcement hit point pool").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._guardian_hitpoints = IntegerEntry(left_frame)
        self._guardian_hitpoints.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._guardian_hitpoints)

        row += 1
        tk.Label(left_frame, text="Access to prismatic shields").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._usePrismatic = tk.IntVar(self)
        self._usePrismatic.set(1)
        self._prismatic_check_button = tk.Checkbutton(left_frame, variable=self._usePrismatic, command=self._set_prismatic_shields_command)
        self._prismatic_check_button.grid(row=row, column=1, sticky=tk.W, pady=padding)
        self._lockable_ui_elements.append(self._prismatic_check_button)

        row += 1
        row = headline(left_frame, "[Attacker]", row)

        row += 1
        tk.Label(left_frame, text="Explosive DPS").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._explosive_dps_entry = IntegerEntry(left_frame)
        self._explosive_dps_entry.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._explosive_dps_entry)

        row += 1
        tk.Label(left_frame, text="Kinetic DPS").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._kinetic_dps_entry = IntegerEntry(left_frame)
        self._kinetic_dps_entry.insert(0, 50)
        self._kinetic_dps_entry.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._kinetic_dps_entry)

        row += 1
        tk.Label(left_frame, text="Thermal DPS").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._thermal_dps_entry = IntegerEntry(left_frame)
        self._thermal_dps_entry.insert(0, 50)
        self._thermal_dps_entry.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._thermal_dps_entry)

        row += 1
        tk.Label(left_frame, text="Absolute DPS (Thargoids)").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._absolute_dps_entry = IntegerEntry(left_frame)
        self._absolute_dps_entry.insert(0, 10)
        self._absolute_dps_entry.grid(row=row, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._absolute_dps_entry)

        row += 1
        tk.Label(left_frame, text="Damage effectiveness in %").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._effectiveness_slider = tk.Scale(left_frame, from_=1, to=100, orient=tk.HORIZONTAL, length=175, takefocus=True)
        self._effectiveness_slider.set(65)
        self._effectiveness_slider.grid(row=row, column=1, sticky=tk.E, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._effectiveness_slider)

        row += 1
        row = headline(left_frame, "[Misc]", row)

        row += 1
        tk.Label(left_frame, text="Use short list").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._use_short_list = tk.IntVar(self)
        self._use_short_list.set(1)
        self._use_short_list_check_button = tk.Checkbutton(left_frame, variable=self._use_short_list, command=self._set_short_list_command)
        self._use_short_list_check_button.grid(row=row, column=1, sticky=tk.W, pady=padding)
        self._lockable_ui_elements.append(self._use_short_list_check_button)

        row += 1
        tk.Label(left_frame, text="Preliminary filtering of shield generators\n"
                                  "(might not find the best loadout)", justify="left").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._use_filtering = tk.IntVar(self)
        self._use_filtering.set(0)
        self._use_filtering_check_button = tk.Checkbutton(left_frame, variable=self._use_filtering, command=self._set_filtering_command)
        self._use_filtering_check_button.grid(row=row, column=1, sticky=tk.W, pady=padding)
        self._lockable_ui_elements.append(self._use_filtering_check_button)

        row += 1
        tk.Label(left_frame, text="CPU cores to use").grid(row=row, column=0, sticky=tk.SW, padx=padding)
        self._cores_slider = tk.Scale(left_frame, from_=1, to=os.cpu_count(), orient=tk.HORIZONTAL, length=175, takefocus=True)
        self._cores_slider.set(os.cpu_count())
        self._cores_slider.grid(row=row, column=1, sticky=tk.E, padx=padding)
        self._lockable_ui_elements.append(self._cores_slider)

        row += 1
        tk.Label(left_frame, text="Shield loadouts to be tested", justify="left").grid(row=row, column=0, sticky=tk.SW, padx=padding, pady=padding)
        self._number_of_tests_label = tk.Label(left_frame, text="")
        self._number_of_tests_label.grid(row=row, column=1, sticky=tk.W, padx=padding, pady=padding)

        row += 1
        button_frame = tk.Frame(left_frame)
        button_frame.grid(row=row, columnspan=2, sticky=tk.NSEW, padx=padding, pady=padding)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        self._compute_button = tk.Button(button_frame, text="Compute best loadout", command=self._compute)
        self._compute_button.grid(row=0, column=0, sticky=tk.EW, padx=padding, pady=padding)
        self._lockable_ui_elements.append(self._compute_button)

        self._cancel_button = tk.Button(button_frame, text="       Cancel       ", command=self._cancel_command)
        self._cancel_button.grid(row=0, column=1, sticky=tk.EW, padx=padding, pady=padding)
        self._cancel_button.config(state=tk.DISABLED)
        #self._lockable_ui_elements.append(self._cancel_button)

        self._coriolis_button = tk.Button(button_frame, text=" Export to Coriolis ", command=self._open_coriolis_command)
        self._coriolis_button.grid(row=0, column=2, sticky=tk.E, padx=padding, pady=padding)
        self._coriolis_button.config(state=tk.DISABLED)
        #self._lockable_ui_elements.append(self._compute_button)

        row += 1
        self._progress_bar = ttk.Progressbar(left_frame, orient="horizontal", mode="determinate")
        self._progress_bar.grid(row=row, columnspan=2, sticky=tk.EW, padx=padding, pady=padding)
        self._progress_bar.config(value=0)

        # ---------------------------------------------------------------------------------------------------
        # right frame
        right_frame = tk.LabelFrame(self, borderwidth=1, text="Output")
        right_frame.grid(row=1, column=2, sticky=tk.NSEW)

        self._tab_parent = ttk.Notebook(right_frame)
        self._tab_parent.grid(row=0, column=0, padx=padding, pady=padding, sticky=tk.NSEW)
        self._tab_parent.rowconfigure(0, weight=1)
        self._tab_parent.columnconfigure(0, weight=1)
        self._tab_parent.bind(ShieldTesterUi.EVENT_TAB_CHANGED, self._event_tab_changed)
        # self._tab_parent.bind("<Button-3>", self._event_close_tab)  # do this when lock and unlocking UI

        quick_guide = scrolledtext.ScrolledText(self._tab_parent, height=27, width=85)
        quick_guide.insert(tk.END, f"\u2191 You can close this tab by {'pressing the middle mouse button' if sys.platform == 'darwin' else 'right clicking'}.")
        quick_guide.config(state=tk.DISABLED)
        self._tabs.setdefault(ShieldTesterUi.KEY_QUICK_GUIDE, TabData(tab=quick_guide))
        self._tab_parent.add(quick_guide, text=ShieldTesterUi.KEY_QUICK_GUIDE)

        # set behaviour for resizing
        self.rowconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        self._lock_ui_elements()
        self.after(100, self._load_data)
        self.after(120, self._load_quick_guide)

        def set_window_size():
            self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())

        self.after(200, set_window_size)

    def _add_tab(self, name: str) -> TabData:
        if name not in self._tabs:
            new_tab = scrolledtext.ScrolledText(self._tab_parent, height=27, width=85)
            new_tab.config(state=tk.DISABLED)
            self._tab_parent.add(new_tab, text=name)
            return self._tabs.setdefault(name, TabData(new_tab))

        return self._tabs[name]

    def _get_name_for_tab(self):
        """ Either use the entered test name or use the ship's name"""
        return self._test_name.get() if self._test_name.get() else self._test_case.ship.name

    def _cancel_command(self):
        t = threading.Thread(target=self._shield_tester.cancel)
        t.start()

    def _set_shield_class_command(self, value=""):
        if value:
            self._generate_new_loadouts(int(value))

    def _set_number_of_boosters_command(self, value=""):
        if self._test_case:
            self._test_case.number_of_boosters_to_test = int(value)
            self._update_number_of_tests_label()

    def _set_prismatic_shields_command(self):
        self._generate_new_loadouts()
        self._update_number_of_tests_label()

    def _set_filtering_command(self):
        self._update_number_of_tests_label()

    def _set_short_list_command(self):
        self._shield_tester.set_boosters_to_test(self._test_case, short_list=True if self._use_short_list.get() else False)
        self._update_number_of_tests_label()

    def _ship_select_command(self, value=None):
        if self._ship_select_var.get():
            test_case = self._shield_tester.select_ship(self._ship_select_var.get())
            if test_case:
                self._test_case = test_case
                slots = self._test_case.ship.utility_slots
                self._booster_slider.config(to=slots)
                self._booster_slider.set(slots)
                min_class, max_class = self._shield_tester.get_compatible_shield_generator_classes(test_case)
                self._sg_class_slider.config(from_=min_class, to=max_class)
                self._sg_class_slider.set(max_class)
                self._shield_tester.set_loadouts_for_class(self._test_case, max_class)

                # set attributes
                # commands of UI elements only trigger when their value changes
                self._test_case.number_of_boosters_to_test = slots
                self._generate_new_loadouts(max_class)
                self._set_short_list_command()

                self._update_number_of_tests_label()

    def _open_coriolis_command(self):
        data = self._tabs.get(self._active_tab_name, None)
        if data and data.test_result:
            webbrowser.open(self._shield_tester.get_coriolis_link(data.test_result.loadout))

    def _generate_new_loadouts(self, shield_class: int = 0):
        use_prismatics = True if self._usePrismatic.get() else False
        if shield_class == 0:
            shield_class = int(self._sg_class_slider.get())

        self._shield_tester.set_loadouts_for_class(self._test_case, module_class=shield_class, prismatics=use_prismatics)

    def _update_number_of_tests_label(self, prelim: int = None):
        use_prelim = self._use_filtering.get()
        if use_prelim:
            self._number_of_tests_label.config(text=f"{self._shield_tester.calculate_number_of_tests(self._test_case, ShieldTesterUi.PRELIMINARY_FILTERING):n}")
        else:
            self._number_of_tests_label.config(text=f"{self._shield_tester.calculate_number_of_tests(self._test_case):n}")

    def _load_quick_guide(self):
        if os.path.exists(QUICK_GUIDE_FILE):
            with open(QUICK_GUIDE_FILE, "r") as file:
                for line in file:
                    self._write_to_text_widget(line, ShieldTesterUi.KEY_QUICK_GUIDE)

    def _load_data(self):
        error_occurred = False
        try:
            self._shield_tester.load_data(DATA_FILE)
        except Exception as e:
            print(e)
            error_occurred = True

        if not error_occurred:
            self._unlock_ui_elements()
            ship_names = self._shield_tester.ship_names
            ship_names.sort()
            # refresh drop down menu
            self._ship_select["menu"].delete(0, tk.END)
            for ship_name in ship_names:
                # noinspection PyProtectedMember
                self._ship_select["menu"].add_command(label=ship_name, command=tk._setit(self._ship_select_var, ship_name, self._ship_select_command))
            if "Anaconda" in ship_names:
                self._ship_select_var.set("Anaconda")
            else:
                self._ship_select_var.set(ship_names[0])
            self._ship_select.config(takefocus=True)
            self._ship_select_command()

        else:
            if tk.messagebox.askretrycancel(
                    "No data", "Could not read JSON file.\nPlease place it in the same directory as this program.\n"
                    "Required: {data}".format(data=os.path.basename(DATA_FILE))):
                self._load_data()

    def _lock_ui_elements(self):
        for element in self._lockable_ui_elements:
            element.config(state=tk.DISABLED)
        self._tab_parent.unbind("<Button-3>")

    def _unlock_ui_elements(self):
        for element in self._lockable_ui_elements:
            element.config(state=tk.NORMAL)
        self._tab_parent.bind("<Button-3>", self._event_close_tab)

    def _event_tab_changed(self, event):
        selected_tab = event.widget.select()
        if selected_tab:
            self._active_tab_name = event.widget.tab(selected_tab, "text")
            data = self._tabs.get(self._active_tab_name, None)
            if data and data.test_result:
                self._coriolis_button.config(state=tk.NORMAL)
            else:
                self._coriolis_button.config(state=tk.DISABLED)

    def _event_close_tab(self, event):
        # noinspection PyProtectedMember
        clicked_tab = self._tab_parent.tk.call(self._tab_parent._w, "identify", "tab", event.x, event.y)
        if clicked_tab != "":
            tab_name = event.widget.tab(clicked_tab, "text")
            self._tab_parent.forget(clicked_tab)
            self._tabs.pop(tab_name)
        if len(self._tabs) == 0:
            self._coriolis_button.config(state=tk.DISABLED)

    def _event_process_output(self, event):
        if not self._message_queue.empty():
            self._write_to_text_widget(self._message_queue.get_nowait())

    def _event_progress_bar_step(self, event):
        if self._progress_bar:
            self._progress_bar.step()

    def _event_compute_cancelled(self, event):
        self._unlock_ui_elements()
        self._progress_bar.stop()
        self._write_to_text_widget("\n")
        self._write_to_text_widget("Cancelled")
        self._coriolis_button.config(state=tk.DISABLED)
        self._cancel_button.config(state=tk.DISABLED)

    def _event_compute_complete(self, event):
        self._unlock_ui_elements()
        self._progress_bar.stop()
        self._cancel_button.config(state=tk.DISABLED)

        data = self._tabs.get(self._active_tab_name)
        if data and data.test_result:
            self._write_to_text_widget("\n")
            self._write_to_text_widget(data.test_result.get_output_string())
            self._coriolis_button.config(state=tk.NORMAL)
            try:
                if not self._test_name.get():
                    self._shield_tester.write_log(self._test_case, data.test_result, data.test_result.loadout.ship_name, time_and_name=True)
                else:
                    self._shield_tester.write_log(self._test_case, data.test_result, self._test_name.get())
            except Exception as e:
                print("Error writing logfile")
                print(e)
                self.event_generate(self.EVENT_WARNING_WRITE_LOGFILE, when="tail")

    def _event_show_warning_logfile(self, event):
        messagebox.showwarning("Could not write logfile.", "Could not write logfile.")

    def _write_to_text_widget(self, text: str, widget_name: str = ""):
        if not widget_name:
            text_widget = self._tabs.get(self._active_tab_name, None)
        else:
            text_widget = self._tabs.get(widget_name, None)
        if text_widget and text_widget.tab:
            text_widget.tab.config(state=tk.NORMAL)
            text_widget.tab.insert(tk.END, text)
            text_widget.tab.config(state=tk.DISABLED)

    def _compute_callback(self, value: int):
        # ensure thread safe communication
        if value == st.ShieldTester.CALLBACK_STEP:
            self.event_generate(self.EVENT_PROGRESS_BAR_STEP, when="tail")
        elif value == st.ShieldTester.CALLBACK_MESSAGE:
            self.event_generate(self.EVENT_COMPUTE_OUTPUT, when="tail")
        elif value == st.ShieldTester.CALLBACK_CANCELLED:
            self.event_generate(self.EVENT_COMPUTE_CANCELLED, when="tail")

    def _compute_background(self, use_prelim: int = 0):
        data = self._tabs.get(self._active_tab_name)
        test_case = copy.deepcopy(self._test_case)
        if use_prelim:
            test_results = self._shield_tester.compute(test_case, callback=self._compute_callback, message_queue=self._message_queue,
                                                       prelim=ShieldTesterUi.PRELIMINARY_FILTERING)
        else:
            test_results = self._shield_tester.compute(test_case, callback=self._compute_callback, message_queue=self._message_queue)
        if data:
            data.test_result = test_results
        self.event_generate(self.EVENT_COMPUTE_COMPLETE, when="tail")

    def _compute(self):
        self._lock_ui_elements()
        self._coriolis_button.config(state=tk.DISABLED)

        # clear old test data
        self._active_tab_name = self._get_name_for_tab()
        tab_data = self._add_tab(self._active_tab_name)
        self._tab_parent.select(tab_data.tab)
        tab_data.tab.config(state=tk.NORMAL)
        tab_data.tab.delete("1.0", tk.END)
        tab_data.tab.config(state=tk.DISABLED)
        tab_data.test_result = None

        # get data from UI
        self._test_case.number_of_boosters_to_test = self._booster_slider.get()
        self._test_case.damage_effectiveness = self._effectiveness_slider.get() / 100.0
        self._test_case.scb_hitpoints = int(self._scb_hitpoints.get()) if self._scb_hitpoints.get() else 0
        self._test_case.guardian_hitpoints = int(self._guardian_hitpoints.get()) if self._guardian_hitpoints.get() else 0
        self._test_case.explosive_dps = int(self._explosive_dps_entry.get()) if self._explosive_dps_entry.get() else 0
        self._test_case.kinetic_dps = int(self._kinetic_dps_entry.get()) if self._kinetic_dps_entry.get() else 0
        self._test_case.thermal_dps = int(self._thermal_dps_entry.get()) if self._thermal_dps_entry.get() else 0
        self._test_case.absolute_dps = int(self._absolute_dps_entry.get()) if self._absolute_dps_entry.get() else 0
        self._shield_tester.cpu_cores = self._cores_slider.get()
        self._shield_tester.use_prismatics = True if self._usePrismatic.get() else False

        use_prelim = self._use_filtering.get()
        if use_prelim:
            steps = int(self._shield_tester.calculate_number_of_tests(self._test_case, ShieldTesterUi.PRELIMINARY_FILTERING)
                        / ShieldTesterUi.PRELIMINARY_FILTERING
                        / st.ShieldTester.MP_CHUNK_SIZE) + 1
        else:
            steps = int(self._shield_tester.calculate_number_of_tests(self._test_case)
                        / len(self._test_case.loadout_list)
                        / st.ShieldTester.MP_CHUNK_SIZE) + 1
        self._progress_bar.config(maximum=steps)

        self._write_to_text_widget(self._test_case.get_output_string())
        self._write_to_text_widget("\n")

        self._cancel_button.config(state=tk.NORMAL)
        t = threading.Thread(target=self._compute_background, args=(use_prelim,))
        t.start()


def main():
    locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
    shield_tester = ShieldTesterUi()
    shield_tester.mainloop()


if __name__ == '__main__':
    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()
    main()
