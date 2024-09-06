#apt-get update && apt-get upgrade
#apt-get install libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxkbcommon-x11-0 -y
#apt-get install libgl1-mesa-glx libglib2.0-0 libxcb-icccm4 libxcb-icccm4-dev libqt5pdf5 graphviz graphviz-dev -y
#apt-get install build-essential -y
#gcc --version
#
#apt-get install libtiff5-dev -y
#ln -s /usr/lib/x86_64-linux-gnu/libtiff.so.6.0.0 /usr/lib/x86_64-linux-gnu/libtiff.so.5
#ln -s /usr/lib/x86_64-linux-gnu/libtiff.so.6.0.0 /usr/local/lib/python3.10/site-packages/PyQt5/Qt5/plugins/imageformats/libtiff.so.5
#ln -s /usr/lib/x86_64-linux-gnu/libtiff.so.6.0.0 /usr/local/lib/python3.10/site-packages/PyQt5/Qt5/plugins/imageformats/libtiff.so
## apt-get install libxcb-randr0-dev libxcb-xtest0-dev libxcb-xinerama0-dev libxcb-shape0-dev libxcb-xkb-dev -y
#
#pip install --upgrade pip
#pip install --no-cache-dir -r requirements.txt
#pip install networkx[default,extra] pygraphviz pydot lxml
#python -m app.main

echo "build" > README.md

apt-get update && apt-get upgrade
apt-get install --no-install-recommends -y
apt-get install build-essential -y
apt-get install libgl1-mesa-glx libqt5pdf5 -y
apt-get install libtiff5-dev -y
ln -s /usr/lib/x86_64-linux-gnu/libtiff.so.6.0.0 /usr/lib/x86_64-linux-gnu/libtiff.so.5
pip install --upgrade pip
pip install poetry
apt-get autoremove -y
poetry config virtualenvs.create false
poetry install --only main
poetry run pip install pyqt5==5.15.11
apt-get install graphviz graphviz-dev -y
apt-get install python-dev graphviz libgraphviz-dev pkg-config -y
apt-get install python3-dev graphviz libgraphviz-dev pkg-config -y
echo | ete3 upgrade-external-tools

chmod -R --reference=/usr/share/fonts/opentype /usr/share/fonts/googlefonts
fc-cache -fv
fc-list
fc-match Segoe UI Emoji

poetry update
poetry run pip install pygraphviz
python -m app.main