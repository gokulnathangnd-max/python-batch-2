from flask import Flask , request ,jsonify


app=Flask(__name__)

@app.route("/",methods=["GET","POST"])
def register():
  if request.method=="GET":
    return jsonify(
      {
        "msg":"enter the userdetails correctly"
      } 
    ) , 200
  frontend=request.get_json(force=True)

  if not frontend:
    return jsonify(
      {
        "msg":"the data is not send"
      }
    ) , 400
  username=frontend.get("username")
  password=frontend.get("password")

  if not username or not password:
    return jsonify(
      {
        "msg":"username or password is missing"
      }
    ) , 400

  return jsonify(
    {
      "msg":"the user is saved succesfully"
    }
  ) , 201


if __name__=="__main__":
  app.run(debug=True)

