#!/bin/bash
echo "Content-Type: text/html"
echo
read input

#get custom stuff
source ~/dir.sh

newlist=$(echo $input | sed 's/&/ /g')
key=$(echo "$newlist" | awk '{print $1}' | sed 's/.*=//g')
server=$(echo "$newlist" | awk '{print $2}' | sed 's/.*=//g')



if [ "$key" = $(cat $dir/key) ]
then

#if [ "$server" = "Start" ]
#then
#       echo "<h2>Server Started</h2>"
#       echo "Please wait up to 5min for server to come up<br>"
#       (echo "<pre> $($dir/arkserver start) </pre>")
#elif [ "$server" = "Stop" ]
#then 
#       echo "<h2>Server Stopped</h2>"
#       echo "<pre> $($dir/arkserver stop) </pre>"
#elif [ "$server" = "Save" ]
#then
#      echo "<h2>Server World Saved</h2>"
#      echo "<pre> $($srcon saveworld) </pre>"
#fi

case $server in

Start )
       echo "<h2>Server Started</h2>"
       echo "Please wait up to 5min for server to come up<br>"
       (echo "<pre> $($dir/arkserver start) </pre>")
;;
Stop )
       echo "<h2>Server Stopped</h2>"
       echo "<pre> $($dir/arkserver stop) </pre>"
;;
Save )
      echo "<h2>Server World Saved</h2>"
      echo "<pre> $($srcon saveworld) </pre>"
;;
* )
echo "something broke"
echo "$input";;
esac

else
echo "<h1>Invalid Key</h1>"
fi



