package main

import (
	"fmt"
	"time"
)

type resultT struct {
	shieldGenerator      generatorT   // shield generator
	shieldBoosterLoadout []int        // shield booster IDs
	loadOutStats         loadOutStatT // statistics of the overall generator + scb + guardian + booster loadout
	survivalTime         float64      // if negative, didn't die
}

func showResults(bestResult resultT, boosterVariants []boosterT, dur time.Duration) {

	var shieldGenerator = bestResult.shieldGenerator

	fmt.Println()
	fmt.Println("---- TEST SETUP ----")
	fmt.Println()

	fmt.Println("      Shield Boosters:", config.shieldBoosterCount)
	fmt.Printf("Shield Cell Bank Pool: %.1f Mj\n", config.scbHitPoint)
	fmt.Printf("  Guardian SR Package: %0.1f Mj\n", config.guardianShieldHitPoint)
	fmt.Println("    Prismatic Shields:", config.prismatics)
	fmt.Println("        Explosive DPS:", config.explosiveDPS)
	fmt.Println("          Kinetic DPS:", config.kineticDPS)
	fmt.Println("          Thermal DPS:", config.thermalDPS)
	fmt.Println("         Absolute DPS:", config.absoluteDPS)
	fmt.Printf(" Damage Effectiveness: %.1f%%\n", config.damageEffectiveness*100)
	fmt.Println("    Calculations took:", dur)

	fmt.Println()
	fmt.Println("---- TEST RESULTS ----")
	fmt.Println()

	if bestResult.survivalTime != 0 {

		if bestResult.survivalTime > 0 {
			fmt.Printf("Survival Time:        %.2f s\n", bestResult.survivalTime)
		} else {
			fmt.Println("Survival Time:       [ Didn't die ]")
		}
		fmt.Println("Shield Generator:    [", shieldGenerator.name, "] - [", shieldGenerator.engineering, "] - [", shieldGenerator.experimental, "]")

		var bestLoadOutStats = bestResult.loadOutStats

		i := 1
		for _, booster := range bestResult.shieldBoosterLoadout {
			var oBooster = boosterVariants[booster-1]
			fmt.Println("Shield Booster", i, "    [", oBooster.engineering, "] - [", oBooster.experimental, "]")
			i++
		}

		fmt.Println()

		fmt.Printf("Shield Hitpoints:     %.1f Mj\n", bestLoadOutStats.hitPoints-config.scbHitPoint)
		fmt.Printf("Shield Regen:         %.2f Mj/s (%.2fs from 50%%)\n", bestLoadOutStats.regenRate, ((bestLoadOutStats.hitPoints - config.scbHitPoint) / (2 * bestLoadOutStats.regenRate)))
		fmt.Printf("Explosive Resistance: %.2f%% (%.0f Mj)\n", (1.0-bestLoadOutStats.explosiveResistance)*100, bestLoadOutStats.hitPoints/bestLoadOutStats.explosiveResistance)
		fmt.Printf("Kinetic Resistance:   %.2f%% (%.0f Mj)\n", (1.0-bestLoadOutStats.kineticResistance)*100, bestLoadOutStats.hitPoints/bestLoadOutStats.kineticResistance)
		fmt.Printf("Thermal Resistance:   %.2f%% (%.0f Mj)\n", (1.0-bestLoadOutStats.thermalResistance)*100, bestLoadOutStats.hitPoints/bestLoadOutStats.thermalResistance)
	} else {
		fmt.Println("No test results. Please change DPS and/or damage effectiveness.")
	}
}
