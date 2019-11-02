package main

type configT struct {
	ShieldBoosterCount                                int
	ExplosiveDPS, KineticDPS, ThermalDPS, AbsoluteDPS float64
	DamageEffectiveness                               float64
	SCBHitPoint, GuardianShieldHitPoint               float64
	boosterFile, generatorFile                        string
}

var config configT

func loadConfig() configT {

	config = configT{
		ShieldBoosterCount:     4,
		ExplosiveDPS:           33,
		KineticDPS:             33,
		ThermalDPS:             33,
		AbsoluteDPS:            0,
		DamageEffectiveness:    0.65, // 1 = always taking damage; 0.5 = Taking damage 50% of the time
		SCBHitPoint:            0,
		GuardianShieldHitPoint: 0,
		boosterFile:            "../../ShieldBoosterVariants_short.csv",
		generatorFile:          "../../ShieldGeneratorVariants.csv",
	}

	return config
}
