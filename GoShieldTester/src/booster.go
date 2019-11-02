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
	Engineering, Experimental                                    string
	ShieldStrengthBonus, ExpResBonus, KinResBonus, ThermResBonus float64
}

/*
 *
 */
func loadboosterVariants() []boosterT {

	fmt.Println("Load shield booster variants")

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

		// ID,Engineering,Experimental,ShieldStrengthBonus,ExpResBonus,KinResBonus,ThermResBonus

		booster.ID, err = strconv.Atoi(record[0])
		booster.Engineering = record[1]
		booster.Experimental = record[2]
		booster.ShieldStrengthBonus, err = strconv.ParseFloat(record[3], 64)
		booster.ExpResBonus, err = strconv.ParseFloat(record[4], 64)
		booster.KinResBonus, err = strconv.ParseFloat(record[5], 64)
		booster.ThermResBonus, err = strconv.ParseFloat(record[6], 64)

		boosterVariants = append(boosterVariants, booster)
	}

	return boosterVariants
}

// def generate_booster_variations(self,
//number_of_boosters: int,
// variations_list: List[List[int]],
// current_booster: int=1
// current_variation: int=1
// variations: List[int]=list()):

// # Generate all possible booster combinations recursively and append them to the given variationsList.
// if current_booster <= number_of_boosters:
//   while current_variation <= len(self._shield_booster_variants):
//     current_variation_list = variations.copy()
//     current_variation_list.append(current_variation)
//     self.generate_booster_variations(number_of_boosters, variations_list, current_booster + 1, current_variation, current_variation_list)
//     current_variation += 1
// else:
// 	# Append to list. Variable is a reference and lives in main function. Therefore it is safe to append lists of booster IDs to it.
//  variations_list.append(variations)

func generateBoosterVariations(numberBoosterVariations int, variationsList [][]int, currentBooster int, currentVariation int, variations []int) [][]int {

	if currentBooster <= config.ShieldBoosterCount {
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

	// fmt.Println(variationsList)

	return variationsList
}
