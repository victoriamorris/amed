python -m PyInstaller bin/amed_pre.py -F
mv dist/amed_pre.exe exe/amed_pre.exe
python -m PyInstaller bin/amed_post.py -F
mv dist/amed_post.exe exe/amed_post.exe
rm -rf amed_tools/__pycache__
rm -rf build
rm *.spec
read -p "Press [Enter]"