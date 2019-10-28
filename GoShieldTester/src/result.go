package main

import "fmt"

type resultT struct {
	shieldGenerator      generatorT
	shieldBoosterLoadout []int
	loadOutStats         loadOutStatT
	survivalTime         float32
}

func showResults(bestResult resultT, boosters []boosterT) {

	var ShieldGenerator = bestResult.shieldGenerator

	var ShieldName = ShieldGenerator.Name
	var ShieldGeneratorEngineering = ShieldGenerator.Engineering
	var ShieldGeneratorExperimental = ShieldGenerator.Experimental

	fmt.Println()
	fmt.Println("---- TEST RESULTS ----")
	fmt.Println("Survival Time [s]: [", bestResult.survivalTime, "]")
	fmt.Println("Shield Generator: [", ShieldName, "] - [", ShieldGeneratorEngineering, "] - [", ShieldGeneratorExperimental, "]")
	fmt.Println("Shield Boosters:")

	var bestLoadOutStats = bestResult.loadOutStats
	var bestBoosterLoadout = bestResult.shieldBoosterLoadout

	for _, booster := range bestBoosterLoadout {
		var oBooster = boosters[booster]
		var ShieldBoosterEngineering = oBooster.Engineering
		var ShieldBoosterExperimental = oBooster.Experimental
		fmt.Println("[", ShieldBoosterEngineering, "] - [", ShieldBoosterExperimental, "]")
	}

	fmt.Println()

	fmt.Println("Shield Hitpoints: [", bestLoadOutStats.HitPoints, "]")
	fmt.Println("Shield Regen: [", bestLoadOutStats.RegenRate, " hp/s]")
	fmt.Println("ExplosivecResistance: [", bestLoadOutStats.ExplosiveResistance*100, "]")
	fmt.Println("Kinetic Resistance: [", bestLoadOutStats.KineticResistance*100, "]")
	fmt.Println("Thermal Resistance: [", bestLoadOutStats.ThermalResistance*100, "]")
}
