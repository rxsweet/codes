echo "down subconverter.tar.gz file : begin !"
wget -O subconverter.tar.gz https://raw.githubusercontent.com/rxsweet/all/main/githubTools/subconverter_linux64.tar.gz
tar -zxvf subconverter.tar.gz -C ./
chmod +x ./subconverter/subconverter && nohup ./subconverter/subconverter >./subconverter.log 2>&1 &
echo "download done !"
