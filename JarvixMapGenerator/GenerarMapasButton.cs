using ArcGIS.Desktop.Framework.Contracts;
using System.Diagnostics;
using System.IO;
using System.Windows;

internal class GenerarMapasButton : Button
{
    protected override void OnClick()
    {
        string pythonExe = @"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe";
        string script = @"C:\Jarvix\Python\generar_mapas.py";

        if (!File.Exists(pythonExe))
        {
            MessageBox.Show($"No se encontro python.exe en:\n{pythonExe}", "JarvixMapGenerator");
            return;
        }

        if (!File.Exists(script))
        {
            MessageBox.Show($"No se encontro el script en:\n{script}", "JarvixMapGenerator");
            return;
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = pythonExe,
            Arguments = $"\"{script}\"",
            UseShellExecute = false,
            CreateNoWindow = true
        };

        Process.Start(startInfo);
    }
}
