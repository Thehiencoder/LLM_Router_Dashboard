#!/bin/bash
# ==============================================================================
#                 LLM Router Dashboard — Starting Containers
# ==============================================================================

set -e

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

docker compose up -d

echo ""
echo "=============================================================================="
echo "                         Application is ONLINE!                              "
echo "=============================================================================="
echo ""
echo "  [1] Local Browser (Your Computer):"
echo "      http://localhost:3000"
echo ""
echo "  [2] Other Devices on the Same Wi-Fi (Phone, Laptop):"
# Detect local IP on Linux / macOS
if command -v hostname >/dev/null 2>&1 && hostname -I >/dev/null 2>&1; then
    for ip in $(hostname -I); do
        echo "      http://$ip:3000"
    done
elif command -v ipconfig >/dev/null 2>&1; then
    ipconfig | grep -i "IPv4" | awk -F': ' '{print "      http://"$2":3000"}'
elif command -v ifconfig >/dev/null 2>&1; then
    ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print "      http://"$2":3000"}'
fi
echo ""
echo "  [3] Backend OpenAPI Documentation:"
echo "      http://localhost:8000/docs"
echo ""
echo "=============================================================================="
echo "  To generate a FREE Public Internet Link for external friends:"
echo "  Run: docker compose --profile tunnel up -d"
echo "  Then view link with: docker compose logs tunnel"
echo "=============================================================================="
echo ""

# Try opening in default browser if in interactive desktop session
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:3000 >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
    open http://localhost:3000 >/dev/null 2>&1 &
fi
