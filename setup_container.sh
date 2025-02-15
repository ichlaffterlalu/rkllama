#!/bin/bash

# Definition of colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Checking for Git repository updates
#echo -e "${CYAN}Checking for updates...${RESET}"
#git pull
#echo -e "${GREEN}Update check completed successfully!${RESET}"

# Creating the RKLLAMA directory
echo -e "${CYAN}Installing resources in ~/RKLLAMA...${RESET}"
ln -s $(pwd)  ~/RKLLAMA

# Installing dependencies
echo -e "${CYAN}Installing dependencies from requirements.txt...${RESET}"
pip3 install -r ./requirements.txt

# Making client.sh and server.sh executable
echo -e "${CYAN}Making ./client.sh and ./server.sh executable${RESET}"
chmod +x ./*.sh

# Exporting client.sh as a global command
echo -e "${CYAN}Creating a global executable for rkllama...${RESET}"
sudo cp ./client.sh /usr/local/bin/rkllama
sudo chmod +x /usr/local/bin/rkllama
echo -e "${CYAN}Executable created successfully: /usr/local/bin/rkllama${RESET}"

# Displaying statuses and available commands
echo -e "${GREEN}+ Configuration: OK.${RESET}"
echo -e "${GREEN}+ Installation : OK.${RESET}"

echo -e "${BLUE}Server${GREEN}  : ./server.sh${RESET}"
echo -e "${BLUE}Client${GREEN}  : ./client.sh${RESET}\n"
echo -e "${BLUE}Global command  : ${RESET}rkllama"
