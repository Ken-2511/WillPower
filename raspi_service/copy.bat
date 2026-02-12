@echo off
ssh ken@rpi0 "sudo rm -rf ~/WillPower/raspi_service; mkdir -p ~/WillPower/raspi_service"
scp -r "%~dp0." ken@rpi0:~/WillPower/raspi_service/
ssh ken@rpi0 "sudo sed -i 's/\r$//' ~/WillPower/raspi_service/tools.sh && chmod +x ~/WillPower/raspi_service/tools.sh"
