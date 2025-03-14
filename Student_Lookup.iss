[Setup]
; NOTE: The value of AppId uniquely identifies this application
AppId=e3b4b47e-92f3-430f-b8cc-ba6543e437b1
AppName=Student Lookup
AppVersion=1.0.1
AppPublisher=Digiasati.com
DefaultDirName={pf}\Student Lookup
DefaultGroupName=Student Lookup
OutputBaseFilename=StudentLookupInstaller
SetupIconFile=Student_Lookup.ico
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\Student_Lookup.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Student_Lookup.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "Student_Lookup.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Student Lookup"; Filename: "{app}\Student_Lookup.exe"; IconFilename: "{app}\Student_Lookup.ico"
Name: "{group}\Uninstall Student Lookup"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Student Lookup"; Filename: "{app}\Student_Lookup.exe"; IconFilename: "{app}\Student_Lookup.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\Student_Lookup.exe"; Description: "{cm:LaunchProgram,Student Lookup}"; Flags: postinstall nowait skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  // Optional: Check for previous versions and uninstall if needed
  if RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Student Lookup') then
  begin
    if MsgBox('A previous version of Student Lookup is installed. Do you want to uninstall it first?', 
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      // This assumes a standard uninstall process
      Exec('rundll32.exe', 'shell32.dll,Control_RunDLL appwiz.cpl', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
      Result := True;
    end
    else
    begin
      Result := False;
    end;
  end
  else
  begin
    Result := True;
  end;
end;