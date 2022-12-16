# !/bin/sh

value=`cat reload`
# pstree -ap|grep gunic
echo "Stopping PID $value..."
sudo kill -9 $value
