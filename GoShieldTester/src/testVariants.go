package main

import "fmt"

func testCase(ShieldGenerator generatorT, boosterVariants []boosterT, ShieldBoosterLoadoutList [][]int, config configT) resultT {
	bestResult := resultT{survivalTime: 0.0}

	for _, ShieldBoosterLoadout := range ShieldBoosterLoadoutList {
		// Calculate the resistance, regen-rate and hitpoints of the current loadout
		var LoadoutStats = getLoadoutStats(ShieldGenerator, ShieldBoosterLoadout, boosterVariants)

		var ActualDPS float64 = config.DamageEffectiveness*(config.ExplosiveDPS*(1-LoadoutStats.ExplosiveResistance)+
			config.KineticDPS*(1-LoadoutStats.KineticResistance)+
			config.ThermalDPS*(1-LoadoutStats.ThermalResistance)+config.AbsoluteDPS) -
			LoadoutStats.RegenRate*(1-config.DamageEffectiveness)
		var SurvivalTime float64 = LoadoutStats.HitPoints / ActualDPS

		if SurvivalTime > bestResult.survivalTime {
			bestResult.shieldGenerator = ShieldGenerator
			bestResult.shieldBoosterLoadout = setLoadout(config.ShieldBoosterCount, ShieldBoosterLoadout)
			bestResult.loadOutStats = LoadoutStats
			bestResult.survivalTime = SurvivalTime
		}
	}

	return bestResult
}

func testGenerators(generators []generatorT, boosterVariants []boosterT, boosterList [][]int) resultT {
	var result resultT
	bestResult := resultT{survivalTime: 0.0}

	fmt.Println("Total tests [", len(generators), "]")

	fmt.Print("[")

	for _, generator := range generators {
		fmt.Print("#")

		result = testCase(generator, boosterVariants, boosterList, config)
		if result.survivalTime > bestResult.survivalTime {
			bestResult = result
		}
	}

	fmt.Println("]")

	return bestResult
}
