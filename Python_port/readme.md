# Shield Tester (Python Version)
This is an implementation in Python 3 of [Down to Earth Astronomy's](https://github.com/DownToEarthAstronomy/D2EA_Shield_tester) Power Shell script.

You can find pre-compiled executables at [Thurion's Fork](https://github.com/Thurion/D2EA_Shield_tester/releases) if you don't want to run it from source. Feel free to open an issue for bugs or feature requests for the Python version over there.

## Abstract
Many of us run many different ships, with many stored shield generators and modules with many forms of engineering. It might be tempting to just put on Heavy Duty / Deep plating, but is that really the best alternative? How do you choose the best loadout? 

Before D2EA's shield tester tool, it was the usual metas, which undeniably work. However, there's so many combinations, it's hard to say for sure if the meta for your ship and combat or defence scenario is the best alternative. 

We need a way of figuring out the best combination of generator and shield boosters for situational scenarios. For example, you might want to change between mining to fighting Thargoid Interceptors or NPCs in combat zones. All of three scenarios require slightly different loadouts. 

### Why a Python version? 
tl;dr: Speed. Nothing else. The other versions work just fine. 

The original Powershell version is groundbreaking research, but is fairly slow, and thus might discourage some from running the tool when they change ships or combat scenarios. 

The multi-threaded Python port is many times faster per CPU thread. It might not be as fast as the Go version but it's fast enough to run any amount of shield boosters within a reasonable time.

### Improvements to these tools
In a [comment](https://www.youtube.com/watch?v=87DMWz8IeEE&lc=Ugz-fl387Mi0ePTFCZ94AaABAg) to the original D2EA video, Cmdr Kaethena listed a few limitations and scenarios that you should read to understand that these tools are a good starting point, but possibly not the ending point for your shield loadouts. There are a lot of situations where a more generalist loadout might help you more than a max survivability loadout from this tool. YMMV. 

## How to use

![](interface.png)

### Name of test

It is possible to give the test run a name. This will determine the name of the log file and tab in the interface. All tests with the same chosen name will be written into the same file. If no name is specified, the testes ship name followed by the current time stamp will be used (i.e. Anaconda 2019-11-16 23.04.23.txt).\
Because this affects the file name and not every character is allowed for a file name, only letters, numbers, and `,`, `.`, `_`, `-` including spaces are permitted. 

### Defender
This section describes settings related to the defending ship.

#### Class of shield generator
In case you don't want to fit the biggest possible shield and go for a smaller one, select a different class (classes are 1 - 8). The rating will always be A or C for bi-weaves.\
However, only shield classes that can actually be fitted can be selected. The interface handles this automatically.

#### Number of boosters
Choose between 0 and the maximum your ship can use (max 8) to fill up those utility slots. Like with the class for the shield generator, the porgram automatically won't let you choose invalid setups.

#### Shield cell bank (SCBs) hitpoint pool
If you have SCBs, include their regen hitpoints here. Keep in mind that you can only use one at a time. Which means that if the fight is too short, you won't be able to use all SCBs. And don't forget that they will increase your heat by a lot which is not simulated by this tool.

#### Guardian shield reinforcement hitpoint pool
If you have Guardian Shield Reinforcement Packages, include their combined hitpoints here. 

#### Access to prismatic shields
There is a checkbox you can uncheck if you don't want prismatic shields to be taken into consideration when running tests.

### Attacker
This section describes settings related to the attacking ship.

#### Damage per second
These are expressed in incoming damage per second per type. It is not easy to come up with meaningful values. One thing you could do is to plan a ship on Coriolis and plug those DPS stats into the tool.

#### Damage effectiveness
Damage effectiveness is the percentage of time you'll be taking fire. Something like a PvP Commander who is using turrets might
be able to hit you say 65% of the time. A Cmdr using fixed plasma or rail weapons will hit you may be 10% of the time, allowing 
you to regenerate your shields between hits. Obviously the latter really hurt, so ... really up that DPS when you lower this score.

### Misc
This section describes some settings that affect performance of the calculations.

#### Use short list
The short list contains only 12 instead of 20 items. That makes the calculations much faster with the disadvantage of not having any explosive resistance focused boosters taken into account.

#### CPU cores to use
Using more cores can speed up the program by a considerable amount.

#### Buttons
When you are ready to go, press `Compute best loadout`. As soon as the calculations start, the `Cancel`button will become available. This can be really helpful in case you started a test with almost 100 million loadouts on just 1 core.

Once the results become available, you can press the `Export to Coriolis` button to open the test result's ship loadout. The shield generator will always be fitted into the highest class slot even if you chose a smaller one. Just drag and drop it on Coriolis where you want to have it. The itnernal modules will be non-engineered default ones.\
Import from Coriolis is not available at this time.

### Output
Each unique name of a test run will have its own tab but the output will be cleared when a new test is started with the same name. You will have all your results in the log files in case you need to look up something.\
When you don't fill in a name, the tab name will be the same as the ship (e.g. Anaconda).

You can close tabs by right clicking it. However, on Linux or Mac the button might be a different one.

## Information for programmers
You can use the program without an interface by importing the module `shield_tester`. Here is a working but probably incomplete example:
```python
import shield_tester as st

def main():
    tester = st.ShieldTester()
    tester.load_data("data.json")

    # get a list of ships and select one
    print(tester.ship_names)
    if tester.select_ship("Anaconda"):
        print("Anaconda selected")
    else:
        print(":(")
        return

    # get a new test case
    test_case = tester.get_test_case()

    # get some information
    print("Number of boosters: {}".format(test_case.ship.utility_slots))
    # can call without test_case, then internally stored test_case will be used
    min_class, max_class = tester.get_compatible_shield_generator_classes(test_case)
    print("Can fit class {min} to {max} shield generators".format(min=min_class, max=max_class))

    # set defender data
    test_case.number_of_boosters_to_test = 2
    # we don't have access to prismatic
    tester.use_prismatics = False  # this triggers the creation of a new list of shield generators
    # ... but we got some guardian boosters
    test_case.guardian_hitpoints = 420
    # we want a class 6 shield instead
    tester.create_loadouts_for_class(6, test_case=test_case)

    # set attacker data
    test_case.absolute_dps = 10
    test_case.thermal_dps = 50
    test_case.kinetic_dps = 50
    test_case.damage_effectiveness = 0.65

    # misc settings
    tester.cpu_cores = 2
    tester.use_short_list = True  # default value

    print("Number of tests: {}".format(tester.number_of_tests))

    # run the test:
    test_result = tester.compute(test_case)  # can add callback function and a simple queue for messages

    # what is our setup again?
    print(test_case.get_output_string())
    if test_result:
        # print the results, don't forget to add the guardian booster hitpoints. 
        # test_result has no access to the setup and those values are not stored
        print(test_result.get_output_string(test_case.guardian_hitpoints))

        # write the logfile
        tester.write_log(test_case, test_result, filename="my test", time_and_name=True, include_coriolis=True)

        # in case we want to do something with the coriolis link
        link_to_coriolis = tester.get_coriolis_link(test_result.best_loadout)
    else:
        print("Something went wrong...")

if __name__ == '__main__':
    main()
```