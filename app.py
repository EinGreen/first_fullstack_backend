import traceback
import dbconnect
from flask import Flask, request, Response
from flask_cors import CORS
import json
# import bjoern

# Note: pip is for python, npm is for vue and stuff

app = Flask(__name__)
CORS(app)

@app.get("/api/candy")
def get_candy():
    conn = dbconnect.get_db_connection()
    cursor = dbconnect.get_db_coursor(conn)
    candy = None
    
    try:
        # Reminder: bad idea to use * because of inconsistencies
        cursor.execute("SELECT name, description, price, image_url, id FROM candy")
        candy = cursor.fetchall()
    except:
        traceback.print_exc()
        print("Uh oh spaghettio")
    dbconnect.close_db_cursor(cursor)
    dbconnect.close_db_connection(conn)

    if(candy == None):
        return Response("Failed to get candy from Database", mimetype="text/plain", status=500)
    else:
        candy_json = json.dumps(candy, default=str)
        return Response(candy_json, mimetype="application/json", status=200)

@app.post("/api/candy")
def post_candy():
    try:
        candy_name = str(request.json['name'])
        candy_desc = str(request.json['desc'])
        candy_img = str(request.json['img'])
        candy_price = int(request.json['price'])
    except:
        traceback.print_exc()
        print("Uh oh spaghettio")
        return Response("Data Error", mimetype="text/plain", status=400)

    if(candy_name == None or candy_desc == None or candy_img == None or candy_price == None):
        return Response("Data Error", mimetype="text/plain", status=400)

    conn = dbconnect.get_db_connection()
    cursor = dbconnect.get_db_coursor(conn)
    new_id = -1
    
    try:
        cursor.execute(
            "INSERT INTO candy_warmup.candy (name, description, price, image_url) VALUES (?,?,?,?)", 
            [candy_name, candy_desc, candy_price, candy_img])
        conn.commit()
        new_id = cursor.lastrowid
    except:
        traceback.print_exc()
        print("Uh oh spaghettio")
    if new_id == -1:
        return Response("New candy addition failed; try again", mimetype='text/plain   ', status=500)
    else:
        candy_json = json.dumps([candy_name, candy_desc, candy_price, candy_img, new_id], default=str)
        return Response(candy_json, mimetype='application/json', status=200)

    dbconnect.close_db_cursor(cursor)
    dbconnect.close_db_connection(conn)

@app.patch("/api/candy")
def patch_candy():
    candy_id = None
    try:
        candy_id = request.json['id']
        candy_name = request.json.get('name')
        candy_desc = request.json.get('desc')
        candy_price = request.json.get('price')
        candy_img = request.json.get('img')
    except:
        traceback.print_exc()
        return Response("Invalid data input, please try again", mimetype='text/plain', status=400)
    conn = dbconnect.get_db_connection()
    cursor = dbconnect.get_db_coursor(conn)
    candies_arguments = []
    if candy_id != None and candy_id != "":
        try:
            if candy_name != None and candy_name != "":
                cursor.execute("UPDATE candy_warmup.candy SET candy.name = ? WHERE candy.id = ?",
                               [candy_name, candy_id])
                conn.commit()
                candies_arguments.append(candy_name)
        except:
            traceback.print_exc()
            return Response("Failed to update Name, please try again", mimetype='text/plain', status=500)

        try:
            if candy_desc != None and candy_desc != "":
                cursor.execute("UPDATE candy_warmup.candy SET candy.description = ? WHERE candy.id = ?",
                               [candy_desc, candy_id])
                conn.commit()
                candies_arguments.append(candy_desc)
        except:
            traceback.print_exc()
            return Response("Failed to update Description, please try again", mimetype='text/plain', status=500)
        try:
            if candy_price != None and candy_price != "":
                cursor.execute("UPDATE candy_warmup.candy SET candy.price = ? WHERE candy.id = ?",
                               [candy_price, candy_id])
                conn.commit()
                candies_arguments.append(candy_price)
        except:
            traceback.print_exc()
            return Response("Failed to update Price, please try again", mimetype='text/plain', status=500)
        try:
            if candy_img != None and candy_img != "":
                cursor.execute("UPDATE candy_warmup.candy SET candy.image_url WHERE id = ?",
                               [candy_img, candy_id])
                conn.commit()
                candies_arguments.append(candy_img)
        except:
            traceback.print_exc()
            return Response("Failed to update Image, please try again", mimetype='text/plain', status=500)
    else:
        return Response("Something went wrong", mimetype='text/plain', status=400)
    dbconnect.close_db_cursor(cursor)
    dbconnect.close_db_connection(conn)
    if len(candies_arguments) == 0:
        return Response("No updated info inserted", mimetype='text/plain', status=400)
    else:
        candy_json = json.dumps(candies_arguments, default=str)
        return Response(candy_json, mimetype='text/plain', status=200)

@app.delete("/api/candy")
def delete_candy():
    candy_id = None
    try:
        candy_id = int(request.json['id'])
    except:
        traceback.print_exc()
        return Response("Invalid id", mimetype='text/plain', status=400)

    conn = dbconnect.get_db_connection()
    cursor = dbconnect.get_db_coursor(conn)
    try:
        cursor.execute("DELETE FROM candy_warmup.candy WHERE id = ?", [candy_id,])
        conn.commit()
        row_count = cursor.rowcount
    except:
        traceback.print_exc()
        return Response("Please try again", mimetype='text/plain', status=500)
    dbconnect.close_db_cursor(cursor)
    dbconnect.close_db_connection(conn)
    if row_count == 1:
        return Response("Candy deleted!", mimetype='text/plain', status=200)
    else:
        return Response("Something went wrong", mimetype='text/plain', status=500)

app.run(debug=True)
# bjoern.run(app, "0.0.0.0", 5001)
