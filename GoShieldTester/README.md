# Introduction

This is the Go port of Down To Earth Astronomy's Elite Dangerous Shield Tester

D2EA's original Powershell version can be found here:
https://github.com/DownToEarthAstronomy/D2EA_Shield_tester

# Abstract

Many of us run many different ships, with many stored shield generators and modules with the different engineering. 

How do you choose the best loadout? Before this tool, it was the usual metas, which undeniably work. However, there's 
so many combinations, it's hard to say for sure if the meta for your ship and combat or defence scenario is the best 
alternative. 

We need a way of figuring out the best combination of generator and shield boosters for situational
scenarios. The original Powershell version is fairly slow, and thus might discourage someone from 
running the tool when they change ships or combat scenarios. 

For example, you're mining and looking for maximum survivability, or you're fighting Thargoid Interceptors, and looking
for maximum absolute damage protection. Or you're fighting NPCs in combat zones. All of these require slightly different
loadouts. 

This tool helps you quickly find the best loadout for your scenario. Even the lengthiest run of the Go port with
8 boosters and all booster variants takes less than 5 seconds on a modern i7 processor, and most common ship loadouts
take less than a second. 

# Building

Building the tool is really simple:

```
go build .
```

# Running

```
go run . 
```

After building, you can also invoke it like any other command line tool. 

```
> .\GoShieldTester -h
Down to Earth Astronomy's ShieldTester (https://github.com/DownToEarthAstronomy/D2EA_Shield_tester)
Go port by Andrew van der Stock, vanderaj@gmail.com

Usage of C:\Users\vande\GitHub\D2EA_Shield_tester\GoShieldTester\GoShieldTester.exe:
  -adps float
        Absolute DPS percentage (use 100 for Thargoids)
  -boosters int
        Number of Shield Boosters (default 2)
  -cucumber
        Useful Cucumber defaults
  -dmg float
        Damage effectiveness (use 0.1 for PvE, 0.5 for PvP, and 0.65 for Thargoids) (default 0.65)
  -edps float
        Explosive DPS percentage (use 0 for Thargoids) (default 33)
  -fullboost
        Load the full booster list
  -gshp float
        Guardian HitPoints (default 0)
  -kdps float
        Kinetic DPS percentage (use 0 for Thargoids) (default 33)
  -scb float
        SCB HitPoints (default 0)
  -tdps float
        Thermal DPS percentage (use 0 for Thargoids) (default 33)
  -thargoid
        Useful Thargoid defaults
```

# Usage

The Go port has a number of command line flags to override the default configuration. 

## Scenario flags 

Included are two scenarios loadout configurations to aid in testing the tool, but also generate useful loadouts for the discerning
Commander who might be fighting Thargoids or D2EA. 

Disabling prismatic shields allows for users who have yet to unlock prismatics to see what their next best alternative might be. 

```
  -cucumber
        Useful Cucumber defaults
  -thargoid
        Useful Thargoid defaults
  -noprismatics
        Disable prismatic shields 
```

Those who have watched the video will recognize the defaults in use. As these override the defaults, using the other DPS flags 
doesn't work. This is a known limitation that might be fixed in a future version.

## Full booster variants

For speed's sake, the original Powershell version excluded a few booster alternatives. This is not necessary for the 
Go version, but for compatibility's sake, it is the default choice. If you want to test all boosters, use the following flag:

```
  -fullboost
        Load the full booster list
```

## Number of boosters

Choose between 1 and 8 boosters to fill up those utility slots. 

```
  -boosters int
        Number of Shield Boosters (default 2)
```

## Damage Effectiveness

Damage effectiveness is the percentage of time you'll be taking fire. Something like a PvP Commander who is using turrets might
be able to hit you say 65% of the time, so use 0.65. A Cmdr using fixed plasma or rail weapons will hit you may be 10% of the time, allowing 
you to regenerate your shields between hits. Obviously the latter really hurt, so ... really up that DPS when you lower this score.

```
  -dmg float
        Damage effectiveness (use 0.1 for PvP with fixed, 0.5 for PvE or PvP with gimballs, and 0.25 for Thargoids) (default 0.5)
```

## Damage Per Second Flags

These are expressed in percentages. A well balanced build should try to make these add up to 100%. Of course you can make these add up to 
anything, but it may affect your survivability and ability to take all forms of damage because the game and this tool may not necessarily
work out modifiers in the same way above 100%. 

```
  -adps float
        Absolute DPS percentage (use 100 for Thargoids)
  -edps float
        Explosive DPS percentage (use 0 for Thargoids) (default 33)
  -kdps float
        Kinetic DPS percentage (use 0 for Thargoids) (default 33)
  -tdps float
        Thermal DPS percentage (use 0 for Thargoids) (default 33)
```

## SCBs

If you have SCBs, include their regen hitpoints here. As you can only use one at a time, only include one. 

```
  -scb float
        SCB HitPoints (default 0)
```

## Guardian Shield Boosters

If you have Guardian Shield Boosters, include their combined hitpoints here. 

```
  -gshp float
        Guardian HitPoints (default 0)
```
