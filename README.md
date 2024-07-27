# Lifespan with AIOMySQL

本项目使用`aiomysql` 创建连接池，介绍 FastAPI 中 Lifespan Events(生命周期事件) 的使用。<br>
- [Lifespan with AIOMySQL](#lifespan-with-aiomysql)
  - [项目起因:](#项目起因)
  - [Lifespan使用场景:](#lifespan使用场景)
  - [Lifespan使用:](#lifespan使用)
    - [使用规则:](#使用规则)
    - [示例代码:](#示例代码)
  - [写法对比:](#写法对比)
    - [新的写法:](#新的写法)
    - [旧的写法:](#旧的写法)
  - [项目运行:](#项目运行)


## 项目起因:

过往，FastAPI在应用启动前，或应用关闭后执行的事件处理器（函数）为`@app.on_event("startup")` 和 `@app.on_event("shutdown")`，但在最新版FastAPI中已经说明这两种方法即将废弃，这里介绍下新的写法。<br>


## Lifespan使用场景:

- 数据库连接
- 加载共享的机器学习模型

**加载共享的机器学习模型**: 模型只需加载一次，然后所有的请求都会使用这个已经加载的模型，而不是每次有新请求时都重新加载一次模型。这样可以节省时间和资源。<br>


## Lifespan使用:

### 使用规则:

- 使用异步上下文管理器( `asynccontextmanager` )装饰。
- 在 `yield` 之前的代码将在应用启动时运行。
- 在 `yield` 之后的代码将在应用关闭时运行。

### 示例代码:

加载模型可能需要相当长的时间，因为它必须从磁盘读取大量数据，一个合理的方式是使用 `lifespan` 在应用程序开始接收请求之前加载好模型。示例如下:<br>

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

def fake_answer_to_everything_ml_model(x: float):
    """构造一个假的回复"""
    return x * 42

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model(加载机器学习模型)
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # Clean up the ML models and release the resources(清理机器学习模型并释放资源)
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/predict")
async def predict(x: float):
    result = ml_models["answer_to_everything"](x)
    return {"result": result}
```

🚨注意:<br>

Lifespan 是指在处理请求之前加载模型，但仅在应用程序开始接收请求之前，而不是在代码加载时。<br>


## 写法对比:

### 新的写法:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """利用aiomysql创建mysql连接池"""
    await mysqler.create_connect_pool()
    yield
    """销毁mysql连接池"""
    await mysqler.disconnect()
```

- `lifespan` 是一个异步上下文管理器，用于管理应用程序的生命周期事件。
- 在 `yield` 之前的代码（`await mysqler.create_connect_pool()`）将在应用启动时运行，创建 MySQL 连接池。
- 在 `yield` 之后的代码（`await mysqler.disconnect()`）将在应用关闭时运行，销毁 MySQL 连接池。

### 旧的写法:

```python
@app.on_event("startup")
async def startup():
    """利用aiomysql创建mysql连接池"""
    await mysqler.create_connect_pool()

@app.on_event("shutdown")
async def shutdown():
    """销毁mysql连接池"""
    await mysqler.disconnect()
```


## 项目运行:

1. 在项目根目录下创建配置文件 `env_config/.env.local`。
2. 在 `.env.local` 填入MySQL连接方式，示例如下:

```log
# mysql连接信息
MYSQL_DB_HOST="localhost"
MYSQL_DB_PORT="3306"
MYSQL_DB_USER="root"
MYSQL_DB_PASSWORD="Flameaway3."
# mysql数据库名称
MYSQL_DB_NAME="irmdata"
```

3. 在MySQL数据库中创建`chat_history`表，SQL语句如下:

```sql
CREATE TABLE chat_history (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  `user_id` INT NOT NULL COMMENT '客户id',
  `conversation_id` VARCHAR(50) NOT NULL COMMENT '会话id',
  `role` ENUM('user', 'assistant') NOT NULL COMMENT '角色',
  `content` TEXT NOT NULL COMMENT '会话内容',
  `entry_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '信息录入时间',
  `modify_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '字段修改时间',
  INDEX idx_user_conv (`user_id`, `conversation_id`)
) COMMENT='聊天记录表';
```

"INDEX idx_user_conv (`user_id`, `conversation_id`)": 表示创建组合索引，加速查询。<br>

4. 终端运行下列指令，安装依赖项:

```bash
pip install -r requirements.txt
```

5. 运行主文件:

```bash
python main.py
```

6. 运行测试脚本查看效果:

```bash
python tests/test_chat_history.py
```

运行效果如下:<br>

```log
(langchain) root@iZ2zea5v77oawjy2qz7xxx:/lifespan_with_aiomysql# python tests/test_chat_history.py 
{'code': 0, 'msg': '信息存储成功', 'data': {'status': True}} <class 'dict'>
{'code': 0, 'msg': '获取用户聊天记录成功', 'data': {'chat_history': [{'role': 'user', 'content': '请介绍一下北京'}, {'role': 'assistant', 'content': '北京是...'}]}} <class 'dict'>
```