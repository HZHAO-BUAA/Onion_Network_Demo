@echo off

netsh -c interface ipv4 add address name="无线网络连接" addr=172.16.1.1 mask=255.255.0.0
netsh -c interface ipv4 add address name="无线网络连接" addr=172.16.2.1 mask=255.255.0.0
netsh -c interface ipv4 add address name="无线网络连接" addr=172.16.3.2 mask=255.255.0.0
netsh -c interface ipv4 add address name="无线网络连接" addr=172.16.4.2 mask=255.255.0.0
netsh -c interface ipv4 add address name="无线网络连接" addr=172.16.5.3 mask=255.255.0.0

echo Network configured!


python Main.py

netsh -c interface ipv4 delete address name="无线网络连接" addr=172.16.1.1 
netsh -c interface ipv4 delete address name="无线网络连接" addr=172.16.2.1 
netsh -c interface ipv4 delete address name="无线网络连接" addr=172.16.3.2 
netsh -c interface ipv4 delete address name="无线网络连接" addr=172.16.4.2 
netsh -c interface ipv4 delete address name="无线网络连接" addr=172.16.5.3 
