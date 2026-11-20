; Instalador do BrUMaRe para Windows (Inno Setup 6)
; Compilado pelo GitHub Actions (.github/workflows/windows.yml) ou à mão:
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\windows\brumare.iss
#define AppName "BrUMaRe"
#ifndef AppVersion
  #define AppVersion "1.3.0"
#endif
#define AppPublisher "Bruno Henrique Dourado Macedo"
#define AppURL "https://brunohdmacedo.tech/brumare/"

[Setup]
LicenseFile=..\..\LICENSE
AppId={{8E2F0D6B-5C1A-4B7E-9F3D-B2A1C7E4D901}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL=https://github.com/brunohdmacedo/brumare/releases
DefaultDirName={autopf}\BrUMaRe
DefaultGroupName=BrUMaRe
DisableProgramGroupPage=yes
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\..\dist
OutputBaseFilename=BrUMaRe-Setup-{#AppVersion}
SetupIconFile=..\..\assets\brumare.ico
UninstallDisplayIcon={app}\BrUMaRe.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ChangesEnvironment=yes

[Languages]
Name: "ptbr"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"
Name: "addpath"; Description: "Adicionar o comando 'brumare' (linha de comando) ao PATH"; GroupDescription: "Linha de comando:"; Flags: unchecked

[Files]
Source: "..\..\dist\BrUMaRe.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\brumare.exe"; DestDir: "{app}\cli"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion
Source: "..\..\LICENCA.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\CITATION.cff"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\brumare.bib"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\brumare-tutorial.pdf"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\BrUMaRe"; Filename: "{app}\BrUMaRe.exe"
Name: "{group}\Tutorial do BrUMaRe (PDF)"; Filename: "{app}\brumare-tutorial.pdf"
Name: "{group}\Site do BrUMaRe"; Filename: "{#AppURL}"
Name: "{group}\Licença do BrUMaRe (GPL-3.0)"; Filename: "{app}\LICENSE.txt"
Name: "{group}\Desinstalar o BrUMaRe"; Filename: "{uninstallexe}"
Name: "{autodesktop}\BrUMaRe"; Filename: "{app}\BrUMaRe.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\cli"; Tasks: addpath; Check: NeedsAddPath(ExpandConstant('{app}\cli'))

[Run]
Filename: "{app}\BrUMaRe.exe"; Description: "Abrir o BrUMaRe agora"; Flags: nowait postinstall skipifsilent

[Code]
function NeedsAddPath(Param: string): boolean;
var OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then begin Result := True; exit; end;
  Result := Pos(';' + Uppercase(Param) + ';', ';' + Uppercase(OrigPath) + ';') = 0;
end;
