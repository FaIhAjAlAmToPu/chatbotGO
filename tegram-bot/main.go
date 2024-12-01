package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/joho/godotenv" // For using a .env file
	"gopkg.in/tucnak/telebot.v2"
)

type JokeResponse struct {
	Joke string `json:"joke"`
}

func getDadJoke() (string, error) {
	req, err := http.NewRequest("GET", "https://icanhazdadjoke.com/", nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("Accept", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var jokeResponse JokeResponse
	if err := json.NewDecoder(resp.Body).Decode(&jokeResponse); err != nil {
		return "", err
	}
	return jokeResponse.Joke, nil
}

// Function to get a useless fact
func getFunFact() string {
	resp, err := http.Get("https://uselessfacts.jsph.pl/random.json?language=en")
	if err != nil {
		return "Error getting fact"
	}
	defer resp.Body.Close()

	var factData struct {
		Text string `json:"text"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&factData); err != nil {
		return "Error decoding fact"
	}
	return factData.Text
}

func main() {
	// Load .env file (optional)
	err := godotenv.Load()
	if err != nil {
		log.Println("No .env file found, using environment variables directly.")
	}

	token := os.Getenv("TELEGRAM_BOT_TOKEN")
	if token == "" {
		log.Fatal("No bot token found. Please set TELEGRAM_BOT_TOKEN environment variable.")
	}

	bot, err := telebot.NewBot(telebot.Settings{
		Token:  token,
		Poller: &telebot.LongPoller{Timeout: 10 * time.Second},
	})
	if err != nil {
		log.Fatal(err)
	}

	// Handle the /fact command to send a random fun fact
	bot.Handle("/fact", func(m *telebot.Message) {
		funFact := getFunFact()
		bot.Send(m.Sender, funFact)
	})

	bot.Handle("/start", func(m *telebot.Message) {
		bot.Send(m.Sender, "Hi! Type /fact to get a fun fact!\nType /aboutme if u pendu!\nType /joke to get a dad joke!")
	})

	// Handle the /aboutme command to send a fun fact using the user's name
	bot.Handle("/aboutme", func(m *telebot.Message) {
		userName := m.Sender.FirstName // You can also use LastName or Username here
		funFact := userName + " you pendu"
		bot.Send(m.Sender, funFact)
	})

	// Handle the /joke command to send a random dad joke
	bot.Handle("/joke", func(m *telebot.Message) {
		joke, err := getDadJoke()
		if err != nil {
			bot.Send(m.Sender, "Sorry, I couldn't fetch a joke right now!")
			return
		}
		bot.Send(m.Sender, joke)
	})

	log.Println("Bot is running...")
	bot.Start()
}
