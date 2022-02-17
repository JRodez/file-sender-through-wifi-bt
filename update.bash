SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
sudo rm -r ./file-sender-through-wifi-bt/
git clone https://github.com/JRodez/file-sender-through-wifi-bt.git
cd file-sender-through-wifi-bt