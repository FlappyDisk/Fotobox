# Fotobox
Entwicklung Fotobox

# Installs
sudo apt install python3 python3-venv python3-full pip libcamera-apps python3-picamera2 git
sudo apt update
sudo apt upgrade

# Git SSH
ssh-keygen
cat ~/.ssh/id_rsa.pub

# Git Init
git config --global user.name "<NAME>"
git config --global user.email "<EMAIL>"
mkdir fotobox
cd fotobox
git init
git branch -m master main
git pull
git remote add origin git@github.com:FlappyDisk/Fotobox.git
