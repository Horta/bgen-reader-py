set PATH=%PYTHON%;%PYTHON%\Scripts;%PATH%
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/horta/zlib.install/master/install.bat', 'install-zlib.bat')" && install-zlib.bat
set PATH=%programfiles%\zlib\bin;%PATH%
set LIBRARY_INC=%programfiles%\zlib\include;%LIBRARY_INC%
set LIBRARY_LIB=%programfiles%\zlib\lib;%LIBRARY_LIB%
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/horta/zstd.install/master/install.bat', 'install-zstd.bat')" && call install-zstd.bat
set PATH=%programfiles%\zstd\bin;%PATH%
set LIBRARY_INC=%programfiles%\zstd\include;%LIBRARY_INC%
set LIBRARY_LIB=%programfiles%\zstd\lib;%LIBRARY_LIB%
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/horta/almosthere/master/install.bat', 'install-athr.bat')" && call install-athr.bat
 set PATH=%programfiles%\athr\bin;%PATH%
 set LIBRARY_INC=%programfiles%\athr\include;%LIBRARY_INC%
 set LIBRARY_LIB=%programfiles%\athr\lib;%LIBRARY_LIB%
 powershell -Command "(New-Object Net.WebClient).DownloadFile('https://raw.githubusercontent.com/limix/bgen/master/install.bat', 'install-bgen.bat')" && install-bgen.bat
 set PATH=%programfiles%\bgen\bin;%PATH%
 set LIBRARY_INC=%programfiles%\bgen\include;%LIBRARY_INC%
 set LIBRARY_LIB=%programfiles%\bgen\lib;%LIBRARY_LIB%