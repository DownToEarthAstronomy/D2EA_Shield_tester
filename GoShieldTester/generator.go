package main

import (
	"encoding/csv"
	"io"
	"log"
	"math"
	"os"
	"strconv"
	"strings"
)

type generatorT struct {
	ID                                  int
	name, engineering, experimental     string
	shieldStrength                      float64
	regenRate, expRes, kinRes, thermRes float64
}

type shieldGenBase struct {
	maxmass, optmass, minmass, maxmul, optmul, minmul, regen float64
}

func getShieldStrengthAndRegen(name string, shieldStrength, hullMass, regenBonus float64) (float64, float64) {
	var shieldRating string
	if name == "Bi-Weave" {
		shieldRating = "C"
	} else {
		shieldRating = "A"
	}
	//import shield generator base info
	var record []string
	var err error
	shieldsfile, err := os.Open(config.shieldStats)
	if err != nil {
		log.Fatal(err)
	}
	r := csv.NewReader(shieldsfile)
	var shieldBaseStats shieldGenBase
	for {
		record, err = r.Read()

		if err == io.EOF {
			break
		}

		if err != nil {
			log.Fatal(err)
		}
		recName, _ := strconv.ParseFloat(record[1], 64)
		if recName == config.shieldGeneratorSize && record[2] == shieldRating && record[3] == name {
			shieldBaseStats.optmass, _ = strconv.ParseFloat(record[5], 64)
			shieldBaseStats.maxmass, _ = strconv.ParseFloat(record[4], 64)
			shieldBaseStats.minmass, _ = strconv.ParseFloat(record[6], 64)
			shieldBaseStats.maxmul, _ = strconv.ParseFloat(record[7], 64)
			shieldBaseStats.optmul, _ = strconv.ParseFloat(record[8], 64)
			shieldBaseStats.minmul, _ = strconv.ParseFloat(record[9], 64)
			shieldBaseStats.regen, _ = strconv.ParseFloat(record[10], 64)
			break
		}
	}
	// calcualte the normalized mass
	MassNorm := math.Min(1, ((shieldBaseStats.maxmass - hullMass) / (shieldBaseStats.maxmass - shieldBaseStats.minmass)))
	// Calculate power function exponent
	Exponent := math.Log10((shieldBaseStats.optmul-shieldBaseStats.minmul)/(shieldBaseStats.maxmul-shieldBaseStats.minmul)) / math.Log10(math.Min(1, ((shieldBaseStats.maxmass-shieldBaseStats.optmass)/(shieldBaseStats.maxmass-shieldBaseStats.minmass))))
	// Calcualte final multiplier
	Multiplier := shieldBaseStats.minmul + math.Pow(MassNorm, Exponent)*(shieldBaseStats.maxmul-shieldBaseStats.minmul)

	ShieldHitPoints := shieldStrength * Multiplier
	ShieldRegen := shieldBaseStats.regen * (1 + regenBonus)

	return ShieldHitPoints, ShieldRegen

}

func loadGenerators(baseShieldStrength, hullMass float64) []generatorT {

	var generators []generatorT
	var record []string
	var err error

	csvfile, err := os.Open(config.generatorFile)
	if err != nil {
		log.Fatal(err)
	}

	r := csv.NewReader(csvfile)

	if err != nil {
		log.Fatal(err)
	}

	// Consume and discard the header row
	record, err = r.Read()

	for {
		var generator generatorT

		record, err = r.Read()

		if err == io.EOF {
			break
		}

		if err != nil {
			log.Fatal(err)
		}

		// if prismatics are disabled, skip those entries
		if !config.prismatics && strings.Contains(record[1], "Prismatic") {
			continue
		}

		// 0ID,1Type,2Engineering,3Experimental,4RegenRateBobus,5ExpRes,6KinRes,7ThermRes,8OptimalMultiplierBonus
		regenBonus, _ := strconv.ParseFloat(record[4], 64)
		generator.ID, err = strconv.Atoi(record[0])
		generator.name = record[1]
		generator.engineering = record[2]
		generator.experimental = record[3]
		generator.shieldStrength, generator.regenRate = getShieldStrengthAndRegen(record[1], baseShieldStrength, hullMass, regenBonus)
		generator.expRes, err = strconv.ParseFloat(record[5], 64)
		generator.expRes = 1.0 - generator.expRes
		generator.kinRes, err = strconv.ParseFloat(record[6], 64)
		generator.kinRes = 1.0 - generator.kinRes
		generator.thermRes, err = strconv.ParseFloat(record[7], 64)
		generator.thermRes = 1.0 - generator.thermRes

		generators = append(generators, generator)
	}

	return generators
}
