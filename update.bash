SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ..
sudo rm -r ./file-sender-through-wifi-bt/
git clone https://github.com/JRodez/file-sender-through-wifi-bt.git
sleep 1
echo LS
ls
cd file-sender*
# cd ../file-sender-through-wifi-bt 
echo OK


