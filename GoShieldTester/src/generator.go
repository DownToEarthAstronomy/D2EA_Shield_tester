package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
)

type generatorT struct {
	ID                                  int
	name, engineering, experimental     string
	shieldStrength                      float64
	regenRate, expRes, kinRes, thermRes float64
}

func loadGenerators() []generatorT {

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

		// ID,Type,Engineering,Experimental,shieldStrength,regenRate,ExpRes,KinRes,ThermRes

		generator.ID, err = strconv.Atoi(record[0])
		generator.name = record[1]
		generator.engineering = record[2]
		generator.experimental = record[3]
		generator.shieldStrength, err = strconv.ParseFloat(record[4], 64)
		generator.regenRate, err = strconv.ParseFloat(record[5], 64)
		generator.expRes, err = strconv.ParseFloat(record[6], 64)
		generator.kinRes, err = strconv.ParseFloat(record[7], 64)
		generator.thermRes, err = strconv.ParseFloat(record[8], 64)

		generators = append(generators, generator)
	}

	fmt.Println("Loaded", len(generators), "boosters")

	return generators
}
