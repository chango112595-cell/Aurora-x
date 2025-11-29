#!/bin/bash

# Aurora-X Docker Deployment Script
# This script helps deploy the Aurora-X application with Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_message "$YELLOW" "Checking prerequisites..."
    
    local missing_deps=0
    
    if ! command_exists docker; then
        print_message "$RED" "✗ Docker is not installed"
        missing_deps=1
    else
        print_message "$GREEN" "✓ Docker is installed"
    fi
    
    if ! command_exists docker-compose; then
        if ! docker compose version >/dev/null 2>&1; then
            print_message "$RED" "✗ Docker Compose is not installed"
            missing_deps=1
        else
            print_message "$GREEN" "✓ Docker Compose (plugin) is installed"
            DOCKER_COMPOSE="docker compose"
        fi
    else
        print_message "$GREEN" "✓ Docker Compose is installed"
        DOCKER_COMPOSE="docker-compose"
    fi
    
    if [ $missing_deps -eq 1 ]; then
        print_message "$RED" "\nPlease install missing dependencies before continuing."
        exit 1
    fi
}

# Function to check environment file
check_env_file() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            print_message "$YELLOW" "\n.env file not found. Creating from .env.example..."
            cp .env.example .env
            print_message "$YELLOW" "Please edit .env file with your actual values before continuing."
            print_message "$YELLOW" "Especially set CF_TUNNEL_TOKEN for Cloudflare tunnel."
            read -p "Press enter to continue after editing .env file..."
        else
            print_message "$RED" "✗ Neither .env nor .env.example found!"
            exit 1
        fi
    else
        print_message "$GREEN" "✓ Environment file exists"
    fi
}

# Function to create necessary directories
create_directories() {
    print_message "$YELLOW" "\nCreating necessary directories..."
    
    mkdir -p data
    mkdir -p runs
    mkdir -p logs
    mkdir -p attached_assets
    mkdir -p docker/ssl
    
    print_message "$GREEN" "✓ Directories created"
}

# Function to build services
build_services() {
    print_message "$YELLOW" "\nBuilding Docker images..."
    
    $DOCKER_COMPOSE -f docker-compose.aurora-x.yml build --no-cache
    
    if [ $? -eq 0 ]; then
        print_message "$GREEN" "✓ Docker images built successfully"
    else
        print_message "$RED" "✗ Failed to build Docker images"
        exit 1
    fi
}

# Function to start services
start_services() {
    print_message "$YELLOW" "\nStarting services..."
    
    $DOCKER_COMPOSE -f docker-compose.aurora-x.yml up -d
    
    if [ $? -eq 0 ]; then
        print_message "$GREEN" "✓ Services started successfully"
    else
        print_message "$RED" "✗ Failed to start services"
        exit 1
    fi
}

# Function to check service health
check_health() {
    print_message "$YELLOW" "\nWaiting for services to be healthy..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        
        # Check if all services are running
        if $DOCKER_COMPOSE -f docker-compose.aurora-x.yml ps | grep -q "unhealthy\|starting"; then
            echo -n "."
            sleep 2
        else
            echo ""
            print_message "$GREEN" "✓ All services are healthy"
            return 0
        fi
    done
    
    echo ""
    print_message "$YELLOW" "⚠ Some services may not be fully healthy yet"
    return 1
}

# Function to show logs
show_logs() {
    print_message "$YELLOW" "\nShowing recent logs..."
    $DOCKER_COMPOSE -f docker-compose.aurora-x.yml logs --tail=50
}

# Function to show status
show_status() {
    print_message "$YELLOW" "\nService Status:"
    $DOCKER_COMPOSE -f docker-compose.aurora-x.yml ps
}

# Function to stop services
stop_services() {
    print_message "$YELLOW" "\nStopping services..."
    $DOCKER_COMPOSE -f docker-compose.aurora-x.yml down
    print_message "$GREEN" "✓ Services stopped"
}

# Function to restart services
restart_services() {
    stop_services
    start_services
}

# Function to update services
update_services() {
    print_message "$YELLOW" "\nPulling latest images and updating services..."
    
    # Pull latest images
    $DOCKER_COMPOSE -f docker-compose.aurora-x.yml pull
    
    # Rebuild with latest code
    build_services
    
    # Restart services
    restart_services
}

# Main menu
show_menu() {
    echo ""
    print_message "$YELLOW" "================================"
    print_message "$YELLOW" "   Aurora-X Deployment Tool"
    print_message "$YELLOW" "================================"
    echo ""
    echo "1) Deploy (Build and Start)"
    echo "2) Start services"
    echo "3) Stop services"
    echo "4) Restart services"
    echo "5) Update and rebuild"
    echo "6) Show status"
    echo "7) Show logs"
    echo "8) Clean (Remove containers and volumes)"
    echo "9) Exit"
    echo ""
    read -p "Select an option: " choice
}

# Function to clean up
cleanup() {
    print_message "$YELLOW" "\nCleaning up Docker resources..."
    
    read -p "This will remove all containers and volumes. Are you sure? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        $DOCKER_COMPOSE -f docker-compose.aurora-x.yml down -v
        print_message "$GREEN" "✓ Cleanup complete"
    else
        print_message "$YELLOW" "Cleanup cancelled"
    fi
}

# Main execution
main() {
    print_message "$GREEN" "\n🚀 Aurora-X Docker Deployment Tool\n"
    
    # Check prerequisites
    check_prerequisites
    
    # Check environment
    check_env_file
    
    # Show menu if no arguments
    if [ $# -eq 0 ]; then
        while true; do
            show_menu
            case $choice in
                1)
                    create_directories
                    build_services
                    start_services
                    check_health
                    show_status
                    ;;
                2)
                    start_services
                    check_health
                    show_status
                    ;;
                3)
                    stop_services
                    ;;
                4)
                    restart_services
                    check_health
                    show_status
                    ;;
                5)
                    update_services
                    check_health
                    show_status
                    ;;
                6)
                    show_status
                    ;;
                7)
                    show_logs
                    ;;
                8)
                    cleanup
                    ;;
                9)
                    print_message "$GREEN" "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_message "$RED" "Invalid option"
                    ;;
            esac
        done
    else
        # Handle command line arguments
        case "$1" in
            deploy|build)
                create_directories
                build_services
                start_services
                check_health
                show_status
                ;;
            start)
                start_services
                check_health
                show_status
                ;;
            stop)
                stop_services
                ;;
            restart)
                restart_services
                check_health
                show_status
                ;;
            update)
                update_services
                check_health
                show_status
                ;;
            status)
                show_status
                ;;
            logs)
                show_logs
                ;;
            clean)
                cleanup
                ;;
            *)
                print_message "$RED" "Unknown command: $1"
                echo "Available commands: deploy, start, stop, restart, update, status, logs, clean"
                exit 1
                ;;
        esac
    fi
}

# Run main function
main "$@"