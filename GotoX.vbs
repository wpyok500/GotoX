'���� GotoX ϵͳ���̸������ߣ�λ�� GotoX ��Ŀ¼����Ч��
'Ҳ������ create_shortcut.js �����洴�� GotoX �Ŀ�ݷ�ʽ��
Dim objShell
Set objShell = WScript.CreateObject("WScript.Shell")
objShell.CurrentDirectory = objShell.CurrentDirectory + "\python"
objShell.Run "python.exe ..\launcher\win32.py",,False
Set objShell = NoThing
WScript.quit
