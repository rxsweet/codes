#准备好所需文件
echo "down clash & lite & proxychains.conf file : begin !"
#wget -O clash.gz https://github.com/Dreamacro/clash/releases/download/v1.12.0/clash-linux-amd64-v1.12.0.gz
wget -O clash.gz https://raw.githubusercontent.com/rxsweet/all/main/githubTools/clash-linux-amd64-v1.11.4.gz
gunzip clash.gz
#wget -O lite.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.13.0/lite-linux-amd64-v0.13.0.gz
wget -O lite.gz https://raw.githubusercontent.com/rxsweet/all/main/githubTools/lite-linux-amd64-v0.11.2m.gz
gunzip lite.gz
wget -O proxychains.conf https://raw.githubusercontent.com/rxsweet/codes/main/grabNode-main/utils/litespeedtest/proxychains.conf
#cp ./utils/litespeedtest/proxychains.conf ./proxychains.conf
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
sudo nohup proxychains ./lite --config ./utils/litespeedtest/lite_config.json --test https://raw.githubusercontent.com/rxsweet/crawlNode/main/sub/sources/noCheckClash.yml >speedtest.log 2>&1 &


