#coding=utf-8
#chenfei 20180706

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from datetime import timedelta
from data import get_articles
from config import MYSQL_CONFIG
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

from flask import jsonify

from flask_restful import Resource, Api

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

# restful api
api = Api(app)

# mysql config
app.config['MYSQL_HOST'] = MYSQL_CONFIG['host']
app.config['MYSQL_USER'] = MYSQL_CONFIG['username']
app.config['MYSQL_PASSWORD'] = MYSQL_CONFIG['password']
app.config['MYSQL_DB'] = MYSQL_CONFIG['db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # 结果是字典格式

# init mysql
mysql = MySQL(app)




@app.route("/")
def index():
    results = {
        'page': 'index',
    }

    return render_template('home.html', results=results)

@app.route("/about/")
def about():
    results = {
        'page': 'about',
    }
    return render_template('about.html', results=results)


class Category(Resource):
    def get(self, id):
        cur = mysql.connection.cursor()
        cur.execute("select * from category where id={};".format(int(id)))
        rs = cur.fetchone()
        cur.close()
        return rs

@app.route("/api/pshot/categories/", methods=['POST'])
def get_all_category():
    '''
    获取图片分类
    '''
    rs = {
        'code': 0,
        'msg': '',
        'data': {}
    }
    try:
        cur = mysql.connection.cursor()
    except:
        rs['code'] = -1
        rs['msg'] = 'mysql connect failed.'
    else:
        cur.execute("select * from category;")
        rs['data']['results'] = cur.fetchall()
        cur.close()
    return jsonify(rs)


@app.route("/api/pshot/images/", methods=['POST'])
def get_images():
    '''
    根据分类获取图片
    '''
    rs = {
        'code': 0,
        'msg': '',
        'data': {}
    }
    args = request.json
    if args == None:
        rs['code'] = '-1'
        rs['msg'] = 'we need json data!, and add Content-Type: application/json to headers'
        return jsonify(rs)
    c_id = int(args.get('category', 1))
    limit = int(args.get('limit', 10))
    page = int(args.get('page', 1))
    size = args.get('size', 'XS').upper()
    try:
        cur = mysql.connection.cursor()
    except:
        rs['code'] = -1
        rs['msg'] = 'mysql connect failed.'
    else:
        cur.execute("select * from image where category={} and size='{}' order by id desc limit {},{};".format(c_id, size, limit*(page-1) + 1, limit*page))
        data = cur.fetchall()
        cur.execute("select count(*) as count from image where category={} and size='{}';".format(c_id, size))
        rs['data'].update(cur.fetchone())
        cur.close()
        for each in data:
            each.update({
                'url': 'http://ffcc.racing/pshot/images/{}/{}'.format(each['category'], each['name']),
                'url_max': 'http://ffcc.racing/pshot/images/{}/{}'.format(each['category'], each['name'].split('_')[0] + '_l.jpg')
                })
        rs['data']['results'] = data
        if rs['data']['count'] > page * limit:
            rs['data']['next'] = 'http://ffcc.racing:5000/api/pshot/images/?limit={limit}&page={page}&category={category}&size={size}'.format(limit=limit, page=page + 1, category=c_id, size=size)
    return jsonify(rs)

api.add_resource(Category, '/api/pshot/category/')

if __name__ == '__main__':
    # 设置静态文件缓存过期时间
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
    app.debug = True
    #也可以这样写：
    #app.send_file_max_age_default = timedelta(seconds=1)
    app.secret_key = 'secret_chenfei_sdfhUjn(fIh'
    app.run(host='0.0.0.0')