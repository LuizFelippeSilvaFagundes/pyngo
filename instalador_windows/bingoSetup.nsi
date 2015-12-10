;NSIS Modern User Interface

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"
  !include LogicLib.nsh  
  !include "WordFunc.nsh"
  !include "TextFunc.nsh"


;--------------------------------
;General

  !addplugindir ".\plugins"
  ;Name and file
  Name "Bingo AIM"
  OutFile "BingoSetup.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\BingoAIM"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\BingoAIM" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

  ;--------------------------------
  ;Variables
  Var Username
  Var StartMenuFolder  
;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  
  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\BingoAIM" 
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  
  !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English" ;first language is the default language
  !insertmacro MUI_LANGUAGE "Spanish"

;--------------------------------
;Reserve Files
  
  ;If you are using solid compression, files that are required before
  ;the actual installation should be stored first in the data block,
  ;because this will make your installer start faster.
  
  !insertmacro MUI_RESERVEFILE_LANGDLL
;--------------------------------
;Installer Sections

Section "BingoAIM" SecBingoAIM

	SetOutPath "$INSTDIR"
	
  	;ADD YOUR OWN FILES HERE...
	File /r sourceSetup\*.*
		
	;Create uninstaller
	WriteUninstaller "$INSTDIR\Uninstall.exe"
	
	AccessControl::GetCurrentUserName
	Pop $Username

	AccessControl::GrantOnFile "$INSTDIR"  "$Username" "FullAccess"
	Pop $R0
	${If} $R0 == error
		Pop $R0
		DetailPrint `AccessControl error: $R0`
		Abort
	${EndIf}

	!insertmacro MUI_STARTMENU_WRITE_BEGIN Application

	;Create shortcuts
	CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
	CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
	CreateShortCut "$SMPROGRAMS\$StartMenuFolder\bingoaim.lnk" "$INSTDIR\bingo.exe"

	!insertmacro MUI_STARTMENU_WRITE_END
	
	;Store installation folder
	WriteRegStr HKCU "Software\BingoAIM" "" "$INSTDIR"
		
SectionEnd

;--------------------------------
;Installer Functions

Function .onInit
	!insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecBingoAIM ${LANG_ENGLISH} "Bingo AIM"
  LangString DESC_SecBingoAIM ${LANG_SPANISH} "Bingo AIM"

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecBingoAIM} $(DESC_SecBingoAIM)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...
  ;Paro todo a saco
	
  Delete "$INSTDIR\Uninstall.exe"  

  RMDir /r "$INSTDIR"
  RMDir "$INSTDIR"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\bingoaim.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"  
  
  DeleteRegKey HKCU "Software\BingoAIM"

SectionEnd


;--------------------------------
;Uninstaller Functions

Function un.onInit

  !insertmacro MUI_UNGETLANGUAGE  
  
FunctionEnd



