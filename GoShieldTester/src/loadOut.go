package main

type loadOutT struct {
	slots        int
	utilitySlots []int
}

type loadOutStatT struct {
	HitPoints           float64
	RegenRate           float64
	ExplosiveResistance float64
	KineticResistance   float64
	ThermalResistance   float64
}

// Packs a set of booster IDs as an slice (array) of ints
func setLoadout(slots int, loadOutArray []int) loadOutT {

	newLoadOut := loadOutT{
		slots:        slots,
		utilitySlots: loadOutArray,
	}

	return newLoadOut
}

func getLoadoutStats(ShieldGeneratorVariant generatorT, ShieldBoosterLoadout []int, boosterVariants []boosterT) loadOutStatT {

	var ExpModifier float64 = 1.0
	var KinModifier float64 = 1.0
	var ThermModifier float64 = 1.0
	var HitPointBonus float64 = 0.0

	var finalExpRes, finalKinRes, finalThermRes, finalHitPoints float64

	// Compute non diminishing returns modifiers
	for _, booster := range ShieldBoosterLoadout {

		var boosterVariantstats = boosterVariants[booster-1]

		ExpModifier = ExpModifier * (1 - boosterVariantstats.ExpResBonus)
		KinModifier = KinModifier * (1 - boosterVariantstats.KinResBonus)
		ThermModifier = ThermModifier * (1 - boosterVariantstats.ThermResBonus)
		HitPointBonus = HitPointBonus + boosterVariantstats.ShieldStrengthBonus
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
	finalExpRes = 1 - ((1 - ShieldGeneratorVariant.ExpRes) * ExpModifier)
	finalKinRes = 1 - ((1 - ShieldGeneratorVariant.KinRes) * KinModifier)
	finalThermRes = 1 - ((1 - ShieldGeneratorVariant.ThermRes) * ThermModifier)

	// Compute final Hitpoints
	finalHitPoints = (1 + HitPointBonus) * ShieldGeneratorVariant.ShieldStrength

	var LoadoutStat = loadOutStatT{
		HitPoints:           finalHitPoints + config.SCBHitPoint + config.GuardianShieldHitPoint,
		RegenRate:           ShieldGeneratorVariant.RegenRate,
		ExplosiveResistance: finalExpRes,
		KineticResistance:   finalKinRes,
		ThermalResistance:   finalThermRes,
	}

	return LoadoutStat
}
