*day-1*

# Flask Learning Notes(app.py)

## Import
- We import Flask class from flask module

## App Creation
- app = Flask(__name__)
- app is an object of Flask class
- __name__ defines the current file/module which is running

## Routing
- @app.route('/user', methods=['GET'])
- Decorator attaches URL to the function below it
- Function name can be different from URL

## Function
- def user()
- This function runs when /user URL is accessed

## Return
- return "hello world"
- Sends response back to browser

## Main Block
- if __name__ == "__main__":
- Left side is variable, right side is string
- Ensures app runs only when file is executed directly

## Debug Mode
- app.run(debug=True)
- Automatically reloads server on changes

*day-2*

## Import
- from flask import Flask, request, jsonify
- we import Flask class from flask module
- request is used to take data from frontend
- jsonify is used to convert data into JSON format

- from flask_cors import CORS
- used because frontend and backend connect issue happens in browser

## CORS
- CORS(app)
- allows frontend to connect with backend without blocking error
# Flask Learning Notes (app.py)

## Import
- from flask import Flask, request, jsonify
- we import Flask class from flask module

## Routing
- @app.route('/user',methods = ['POST'])
- decorator attaches URL to the function below it
- we use POST because we want to take data and send response


## Get JSON data
- data = request.get_json()
- send req to take json data

## Get name
- name = data.get('name')
- gets name from json format

## Validation
- if not name or not name.strip()
- if name is empty or space only, strip removes space

## Error response
- response = {
    "status":"error",
    "message":"invalid name"
  }
- response json format to send to js file
- return jsonify(response)
- send response json format only if condition is true

## Success response
- msg = {
    "status": "success",
    "message": f"Hello {name}, request received successfully!"
  }
- msg json format if its successful

## Return
- return jsonify(msg)
- sends msg json format if its successful






# Flask Learning Notes(index.html script)

## Function
- async function sendData()
- This function runs when we click the button
- async means the function will wait for backend response (server reply)

## Getting value from input
- let name = document.getElementById("nameInput").value;
- document means whole HTML page
- getElementById finds the input box using id nameInput
- value means whatever user typed in input box

## Fetch (send data to backend)
- let response = await fetch("http://127.0.0.1:5000/user", {...})
- fetch is used to send request from frontend to backend (Flask server)
- it connects frontend and backend
- await means wait until server accepts and replies

## Method
- method: "POST"
- POST is used because we are sending data to server
- not just asking data, but sending input

## Headers
- "Content-Type": "application/json"
- tells backend that we are sending data in JSON format
- helps Flask understand request properly

## Body (data sending part)
- body: JSON.stringify({ name: name })
- actual data sent to backend
- converts JS object into JSON format
- example: { name: "Urvashi" }

## Getting response from backend
- let data = await response.json();
- this stores server response
- converts JSON response into JavaScript object

## Showing output on screen
- document.getElementById("result").innerText =
  data.status + "\n" + data.message;

- finds result section in HTML
- shows response from backend
- data.status means status from Flask
- data.message means message from Flask

## Flow of whole process
- user types name
- JS takes input
- fetch sends data to Flask
- Flask processes request
- Flask sends JSON response
- JS receives response
- result is shown on screen
