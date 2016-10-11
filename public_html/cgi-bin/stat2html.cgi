#!/bin/bash 

#get custom stuff
source ~/arkpagesource

html=$web/status.html
html2=$web/modlist.html
html3=$web/playerlist.html
html4=$web/chat.html

#My Status PNG's brings all the boys to the yard
up="<img src="/images/up.png"  width="12" height="12" align="justify">"
down="<img src="/images/down.png"  width="12" height="12" align="justify">"
warn="<img src="/images/warning.png"  width="12" height="12" align="justify">"

maxcount=15
count=$maxcount
sleep=4
round=1

while :
do

#=========== SERVER PROCESS ===========
process="./ShooterGameServer"
start="arkserver start"
stop="arkserver stop"
#Need to escape special character "+"
Userver=" \+app_update 376030 \+quit"
Umods="steamcmd \+login anonymous \+workshop_download_item"

startfile=$dir/log/script/ark-server-script.log
startdate=$(grep "START: PASS: Started ark-server" $startfile | awk '{print $1" "$2" "$3}')
stopdate=$(grep "STOP: PASS: Stopped ark-server" $startfile | awk '{print $1" "$2" "$3}')
started=$(if [ -z "$startdate" ]; then echo ""; else echo "$(date --date "$startdate" "+%b %d %r")"; fi)
stopped=$(if [ -z "$stopdate" ]; then echo ""; else echo "$(date --date "$stopdate" "+%b %d %r")"; fi)

if  [[ $(pgrep -u $(whoami) -f "$stop") ]]
then
p="$warn <font face="verdana" color="orange"> Stopping...</font>"
elif  [[ $(pgrep -u $(whoami) -f "$Userver") ]]
then
p="$warn <font face="verdana" color="orange"> Updating Server...</font>"
elif  [[ $(pgrep -u $(whoami) -f "$Umods") ]]
then
p="$warn <font face="verdana" color="orange"> Downloading Mods...</font>"
elif  [[ $(pgrep -u $(whoami) -f "$start") ]]
then
p="$warn <font face="verdana" color="orange"> Starting...</font>"
elif [[ $(pgrep -u $(whoami) -f "$process") ]]
then
p="$up <font face="verdana" color="green"> Running</font>"
elif [ -z "$stopped" ]
then
p="$warn <font face="verdana" color="orange"> Crashed </font>"
else
p="$down <font face="verdana" color="red"> Stopped </font>"
fi


#=========== RCON STATUS + More ===========

case $round in

