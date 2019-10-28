package main

type configT struct {
	ShieldBoosterCount                                int
	ExplosiveDPS, KineticDPS, ThermalDPS, AbsoluteDPS float32
	DamageEffectiveness                               float32
	shortBoosterList                                  bool
}

func loadConfig() configT {

	config := configT{
		ShieldBoosterCount:  4,
		ExplosiveDPS:        0,
		KineticDPS:          0,
		ThermalDPS:          0,
		AbsoluteDPS:         100,
		DamageEffectiveness: 0.10, // 1 = always taking damage; 0.5 = Taking damage 50% of the time
		shortBoosterList:    true,
	}

	return config
}
