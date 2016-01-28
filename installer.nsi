; Turn off old selected section
; 26 06 2015: Fadiga Ibrahima

; -------------------------------
; Start

  !define MUI_PRODUCT "ORTM-VC"
  !define MUI_FILE "ortm-vc"
  !define MUI_VERSION "1.0"
  !define MUI_BRANDINGTEXT "${MUI_PRODUCT} ${MUI_VERSION}"
  ;CRCCheck On

  !include "${NSISDIR}\Contrib\Modern UI\System.nsh"


;---------------------------------
;General

  OutFile "Install-${MUI_PRODUCT} ${MUI_VERSION}.exe"
  ShowInstDetails "nevershow"
  ShowUninstDetails "nevershow"
  ;SetCompressor off

  !define MUI_ICON "flash-video-encoder.ico"
  !define MUI_UNICON "flash-video-encoder.ico"


;--------------------------------
;Folder selection page

  InstallDir "C:\${MUI_PRODUCT}"


;--------------------------------
;Data

  ;LicenseData "README.txt"


;--------------------------------
;Installer Sections
;Section "install" Installation info
Section "install"

;Add files
  SetOutPath "$INSTDIR"

  ;File "${MUI_FILE}.exe"
  ;File "README.txt"

  ; List of files/folders to copy
  File /r dist\*.*
  File *.dll
  File *.manifest
  File ffmpeg.exe
  File flash-video-encoder.ico
  File logo_ortm.png
  File logo_tm2.png
  File /r toast

;create desktop shortcut
  CreateShortCut "$DESKTOP\${MUI_PRODUCT}.lnk" "$INSTDIR\${MUI_FILE}.exe" parameters "$INSTDIR\${MUI_ICON}"

;create start-menu items
  CreateDirectory "$SMPROGRAMS\${MUI_PRODUCT}"
  CreateShortCut "$SMPROGRAMS\${MUI_PRODUCT}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\${MUI_ICON}" 0
  CreateShortCut "$SMPROGRAMS\${MUI_PRODUCT}\${MUI_PRODUCT}.lnk" "$INSTDIR\${MUI_FILE}.exe" "" "$INSTDIR\${MUI_ICON}" 0

;write uninstall information to the registry
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${MUI_PRODUCT}" "DisplayName" "${MUI_PRODUCT} (remove only)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${MUI_PRODUCT}" "UninstallString" "$INSTDIR\Uninstall.exe"

  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


;--------------------------------
;Uninstaller Section
Section "Uninstall"

;Delete Files
RMDir /r "$INSTDIR\*.*"

;Remove the installation directory
RMDir "$INSTDIR"

;# now delete installed file
;delete $INSTDIR\*.exe
;delete $INSTDIR\*.dll
;delete $INSTDIR\*.manifest
;delete $INSTDIR\*.lib
;delete $INSTDIR\*.zip
;delete $INSTDIR\*.png
;delete $INSTDIR\*.ico
;delete $INSTDIR\*.pyd
;
;RMDir /r $INSTDIR\build
;RMDir /r $INSTDIR\toast
;RMDir /r $INSTDIR\dist
;RMDir /r $INSTDIR\tcl

;Delete Start Menu Shortcuts
  Delete "$DESKTOP\${MUI_PRODUCT}.lnk"
  Delete "$SMPROGRAMS\${MUI_PRODUCT}\*.*"
  RmDir  "$SMPROGRAMS\${MUI_PRODUCT}"

;Delete Uninstaller And Unistall Registry Entries
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\${MUI_PRODUCT}"
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${MUI_PRODUCT}"

SectionEnd

;--------------------------------
Function .onInstSuccess
   SetOutPath $INSTDIR
   ExecShell "" '"$INSTDIR\convert-video-tk.exe"'
FunctionEnd

Function un.onUninstSuccess
  MessageBox MB_OK "You have successfully uninstalled ${MUI_PRODUCT}."
FunctionEnd

;eof
