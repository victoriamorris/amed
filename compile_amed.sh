python setup.py install
pyinstaller amed_tools.py -F
read -p "Press [Enter]"
mv dist/amed_tools.exe amed_tools.exe
rmdir dist
rm -rf __pycache__
rm -rf build
read -p "Press [Enter]"