$wc = New-Object 'System.Net.WebClient';
Get-ChildItem .\reports |
Foreach-Object {
   $wc.UploadFile("https://ci.appveyor.com/api/testresults/junit/$($env:APPVEYOR_JOB_ID)", (Resolve-Path $_.FullName))
}
