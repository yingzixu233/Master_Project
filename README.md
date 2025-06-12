# Master Project

一）关于软件下载：

1.下载visual studio (community 2022)
1) ASP.NET和Web开发
使用ASP.NET Core, ASP.NET, HTML/JavaScript 和包括Docker支持的容器生成Web应用程序
2）.Net 桌面开发：
将C#, VISUAL BASIC,和F#
与.net 和Net Framework 一起使用
生成WPF,windows窗体和控制台应用程序
3）使用C++的桌面开发
使用所选工具（包括MSVC,Clang,CMake或MSBuild）生成使用于Windows的现代C++应用

2.下载Docker
安装 Docker Desktop

3.下载Anaconda

4.下载Pycharm Community

5.下载Revit


二）关于PyCharm项目：

1. 在anaconda中部署环境（SCI2025）为 Pycharm项目（BIM_Data_Preprocessing） 配置环境
- create: 创建一个新环境
- search: 搜索栏搜索numpy库, python-dotenv库（用于从环境文件中获取值），pandas库直接安装
- open terminal: 添加neo4j 库 和ifcopenshell 库
  ifcopenshell 安装命令: pip install ifcopenshell
  neo4j driver 安装命令: python -m pip install neo4j

2. 从Anaconda 环境（SCI2025）中launch Pycharm Community 以打开 Pycharm项目（BIM_Data_Preprocessing）
备注：
-若PyCharm 未正确使用 Anaconda 环境
问题：PyCharm 可能未关联到你创建的 Conda 环境，而是使用了其他解释器（如系统 Python 或虚拟环境）。
- 打开 PyCharm，进入 File > Settings > Project: [项目名] > Python Interpreter。
- 点击右上角的齿轮图标，选择 Add Interpreter > Add Local Interpreter。
- 选择 Conda Environment，勾选 Existing environment，然后从下拉菜单中选择你的 Conda 环境路径（通常位于 Anaconda3/envs/你的环境名）。
- 点击 OK 应用更改。

3. 在Pycharm项目中运行docker-compose-neo4j.yml 为 Neo4J Graph DB配置环境
- 打开Docker Desktop
- 在PyCharm中安装Docker插件： Control+Alt+S (设置) > Plugins（插件） > 搜索Docker，点击安装  
- 在Pycharm中配置Docker：  Control+Alt+S (设置) > Build, Execution, Deployment (构建，执行，部署) > Docker>点击＋号 >确定
- 运行Pycharm项目中的docker-compose-neo4j.yml 文件：1）Debug键左侧下拉箭头编辑运行/调试 > 添加 >Docker>Docker Compose>命名为Docker-Compose-Neo4j并选择运行路径>应用；2）Debug键左侧下拉选择Docker-Compose>运行>（等待，直到控制台出现Container Neo4j started）

验证是否配置成功：打开 Neo4j Browser中的Graph DB 实例
- Neo4j 项目实例（空） : console切换到仪表板点击链接http://localhost:7474/ > 输入docker-compose-neo4j.yml 中预先定义的密码

4. 运行main文件以生成完整的图形数据模型
自动连接Neo4j 以建立 Graph Structure
自动存储数据
验证方式：点击链接http://localhost:7474/ > 输入docker-compose-neo4j.yml 中预先定义的密码> 输入cypher查询语句

5.运行CsvFileWriter文件以生成用于写入C#/.Net Framework环境的csv文件
打开csvfile进行检查，将几何变换属性值为“Any”的改成自己希望设定的变换值

三）关于Visual Studio C#/.Net Framework项目（Revit Addin Development）
1. 在 Visual Studio 中新建 类库 (.NET Framework) 项目（必须选择 .NET Framework 4.8 或与 Revit 版本匹配的框架）
2. 添加 Revit API 引用：
   - 右键项目 → 添加引用 → 浏览
   - 导航到 Revit 安装目录下的 DLL 文件（默认路径）：
      C:\Program Files\Autodesk\Revit 20XX\RevitAPI.dll
      C:\Program Files\Autodesk\Revit 20XX\RevitAPIUI.dll
      勾选这两个文件并确认
      

