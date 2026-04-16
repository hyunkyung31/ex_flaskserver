import json
import pymysql
#만드는 이유 : flask_server.py 호출(데이터를 전달하거나 수신받기위해서 만들었다)
#target은 flask_server
def getConnection():
    return pymysql.connect(host= '136.112.163.216',
                           port = 3306,
                           user = 'piehyun31',
                           password = 'gusrud91354@',
                           database = 'Daejeon', 
                           charset = 'utf8', 
                           autocommit = True)                 

def getSungjuk() : #get 방식으로 전체 데이터를 가져온다
    conn = getConnection()
    cur = conn.cursor()
    cur.callproc("student_select")
    if (cur.rowcount) :
        result = cur.fetchall()
        result_rowcount = cur.rowcount
        print('rowcount = ', result_rowcount)
    else :
        result = []
        print('rowcount', cur.rowcount)
    cur.close()
    conn.close()
    return result

#번호가 주어지면 1인분만 가져온다
def getBunhoSungjuk(bunho):
    conn = getConnection()
    cur = conn.cursor()
    args = [(bunho)]
    cur.callproc('select_with_bunho', args)
    if (cur.rowcount) :
        result = cur.fetchall()
        print(result)
    else :
        result =[]
    cur.close()
    conn.close()
    return result

#입력
def setSungjuk(sungData):
    conn = getConnection()
    cur = conn.cursor()
    args = (sungData['name'], sungData['kor'], sungData['mat'], sungData['eng'], sungData['schoolcode'], 0)
    cur.callproc('student_insert', args)
    result = cur.rowcount
    print(result)
    cur.close()
    conn.close()
    return result

#번호로 수정
def update_Bunho_Name(bunho, name) :
    conn = getConnection()
    cur = conn.cursor()
    try : 
        args = (bunho, name, 0)
        cur.callproc("sungjuk_with_bunho", args)
        #OUT파라미터 조회
        cur.execute("SELECT @_sungjuk_with_bunho_2")
        result = cur.fetchone()
        conn.commit()
        return result
    finally :
        cur.close()
        conn.close()

#삭제
def delete_Bunho(bunho):
    conn = getConnection()
    cur = conn.cursor()
    try :
        args = (bunho, 0)
        cur.callpro("sungjuk_delete_bunho", agrs)
        cur.execute("SELECT @_select_wiht_bunho")
        result = cur.fetchone()
        conn.commit()
    finally :
        cur.close()
        conn.close()
