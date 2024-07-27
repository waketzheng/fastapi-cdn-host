# FastAPI CDN host for docs ui

API接口文档页面有时候打开会很慢，因为它默认使用的是https://cdn.jsdelivr.net/npm

为实现加快/docs页面的打开速度这么一个小小功能，常常需要放置N行代码来[自定义文档](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/?h=static#custom-cdn-for-javascript-and-css)的响应路由。

由于很多个项目都需要这么操作，故开发了一个插件了简化代码，现只需一行就搞定了：
`fastapi_cdn_host.patch_docs(app)`

[English](./README.md) | **中文**

## 安装

```bash
pip install fastapi-cdn-host
```

## 使用
1. 国内访问fastapi接口文档页面的默认CDN(https://cdn.jsdelivr.net)会比较慢，使用插件后会自动对比它跟unpkg.com的速度，然后采用响应快的那个
2. 如果是离线环境，这时候外部CDN是访问不了的，只需在同级目录下的static里放置swagger-ui-bundle.js和swagger-ui.css就会自动挂载它们。
```py
import fastapi_cdn_host
from fastapi import FastAPI

app = FastAPI()
# 注册路由、挂载静态文件等 ...

fastapi_cdn_host.patch_docs(app)
```
更多示例见：
- examples/
- tests/

## 详解

使用`fastapi_cdn_host.patch_docs(app)`启用插件后，uvicorn(或gunicorn等)启动服务时，
会先查找本地文件夹里是否有swagger-ui.css，有的话自动挂载到app并改写/docs的依赖为本地文件。
没有的话，使用协程并发对比https://cdn.jsdelivr.net、https://unpkg.com、https://cdnjs.cloudflare.com、https://cdn.bootcdn.net
等几个CDN的响应速度，然后自动采用速度最快的那个。

## 加入其他CDN作为备选

- 参考：https://github.com/lecepin/blog/blob/main/%E5%9B%BD%E5%86%85%E9%AB%98%E9%80%9F%E5%89%8D%E7%AB%AF%20Unpkg%20CDN%20%E6%9B%BF%E4%BB%A3%E6%96%B9%E6%A1%88.md
```py
from fastapi_cdn_host import CdnHostEnum, CdnHostItem

fastapi_cdn_host.patch_docs(
    app,
    docs_cdn_host=CdnHostEnum.extend(
        ('https://lf9-cdn-tos.bytecdntp.com/cdn/expire-1-M', ('/swagger-ui/{version}/', '')),
        CdnHostItem('https://raw.githubusercontent.com/swagger-api/swagger-ui/v5.14.0/dist/swagger-ui.css'),  # github
    )
)
```

## 不修改源代码只是启动时加载插件的方式(需要fastapi>=0.111.0)：

```bash
fastcdn main.py
```

## 手动将js/css/redoc等文件下载到当前目录的static文件夹里

```bash
fastcdn offline
```

## 许可证

[MIT](./LICENSE)
