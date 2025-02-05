package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
)

const (
	baseURL  = "http://localhost:8000"
	usageMsg = "Uso: go run main.go -ano=2023 [-rodada=37]"
	helpMsg  = "Se a rodada não for informada, mostra o campeão do ano"
)

type Team struct {
	Name  string `json:"nome"`
	Goals int    `json:"gols"`
}

type Match struct {
	Date     string `json:"data"`
	HomeTeam Team   `json:"mandante"`
	AwayTeam Team   `json:"visitante"`
	Score    string `json:"placar"`
}

type Round struct {
	Year    string  `json:"ano"`
	Number  string  `json:"rodada"`
	Matches []Match `json:"jogos"`
}

type Champion struct {
	Year         string `json:"ano"`
	ChampionTeam string `json:"campeao"`
}

type ErrorResponse struct {
	Message string `json:"erro"`
}

type APIClient struct {
	client *http.Client
}

func NewAPIClient() *APIClient {
	return &APIClient{
		client: &http.Client{},
	}
}

func (c *APIClient) GetMatches(year, round string) (*Round, error) {
	url := fmt.Sprintf("%s/jogos/%s/%s", baseURL, year, round)
	result := &Round{}
	err := c.makeRequest(url, result)
	return result, err
}

func (c *APIClient) GetChampion(year string) (*Champion, error) {
	url := fmt.Sprintf("%s/campeao/%s", baseURL, year)
	result := &Champion{}
	err := c.makeRequest(url, result)
	return result, err
}

func (c *APIClient) makeRequest(url string, result interface{}) error {
	resp, err := c.client.Get(url)
	if err != nil {
		return fmt.Errorf("request error: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("response read error: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		return c.handleErrorResponse(body)
	}

	return json.Unmarshal(body, result)
}

func (c *APIClient) handleErrorResponse(body []byte) error {
	var errorResp ErrorResponse
	if err := json.Unmarshal(body, &errorResp); err != nil {
		return fmt.Errorf("unknown server error")
	}
	return fmt.Errorf(errorResp.Message)
}

func (c *APIClient) decodeJSON(data []byte, result interface{}) error {
	if err := json.Unmarshal(data, result); err != nil {
		return fmt.Errorf("JSON decode error: %v", err)
	}
	return nil
}

type CLIHandler struct {
	client *APIClient
}

func NewCLIHandler(client *APIClient) *CLIHandler {
	return &CLIHandler{client: client}
}

func (h *CLIHandler) Run() {
	year, round := h.parseFlags()

	if round == "" {
		h.handleChampionQuery(year)
		return
	}

	h.handleRoundQuery(year, round)
}

func (h *CLIHandler) parseFlags() (string, string) {
	year := flag.String("ano", "", "ano do campeonato (ex: 2023)")
	round := flag.String("rodada", "", "número da rodada (ex: 37)")
	flag.Parse()

	if *year == "" {
		fmt.Println(usageMsg)
		fmt.Println(helpMsg)
		os.Exit(1)
	}

	return *year, *round
}

func (h *CLIHandler) handleChampionQuery(year string) {
	champion, err := h.client.GetChampion(year)
	if err != nil {
		fmt.Printf("%v\n", err)
		os.Exit(0)
	}

	if champion.ChampionTeam == "" {
		fmt.Printf("Ainda não houve campeão para o Brasileirão %s\n", year)
		os.Exit(0)
	}

	fmt.Printf("Campeão do Brasileirão %s: %s\n", champion.Year, champion.ChampionTeam)
}

func (h *CLIHandler) handleRoundQuery(year, round string) {
	data, err := h.client.GetMatches(year, round)
	if err != nil {
		fmt.Printf("Erro: %v\n", err)
		os.Exit(1)
	}

	if len(data.Matches) == 0 {
		fmt.Printf("Ainda não há jogos disponíveis para o Brasileirão %s\n", year)
		os.Exit(0)
	}

	h.displayMatches(data)
}

func (h *CLIHandler) displayMatches(data *Round) {
	fmt.Printf("Jogos da rodada %s do Brasileirão %s:\n\n", data.Number, data.Year)

	for _, match := range data.Matches {
		fmt.Printf("%s: %s %s %s\n",
			match.Date,
			match.HomeTeam.Name,
			match.Score,
			match.AwayTeam.Name,
		)
	}
}

func main() {
	client := NewAPIClient()
	handler := NewCLIHandler(client)
	handler.Run()
}
