#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICES="picamera.service picamera_http.service"

copy_services() {
    for svc in $SERVICES; do
        sudo cp "$DIR/$svc" /etc/systemd/system/$svc
    done
    sudo systemctl daemon-reload
    echo "Service files copied and daemon reloaded."
}

enable_services() {
    for svc in $SERVICES; do
        sudo systemctl enable $svc
    done
    echo "Services enabled."
}

disable_services() {
    for svc in $SERVICES; do
        sudo systemctl disable $svc
    done
    echo "Services disabled."
}

start_services() {
    for svc in $SERVICES; do
        sudo systemctl start $svc
    done
    echo "Services started."
}

stop_services() {
    for svc in $SERVICES; do
        sudo systemctl stop $svc
    done
    echo "Services stopped."
}

copy_nginx() {
    sudo cp "$DIR/nginx_config.txt" /etc/nginx/sites-available/picamera
    sudo ln -sf /etc/nginx/sites-available/picamera /etc/nginx/sites-enabled/picamera
    sudo systemctl restart nginx
    echo "Nginx config copied and restarted."
}

echo "=== WillPower Raspi Tools ==="
echo "1) Copy service files"
echo "2) Enable all services"
echo "3) Disable all services"
echo "4) Start all services"
echo "5) Stop all services"
echo "6) Copy nginx config & restart nginx"
echo "7) Full install (copy + enable + start + nginx)"
echo "0) Exit"
echo ""
read -p "Select option: " choice

case $choice in
    1) copy_services ;;
    2) enable_services ;;
    3) disable_services ;;
    4) start_services ;;
    5) stop_services ;;
    6) copy_nginx ;;
    7) copy_services; enable_services; start_services; copy_nginx ;;
    0) exit 0 ;;
    *) echo "Invalid option." ; exit 1 ;;
esac
