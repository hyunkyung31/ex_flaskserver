from flask import Flask, Blueprint, request, render_template
from flask import jsonify, redirect, make_response, url_for
import os
import json
import pymysql
import logging
from logging.config import dictConfig
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField ,SubmitField 
from wtforms.validators import InputRequired, Length

from dao import sungjuk #dao디렉토리에서 sungjuk을 임포트해라 => module import
from dao import sungjukone

dictConfig({ #서버에 무슨일이 생기면 기록을 남길건데, 어떻게 남길지
    'version': 1,
    'formatters': { #[날짜] 등급이름 : 메시지 식으로 나옴
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': { #에러가 나면 터미널창에 보여줘라 
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': { #터미널뿐만 아니라 flask_server.log형식으로 파일로도 저장해줘라
            'class': 'logging.FileHandler',
            'filename': 'flask_server.log',
            'formatter': 'default',
            'level': 'INFO',
            'encoding': 'utf-8'
        }
    },
    'root': {
        'level': 'INFO', #너무 사소한건 무시, 중요한정보"INFO"이상의 로그만 기록하겠다 등급설정
        'handlers': ['wsgi', 'file']
    }
})

app = Flask(__name__) #flask서버 인스턴스 #__name__이 의미 : 현재 file 의미
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO0000'
app.config['JSON_AS_ASCII'] = False
app.config['MYSQL_HOST'] = '136.112.163.216'
app.config['MYSQL_USER'] = 'piehyun31'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_PASSWORD'] ='gusrud91354@'
app.config['MYSQL_DB'] = 'Daejeon'

def getConnection():
    return pymysql.connect(
        host = app.config['MYSQL_HOST'],
        port = app.config['MYSQL_PORT'],
        user = app.config['MYSQL_USER'],
        password = app.config['MYSQL_PASSWORD'],
        db = app.config['MYSQL_DB']
    )

@app.route("/") #라우팅, document 루트폴더면 밑의 함수가 작동해라
def index():
    app.logger.info('%s logged in successfully', '성공')
    app.logger.info(f'[{request.method}] {request.path}')
    return render_template('index.html') #template를 렌더링해서 클라이언트로 보내야하는데 file이 필요

@app.route("/set_cookie") #주소
def set_cookie(): #주소로 요청이 오면 함수를 실행시켜라
    data = {"message": "쿠키가 설정되었습니다."}
    resp = make_response(jsonify(data), 200) # JSON으로 변경, 상태코드 200 은 성공으로 표현해라
    resp.set_cookie("token", "abc123", httponly=True, samesite = "Strict", max_age = 60*60*24) #옵션 http작동할때만 같은 싸이트 요청이 들어오면 넘겨라, 이때되면 종료시켜라
    resp.headers["X-Custom-Header"] = "MyValue" #헤더 달아주기
    return resp

