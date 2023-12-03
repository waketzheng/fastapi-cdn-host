# FastAPI CDN host for docs ui

API接口文档页面有时候打开会很慢，因为它默认使用的是https://cdn.jsdelivr.net/npm

为实现加快/docs页面的打开速度这么一个小小功能，常常需要放置N行代码来自定义文档的响应路由。

由于很多个项目都需要这么操作，故开发了一个插件了简化代码，现只需一行就搞定了：
`monkey_patch_for_docs_ui(app)`

[English](./README.md) | **中文**

## 安装

```bash
pip install fastapi-cdn-host
```

## 使用
```py
from fastapi import FastAPI
from fastapi_cdn_host import monkey_patch_for_docs_ui

app = FastAPI()
# 注册路由、挂载静态文件等 ...

monkey_patch_for_docs_ui(app)
```

## 详解

使用`monkey_patch_for_docs_ui(app)`启用插件后，uvicorn(或gunicorn等)启动服务时，
会先查找本地文件夹里是否有swagger-ui.css，有的话自动挂载到app并改写/docs的依赖为本地文件。
没有的话，使用协程并发对比https://cdn.jsdelivr.net、https://unpkg.com、https://cdnjs.cloudflare.com
三个CDN的响应速度，然后自动采用速度最快的那个。

## 许可证

[MIT](./LICENSE)
