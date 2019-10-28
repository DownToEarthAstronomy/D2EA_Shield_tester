package main

type loadOutT struct {
	ID           int
	utilitySlots []int
}

type loadOutStatT struct {
	HitPoints           float32
	RegenRate           float32
	ExplosiveResistance float32
	KineticResistance   float32
	ThermalResistance   float32
}

func getLoadoutStats(ShieldGeneratorVariant generatorT, ShieldBoosterLoadout []int, boosters []boosterT) loadOutStatT {

	var ExpModifier float32 = 1.0
	var KinModifier float32 = 1.0
	var ThermModifier float32 = 1.0
	var HitPointBonus float32 = 0.0

	// Compute non diminishing returns modifiers

	for _, booster := range ShieldBoosterLoadout {

		var boosterStats = boosters[booster]

		ExpModifier = ExpModifier * (1 - boosterStats.ExpResBonus)
		KinModifier = KinModifier * (1 - boosterStats.KinResBonus)
		ThermModifier = ThermModifier * (1 - boosterStats.ThermResBonus)
		HitPointBonus = HitPointBonus + boosterStats.ShieldStrengthBonus
	}

	// Compensate for diminishing returns
	if ExpModifier < 0.7 {
		ExpModifier = 0.7 - (0.7-ExpModifier)/2
	}

	if KinModifier < 0.7 {
		KinModifier = 0.7 - (0.7-KinModifier)/2
	}

	if ThermModifier < 0.7 {
		ThermModifier = 0.7 - (0.7-ThermModifier)/2
	}

	// Compute final Resistance
	var finalExpRes = 1 - ((1 - ShieldGeneratorVariant.ExpRes) * ExpModifier)
	var finalKinRes = 1 - ((1 - ShieldGeneratorVariant.KinRes) * KinModifier)
	var finalThermRes = 1 - ((1 - ShieldGeneratorVariant.ThermRes) * ThermModifier)

	// Compute final Hitpoints
	var finalHitPoints = (1 + HitPointBonus) * ShieldGeneratorVariant.ShieldStrength

	var LoadoutStat = loadOutStatT{
		HitPoints:           finalHitPoints,
		RegenRate:           ShieldGeneratorVariant.RegenRate,
		ExplosiveResistance: finalExpRes,
		KineticResistance:   finalKinRes,
		ThermalResistance:   finalThermRes,
	}

	return LoadoutStat
}
