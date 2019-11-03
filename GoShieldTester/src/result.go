package main

import (
	"fmt"
)

type resultT struct {
	shieldGenerator      generatorT
	shieldBoosterLoadout []int
	loadOutStats         loadOutStatT
	survivalTime         float64
}

func showResults(bestResult resultT, boosterVariants []boosterT) {

	var shieldGenerator = bestResult.shieldGenerator

	fmt.Println()
	fmt.Println("---- TEST SETUP ----")
	fmt.Println("Shield Booster Count: [", config.shieldBoosterCount, "]")
	fmt.Println("Shield Cell Bank Hit Point Pool: [", config.scbHitPoint, "]")
	fmt.Println("Guardian Shield Reinforcement Hit Point Pool: [", config.guardianShieldHitPoint, "]")
	fmt.Println("Explosive DPS: [", config.explosiveDPS, "]")
	fmt.Println("Kinetic DPS: [", config.kineticDPS, "]")
	fmt.Println("Thermal DPS: [", config.thermalDPS, "]")
	fmt.Println("Absolute DPS: [", config.absoluteDPS, "]")
	fmt.Println("Damage Effectiveness:", config.damageEffectiveness, "]")

	fmt.Println()
	fmt.Println("---- TEST RESULTS ----")
	fmt.Println("Survival Time [s]: [", bestResult.survivalTime, "]")
	fmt.Println("Shield Generator: [", shieldGenerator.name, "] - [", shieldGenerator.engineering, "] - [", shieldGenerator.experimental, "]")
	fmt.Println("Shield boosters:")

	var bestLoadOutStats = bestResult.loadOutStats

	for _, booster := range bestResult.shieldBoosterLoadout {
		var oBooster = boosterVariants[booster-1]
		fmt.Println("[", oBooster.engineering, "] - [", oBooster.experimental, "]")
	}

	fmt.Println()

	fmt.Printf("Shield Hitpoints:     %.1f hp\n", bestLoadOutStats.hitPoints-config.scbHitPoint)
	fmt.Printf("Shield Regen:         %.2f hp/s\n", bestLoadOutStats.regenRate)
	fmt.Printf("Explosive Resistance: %.2f%%\n", bestLoadOutStats.explosiveResistance*100)
	fmt.Printf("Kinetic Resistance:   %.2f%%\n", bestLoadOutStats.kineticResistance*100)
	fmt.Printf("Thermal Resistance:   %.2f%%\n", bestLoadOutStats.thermalResistance*100)
}
