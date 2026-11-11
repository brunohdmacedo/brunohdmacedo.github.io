; Instalador do Bruma para Windows (Inno Setup 6)
; Compilado pelo GitHub Actions (.github/workflows/windows.yml) ou à mão:
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\windows\bruma.iss
#define AppName "Bruma"
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif
#define AppPublisher "Bruno Henrique Dourado Macedo"
#define AppURL "https://brunohdmacedo.tech/bruma/"

[Setup]
AppId={{8E2F0D6B-5C1A-4B7E-9F3D-B2A1C7E4D901}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL=https://github.com/brunohdmacedo/bruma-dft/releases
DefaultDirName={autopf}\Bruma
DefaultGroupName=Bruma
DisableProgramGroupPage=yes
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\..\dist
OutputBaseFilename=Bruma-Setup-{#AppVersion}
SetupIconFile=..\..\assets\bruma.ico
UninstallDisplayIcon={app}\Bruma.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ChangesEnvironment=yes

[Languages]
Name: "ptbr"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"
Name: "addpath"; Description: "Adicionar o comando 'bruma' (linha de comando) ao PATH"; GroupDescription: "Linha de comando:"; Flags: unchecked

[Files]
Source: "..\..\dist\Bruma.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\bruma.exe"; DestDir: "{app}\cli"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\CITATION.cff"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\bruma.bib"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\bruma-tutorial.pdf"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Bruma"; Filename: "{app}\Bruma.exe"
Name: "{group}\Tutorial do Bruma (PDF)"; Filename: "{app}\bruma-tutorial.pdf"
Name: "{group}\Site do Bruma"; Filename: "{#AppURL}"
Name: "{group}\Desinstalar o Bruma"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Bruma"; Filename: "{app}\Bruma.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\cli"; Tasks: addpath; Check: NeedsAddPath(ExpandConstant('{app}\cli'))

[Run]
Filename: "{app}\Bruma.exe"; Description: "Abrir o Bruma agora"; Flags: nowait postinstall skipifsilent

[Code]
function NeedsAddPath(Param: string): boolean;
var OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then begin Result := True; exit; end;
  Result := Pos(';' + Uppercase(Param) + ';', ';' + Uppercase(OrigPath) + ';') = 0;
end;
