package main

import "fmt"

func testCase(shieldGenerator generatorT, boosterVariants []boosterT, shieldBoosterLoadoutList [][]int) resultT {
	bestTestCase := resultT{
		survivalTime: 0.0,
	}

	for _, shieldBoosterLoadout := range shieldBoosterLoadoutList {
		// Calculate the resistance, regen-rate and hitpoints of the current loadout
		var loadoutStats = getLoadoutStats(shieldGenerator, shieldBoosterLoadout, boosterVariants)

		var actualDPS float64 = config.damageEffectiveness*
			(config.explosiveDPS*(1-loadoutStats.explosiveResistance)+
				config.kineticDPS*(1-loadoutStats.kineticResistance)+
				config.thermalDPS*(1-loadoutStats.thermalResistance)+
				config.absoluteDPS) - loadoutStats.regenRate*(1-config.damageEffectiveness)

		var survivalTime float64 = loadoutStats.hitPoints / actualDPS

		if survivalTime > bestTestCase.survivalTime {
			bestTestCase.shieldGenerator = shieldGenerator
			bestTestCase.shieldBoosterLoadout = shieldBoosterLoadout
			bestTestCase.loadOutStats = loadoutStats
			bestTestCase.survivalTime = survivalTime
		}
	}

	return bestTestCase
}

func testGenerators(generators []generatorT, boosterVariants []boosterT, boosterList [][]int) resultT {
	bestResult := resultT{survivalTime: 0.0}

	fmt.Print("Tests [")

	for _, generator := range generators {
		fmt.Print("#")

		result := testCase(generator, boosterVariants, boosterList)
		if result.survivalTime > bestResult.survivalTime {
			bestResult = result
		}
	}

	fmt.Println("]")

	return bestResult
}
