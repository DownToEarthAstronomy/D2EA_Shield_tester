package main

import (
	"fmt"
	"runtime"
)

func main() {
	// var NumberOfLogicalProcessors = runtime.NumCPU()

	fmt.Println("Loading modules")

	var config configT = loadConfig()

	var generators = loadGenerators()
	var boosters = loadBoosters(config.shortBoosterList)

	fmt.Println("Generating list of booster loadouts")
	fmt.Println("Shield Generator Count: ", len(generators))
	fmt.Println("Shield Booster Count: ", config.ShieldBoosterCount)
	fmt.Println("Shield Booster Variants: ", len(boosters))

	var ShieldBoosterLoadoutList = getBoosterLoadoutList(config, boosters)

	fmt.Println("Shield loadouts to be tested: ", len(ShieldBoosterLoadoutList)*len(generators))
	fmt.Println("Number of parallel threads: ", runtime.NumCPU())

	var result = testGenerators(config, generators, boosters, ShieldBoosterLoadoutList)

	showResults(result, boosters)
}
