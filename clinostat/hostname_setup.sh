#!/bin/sh

PREFIX="controller"
SERIAL=$(awk '/Serial/ {print $3}' /proc/cpuinfo)
SERIAL_LAST4=$(echo "$SERIAL" | awk '{print substr($0, length($0)-3)}')
NEW_HOSTNAME="${PREFIX}-${SERIAL_LAST4}"
echo "Setting hostname to: $NEW_HOSTNAME"
sudo hostnamectl set-hostname "$NEW_HOSTNAME"
sudo sed -i "s/127\.0\.1\.1.*/127.0.1.1\t$NEW_HOSTNAME/" /etc/hosts

echo "Setup complete! Please reboot for changes to take effect."
echo "Do you want to reboot now? (y/n): \c"
read REBOOT_ANSWER

if [ "$REBOOT_ANSWER" = "y" ] || [ "$REBOOT_ANSWER" = "Y" ]; then
    echo "Rebooting now..."
    sudo reboot
else
    echo "Reboot skipped. Remember to reboot later!"
fi