1 )
    rconpull=$($srcon listplayers 2>&1)
    if [ "$(echo "$rconpull" | grep "Connection refused")" != "" ]
    then
    r="$down <font face="verdana" color="red"> Connection Refused </font>"
    elif [ "$(echo "$rconpull" | grep "Couldn't Authenticate")" != "" ]
    then
    r="$warn <font face="verdana" color="Orange"> Couldn't Authenticate </font>"
    elif [ "$(echo "$rconpull" | grep "received")" != "" ] || [ "$(echo "$rconpull" | grep "No Players Connected")" != "" ] || [ "$(echo "$rconpull" | head -1)" = "" ] 
    then
	if [ "$(echo "$rconpull" | head -1)" = "" ]
	then
	plist=$(echo "<table>")
	clean=$(echo "$rconpull" | sed '/^\s*$/d' )
	while read -r player
	do
	pname=$(echo "$player" | sed '/^\s*$/d' | cut -c 4- | cut -d',' -f1)
	pid=$(echo "$player" | sed '/^\s*$/d' | cut -c 4- | cut -d',' -f2 | tr -d ' ')
	plist+=$(echo "<tr>
	<td><a href="http://steamcommunity.com/profiles/$pid " target="_blank">View Profile -</a></td>
	<td>$pname</td>
	</tr>
	")
	done <<< "$clean"
	plist+=$(echo "</table>")
	echo "$plist" > $html3
	else
	echo "$rconpull" > $html3
	fi
    r="$up <font face="verdana" color="green"> Server Received </font>"
    elif [ "$(echo "$rconpull" | grep "Password Refused")" != "" ]
    then
    r="$warn <font face="verdana" color="Orange"> Password Refused </font>"
    else
    r="$down <font face="verdana" color="red"> HALP - $(echo "$rconpull")</font>"
    fi
	round=2
    ;;
2 )
    rconpull=$($srcon getchat 2>&1)
    if [ "$(echo "$rconpull" | grep "Connection refused")" != "" ]
    then
    r="$down <font face="verdana" color="red"> Connection Refused </font>"
    elif [ "$(echo "$rconpull" | grep "Couldn't Authenticate")" != "" ]
    then
    r="$warn <font face="verdana" color="Orange"> Couldn't Authenticate </font>"
    elif [ "$(echo "$rconpull" | grep "received")" != "" ]
    then
    r="$up <font face="verdana" color="green"> Server Received </font>"
    elif [ "$(echo "$rconpull" | grep "Password Refused")" != "" ]
    then
    r="$warn <font face="verdana" color="Orange"> Password Refused </font>"
    elif [ "$(echo "$rconpull" | grep " command not found")" = "" ]
    then
	clean=$(echo "$rconpull" | sed '/^\s*$/d' )
	unset chat
	while read -r chatline
	do
        chat+=$(echo -e "\n<b>$(date "+[%m/%d %H:%M]")</b>$chatline<br>")
	done <<< "$clean"
	echo "$chat" >> $html4
    r="$up <font face="verdana" color="green"> Server Received </font>"
    else
    r="$down <font face="verdana" color="red"> HALP - $(echo "$rconpull")</font>"
    fi
	round=1
    ;;
esac

#=========== WORLD SAVE DATE ===========
wfile=$dir/serverfiles/ShooterGame/Saved/SavedArks/$worldsave
wdiff=$(expr $(date +%s) - $(date -r $wfile +%s))
wsave=$(date -r $wfile "+%b %d %r")


if [ -f "$wfile" ]
then

    if [ $wdiff -gt 930 ]
    then
	if [ "$(echo "$rconpull" | grep "received")" != "" ]
	then
	echo "rcon is up, world save is old. Saving."
	$srcon saveworld
	fi
    w="$down <font face="verdana" color="red">$(echo $wsave) </font>"
    else
    w="$up <font face="verdana" color="green">$(echo $wsave) </font>"
    fi

else
w="$down <font face="verdana" color="red">$worldsave Missing </font>"
fi


if [ $count -gt $maxcount ]
then
echo "Running Server/Mod Update"
modpulldate=$(date +"%b %d %r PST")

 #=========== MOD UPDATES ===========
 config="$dir/serverfiles/ShooterGame/Saved/Config/LinuxServer/GameUserSettings.ini"
 modlist=$(grep "ActiveMods" $config | sed 's/ActiveMods=//g' | sed 's/,/ /g')

 modpull () {
    up="<img src="/images/up.png"  width="12" height="12" align="justify">"
    down="<img src="/images/down.png"  width="12" height="12" align="justify">"
    warn="<img src="/images/warning.png"  width="12" height="12" align="justify">"

    source ~/arkpagesource
    mod=$1
    moddir="$dir/serverfiles/Engine/Binaries/ThirdParty/SteamCMD/Linux/steamapps/workshop/content/346110"
    steamurl="https://steamcommunity.com/sharedfiles/filedetails/?id="
    tmppull=$(curl -s $steamurl$mod)
    modname=$(echo "$tmppull" | grep "workshopItemTitle" | sed 's/<div class="workshopItemTitle">//g' | sed 's/<\/div>//g' | sed 's/\r//g' | sed -e 's/^[ \t]*//' )
    moddate=$(echo "$tmppull"| grep "detailsStatRight" | grep "@" | tail -1 | sed 's/<div class="detailsStatRight">//g' | sed 's/<\/div>//g' | sed 's/@//g')
    ourmoddate=$(date -r $moddir/$mod)

 if [ $(date --date "$moddate" +%s) -gt $(date --date "$ourmoddate" +%s) ]
 then
    status="$warn <font face="verdana" color="orange">UPDATE</font>"
 else
    status="$up <font face="verdana" color="green">OK</font>"
 fi

    echo "
    <tr>
    <td>
    <div class="tooltip">$status<span class="tooltiptext">Pull:$(date --date "$moddate" "+%b %d %r")<br>Our:$(date --date "$ourmoddate" "+%b %d %r")</span></div>
    </td>
    <td>$mod</td>
    <td><a href="$steamurl$mod" target="_blank">$modname</a></td>
    </tr>
    "
 }

 export -f modpull

 output=$(parallel -k "modpull" ::: $modlist)

 if [ "$(echo "$output" | grep ">UPDATE<")" != "" ]
  then
    modstatus="$warn <font face="verdana" color="orange">Update Available</font>"
  else
    modstatus="$up <font face="verdana" color="green">Up to Date</font>"
 fi

 #=========== SERVER UPDATES ===========
 devbuild=$(curl -s https://steamdb.info/app/376030/depots/?branch=public | grep "app-json" | cut -c45-51)
 ourbuild=$(grep -i "buildid" $dir/serverfiles/steamapps/appmanifest_376030.acf | awk '{print $2}' | sed 's/"//g')

 if [ $devbuild -gt $ourbuild ]
 then
 build="$warn <font face="verdana" color="orange">Update Available</font>"
 else
 build="$up <font face="verdana" color="green">Up to Date</font>"
 fi

count=1

else
count=$(expr $count + 1)
fi



#===========  FINAL OUTPUT ===========

echo '
<div style="border-style: groove;border-width: 5px; width: 97%">
'$banner'
<center><FONT FACE="garamond"><b>Pull:</b> '$(date +"%b %d %r PST")'</FONT></center>
<table>
  <tr>
    <td><b>Started:</b></td>
    <td><mark><b>'$started'</b></mark></td>
  </tr>
  <tr>
    <td><b>Stopped:</b></td>
    <td><mark><b>'$stopped'</b></mark></td>
  </tr>
  <tr>
    <td><b>Server Process:</b></td>
    <td>'$p'</td>
  </tr>
  <tr>
    <td><b>Remote Console:</b></td>
    <td>'$r'</td>
  </tr>
  <tr>
    <td><b><div class="tooltip">Last World Save:<span class="tooltiptext">Every 15 Minutes</span></div></b></td>
    <td>'$w'</td>
  </tr>
</table>
</div>

<h2>Update Status + Mod List</h2>
<div style="border-left: groove;border-right: groove;border-top: groove;border-width: 5px; width: 97%">
<center><FONT FACE="garamond"><b>Pull:</b> '$modpulldate'</FONT></center>
<table>
  <tr>
    <td><div class="tooltip"><a href="https://steamdb.info/app/376030/depots/?branch=public" target="_blank">Server Build:&nbsp;<span class="tooltiptext">DevBuild:'$devbuild'<br>OurBuild:'$ourbuild'</span></a></div></td>
    <td>'$build'</td>
    <td>&nbsp;&nbsp;
    <td><b>Server Mods:&nbsp;</b></td>
    <td>'"$modstatus"'</td>
  </tr>
</table>
</div>
' > $html

echo '
<table id="modtable">
 <th>Status</th>
 <th>ID</th>
 <th>Name</th>
'"$output"'
</table>


' > $html2


sleep $sleep
done
