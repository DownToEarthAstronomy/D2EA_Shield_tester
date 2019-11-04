package main

type configT struct {
	shieldBoosterCount                                int
	prismatics                                        bool
	explosiveDPS, kineticDPS, thermalDPS, absoluteDPS float64
	damageEffectiveness                               float64
	scbHitPoint, guardianShieldHitPoint               float64
	boosterFile, generatorFile                        string
}

var config configT

func loadConfig() configT {

	config = configT{
		shieldBoosterCount:     2,
		prismatics:             true,
		explosiveDPS:           0,
		kineticDPS:             0,
		thermalDPS:             0,
		absoluteDPS:            200,
		damageEffectiveness:    0.65, // 1 = always taking damage; 0.5 = Taking damage 50% of the time
		scbHitPoint:            0,
		guardianShieldHitPoint: 0,
		boosterFile:            "../ShieldBoosterVariants_short.csv",
		generatorFile:          "../ShieldGeneratorVariants.csv",
	}

	return config
}
