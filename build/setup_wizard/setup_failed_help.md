If you have encountered something error in installation, please check and 
follow the steps to fix this problem:

- I'm using Windows 7 (32-bit)
    - The error shows 'DLL load failed...'
        - Go to 'depsland/build/windows_patch/windows-7-sp1-32bit' folder
        - Setup 'KB2999226-x86.msu' and 'KB3063858-x86.msu'
        - Restart your computer
        - Retry to setup this program
    - The error shows 'api-ms-core-... is misssing'
        - Go to 'depsland/build/windows_patch/windows-7-sp1-32bit' folder
        - Setup 'KB2999226-x86.msu'
        - Retry to setup this program (no need to restart computer)
    
- I'm using Windows 7 (64-bit)
    - The error shows 'DLL load failed...'
        - Go to 'depsland/build/windows_patch/windows-7-sp1-64bit' folder
        - Setup 'KB2999226-x64.msu' and 'KB3063858-x64.msu'
        - Restart your computer
        - Retry to setup this program
    - The error shows 'api-ms-core-... is misssing'
        - Go to 'depsland/build/windows_patch/windows-7-sp1-64bit' folder
        - Setup 'KB2999226-x64.msu'
        - Retry to setup this program (no need to restart computer)

- I'm using Windows 8 (32-bit)
    - Go to 'depsland/build/windows_patch/windows-8-32bit' folder
    - Setup 'vcredist-2015-x86.exe'
    - Retry to setup this program (no need to restart computer)
    
- I'm using Windows 8 (64-bit)
    - Go to 'depsland/build/windows_patch/windows-8-64bit' folder
    - Setup 'vcredist-2015-x64.exe'
    - Retry to setup this program (no need to restart computer)
    
- I have other problem

    Please contact the supplier or depsland project owner (mail to
    likianta@foxmail.com) for more help.
