#!/bin/bash
echo "Content-Type: text/html"
echo
source ~/dir.sh
file="$dir/serverfiles/ShooterGame/Saved/Config/LinuxServer/Game.ini"
echo "<pre>"
echo "$(sed 's/ServerAdminPassword=.*/ServerAdminPassword=N0J0d@$/g' "$file")"
echo "</pre>"
echo "</html>"


