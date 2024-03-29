from flask import Flask
import request
from functools import wraps
import json, time
from datetime import datetime
import random
import pymysql.cursors
import base64
app = Flask(__name__)


global cursor

# DECORATOR
# declares json app.route given app.route string
# return simple python option1bject in the function you write
# example:
# @app.route("/app.route_string")
# def function():
#     result = {...}




connection = pymysql.connect(host='52.41.147.246',
                                         user='hillffair',
                                         password='1qaz2wsx',
                                         db='Hillffair2k18',
                                         cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

@app.route('/')
def hello():
    if request.method=='GET':
        return "hello"
    else:
        return "Hiiiii"

@app.route('/postwall/<rollno>/<imageurl>')
# Sample Response: [{"id": 1, "name": "Daniyaal Khan", "rollno": "17mi561", "likes": 2}]
def postwall(rollno,imageurl):

    imageurl=imageurl
    #print("INSERT into wall values(NULL,'"+rollno+"','"+imageurl+"', "+str(int(time.time()+19800))+")")
    query = cursor.execute("INSERT into Wall values(NULL,'"+rollno+"','"+imageurl+"', "+str(int(time.time()+19800))+")")
    cursor.execute(query);
    connection.commit();
    return {'status': 'success'}


@app.route('/getwall/<int:start>/<user_id>')
# Sample Response: [{"id": 1, "name": "Daniyaal Khan", "rollno": "17mi561", "likes": 2}]
def getwall(start,user_id):
    query = cursor.execute("SELECT w.id as id, p.name as name, p.id as rollno, (SELECT COUNT(*) FROM likes WHERE post_id=w.id) AS likes, (Select count(*) from likes where post_id=w.id AND profile_id='"+user_id+"') as liked, w.image_url, p.image_url AS profile_pic  FROM wall as w, profile as p WHERE p.id=w.profile_id ORDER BY w.time DESC")
    result = cursor.fetchall()
    return result


@app.route('/getlike/<int:image_id>')
# Sample Response: {"likes": 2}
def getlike(image_id):
    query = cursor.execute("SELECT COUNT(*) AS likes FROM likes WHERE post_id="+str(image_id))
    result = cursor.fetchone()
    return result


@app.route('/postlike/<int:image_id>/<user_id>/<int:action>')
def postlike(image_id, user_id,action):
        if action==1:
            query = cursor.execute("INSERT INTO likes VALUES(NULL, '"+user_id+"', "+str(image_id)+")")
            if query:
                return {'status': 'success'}
            else:
                return {'status': 'fail'}
        else:
            query = cursor.execute("DELETE from likes where profile_id = '"+user_id+"' AND post_id = '"+str(image_id)+"'")
            if query:
                return {'status': 'success'}
            else:
                return {'status': 'fail'}

@app.route('/getleaderboard')
# Sample Response: [{"id": "17mi561", "name": "Daniyaal Khan", "score": 60.0}, {"id": "17mi560", "name": "Check", "score": 10.0}]
def getleaderboard():
    #print("SELECT p.id, p.name, p.image_url, ((SELECT SUM(amount) FROM score WHERE profile_id=p.id AND time>=(UNIX_timestamp(timestamp(current_date))+19800)+(SELECT SUM(referal_score) FROM score WHERE profile_id=p.id)) as score FROM profile AS p ORDER BY score DESC LIMIT "+str(startfrom)+", "+str(startfrom+10))
    query = cursor.execute("SELECT p.id, p.name, p.image_url, ((SELECT SUM(amount) FROM score WHERE profile_id=p.id AND time>=(UNIX_timestamp(timestamp(current_date))+19800) AND referal_score=0)) as score FROM profile AS p ORDER BY score DESC")
    result = cursor.fetchall()
    return result


@app.route('/postpoint/<rollno>/<int:points>')
def postpoint(rollno, points):
    query = cursor.execute("INSERT INTO score VALUES(NULL, '"+rollno+"', "+str(points)+", "+str(time.time()+19800)+",0.0)")
    if query:
        return {'status': 'success'}
    else:
        return {'status': 'fail'}

@app.route('/getpoint/<rollno>')
def getpoint(rollno):
    query = cursor.execute("SELECT SUM(amount) AS points FROM score WHERE profile_id = '"+rollno+"' AND time>=(UNIX_timestamp(timestamp(current_date))+19800)")
    result = cursor.fetchone()
    return result

@app.route('/getschedule')
def getschedule():
    query = cursor.execute("SELECT name as club_name, event_id,event_name,event_time,club_logo FROM events,clubs WHERE events.club_id=clubs.id")
    result = cursor.fetchall()
    #for x in result:
        #x["event_time"] = x["event_time"].timestamp()
    return result

@app.route('/posteventlike/<user_id>/<event_id>')
def posteventlike(user_id, event_id):
    userCheck = cursor.execute("SELECT * from profile where id = %s", (user_id))
    if userCheck == 0:
        return {'status': 'No such user'}
    eventCheck = cursor.execute("SELECT * from events where event_id = %s", (event_id))
    if eventCheck == 0:
        return {'status': 'No such event'}
    query = cursor.execute("SELECT * from event_likes where user_id = %s AND event_id = %s", (user_id, event_id))
    if query == 0:
        cursor.execute("INSERT INTO event_likes VALUES (NULL, %s, %s)", (event_id, user_id))
        return {'status': 'success'}
    else:
        return {'status': 'Already Liked'}

@app.route('/geteventlike/<event_id>')
def geteventlike(event_id):
    query = cursor.execute("SELECT COUNT(*) from event_likes where event_id = %s", event_id)
    result = cursor.fetchone()
    return {'likes': result["COUNT(*)"]}

@app.route('/getclubs')
def getclubs():
    query = cursor.execute("SELECT * FROM clubs")
    result = cursor.fetchall()
    return result

@app.route('/getcoreteam')
def getcoreteam():
    query = cursor.execute("SELECT * FROM coreteam")
    result = cursor.fetchall()
    return result

@app.route('/getsponsor')
def getsponsor():
    query = cursor.execute("SELECT * FROM sponsors")
    result = cursor.fetchall()
    return result

winarray = list(range(1,91))
random.shuffle(winarray)

@app.route('/gettambolanumber')
def gettambolanumber():
    time = int(datetime(2018, datetime.now().month, datetime.now().day, 22, 0).timestamp())
    current = int(datetime.now().timestamp())
    if(0 <= current - time <= 3600):
        i = ((current - time) // 15) % 90
        return {'number' : winarray[i]}
    else:
        return {'status': 'Unavailable'}

@app.route('/posttambolaresult')
def posttambolaresult():
    return 'Hello, World!'

@app.route('/getquiz')
def getquiz():
    # returns 10 random questions from category (day)%num_cat
    NUM_CATEGORIES = 7
    day_of_year = datetime.now().timetuple().tm_yday
    curr_cat = (day_of_year % NUM_CATEGORIES)
    query = cursor.execute("SELECT * FROM quiz WHERE category = %s",curr_cat)
    result = cursor.fetchall()
    # choose random 10 from all these
    random.shuffle(result)
    return {'questions':result[:10]}

@app.route('/postprofile/<name>/<rollno>/<phone_no>/<referal>/<imageurl>')
def postprofile(name,rollno,phone_no,referal,imageurl):
    referal=base64.b64decode(referal)
    imageurl=base64.b64decode(imageurl)
    imageurl=(imageurl).decode('utf-8')
    referal=(referal).decode('utf-8')
    # print((imageurl).decode('utf-8')) 
    print(imageurl)
    print(referal)
    try:
        # print("INSERT into profile VALUES('"+rollno+"',"+str(phone_no)+",'"+name+"','"+str(imageurl)+"','"+referal+"')")
        query = cursor.execute("INSERT into profile VALUES('"+rollno+"',"+str(phone_no)+",'"+name+"','"+imageurl+"','"+referal+"')")
        # print(query)
    except:
        # print("UPDATE profile set name = '"+name+"',phone = "+str(phone_no)+",image_url = '"+imageurl+"' where id='"+rollno+"'");
        query = cursor.execute("UPDATE profile set name = '"+name+"',phone = "+str(phone_no)+",image_url = '"+str(imageurl)+"' where id='"+rollno+"'")
        print(query)

        return {'status': 'success'}

    else:
        #print("INSERT INTO score VALUES(NULL, '"+rollno+"',10,"+str(1537940897)+",1),(NULL, '"+referal+"',10,"+str(1537940897)+",1)")
        #query = cursor.execute("INSERT INTO score VALUES(NULL, '"+rollno+"',10,"+str(1537940897)+",1),(NULL, '"+referal+"',10,"+str(1537940897)+",1)")
        query = cursor.execute("INSERT INTO score VALUES(NULL, '"+rollno+"',10,"+str(time.time()+(3600*24*30*6))+",1),(NULL, '"+referal+"',10,"+str(time.time()+(3600*24*30*6))+",1)")
        #query = cursor.execute("INSERT into profile VALUES('"+rollno+"',"+str(phone_no)+",'"+name+"',NULL, NULL)")
    return {'status': 'success'}

@app.route('/checkuser/<phone_no>')
def checkuser(phone_no):
    query = cursor.execute("SELECT COUNT(*) as user_count from profile where phone="+phone_no)
    result = cursor.fetchone()
    print(result['user_count'])
    if result['user_count'] > 0:
        query = cursor.execute("SELECT * from profile where phone="+phone_no)
        result = {'exists': True, 'data': cursor.fetchone()}
        return result
    else:
        return {'exists': False, 'data': {}}


@app.route('/getprofile/<user_id>')
def getprofile(user_id):
    #print("SELECT profile.name as name, profile.id as rollno, profile.image_url as profile_pic, (SELECT SUM(amount) FROM score WHERE profile_id=p.id AND time>=UNIX_timestamp(timestamp(current_date)+19800)) as score FROM profile WHERE profile.id ='"+user_id+"'")
    query = cursor.execute("SELECT profile.name as name, profile.id as rollno, profile.image_url as profile_pic, (SELECT SUM(referal_score) FROM score WHERE score.profile_id=rollno) as score FROM profile WHERE profile.id ='"+user_id+"'")
    result = cursor.fetchall()
    # print(result1)
    return result

@app.route('/deletewallpost/<int:image_id>')
def deletewallpost(image_id):
    query = cursor.execute("DELETE from wall where wall.id='"+str(image_id)+"'")
    if query:
        return {'status': 'success'}
    else:
        return {'status': 'fail'}

@app.route('/postgamestatus/<user_id>')
def postgamestatus(user_id):
    query = cursor.execute("INSERT into game_status values ('"+user_id+"',0,0,0)")
    if query:
        return {'status':'success'}
    else:
        return {'status': 'failure'}

@app.route('/gettambolastatus/<user_id>')
def gettambolastatus(user_id):
    query = cursor.execute("SELECT FORMAT(SUM(tambola_status),0) as tambolastatus from game_status where user_id='"+user_id+"'")
    result = cursor.fetchone()
    return result

@app.route('/posttambolastatus/<user_id>')
def posttambolastatus(user_id):
    query = cursor.execute("INSERT into game_status values ('"+user_id+"',0,1,0)")
    if query:
        return {'status':'success'}
    else:
        return {'status': 'failure'}

@app.route('/getquizstatus/<user_id>')
def getquizstatus(user_id):
    query = cursor.execute("SELECT FORMAT(SUM(quiz_status),0) as quizstatus from game_status where user_id='"+user_id+"'")
    # print("SELECT FORMAT(SUM(quiz_status),0) as quizstatus from game_status where user_id='"+user_id+"'")
    result = cursor.fetchone()
    return result

@app.route('/postquizstatus/<user_id>')
def postquizstatus(user_id):
    query = cursor.execute("INSERT into game_status values ('"+user_id+"',1,0,0)")
    if query:
        return {'status':'success'}
    else:
        return {'status': 'failure'}

@app.route('/getroulettecount/<user_id>')
def getroulettecount(user_id):
    query = cursor.execute("SELECT FORMAT(SUM(roulette_status),0) as roulettecount from game_status where user_id='"+user_idx+"'")
    result = cursor.fetchone()
    return result

@app.route('/postroulettecount/<user_id>')
def postroulettecount(user_id):
    query = cursor.execute("INSERT into game_status values ('"+user_id+"',0,0,1)")
    if query:
        return {'status':'success'}
    else:
        return {'status': 'failure'}



if __name__ == '__main__':
    app.run(debug = True)
