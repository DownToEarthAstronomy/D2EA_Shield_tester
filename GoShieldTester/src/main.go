package main

/*
 * Go version of Down To Earth Astronomy's Shield Tester
 * Original version here:  https://github.com/DownToEarthAstronomy/D2EA_Shield_tester
 *
 * Go port by Andrew van der Stock, vanderaj@gmail.com
 *
 * Why this version? It's extremely fast. No other reason
 */

import (
	"fmt"
	"runtime"
	"time"
)

func main() {
	fmt.Println("D2EA GoShieldTester\n")

	fmt.Println("Test started at: ", time.Now().Format(time.RFC1123))

	config = loadConfig()

	var generators = loadGenerators()
	var boosterVariants = loadboosterVariants()

	fmt.Println("Generating list of booster loadouts")
	fmt.Println("Shield Generator Count: ", len(generators))
	fmt.Println("Shield Booster Count: ", config.ShieldBoosterCount)
	fmt.Println("Shield Booster Variants: ", len(boosterVariants))

	var ShieldBoosterLoadoutList = getBoosterLoadoutList(len(boosterVariants))

	fmt.Println("Shield loadouts to be tested: ", len(ShieldBoosterLoadoutList)*len(generators))
	fmt.Println("Number of parallel threads: ", runtime.NumCPU())

	startTime := time.Now()

	var result = testGenerators(generators, boosterVariants, ShieldBoosterLoadoutList)

	endTime := time.Now()

	fmt.Println("Time elapsed: [", endTime.Sub(startTime), "]")
	fmt.Println()

	showResults(result, boosterVariants)
}
