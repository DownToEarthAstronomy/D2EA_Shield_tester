package main

import "fmt"

type generatorT struct {
	ID                                  int
	Name, Engineering, Experimental     string
	ShieldStrength                      float32
	RegenRate, ExpRes, KinRes, ThermRes float32
}

func loadGenerators() []generatorT {

	fmt.Println("Load shield generator variants")

	var generators = []generatorT{
		generatorT{
			1, "Normal", "Kinetic Resistance", "Fast Charge", 595, 2.1, 0.4925, 0.6955, -0.4007,
		},
		generatorT{
			2, "Normal", "Kinetic Resistance", "Multi-Weave", 595, 1.8, 0.515, 0.709, -0.3386,
		},
		generatorT{
			3, "Normal", "Kinetic Resistance", "Hi-Cap", 631, 1.8, 0.5, 0.7, -0.38,
		},
		generatorT{
			4, "Normal", "Kinetic Resistance", "Thermo Block", 577, 1.8, 0.5, 0.7, -0.2696,
		},
		generatorT{
			5, "Normal", "Kinetic Resistance", "Force Block", 577, 1.8, 0.5, 0.724, -0.38,
		},
		generatorT{
			6, "Normal", "Reinforced", "Fast Charge", 821, 2.1, 0.5762, 0.4915, -0.017,
		},
		generatorT{
			7, "Normal", "Reinforced", "Multi-Weave", 821, 1.8, 0.595, 0.514, 0.0281,
		},
		generatorT{
			8, "Normal", "Reinforced", "Hi-Cap", 870, 1.8, 0.5825, 0.499, -0.002,
		},
		generatorT{
			9, "Normal", "Reinforced", "Thermo Block", 796, 1.8, 0.5825, 0.499, 0.0782,
		},
		generatorT{
			10, "Normal", "Reinforced", "Force Block", 796, 1.8, 0.5825, 0.5391, -0.002,
		},
		generatorT{
			11, "Normal", "Thermal Resistance", "Fast Charge", 595, 2.1, 0.4925, 0.2692, 0.391,
		},
		generatorT{
			12, "Normal", "Thermal Resistance", "Multi-Weave", 595, 1.8, 0.515, 0.3016, 0.418,
		},
		generatorT{
			13, "Normal", "Thermal Resistance", "Hi-Cap", 631, 1.8, 0.5, 0.28, 0.4,
		},
		generatorT{
			14, "Normal", "Thermal Resistance", "Thermo Block", 577, 1.8, 0.5, 0.28, 0.448,
		},
		generatorT{
			15, "Normal", "Thermal Resistance", "Force Block", 577, 1.8, 0.5, 0.3376, 0.4,
		},
		generatorT{
			16, "Bi-Weave", "Kinetic Resistance", "Fast Charge", 490, 5.1, 0.4925, 0.6955, -0.4007,
		},
		generatorT{
			17, "Bi-Weave", "Kinetic Resistance", "Multi-Weave", 490, 4.4, 0.515, 0.709, -0.3386,
		},
		generatorT{
			18, "Bi-Weave", "Kinetic Resistance", "Hi-Cap", 519, 4.4, 0.5, 0.7, -0.38,
		},
		generatorT{
			19, "Bi-Weave", "Kinetic Resistance", "Thermo Block", 475, 4.4, 0.5, 0.7, -0.2696,
		},
		generatorT{
			20, "Bi-Weave", "Kinetic Resistance", "Force Block", 475, 4.4, 0.5, 0.724, -0.38,
		},
		generatorT{
			21, "Bi-Weave", "Reinforced", "Fast Charge", 676, 5.1, 0.5762, 0.4915, -0.017,
		},
		generatorT{
			22, "Bi-Weave", "Reinforced", "Multi-Weave", 676, 4.4, 0.595, 0.514, 0.0281,
		},
		generatorT{
			23, "Bi-Weave", "Reinforced", "Hi-Cap", 717, 4.4, 0.5825, 0.499, -0.002,
		},
		generatorT{
			24, "Bi-Weave", "Reinforced", "Thermo Block", 656, 4.4, 0.5825, 0.499, 0.0782,
		},
		generatorT{
			25, "Bi-Weave", "Reinforced", "Force Block", 656, 4.4, 0.5825, 0.5391, -0.002,
		},
		generatorT{
			26, "Bi-Weave", "Thermal Resistance", "Fast Charge", 490, 5.1, 0.4925, 0.2692, 0.391,
		},
		generatorT{
			27, "Bi-Weave", "Thermal Resistance", "Multi-Weave", 490, 4.4, 0.515, 0.3016, 0.418,
		},
		generatorT{
			28, "Bi-Weave", "Thermal Resistance", "Hi-Cap", 519, 4.4, 0.5, 0.28, 0.4,
		},
		generatorT{
			29, "Bi-Weave", "Thermal Resistance", "Thermo Block", 475, 4.4, 0.5, 0.28, 0.448,
		},
		generatorT{
			30, "Bi-Weave", "Thermal Resistance", "Force Block", 475, 4.4, 0.5, 0.3376, 0.4,
		},
		generatorT{
			31, "Prismatic", "Kinetic Resistance", "Fast Charge", 700, 1.3, 0.4925, 0.6955, -0.4007,
		},
		generatorT{
			32, "Prismatic", "Kinetic Resistance", "Multi-Weave", 700, 1.1, 0.515, 0.709, -0.3386,
		},
		generatorT{
			33, "Prismatic", "Kinetic Resistance", "Hi-Cap", 742, 1.1, 0.5, 0.7, -0.38,
		},
		generatorT{
			34, "Prismatic", "Kinetic Resistance", "Thermo Block", 679, 1.1, 0.5, 0.7, -0.2696,
		},
		generatorT{
			35, "Prismatic", "Kinetic Resistance", "Force Block", 679, 1.1, 0.5, 0.724, -0.38,
		},
		generatorT{
			36, "Prismatic", "Reinforced", "Fast Charge", 966, 1.3, 0.5762, 0.4915, -0.017,
		},
		generatorT{
			37, "Prismatic", "Reinforced", "Multi-Weave", 966, 1.1, 0.595, 0.514, 0.0281,
		},
		generatorT{
			38, "Prismatic", "Reinforced", "Hi-Cap", 1024, 1.1, 0.5825, 0.499, -0.002,
		},
		generatorT{
			39, "Prismatic", "Reinforced", "Thermo Block", 937, 1.1, 0.5825, 0.499, 0.0782,
		},
		generatorT{
			40, "Prismatic", "Reinforced", "Force Block", 937, 1.1, 0.5825, 0.5391, -0.002,
		},
		generatorT{
			41, "Prismatic", "Thermal Resistance", "Fast Charge", 700, 1.3, 0.4925, 0.2692, 0.391,
		},
		generatorT{
			42, "Prismatic", "Thermal Resistance", "Multi-Weave", 700, 1.1, 0.515, 0.3016, 0.418,
		},
		generatorT{
			43, "Prismatic", "Thermal Resistance", "Hi-Cap", 742, 1.1, 0.5, 0.28, 0.4,
		},
		generatorT{
			44, "Prismatic", "Thermal Resistance", "Thermo Block", 679, 1.1, 0.5, 0.28, 0.448,
		},
		generatorT{
			45, "Prismatic", "Thermal Resistance", "Force Block", 679, 1.1, 0.5, 0.3376, 0.4,
		},
	}

	return generators
}
