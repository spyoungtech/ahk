KEEPALIVE := Chr(57344)

SetTimer, keepalive, 1000

keepalive:
global KEEPALIVE
FileAppend, %KEEPALIVE%`n, *, UTF-8

#n::
FileAppend, %A_ThisHotkey%`n, *, UTF-8
return
