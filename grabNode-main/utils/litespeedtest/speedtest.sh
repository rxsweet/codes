#准备好所需文件
echo "down clash & lite & proxychains.conf file : begin !"
wget -O clash.gz https://raw.githubusercontent.com/rxsweet/all/main/githubTools/clash-linux-amd64-v1.11.4.gz
gunzip clash.gz
wget -O lite.gz https://raw.githubusercontent.com/rxsweet/all/main/githubTools/lite-linux-amd64-v0.11.2m.gz
gunzip lite.gz
wget -O proxychains.conf https://raw.githubusercontent.com/rxsweet/fetchProxy/main/utils/litespeedtest/proxychains.conf
echo "download done !"

#初始化 Clash
chmod +x ./clash && ./clash &
#安装并配置 proxychains
sudo apt-get install proxychains
sudo chmod 777 ../../../../../etc/proxychains.conf
mv -f proxychains.conf ../../../../../etc/proxychains.conf

#开始运行 Clash
sudo pkill -f clash
./clash -f ./utils/litespeedtest/clash_config.yml &

#运行 LiteSpeedTest
echo "lite speed test start !"
chmod +x ./lite
sudo nohup proxychains ./lite --config ./utils/litespeedtest/lite_config.json --test https://raw.githubusercontent.com/rxsweet/fetchProxy/main/sub/sources/nocheckClash.yaml >speedtest.log 2>&1 &


