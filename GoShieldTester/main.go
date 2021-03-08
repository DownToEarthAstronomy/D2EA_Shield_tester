package main

/*
 * Go version of Down To Earth Astronomy's Shield Tester
 * Original version here:  https://github.com/DownToEarthAstronomy/D2EA_Shield_tester
 *
 * Go port by Andrew van der Stock, vanderaj@gmail.com
 *
 * Why this version? It's fast - about 15,500 times faster than the PowerShell version, so multi-threading is not necessary even with 8 utility slots and the full list
 */

import (
	"flag"
	"fmt"
	"time"
)

func processFlags() {
	flag.IntVar(&config.shieldBoosterCount, "boosters", config.shieldBoosterCount, "Number of Shield Boosters")
	flag.Float64Var(&config.explosiveDPS, "edps", config.explosiveDPS, "Explosive DPS percentage (use 0 for Thargoids)")
	flag.Float64Var(&config.kineticDPS, "kdps", config.kineticDPS, "Kinetic DPS percentage (use 0 for Thargoids)")
	flag.Float64Var(&config.thermalDPS, "tdps", config.thermalDPS, "Thermal DPS percentage (use 0 for Thargoids)")
	flag.Float64Var(&config.absoluteDPS, "adps", config.absoluteDPS, "Absolute DPS percentage (use 100 for Thargoids)")
	flag.Float64Var(&config.damageEffectiveness, "dmg", config.damageEffectiveness, "Damage effectiveness (25 for fixed weapons, 65 for hazrez PvP, 100 constant attack)")
	flag.Float64Var(&config.scbHitPoint, "scb", config.scbHitPoint, "SCB HitPoints (default 0)")
	flag.Float64Var(&config.guardianShieldHitPoint, "gshp", config.guardianShieldHitPoint, "Guardian HitPoints (default 0)")

	prismatics := flag.Bool("noprismatics", false, "Disable Prismatic shields")
	thargoid := flag.Bool("thargoid", false, "Useful Thargoid defaults")
	cucumber := flag.Bool("cucumber", false, "Useful Cucumber defaults")
	shortboost := flag.Bool("shortboost", false, "Load the short booster list")

	flag.Parse()
	config.damageEffectiveness = config.damageEffectiveness / 100 // convert from integer to percentage

	if config.shieldBoosterCount < 0 {
		fmt.Println("Can't have negative shield boosters, setting to 0")
		config.shieldBoosterCount = 0
	}

	if config.shieldBoosterCount > 8 {
		fmt.Println("No current ship has more than 8 shield boosters, setting to 8")
		config.shieldBoosterCount = 8
	}

	if *prismatics {
		fmt.Println("Disabling Prismatics")
		config.prismatics = false
	}

	if *thargoid && *cucumber {
		fmt.Println("D2EA is not a Thargoid, loading only Cucumber")
		*thargoid = false
	}

	if *shortboost {
		fmt.Println("Loading short booster list")
		config.boosterFile = "../ShieldBoosterVariants_short.csv"
	}

	if *cucumber {
		fmt.Println("Loading Cucumber defenses")
		config.explosiveDPS = 0
		config.kineticDPS = 83
		config.thermalDPS = 47
		config.absoluteDPS = 0
		config.damageEffectiveness = 0.25
		config.shieldBoosterCount = 7
	}
	if *thargoid {
		fmt.Println("Loading Thargoid defenses")
		config.explosiveDPS = 0
		config.kineticDPS = 0
		config.thermalDPS = 0
		config.absoluteDPS = 200
		config.damageEffectiveness = 0.10
		config.shieldBoosterCount = 7
	}
}

func main() {
	fmt.Println("Down to Earth Astronomy's ShieldTester (https://github.com/DownToEarthAstronomy/D2EA_Shield_tester)")
	fmt.Println("Go port by Andrew van der Stock, vanderaj@gmail.com")
	fmt.Println()

	config = loadConfig()

	processFlags()
	var baseShieldStrength, hullMass = loadShipStats(config.shipName)
	var generators = loadGenerators(baseShieldStrength, hullMass)
	var boosterVariants = loadboosterVariants()
	fmt.Printf("Loaded %d shields and %d boosters\n", len(generators), len(boosterVariants))

	var shieldBoosterLoadoutList = getBoosterLoadoutList(len(boosterVariants))

	startTime := time.Now()
	var result = testGenerators(generators, boosterVariants, shieldBoosterLoadoutList)
	endTime := time.Now()
	dur := endTime.Sub(startTime)

	fmt.Println("Tested", len(shieldBoosterLoadoutList)*len(generators), "loadouts in", dur)

	showResults(result, boosterVariants, dur)
}
