#encoding=utf-8

from PIL import Image

import MySQLdb
import MySQLdb.cursors

import os


def mysql_execute(sql):
    mysql = MySQLdb.connect('ffcc.racing', 
                            'root', 
                            'Cf123!@#', 
                            'pshot', 
                            charset='utf8', 
                            cursorclass = MySQLdb.cursors.DictCursor)
    cursor = mysql.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    mysql.close()
    return rs


images = mysql_execute("select id, category, name from image;")

mysql = MySQLdb.connect('ffcc.racing', 
                            'root', 
                            'Cf123!@#', 
                            'pshot', 
                            charset='utf8', 
                            cursorclass = MySQLdb.cursors.DictCursor)
cursor = mysql.cursor() 
sql = "update image set width={}, height={} where id={}"

for obj in images:
    image_id = obj.get('id')
    category = obj.get('category')
    name = obj.get('name')
    path = os.path.join('/home/ffcc/pshot/images', '{}/{}'.format(category, name))
    img = Image.open(path)
    cursor.execute(sql.format(img.width, img.height, image_id))
mysql.close()

