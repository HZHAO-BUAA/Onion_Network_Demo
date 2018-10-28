#! /bin/bash  
echo Srtarting shallot network demo...
echo Configuring newwork alias, password needed:

cd "$(dirname -- "$0")"

sudo ifconfig lo0 alias 172.16.1.1
sudo ifconfig lo0 alias 172.16.2.1
sudo ifconfig lo0 alias 172.16.3.2
sudo ifconfig lo0 alias 172.16.4.2
sudo ifconfig lo0 alias 172.16.5.3
sudo ifconfig lo0 alias 172.16.6.4
sudo ifconfig lo0 alias 172.16.7.5
sudo ifconfig lo0 alias 172.16.8.6

echo Network configured!

python Main.py

sudo ifconfig lo0 -alias 172.16.1.1
sudo ifconfig lo0 -alias 172.16.2.1
sudo ifconfig lo0 -alias 172.16.3.2
sudo ifconfig lo0 -alias 172.16.4.2
sudo ifconfig lo0 -alias 172.16.5.3
sudo ifconfig lo0 -alias 172.16.6.4
sudo ifconfig lo0 -alias 172.16.7.5
sudo ifconfig lo0 -alias 172.16.8.6


