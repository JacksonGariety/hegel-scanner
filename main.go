package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

type CountedWord struct {
	Word string
	Count int
}

func extract(filepath string) ([]string) {
	file, err := os.Open(filepath)
	if err != nil {
		panic(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	scanner.Split(bufio.ScanWords)

	var words []string
	for scanner.Scan() {
		word := scanner.Text()
		trimmedWord := strings.Trim(word, ",.—;'\"_)( ")
		words = append(words, trimmedWord)
	}

	return words
}

func filter(wordCountMap map[string]int, resolution int) (map[string]int, error) {
	// remove modal (i.e. most freqeuently used) words
	modalWords := extract("./resources/modal-words.txt")

	for i := 0; i < resolution; i++ {
		word := modalWords[i]
		if _, ok := wordCountMap[word]; ok {
			delete(wordCountMap, word)
		}
	}

	return wordCountMap, nil
}

func count(words []string) ([]CountedWord, error) {
	// make a map of word-count pairs
	var wordCountMap = make(map[string]int)
	for _, word := range words {
		if count, ok := wordCountMap[word]; ok {
			wordCountMap[word] = count + 1
		} else {
			wordCountMap[word] = 1
		}
	}

	wordCountMap, err := filter(wordCountMap, 800)
	if err != nil {
		return nil, err
	}

	// convert it to a slice
	var countedWords []CountedWord
	for word, count := range wordCountMap {
		countedWords = append(countedWords, CountedWord{word, count})
	}

	// sort the slice
	sort.Slice(countedWords, func (i, j int) bool {
		return countedWords[i].Count > countedWords[j].Count
	})

	return countedWords, nil
}

func dump(countedWords []CountedWord) {
	file, err := os.Create("dump.txt")
	if err != nil {
		panic(err)
	}

	for _, countedWord := range countedWords {
		if _, err = file.WriteString(countedWord.Word + ": " + strconv.Itoa(countedWord.Count) + "\n"); err != nil {
			panic(err)
		}
	}
}

func main() {
	filepaths := []string{
		"./resources/logik-band-eins.txt",
		// "./resources/logik-band-zwei.txt",
		// "./resources/phänomenologie.txt",
	}

	var hegelianWords []string
	for _, filepath := range filepaths {
		hegelianWords = append(hegelianWords, extract(filepath)...)
	}

	// count them
	countedHegelianWords, err := count(hegelianWords)
	if err != nil {
		panic(err)
	}

	for i := 0; i < 50; i++ {
		fmt.Printf("%s: %d\n", countedHegelianWords[i].Word, countedHegelianWords[i].Count)
	}

	dump(countedHegelianWords)
}
