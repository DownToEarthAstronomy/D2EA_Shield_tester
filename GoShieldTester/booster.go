package main

import (
	"encoding/csv"
	"fmt"
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
func loadboosterVariants() []boosterT {

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

		booster.ID, err = strconv.Atoi(record[0])
		booster.engineering = record[1]
		booster.experimental = record[2]
		booster.shieldStrengthBonus, err = strconv.ParseFloat(record[3], 64)
		booster.expResBonus, err = strconv.ParseFloat(record[4], 64)
		booster.kinResBonus, err = strconv.ParseFloat(record[5], 64)
		booster.thermResBonus, err = strconv.ParseFloat(record[6], 64)

		boosterVariants = append(boosterVariants, booster)
	}

	fmt.Println("Loaded", len(boosterVariants), "boosters")
	return boosterVariants
}

func generateBoosterVariations(numberBoosterVariations int, variationsList [][]int, currentBooster int, currentVariation int, variations []int) [][]int {

	if currentBooster <= config.shieldBoosterCount {
		for currentVariation <= numberBoosterVariations {
			currentVariationList := variations
			currentVariationList = append(currentVariationList, currentVariation)
			variationsList = generateBoosterVariations(numberBoosterVariations, variationsList, currentBooster+1, currentVariation, currentVariationList)
			currentVariation++
		}
	} else {
		variationsList = append(variationsList, variations)
	}

	return variationsList
}

func getBoosterLoadoutList(numBoosterVariants int) [][]int {
	var variationsList [][]int
	var currentVariationList []int

	variationsList = generateBoosterVariations(numBoosterVariants, variationsList, 1, 1, currentVariationList)

	return variationsList
}
