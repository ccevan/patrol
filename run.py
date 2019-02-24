# coding=utf-8

from flask_migrate import Migrate, MigrateCommand
from flask_script import  Manager
from app import create_app
from app.tools.listenRedis import run_listen_redis
from app.models.models import Task, TaskItemRelationship, Item, Fault, FaultItemRelationship, FaultCount, Channel

app, db = create_app("baseConfig")


manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

# run_listen_redis(app)  # 跑接口的

if __name__ == '__main__':
    print(app.url_map)
    manager.run()

