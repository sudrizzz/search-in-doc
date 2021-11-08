# Search in Doc

搜索文档中的关键词，支持多关键词搜索。双击搜索结果可直接打开文档，也可右键复制文档所在路径。  

使用 Python + PyQt5 + PyPandoc 开发，支持的文档类型：commonmark, docbook, docx, epub, haddock, html, latex, markdown, odt, opml, org, rst, t2t, textile, twiki  

# 界面

![screenshot](screenshot.png)

# 使用

首先在本地配置 Pandoc，修改 main.spec 文件中 Pandoc 路径。

使用 PyInstaller 进行打包，执行下列命令即可，打包后文件在 dist 文件夹中。  

```bash
pyinstaller main.spec
```