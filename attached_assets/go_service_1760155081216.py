GO_MAIN = """package main

import (
	"encoding/json"
	"log"
	"net/http"
)

type Echo struct {
	Message string `json:"message"`
}

func health(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"ok":true}`))
}

func echo(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		w.Write([]byte(`{"error":"POST required"}`))
		return
	}
	var e Echo
	if err := json.NewDecoder(r.Body).Decode(&e); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		w.Write([]byte(`{"error":"invalid json"}`))
		return
	}
	json.NewEncoder(w).Encode(e)
}

func main() {
	http.HandleFunc("/health", health)
	http.HandleFunc("/echo", echo)
	log.Println("go service listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
"""


def render_go_service(name: str) -> dict:
    return {"files": {"main.go": GO_MAIN}, "hint": "Run: go run .   (then GET /health)"}
