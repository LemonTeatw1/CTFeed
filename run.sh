#!/bin/bash

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${CYAN}===================================${NC}"
echo -e "${WHITE}       CTFeed Bot Runner${NC}"
echo -e "${CYAN}===================================${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}.env file not found!${NC}"
    echo ""
    echo -e "${YELLOW}Please run setup first:${NC}"
    echo -e "${WHITE}./setup_env.sh${NC}"
    echo ""
    exit 1
fi

# Function to check required tools
check_tools() {
    echo -e "${BLUE}Checking available tools...${NC}"
    
    if command -v docker > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker is available: ${WHITE}$(docker --version)${NC}"
        DOCKER_AVAILABLE=true
    else
        echo -e "${RED}✗ Docker is not installed${NC}"
        DOCKER_AVAILABLE=false
    fi
    
    if command -v docker-compose > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker Compose is available: ${WHITE}$(docker-compose --version)${NC}"
        COMPOSE_AVAILABLE=true
    else
        echo -e "${RED}✗ Docker Compose is not installed${NC}"
        COMPOSE_AVAILABLE=false
    fi
    
    echo ""
}

# Function to show deployment options
show_options() {
    echo -e "${CYAN}===================================${NC}"
    echo -e "${WHITE}      Deployment Options${NC}"
    echo -e "${CYAN}===================================${NC}"
    echo ""
    
    local option_num=1
    
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
        echo -e "${GREEN}${option_num}) ${WHITE}Docker (background) - Recommended${NC}"
        echo -e "   ${BLUE}sudo docker-compose up -d --build${NC}"
        DOCKER_BG_OPTION=$option_num
        option_num=$((option_num + 1))
        echo ""
        
        echo -e "${GREEN}${option_num}) ${WHITE}Docker (foreground) - See logs${NC}"
        echo -e "   ${BLUE}sudo docker-compose up --build${NC}"
        DOCKER_FG_OPTION=$option_num
        option_num=$((option_num + 1))
        echo ""
    fi
    
    echo -e "${RED}${option_num}) ${WHITE}Exit${NC}"
    EXIT_OPTION=$option_num
    echo ""
}

# Function to run deployment
run_deployment() {
    while true; do
        echo -e -n "${YELLOW}Choose deployment method (1-${EXIT_OPTION}): ${NC}"
        read choice
        echo ""
        
        if [ "$choice" = "$DOCKER_BG_OPTION" ] && [ -n "$DOCKER_BG_OPTION" ]; then
            echo -e "${BLUE}Starting CTFeed bot in background...${NC}"
            sudo docker-compose up -d --build
            echo ""
            echo -e "${GREEN}✓ Bot is running in background!${NC}"
            echo ""
            echo -e "${WHITE}Useful commands:${NC}"
            echo -e "${CYAN}   View logs:    ${WHITE}sudo docker-compose logs -f ctfeed${NC}"
            echo -e "${CYAN}   Stop bot:     ${WHITE}sudo docker-compose down${NC}"
            echo -e "${CYAN}   Restart bot:  ${WHITE}sudo docker-compose restart ctfeed${NC}"
            break
            
        elif [ "$choice" = "$DOCKER_FG_OPTION" ] && [ -n "$DOCKER_FG_OPTION" ]; then
            echo -e "${BLUE}Starting CTFeed bot (foreground - press Ctrl+C to stop)...${NC}"
            echo ""
            sudo docker-compose up --build
            break
            
        elif [ "$choice" = "$EXIT_OPTION" ]; then
            echo -e "${BLUE}Exiting...${NC}"
            exit 0
            
        else
            echo -e "${RED}✗ Invalid choice. Please try again.${NC}"
            echo ""
        fi
    done
}

# Main execution
check_tools
show_options
run_deployment