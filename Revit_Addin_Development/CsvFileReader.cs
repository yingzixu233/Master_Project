using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Revit_Addin_Development
{
    class CsvFileReader
    {
        public static List<string> ReadCSV(string path)
        {
            StreamReader sr;
            List<string> data = new List<string>();
            try
            {
                // 注册编码提供程序（只需调用一次）
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

                // 安全获取编码
                Encoding encoding = Encoding.GetEncoding("GB2312");
                using (sr = new StreamReader(path, encoding))
                {
                    string str = "";
                    while ((str = sr.ReadLine()) != null)
                    {
                        data.Add(str);
                    }
                }
            }
            catch (Exception ex)
            {
                foreach (Process process in Process.GetProcesses())
                {
                    if (process.ProcessName.ToUpper().Equals("EXCEL"))
                        process.Kill();
                }
                GC.Collect();
                Thread.Sleep(10);
                Console.WriteLine(ex.StackTrace);

                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

                // 安全获取编码
                Encoding encoding = Encoding.GetEncoding("GB2312");
                using (sr = new StreamReader(path, encoding))
                {
                    string str = "";
                    while ((str = sr.ReadLine()) != null)
                    {
                        data.Add(str);
                    }
                }
            }
            return data;
        }
    }
}
