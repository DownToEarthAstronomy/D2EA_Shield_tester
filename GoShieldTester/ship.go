package main

import (
	"encoding/csv"
	"io"
	"log"
	"os"
	"strconv"
)

type shipT struct {
	ID                           int
	name                         string
	hullMass, baseShieldStrength float64
}

func loadShipStats(name string) (float64, float64) {

	var err error
	shipfile, err := os.Open(config.shipFile)
	if err != nil {
		log.Fatal(err)
	}

	r := csv.NewReader(shipfile)
	record, err := r.Read()

	for {

		record, err = r.Read()
		if err == io.EOF {
			break
		}
		if record[1] == name {
			baseShieldStrength, _ := strconv.ParseFloat(record[3], 64)
			hullMass, _ := strconv.ParseFloat(record[2], 64)
			return baseShieldStrength, hullMass
		}
	}
	return 0, 0
}
