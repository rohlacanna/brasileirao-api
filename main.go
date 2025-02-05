package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
)

type Time struct {
	Nome string `json:"nome"`
	Gols int    `json:"gols"`
}

type Jogo struct {
	Data      string `json:"data"`
	Mandante  Time   `json:"mandante"`
	Visitante Time   `json:"visitante"`
	Placar    string `json:"placar"`
}

type Rodada struct {
	Ano    string `json:"ano"`
	Rodada string `json:"rodada"`
	Jogos  []Jogo `json:"jogos"`
}

type Campeao struct {
	Ano     string `json:"ano"`
	Campeao string `json:"campeao"`
}

type ErroResponse struct {
	Erro string `json:"erro"`
}

func getJogos(ano, rodada string) (*Rodada, error) {
	url := fmt.Sprintf("http://localhost:8000/jogos/%s/%s", ano, rodada)
	return fazerRequisicao[Rodada](url)
}

func getCampeao(ano string) (*Campeao, error) {
	url := fmt.Sprintf("http://localhost:8000/campeao/%s", ano)
	return fazerRequisicao[Campeao](url)
}

func fazerRequisicao[T any](url string) (*T, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("erro ao fazer requisição: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("erro ao ler resposta: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		var erroResp ErroResponse
		if err := json.Unmarshal(body, &erroResp); err != nil {
			return nil, fmt.Errorf("erro desconhecido do servidor")
		}
		return nil, fmt.Errorf(erroResp.Erro)
	}

	var data T
	if err := json.Unmarshal(body, &data); err != nil {
		return nil, fmt.Errorf("erro ao decodificar JSON: %v", err)
	}

	return &data, nil
}

func main() {
	ano := flag.String("ano", "", "ano do campeonato (ex: 2023)")
	rodada := flag.String("rodada", "", "número da rodada (ex: 37)")
	flag.Parse()

	if *ano == "" {
		fmt.Println("Uso: go run main.go -ano=2023 [-rodada=37]")
		fmt.Println("Se a rodada não for informada, mostra o campeão do ano")
		os.Exit(1)
	}

	if *rodada == "" {
		campeao, err := getCampeao(*ano)
		if err != nil {
			fmt.Printf("%v\n", err)
			os.Exit(0)
		}
		if campeao.Campeao == "" {
			fmt.Printf("Ainda não houve campeão para o Brasileirão %s\n", *ano)
			os.Exit(0)
		}
		fmt.Printf("Campeão do Brasileirão %s: %s\n", campeao.Ano, campeao.Campeao)
		return
	}

	dados, err := getJogos(*ano, *rodada)
	if err != nil {
		fmt.Printf("Erro: %v\n", err)
		os.Exit(1)
	}

	if len(dados.Jogos) == 0 {
		fmt.Printf("Ainda não há jogos disponíveis para o Brasileirão %s\n", *ano)
		os.Exit(0)
	}

	fmt.Printf("Jogos da rodada %s do Brasileirão %s:\n\n", dados.Rodada, dados.Ano)
	for _, jogo := range dados.Jogos {
		fmt.Printf("%s: %s %s %s\n",
			jogo.Data,
			jogo.Mandante.Nome,
			jogo.Placar,
			jogo.Visitante.Nome,
		)
	}
}
