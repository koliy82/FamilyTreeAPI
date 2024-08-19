apt-get update && apt-get upgrade
apt-get install libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxkbcommon-x11-0 -y
apt-get install libgl1-mesa-glx libglib2.0-0 libxcb-icccm4 libxcb-icccm4-dev libqt5pdf5 graphviz graphviz-dev -y
apt-get install build-essential -y
gcc --version

apt-get install libtiff5-dev -y
ln -s /usr/lib/x86_64-linux-gnu/libtiff.so.6 /usr/local/lib/python3.10/site-packages/PyQt5/Qt5/plugins/imageformats/libtiff.so.5
# apt-get install libxcb-randr0-dev libxcb-xtest0-dev libxcb-xinerama0-dev libxcb-shape0-dev libxcb-xkb-dev -y

pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install networkx[default,extra] pygraphviz pydot lxml
python -m app.main