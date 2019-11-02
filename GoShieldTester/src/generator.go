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
	Name, Engineering, Experimental     string
	ShieldStrength                      float64
	RegenRate, ExpRes, KinRes, ThermRes float64
}

func loadGenerators() []generatorT {

	fmt.Println("Load shield generator variants")
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

		// ID,Type,Engineering,Experimental,ShieldStrength,RegenRate,ExpRes,KinRes,ThermRes

		generator.ID, err = strconv.Atoi(record[0])
		generator.Name = record[1]
		generator.Engineering = record[2]
		generator.Experimental = record[3]
		generator.ShieldStrength, err = strconv.ParseFloat(record[4], 64)
		generator.RegenRate, err = strconv.ParseFloat(record[5], 64)
		generator.ExpRes, err = strconv.ParseFloat(record[6], 64)
		generator.KinRes, err = strconv.ParseFloat(record[7], 64)
		generator.ThermRes, err = strconv.ParseFloat(record[8], 64)

		generators = append(generators, generator)
	}

	return generators
}
