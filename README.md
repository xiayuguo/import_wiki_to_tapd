# Import_Wiki_To_Tapd
Import Wiki to Tapd.

# Env
```
pip install -r requirements.txt
```

# Usage
```
usage: main.py [-h] -u xxx@mail.com -p ****** [-F /home/hugo/project]
               [-f /home/hugo/project/home.md] [-d {0,1}] [-e EXECUTABLEPATH]
               [-g GIT] [-c CLASSIFY] [-v]

Import Wiki to Tapd.

optional arguments:
  -h, --help            show this help message and exit
  -u xxx@mail.com, --username xxx@mail.com
                        username for tapd
  -p ******, --password ******
                        password for tapd
  -F /home/hugo/project, --folder /home/hugo/project
                        folder path of import files
  -f /home/hugo/project/home.md, --file /home/hugo/project/home.md
                        file path of import files
  -d {0,1}, --debug {0,1}
                        headless status
  -e EXECUTABLEPATH, --executablePath EXECUTABLEPATH
                        path to a Chromium or Chrome executable
  -g GIT, --git GIT     git repository url
  -c CLASSIFY, --classify CLASSIFY
                        wiki parent name
  -v, --version         show program's version number and exit
```
