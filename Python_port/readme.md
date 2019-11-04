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

## Number of boosters

Choose between 0 and 8 boosters to fill up those utility slots. 

## Damage Effectiveness

Damage effectiveness is the percentage of time you'll be taking fire. Something like a PvP Commander who is using turrets might
be able to hit you say 65% of the time. A Cmdr using fixed plasma or rail weapons will hit you may be 10% of the time, allowing 
you to regenerate your shields between hits. Obviously the latter really hurt, so ... really up that DPS when you lower this score.

## Damage Per Second

These are expressed in incoming damage per second per type. This is not easy to come up with meaningful values. One thing you could do is to plan a ship on Coriolis and plug those DPS stats into the tool.

## SCBs

If you have SCBs, include their regen hitpoints here. Keep in mind that you can only use one at a time. Which means that if the fight is too short, you won't be able to use all SCBs. And don't forget that they will increase your heat by a lot which is not simulated by this tool.

## Guardian Shield Boosters

If you have Guardian Shield Reinforcement Packages, include their combined hitpoints here. 

## Python program specifics

![](interface.png)

For some reason multi-core computation might be slower when using the executable instead running from source.
This has an impact on the time it takes to run a simulation, therefore it might be better to run tests with up to 4 shield boosters on just 1 core.
The difference isn't huge but noticeable. Just test it and choose whatever works best for you.

### Access to Prismatic Shields

There is a checkbox you can uncheck if you don't want prismatic shields to be taken into consideration when running tests.
