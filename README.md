# ~~还在施工~~一部分可以用

## 功能
- [x] 传入本子`ID`返回`base64`或文件二进制
- [x] 提供输出加密
- [ ] 文件提供
- [ ] 支持传入列表以批量下载本子


## 运行

### 推荐（通用）
1. **环境**
    ```plaintext
    理论 CPython >= 3.8 均可 (推荐使用 PyPy3.10 或 CPython3.13)
    ```
2. **安装**
    ```bash
    pip install jmcomic_api
    ```
3. **运行**
    ```bash
    python -m jmcomic_api
    ```

## 配置
配置路径均在软件输出,暂不提供更换配置路径

## 使用
访问 [`http://Host:Port/`](http://localhost:5000/) 查看 `FastAPI` 自带的文档（默认端口是 `5000` ）

## 谢谢他们和它们
- [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)
- [![Contributors](https://contributors-img.web.app/image?repo=Shua-github/JMComic-API-Python)](https://github.com/Shua-github/JMComic-API-Python/graphs/contributors)

## 其它
出现问题请开 [`Issues`](https://github.com/Shua-github/JMComic-API-Python/issues/new?template=Blank+issue)