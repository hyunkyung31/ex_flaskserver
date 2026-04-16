import json
import pymysql      
from flask import jsonify
     
def getConnection():
    return pymysql.connect(host= '136.112.163.216',
                           port = 3306,
                           user = 'piehyun31',
                           password = 'gusrud91354@',
                           database = 'Daejeon', 
                           charset = 'utf8', 
                           autocommit = True)         
def getSungjuk():
	conn = getConnection()
	cur = conn.cursor()
	cur.callproc("student_select")
	if cur.rowcount>0:
		result = cur.fetchall()
		print(result)
	else:
		result = 0;
	cur.close()
	conn.close()
	return result   #  json.dumps({'object_list' : result})

def getJsonSungjuk():
    conn = getConnection()
    cur = conn.cursor()
    cur.callproc("student_select")    
    if cur.rowcount > 0:
        result = cur.fetchall()
    else:
        result = []        
    cur.close()
    conn.close()    
    return jsonify(result) #결과를 JSON으로 돌려준다

def setSungjuk(sungData):
	conn = getConnection()
	cur = conn.cursor()
	args = (sungData['name'], sungData['kor'], sungData['mat'], sungData['eng'], 'CH00000001', 0)
	cur.callproc("student_insert",args)
	cur.execute('SELECT @_student_insert_5')
	result = cur.fetchone()
	cur.close()
	conn.close()
	return json.dumps({'rows' : result})

def delSungjuk(in_id):
	conn = getConnection()
	cur = conn.cursor()
	args = (in_id, 0)
	cur.callproc("student_delete_id", args)
	cur.execute('SELECT @_student_delete_id_1')
	result = cur.fetchone()
	cur.close()
	conn.close()
	return json.dumps({'rows' : result}) #JSON string

def putSungjuk(sungData):
	conn = getConnection()
	cur = conn.cursor()
	args = (sungData["id1"], sungData["name1"],sungData["kor1"],sungData["mat1"],sungData["eng1"], 0) # tuple
	cur.callproc("student_update", args)
	cur.execute('SELECT @_sungjuk_update_5')
	result = cur.fetchone()
	cur.close()
	conn.close()
	return json.dumps({'rows' : result})