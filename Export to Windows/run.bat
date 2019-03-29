"C:\Program Files\iSpy\iSpy.exe" commands "allon"
timeout 10 >nul
"C:\Program Files\iSpy\iSpy.exe" commands "record"
timeout 5 >nul
python MonoWindows.py
timeout 10 >nul
"C:\Program Files\iSpy\iSpy.exe" commands "recordstop"
timeout 10 >nul
"C:\Program Files\iSpy\iSpy.exe" commands "alloff"
