# amed <a id="amed"/>
Tools for processing AMED data

[[back to top]](#amed)

## Requirements

Requires:
- the regex module from https://bitbucket.org/mrabarnett/mrab-regex. 
The built-in re module is not sufficient.
- the sqlite3 module (https://docs.python.org/3/library/sqlite3.html), 
which may be package as part of the Python standard library.

[[back to top]](#amed)

## Installation

### Direct download
Pre-compiled executable files are provided in the folder [/exe](https://github.com/victoriamorris/amed/tree/master/exe).

### From source code in GitHub
```shell
python -m pip install git+https://github.com/victoriamorris/AMED.git@main
```

To create stand-alone executable (.exe) files for individual scripts 
from downloaded source code:

```python
python -m PyInstaller bin/<script_name>.py -F
```

Executable files will be created in the folder \dist, 
and should be copied to an executable path.

Both of the above commands can be carried out by running the shell script:

```shell
compile_amed.sh
```
    
[[back to top]](#amed)

## Overview
$${\color{green}amed_pre.exe}$$ is used to process ETOC records before import to Excel.
Processed records are then imported to the spreadsheet $${\color{green}AMED processing.xlsm}$$, where index terms can be added.
The records are exported from Excel, and processing is completed using $${\color{green}amed_post.exe}$$.