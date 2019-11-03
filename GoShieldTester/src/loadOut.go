package main

type loadOutStatT struct {
	hitPoints           float64
	regenRate           float64
	explosiveResistance float64
	kineticResistance   float64
	thermalResistance   float64
}

func getLoadoutStats(shieldGeneratorVariant generatorT, shieldBoosterLoadout []int, boosterVariants []boosterT) loadOutStatT {

	var expModifier float64 = 1.0
	var kinModifier float64 = 1.0
	var thermModifier float64 = 1.0
	var hitPointBonus float64 = 0.0

	var expRes, kinRes, thermRes, hitPoints float64

	// Compute non diminishing returns modifiers
	for _, booster := range shieldBoosterLoadout {

		var boosterVariantStats = boosterVariants[booster-1]

		expModifier = expModifier * (1 - boosterVariantStats.expResBonus)
		kinModifier = kinModifier * (1 - boosterVariantStats.kinResBonus)
		thermModifier = thermModifier * (1 - boosterVariantStats.thermResBonus)
		hitPointBonus = hitPointBonus + boosterVariantStats.shieldStrengthBonus
	}

	// Compensate for diminishing returns
	if expModifier < 0.7 {
		expModifier = 0.7 - (0.7-expModifier)/2
	}

	if kinModifier < 0.7 {
		kinModifier = 0.7 - (0.7-kinModifier)/2
	}

	if thermModifier < 0.7 {
		thermModifier = 0.7 - (0.7-thermModifier)/2
	}

	// Compute final Resistance
	expRes = 1 - ((1 - shieldGeneratorVariant.expRes) * expModifier)
	kinRes = 1 - ((1 - shieldGeneratorVariant.kinRes) * kinModifier)
	thermRes = 1 - ((1 - shieldGeneratorVariant.thermRes) * thermModifier)

	// Compute final Hitpoints
	hitPoints = (1+hitPointBonus)*shieldGeneratorVariant.shieldStrength + config.scbHitPoint + config.guardianShieldHitPoint

	return loadOutStatT{
		hitPoints:           hitPoints,
		regenRate:           shieldGeneratorVariant.regenRate,
		explosiveResistance: expRes,
		kineticResistance:   kinRes,
		thermalResistance:   thermRes,
	}
}
