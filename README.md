# Natural Language Processing Demos

These demos are presented and maintained by the National University of Singapore, Massey University and University of Auckland.

# How to start the service
Due to the security concern, Ask Mingzhe Du (mingzhe@nus.edu.sg) to get the service start command.

# How to stop the service
pstree -ap|grep gunicorn
sudo kill -9 PROCESS_ID


# Add Swap space
sudo swapoff -a
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo swapon --show