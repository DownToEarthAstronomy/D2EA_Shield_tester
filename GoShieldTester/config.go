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
		shieldBoosterCount:     3,    // 1-4 = small ships (2 typical), 2-6 = medium ships (4 typical), 4-8 = large ships (6-7 typical)
		prismatics:             true, // do you have prismatics unlocked?
		explosiveDPS:           0,    // missles
		kineticDPS:             33,   // cannons and missles
		thermalDPS:             33,   // laser weapons
		absoluteDPS:            0,    // 0 for most NPCs except Thargoids, 100 for a Cyclops, 150 for a Basilisk, 200 for a Hydra
		damageEffectiveness:    65,   // 25 = fixed weapons or single enemy, 65 = hazrez, 100% always being attacked
		scbHitPoint:            0,    // Using Corolis, enter the total in the Defense > Shield Sources > Cells green pie slice. e.g. 2 x 7A SCBs is 3621 MJ *2 = 7242 MJ
		guardianShieldHitPoint: 0,    // Using Corolis, enter the total in the Defense > Shield Sources > Shield Additions yellow pie slice. e.g. 1 x 5D GSRB = 215 MJ
		boosterFile:            "../ShieldBoosterVariants.csv",
		generatorFile:          "../ShieldGeneratorVariants.csv",
	}

	return config
}
