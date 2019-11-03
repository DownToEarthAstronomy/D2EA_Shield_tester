package main

type configT struct {
	shieldBoosterCount                                int
	explosiveDPS, kineticDPS, thermalDPS, absoluteDPS float64
	damageEffectiveness                               float64
	scbHitPoint, guardianShieldHitPoint               float64
	boosterFile, generatorFile                        string
}

var config configT

func loadConfig() configT {

	config = configT{
		shieldBoosterCount:     2,
		explosiveDPS:           33,
		kineticDPS:             33,
		thermalDPS:             33,
		absoluteDPS:            0,
		damageEffectiveness:    0.65, // 1 = always taking damage; 0.5 = Taking damage 50% of the time
		scbHitPoint:            0,
		guardianShieldHitPoint: 0,
		boosterFile:            "../ShieldBoosterVariants_short.csv",
		generatorFile:          "../shieldGeneratorVariants.csv",
	}

	return config
}
