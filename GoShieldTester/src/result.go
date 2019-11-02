package main

import (
	"fmt"
)

type resultT struct {
	shieldGenerator      generatorT
	shieldBoosterLoadout loadOutT
	loadOutStats         loadOutStatT
	survivalTime         float64
}

func showResults(bestResult resultT, boosterVariants []boosterT) {

	var ShieldGenerator = bestResult.shieldGenerator

	var ShieldName = ShieldGenerator.Name
	var ShieldGeneratorEngineering = ShieldGenerator.Engineering
	var ShieldGeneratorExperimental = ShieldGenerator.Experimental

	fmt.Println()
	fmt.Println("---- TEST SETUP ----")
	fmt.Println("Shield Booster Count: [", config.ShieldBoosterCount, "]")
	fmt.Println("Shield Cell Bank Hit Point Pool: [", config.SCBHitPoint, "]")
	fmt.Println("Guardian Shield Reinforcement Hit Point Pool: [", config.GuardianShieldHitPoint, "]")
	fmt.Println("Explosive DPS: [", config.ExplosiveDPS, "]")
	fmt.Println("Kinetic DPS: [", config.KineticDPS, "]")
	fmt.Println("Thermal DPS: [", config.ThermalDPS, "]")
	fmt.Println("Absolute DPS: [", config.AbsoluteDPS, "]")
	fmt.Println("Damage Effectiveness:", config.DamageEffectiveness, "]")

	fmt.Println()
	fmt.Println("---- TEST RESULTS ----")
	fmt.Println("Survival Time [s]: [", bestResult.survivalTime, "]")
	fmt.Println("Shield Generator: [", ShieldName, "] - [", ShieldGeneratorEngineering, "] - [", ShieldGeneratorExperimental, "]")
	fmt.Println("Shield boosters:")

	var bestLoadOutStats = bestResult.loadOutStats
	var bestBoosterLoadout = bestResult.shieldBoosterLoadout

	for _, booster := range bestBoosterLoadout.utilitySlots {
		var oBooster = boosterVariants[booster-1]
		var ShieldBoosterEngineering = oBooster.Engineering
		var ShieldBoosterExperimental = oBooster.Experimental
		fmt.Println("[", ShieldBoosterEngineering, "] - [", ShieldBoosterExperimental, "]")
	}

	fmt.Println()

	fmt.Printf("Shield Hitpoints:     %.1f hp\n", bestLoadOutStats.HitPoints)
	fmt.Printf("Shield Regen:         %.2f hp/s\n", bestLoadOutStats.RegenRate)
	fmt.Printf("Explosive Resistance: %.2f%%\n", bestLoadOutStats.ExplosiveResistance*100)
	fmt.Printf("Kinetic Resistance:   %.2f%%\n", bestLoadOutStats.KineticResistance*100)
	fmt.Printf("Thermal Resistance:   %.2f%%\n", bestLoadOutStats.ThermalResistance*100)
}