@app.route("/createtable")
def create_table():
    try:
        print('Creating Table Started =====')
        mysql = getConnection()
        cur = mysql.cursor()
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY ,
                name VARCHAR(255) NOT NULL,
                description TEXT
            )
            '''        )
        mysql.commit()
        cur.close()
        mysql.close()
    except Exception as e:
        return render_template("fail.html")
    return render_template("success.html")

class ItemForm(FlaskForm) : #flaskform을 상속받음 = datafield 쉽게 만들고 #자동으로 검증할수있게 
    username = StringField('Username', validators=[InputRequired('입력필요!'), Length(min=3, max=5, message="3 to 5 자로 입력")])
    description = StringField('Description', validators=[InputRequired('입력필요'), Length(min=5, max=200, message="5 to 200자로 입력")])
    submit = SubmitField('Submit')

@app.route("/item_create", methods=['GET']) #get방식으로 가져온다 
def item_create():    
    form = ItemForm()
    if request.method == 'GET':
        return render_template("itemcreate.html", form = form)
    return render_template("itemcreate.html", form = form)
            

@app.route("/item_crud", methods=['GET','POST']) #get방식과 post방식만 가능하다
def item_crud(): # create에서 보낸 데이터 저장, 모든 데이터를 화면에 출력
    form = ItemForm() #itemform인스턴스
    if request.method == 'GET': #get방식이면 데이터를 채워서 전달하는거
        try:
            mysql = getConnection()
            cur = mysql.cursor()
            sql = ''' select * from items'''
            cur.execute(sql)
            data = cur.fetchall()
            print("Get 요청 들어옴")
            print(data)
            cur.close()
            mysql.close()
        except Exception as e:
            return render_template("fail.html")
        return render_template("item_crud.html", data=data)
    
    elif request.method == 'POST':
        print("POST 요청 들어옴")
        print("검증 결과:", form.validate_on_submit())
        print("에러:", form.errors) #터미널에 출력되는거(print) tag되는건 브라우저 상에서 보인다
        if form.validate_on_submit():  
            print("검증에 들어옴")
            try:
                mysql = getConnection()
                cur = mysql.cursor()
                sql = ''' insert into items(name, description) values(%s,%s) '''
                cur.execute(sql,  (form.username.data, form.description.data) )
                mysql.commit()
                cur.close()
                mysql.close()
            except Exception as e:
                print("에러 발생:", e)
                return render_template("fail.html")
            return redirect(url_for("item_crud"))

    return redirect(url_for("item_crud"))

@app.route("/item_update", methods=["GET", "POST"])
def item_update():
    if request.method == "GET":
        username = request.args.get("username") #args는 get방식으로 데이터를 전달하면 args로 파싱, 파싱한 데이터 중에 username을 가져와라

        # 기존 데이터 조회
        mysql = getConnection()
        cur = mysql.cursor()
        sql = "SELECT name, description FROM items WHERE name=%s" #번호, 이름으로 아이템이랑 디스크립션 가져온다
        cur.execute(sql, (username,))
        item = cur.fetchone()

        cur.close()
        mysql.close()

        return render_template("itemupdate.html", item=item)

    elif request.method == "POST":
        username = request.form.get("username")
        description = request.form.get("description")

        try:
            mysql = getConnection()
            cur = mysql.cursor()

            sql = "UPDATE items SET description=%s WHERE name=%s"
            cur.execute(sql, (description, username))
            mysql.commit()

            cur.close()
            mysql.close()

        except Exception as e:
            print("수정 오류:", e)
            return render_template("fail.html")
        return redirect(url_for("item_crud"))

@app.route("/item_delete", methods=["GET", "POST"])
def item_delete():
    if request.method == "GET":
        username = request.args.get("username")
        return render_template("itemdelete.html", username=username)

    elif request.method == "POST":
        username = request.form.get("username")

        try:
            mysql = getConnection()
            cur = mysql.cursor()

            sql = "DELETE FROM items WHERE name=%s"
            cur.execute(sql, (username,))
            mysql.commit()

            cur.close()
            mysql.close()

        except Exception as e:
            print("삭제 오류:", e)
            return render_template("fail.html")

        return redirect(url_for("item_crud"))

@app.route("/bootstraps")
def bootstraps():
    return render_template("bootstraps.html")

@app.route('/ajaxcall')
def ajaxcall():
    return render_template('ajaxcall.html')

@app.route('/_add_numbers') #get방식 요청 데이터 처리
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)

    return jsonify(result = a + b) #{result: 값 30}

#라우트 정의함수
@app.route('/sungjuk_call')
def sungjuk_call() :
    result = sungjuk.getSungjuk()
    return render_template('sungjuk.html', object_list = result)

#inset함수
@app.route("/sungjuk_insert", methods=['GET', 'POST'])
def sungjuk_insert():
    if request.method == 'GET':
        return render_template("sungjuk_insert.html")
    elif request.method == 'POST':
        name = request.form.get('name1')
        kor  = request.form.get('kor1')
        mat  = request.form.get('mat1')
        eng  = request.form.get('eng1')
        schoolcode = request.form.get('schoolcode1')        
        sungdata = {
            'name': name, 
            'kor': kor, 
            'mat': mat, 
            'eng': eng, 
            'schoolcode': schoolcode
        }
        result_int = sungjuk.setSungjuk(sungdata)
        return render_template("sungjuk_insert_result.html", result_int=result_int)

@app.route("/sungjuk_update", methods=['POST'])
def sungjuk_update():
    if request.method == 'POST':
        bunho = request.form['bunho']
        result=sungjuk.getBunhoSungjuk(bunho)
        return render_template("sungjuk_update.html", object_list=result)

@app.route("/sungjuk_update_result", methods=['POST'])
def sungjuk_update_result():
    result_int = 0
    if request.method == 'POST':
        bunho = request.form['bunho']
        name = request.form['name']
        print("controller", bunho, name)
        result_int=sungjuk.update_Bunho_Name(bunho ,name)
        return  render_template("sungjuk_update_result.html", result_int = result_int)

@app.route("/sungjuk_delete", methods=['POST'])
def sungjuk_delete():
    result_int = 0
    if request.method == 'POST':
        bunho = request.form['bunho']
        result = sungjuk.getBunhoSungjuk(bunho)
        return  render_template("sungjuk_delete.html", object_int = result)


@app.route("/sungjuk_delete_result", methods=['POST'])
def sungjuk_delete_result():
    result_int = 0
    if request.method == 'POST':
        bunho = request.form['bunho'] 
        result_int = sungjuk.delete_sungjuk(bunho)
        return render_template("sungjuk_delete_result.html", result_int = result_int)


#ajax으로 
@app.rout("/sungjukone_call")
def sungjukone_call():
    result = sungjukone.getSungjuk()
    return render_template("sungjukone.html", object_list = result)




if __name__ == '__main__': #얘가 메인페이지면 flask서버를 기동해라
    app.run('0.0.0.0', port=5000, debug=True, use_reloader=True) #debug면 에러가 나면 브라우저에 설명을 달아라 (개발할때 필요), 
                                            #use_reloader(소스가 변경되면 자동으로 실행시켜라)