#Requires AutoHotkey >= 2.0-
{% for directive in directives %}
{% if directive.apply_to_hotkeys_process %}

{{ directive }}
{% endif %}
{% endfor %}


KEEPALIVE := Chr(57344)

stdout := FileOpen("*", "w", "UTF-8")
stdin  := FileOpen("*", "r `n", "UTF-8")

WriteStdout(s) {
    global stdout
    Critical "On"
    stdout.Write(s)
    stdout.Read(0)
    Critical "Off"
}

Crypt32 := DllCall("LoadLibrary", "Str", "Crypt32.dll", "Ptr")

b64decode(&pszString) {
    ; TODO load DLL globally for performance
    ; REF: https://docs.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptstringtobinaryw
    ;  [in]      LPCSTR pszString,  A pointer to a string that contains the formatted string to be converted.
    ;  [in]      DWORD  cchString,  The number of characters of the formatted string to be converted, not including the terminating NULL character. If this parameter is zero, pszString is considered to be a null-terminated string.
    ;  [in]      DWORD  dwFlags,    Indicates the format of the string to be converted. (see table in link above)
    ;  [in]      BYTE   *pbBinary,  A pointer to a buffer that receives the returned sequence of bytes. If this parameter is NULL, the function calculates the length of the buffer needed and returns the size, in bytes, of required memory in the DWORD pointed to by pcbBinary.
    ;  [in, out] DWORD  *pcbBinary, A pointer to a DWORD variable that, on entry, contains the size, in bytes, of the pbBinary buffer. After the function returns, this variable contains the number of bytes copied to the buffer. If this value is not large enough to contain all of the data, the function fails and GetLastError returns ERROR_MORE_DATA.
    ;  [out]     DWORD  *pdwSkip,   A pointer to a DWORD value that receives the number of characters skipped to reach the beginning of the -----BEGIN ...----- header. If no header is present, then the DWORD is set to zero. This parameter is optional and can be NULL if it is not needed.
    ;  [out]     DWORD  *pdwFlags   A pointer to a DWORD value that receives the flags actually used in the conversion. These are the same flags used for the dwFlags parameter. In many cases, these will be the same flags that were passed in the dwFlags parameter. If dwFlags contains one of the following flags, this value will receive a flag that indicates the actual format of the string. This parameter is optional and can be NULL if it is not needed.

    if (pszString = "") {
        return ""
    }

    cchString := StrLen(pszString)

    dwFlags := 0x00000001  ; CRYPT_STRING_BASE64: Base64, without headers.
    getsize := 0 ; When this is NULL, the function returns the required size in bytes (for our first call, which is needed for our subsequent call)
;    buff_size := 0 ; The function will write to this variable on our first call
    pdwSkip := 0 ; We don't use any headers or preamble, so this is zero
    pdwFlags := 0 ; We don't need this, so make it null

    ; The first call calculates the required size. The result is written to pbBinary
    success := DllCall("Crypt32.dll\CryptStringToBinary", "Ptr", StrPtr(pszString), "UInt", cchString, "UInt", dwFlags, "UInt", getsize, "UIntP", &buff_size := 0, "Int", pdwSkip, "Int", pdwFlags )
    if (success = 0) {
        return ""
    }

    ; We're going to give a pointer to a variable to the next call, but first we want to make the buffer the correct size using VarSetCapacity using the previous return value
    ret := Buffer(buff_size)

    ; Now that we know the buffer size we need and have the variable's capacity set to the proper size, we'll pass a pointer to the variable for the decoded value to be written to

    success := DllCall( "Crypt32.dll\CryptStringToBinary", "Ptr", StrPtr(pszString), "UInt", cchString, "UInt", dwFlags, "Ptr", ret.Ptr, "UIntP", &buff_size, "Int", pdwSkip, "Int", pdwFlags )
    if (success=0) {
        return ""
    }
    return StrGet(ret, "UTF-8")
}



{% for hotkey in hotkeys %}

{{ hotkey.keyname }}::
{
    WriteStdout("{{ hotkey._id }}`n")
    return
}
{% endfor %}

{% for hotstring in hotstrings %}
{% if hotstring.replacement %}
:{{ hotstring.options }}:{{ hotstring.trigger }}::
    hostring_{{ hotstring._id }}_func(hs) {
        replacement_b64 := "{{ hotstring._replacement_as_b64 }}"
        replacement := b64decode(&replacement_b64)
        Send(replacement)
    }
{% else %}
:{{ hotstring.options }}:{{ hotstring.trigger }}::
    hostring_{{ hotstring._id }}_func(hs) {
        WriteStdout("{{ hotstring._id }}`n")
    }
{% endif %}


{% endfor %}

{% if on_clipboard %}


ClipChanged(Type) {
    CLIPBOARD_SENTINEL := Chr(57345)
    ret := Format("{}{}`n", CLIPBOARD_SENTINEL, Type)
    WriteStdout(ret)
    return
}

OnClipboardChange(ClipChanged)

{% endif %}
SetTimer KeepAliveFunc, 2000

KeepAliveFunc() {
    global stdin
    global KEEPALIVE
    WriteStdout(Format("{}`n", KEEPALIVE))
    alive_message := RTrim(stdin.ReadLine(), "`n")
    if (alive_message != KEEPALIVE) {
        ; The parent Python process has terminated unexpectedly
        ; Exit to avoid leaving the hotkey process around
        ExitApp
    }
    return
}
