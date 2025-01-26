# ~~还在施工~~一部分可以用

## 功能
- [x] 传入本子`ID`返回`JSON`或文件
- [x] 文件提供
- [ ] 支持传入列表以批量下载本子
- [ ] 支持传入配置，针对用户长期记忆配置
- [ ] 提供输出加密

## 运行

### 推荐（通用）
1. **环境**
    ```plaintext
    理论 Python >= 3.10 均可（推荐使用 3.12）
    ```
2. **安装**
    ```bash
    pip install jmcomic-api
    ```
3. **运行**
    ```bash
    python -m jmcomic-api
    ```

### Windows 用户
1. 前往 [Releases](https://github.com/Shua-github/JMComic-API-Python/releases) 下载 [Windows_OneFile](https://github.com/Shua-github/JMComic-API-Python/releases/latest/download/Windows_OneFile.zip)
2. 解压到一个文件夹
3. 运行 `app.exe`

## 默认配置
配置路径均在软件输出，可以使用 `-c <路径>` 来指定配置路径

## 使用
访问 [http://Host:Port/docs](http://localhost:5000/docs) 查看 FastAPI 自带的文档（默认端口是 5000）

## 谢谢他们和它们
- [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)
- [![Contributors](https://contributors-img.web.app/image?repo=Shua-github/JMComic-API-Python)](https://github.com/Shua-github/JMComic-API-Python/graphs/contributors)

## 其它
出现问题请开 issues