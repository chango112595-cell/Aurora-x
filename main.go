package main

import (
        "encoding/json"
        "fmt"
        "log"
        "net/http"
        "os"
        "time"
)

// Echo struct for JSON echo endpoint
type Echo struct {
        Message   string    `json:"message"`
        Timestamp time.Time `json:"timestamp"`
        Service   string    `json:"service"`
}

// Health check response
type Health struct {
        OK        bool      `json:"ok"`
        Service   string    `json:"service"`
        Version   string    `json:"version"`
        Timestamp time.Time `json:"timestamp"`
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusOK)
        
        health := Health{
                OK:        true,
                Service:   "aurora-go-service",
                Version:   "1.0.0",
                Timestamp: time.Now(),
        }
        
        json.NewEncoder(w).Encode(health)
}

func echoHandler(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        
        if r.Method != http.MethodPost {
                w.WriteHeader(http.StatusMethodNotAllowed)
                json.NewEncoder(w).Encode(map[string]string{
                        "error": "Method not allowed. Use POST",
                })
                return
        }
        
        var echo Echo
        if err := json.NewDecoder(r.Body).Decode(&echo); err != nil {
                w.WriteHeader(http.StatusBadRequest)
                json.NewEncoder(w).Encode(map[string]string{
                        "error": fmt.Sprintf("Invalid JSON: %v", err),
                })
                return
        }
        
        // Add metadata
        echo.Timestamp = time.Now()
        echo.Service = "aurora-go-service"
        
        w.WriteHeader(http.StatusOK)
        json.NewEncoder(w).Encode(echo)
}

func main() {
        mux := http.NewServeMux()
        
        // Register handlers
        mux.HandleFunc("/health", healthHandler)
        mux.HandleFunc("/echo", echoHandler)
        mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
                w.Header().Set("Content-Type", "application/json")
                json.NewEncoder(w).Encode(map[string]string{
                        "service": "Aurora Go Service",
                        "endpoints": "GET /health, POST /echo",
                })
        })
        
        // Start server
        port := os.Getenv("PORT")
        if port == "" {
                port = "8080"
        }
        log.Printf("🚀 Aurora Go Service starting on port %s", port)
        log.Printf("📍 Endpoints: GET /health, POST /echo")
        
        if err := http.ListenAndServe(":"+port, mux); err != nil {
                log.Fatal(err)
        }
}
