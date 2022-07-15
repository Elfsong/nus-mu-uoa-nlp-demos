# Natural Language Processing Demos

These demos are presented and maintained by the National University of Singapore, Massey University and University of Auckland.

# How to start the service
sudo env OPENAI_API_KEY=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  /home/nzsg_nlp_nus/miniconda3/bin/gunicorn -k gevent \ 
                                                                                                                        -w 1 \
                                                                                                                        -b 0.0.0.0:443 \
                                                                                                                        -preload \
                                                                                                                        --access-logfile ./logs/access.log \
                                                                                                                        --error-logfile ./logs/error.log \
                                                                                                                        --log-level DEBUG \
                                                                                                                        --certfile /etc/letsencrypt/live/nlp-platform.online/fullchain.pem \
                                                                                                                        --keyfile /etc/letsencrypt/live/nlp-platform.online/privkey.pem    

# How to stop the service
pstree -ap|grep gunicorn
sudo kill -9 PROCESS_ID


# Add Swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo swapon --show

