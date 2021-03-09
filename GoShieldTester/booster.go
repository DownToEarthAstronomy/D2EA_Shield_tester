package main

import (
	"encoding/csv"
	"io"
	"log"
	"os"
	"strconv"
)

type boosterT struct {
	ID                                                           int
	engineering, experimental                                    string
	shieldStrengthBonus, expResBonus, kinResBonus, thermResBonus float64
}

/*
 *
 */
func loadboosterVariants(config *configT) []boosterT {

	var boosterVariants []boosterT
	var record []string
	var err error

	csvfile, err := os.Open(config.boosterFile)
	if err != nil {
		log.Fatal(err)
	}

	r := csv.NewReader(csvfile)

	if err != nil {
		log.Fatal(err)
	}

	// Consume and discard header row
	record, err = r.Read()

	for {
		var booster boosterT

		record, err = r.Read()

		if err == io.EOF {
			break
		}

		if err != nil {
			log.Fatal(err)
		}
		// naive booster filtering (if 0 dps of type, eliminate booster combination)
		if config.explosiveDPS == 0 {
			if record[2] == "Blast Block" || record[1] == "Blast Resistance" {
				continue
			}
		}
		if config.thermalDPS == 0 {
			if record[2] == "Thermo Block" || record[1] == "Thermal Resistance" {
				continue
			}
		}
		if config.kineticDPS == 0 {
			if record[2] == "Force Block" || record[1] == "Kinetic Resistance" {
				continue
			}
		}
		booster.ID, err = strconv.Atoi(record[0])
		booster.engineering = record[1]
		booster.experimental = record[2]
		booster.shieldStrengthBonus, err = strconv.ParseFloat(record[3], 64)
		booster.expResBonus, err = strconv.ParseFloat(record[4], 64)
		booster.expResBonus = 1.0 - booster.expResBonus
		booster.kinResBonus, err = strconv.ParseFloat(record[5], 64)
		booster.kinResBonus = 1.0 - booster.kinResBonus
		booster.thermResBonus, err = strconv.ParseFloat(record[6], 64)
		booster.thermResBonus = 1.0 - booster.thermResBonus

		boosterVariants = append(boosterVariants, booster)
	}

	return boosterVariants
}

// Combinations with repetition code from
// https://rosettacode.org/wiki/Combinations_with_repetitions#Concise_recursive

func combrep(n int, lst []int) [][]int {
	if n == 0 {
		return [][]int{nil}
	}
	if len(lst) == 0 {
		return nil
	}
	r := combrep(n, lst[1:])
	for _, x := range combrep(n-1, lst) {
		r = append(r, append(x, lst[0]))
	}
	return r
}

func getBoosterLoadoutList(numBoosterVariants int) [][]int {

	input := make([]int, numBoosterVariants)
	var i int
	for i < numBoosterVariants {
		input[i] = i + 1
		i++
	}
	variationsList := combrep(config.shieldBoosterCount, input)

	return variationsList
}
