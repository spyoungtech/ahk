.\venv\Scripts\activate.ps1
coverage run -m behave .\tests\features --format=progress2 --junit
if ($LastExitCode -ne 0) {
  $failure = 1
} else {
  $failure = 0
}
coverage run -a -m pytest .\tests\unittests --junitxml=reports\pytestresults.xml
if ($LastExitCode -ne 0) {
  $failure = 1
}
coverage report
$wc = New-Object 'System.Net.WebClient';
Get-ChildItem .\reports |
Foreach-Object {
   $wc.UploadFile("https://ci.appveyor.com/api/testresults/junit/$($env:APPVEYOR_JOB_ID)", (Resolve-Path $_.FullName))
}
if ($failure -ne 0) { throw }
deactivate
