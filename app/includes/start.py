# coding: utf-8
import os
from flask import current_app, render_template
from sqlalchemy import *


def exist_config():
    return exist_config_file(current_app)


def exist_config_file(app):
    filename = "{}/config.py".format(app.root_path)
    return os.path.exists(filename)


def create_config(username, password, host, db):
    file_path = '{}/templates/admin/start/config_new.html'.format(current_app.root_path)
    with open(file_path, 'r')as f:
        data = f.read().format(username=username.decode('utf-8'), password=password.decode('utf-8'),
                               host=host.decode('utf-8'), db=db.decode('utf-8'))
    print(data)
    filename = '{}/config.py'.format(current_app.root_path)
    fd = open(filename, "w")
    fd.write(data)
    fd.close()


def create_path(app):
    paths, config = [], app.config
    log_path, _ = os.path.split(config["ERROR_LOG"])
    paths.append(os.path.join(app.root_path, log_path))

    paths.append(os.path.join(app.static_folder, config["AVATAR_PATH"]))
    paths.append(os.path.join(app.static_folder, config["TMP_PATH"]))
    paths.append(os.path.join(app.static_folder, config["IMAGE_PATH"]))
    paths.append(os.path.join(app.static_folder, config["BOOK_COVER_PATH"]))
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


def connect_mysql(url):
    """1049 => 数据库不存在
       2005 => 主机地址错误
       1045 => 用户名密码错误"""
    try:
        eng = create_engine(url)
        connection = eng.connect()
    except Exception as e:
        print(e)
        code = 0
        # code, _ = e.orig
        return code
    return 0


def create_tables(db):
    db.create_all()


def exist_table(app):
    url = app.config["SQLALCHEMY_DATABASE_URI"]
    return _exist_table(url)


def _exist_table(url):
    from app.models.site import SiteMeta
    engine = create_engine(url)
    if engine.dialect.has_table(engine, SiteMeta.__tablename__):
        return True
    return False


def set_site(app):
    from app.models.site import SiteMeta
    metas = SiteMeta.all()
    metas = dict([(meta.name, meta.value) for meta in metas])
    app.site = metas


def load_site(app):
    with app.app_context():
        set_site(app)

        def site_context_processor():
            return dict(site=app.site)

        app.context_processor(site_context_processor)
