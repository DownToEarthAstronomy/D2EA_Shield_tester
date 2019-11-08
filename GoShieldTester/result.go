package main

import (
	"fmt"
	"time"
)

type resultT struct {
	shieldGenerator      generatorT
	shieldBoosterLoadout []int
	loadOutStats         loadOutStatT
	survivalTime         float64
}

func showResults(bestResult resultT, boosterVariants []boosterT, dur time.Duration) {

	var shieldGenerator = bestResult.shieldGenerator

	fmt.Println()
	fmt.Println("---- TEST SETUP ----")

	fmt.Println("Shield Booster Count: [", config.shieldBoosterCount, "]")
	fmt.Println("SCB Hit Point Pool:   [", config.scbHitPoint, "]")
	fmt.Println("Guardian Shield Reinforcement HP Pool: [", config.guardianShieldHitPoint, "]")
	fmt.Println("Prismatic Shields:    [", config.prismatics, "]")
	fmt.Println("Explosive DPS:        [", config.explosiveDPS, "]")
	fmt.Println("Kinetic DPS:          [", config.kineticDPS, "]")
	fmt.Println("Thermal DPS:          [", config.thermalDPS, "]")
	fmt.Println("Absolute DPS:         [", config.absoluteDPS, "]")
	fmt.Println("Damage Effectiveness: [", config.damageEffectiveness*100, "% ]")
	fmt.Println("Calculations took:    [", dur, "]")

	fmt.Println()
	fmt.Println("---- TEST RESULTS ----")

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

		fmt.Printf("Shield Hitpoints:     %.1f hp\n", bestLoadOutStats.hitPoints-config.scbHitPoint)
		fmt.Printf("Shield Regen:         %.2f hp/s\n", bestLoadOutStats.regenRate)
		fmt.Printf("Shield Regen Time (from 50%%): [%.2f s]\n", ((bestLoadOutStats.hitPoints - config.scbHitPoint) / (2 * bestLoadOutStats.regenRate)))
		fmt.Printf("Explosive Resistance: %.2f%%\n", bestLoadOutStats.explosiveResistance*100)
		fmt.Printf("Kinetic Resistance:   %.2f%%\n", bestLoadOutStats.kineticResistance*100)
		fmt.Printf("Thermal Resistance:   %.2f%%\n", bestLoadOutStats.thermalResistance*100)
	} else {
		fmt.Println("No test results. Please change DPS and/or damage effectiveness.")
	}
}
