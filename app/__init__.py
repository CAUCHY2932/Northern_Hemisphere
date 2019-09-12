# coding:utf-8
from flask import Flask, redirect, url_for, request
from datetime import datetime
from flask_bootstrap import Bootstrap
from app.config_default import Config as DefaultConfig

bootstrap = Bootstrap()


def check_start(app, db):
    from app.includes.start import exist_config_file, exist_table, load_site, create_path
    create_path(app)
    app.start = False
    if exist_config_file(app):
        from app.config import Config
        app.config.from_object(Config)
        if exist_table(app):
            load_site(app)
            app.start = True
            return

    @app.before_request
    def request_check_start():
        if app.start:
            return
        ends = frozenset(["admin.setup", "admin.install", "static"])
        if request.endpoint in ends:
            return
        if not exist_config_file(app):
            return redirect(url_for("admin.setup"))
        return redirect(url_for("admin.install"))


def template_filters(app):
    @app.template_filter("friendly_time")
    def friendly_time(date):
        now = datetime.now()
        delta = now - date
        if delta.days >= 365:
            return '%d年前' % (delta.days / 365)
        elif delta.days >= 30:
            return '%d个月前' % (delta.days / 30)
        elif delta.days > 0:
            return '%d天前' % delta.days
        elif delta.days < 0:
            return "0秒前"
        elif delta.seconds < 60:
            return "%d秒前" % delta.seconds
        elif delta.seconds < 60 * 60:
            return "%d分钟前" % (delta.seconds / 60)
        else:
            return "%d小时前" % (delta.seconds / 60 / 60)


def create_app():
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)

    from app.models.model import db, login_manager

    bootstrap.init_app(app)
    db.init_app(app)
    db.PREFIX = app.config["DB_PREFIX"]

    app.site = {}

    def site_context_processor():
        return dict(site=app.site)

    app.context_processor(site_context_processor)
    check_start(app, db)

    login_manager.init_app(app)

    from app.web import web
    app.register_blueprint(web)

    from app.admin import admin
    app.register_blueprint(admin, url_prefix="/admin")

    from app.api import api
    app.register_blueprint(api, url_prefix="/api")

    template_filters(app)

    login_manager.login_view = "admin.login"
    login_manager.login_message = "请先登录!!!"

    from app.log import init_logging
    init_logging(app)

    return app
