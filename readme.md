# EzWorks Flask Client

This is an assignment for a college placement company named EzWorks. The task was to create a backend-server in a Python-based backend framework.

To finish this task, I've made use of the following stack:
1. MongoDB
2. Flask
3. Python (3.12)

Other dependency packages are part of the `requirements.txt` stored at the root of the project.

The API was tested with the help of Postman and `curl`. The API is ready for production use with minor changes that depend on the use case of the organization.

### Key points:
1. The API connects itself to a MongoDB Atlas instance which can be easily replaced with a local MongoDB instance.
2. The server stores the password in MongoDB as a hash, not as plain text. This ensures that in the case of a data breach, the user's passwords are never stolen.
3. The server requires a JWT token as the authorization header before allowing the user to perform any actions on the server that are directly part of the authentication process. In other words, except login, and signup, every process requires a JWT token to work.
4. The server creates unique session IDs and associates each session with a JWT token that is generated on login. In order to invalidate a session, a `logout` call must be made to delete the token and the session from the system.
5. A session and its associated JWT is only valid for 365 days after which the user must log-in again and re-generate a JWT.

## Running

Step 0: **Before running the server, make sure to add a .env file to the root directory of the project with the following _strictly required contents_**
```sh
MONGO_CONNECTION_STRING = "<YOUR MONGODB CONNECTION STRING>"
JWT_SECRET = "<YOUR JWT SECRET>"
JWT_ALGO = "HS256"
```
Replace the the content within `<>` with actual content as per the enclosed text. You may replace the `<YOUR MONGODB CONNECTION STRING>` with a local MongoDB instance or one hosted on Mongo Atlas or even AWS.

Step 1: Clone the repository to your local system
In bash or any UNIX or POSIX-compliant shell, run:
```bash
$ git clone git@github.com:103sbavert/EzWorksServer.git
$ cd EzWorksServer
```

For non-UNIX shells, the steps must be similar.

Step 2: Activate the python virtual environment and install required packages (if needed)
```bash
$ source .venv/bin/python3
$ pip install --requirement=./requirements.txt
```

Step 3: Run the flask app
```bash
$ flask run --debug
```
This should output the server's private IP address and the port number that you can then make requests to using `curl` or Postman.

## Explanation of the working
The API is REST-ful and it exposes the following HTTP endpoints

### POST
- /client/signup [(video)](/postmanvideos/client_signup.webm)
- /client/login [(video)](/postmanvideos/client_login.webm)
- /ops/signup [(video)](/postmanvideos/ops_signup.webm)
- /ops/login [(video)](/postmanvideos/ops_login.webm)
- /ops/upload [(video)](/postmanvideos/ops_upload.webm)

### GET
- /logout
- /client/files/\<ops_username\> [(video)](/postmanvideos/client_list_files.webm)
- /client/files/\<ops_username\>/\<file_name\> [(video)](/postmanvideos/client_download_file.webm)

### Using end points
#### 1. /[ops|client]/signup
This URL endpoint only accepts an HTTP `GET` method and in order to work correctly, it expects some form data of the following format:
```json
{
	"username": <username>,
	"password": <password>
}
```
Text wrapped with `<>` should be replaced with valid JSON values representing the actual value you want to pass to the server.

**NOTE: If a username already exists for the provided user type (OPS or CLIENT), the server returns 409 (Conflict) HTTP status code. Two users of the same type cannot have the same username, but two users of different types (suppose one OPS and one CLIENT) can sign up using the same usernames**

#### 2. /[ops|client]/login
Like the last one, this URL end point also only accepts an HTTP `GET` call and it expects the same form data as well.

The only differences between `/login` and `/signup` are that:
	a. When `/login` is called, the server returns a JWT token encoded with the HS256 hashing algorithm as plain text
	b. The server does not return an error if the username is found to be in the server. In fact, it returns a 404 (Not Found) HTTP status code if the username is not found within the database

The response to a successful `/login` call may look like this:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJFeldvcmtzIiwic3ViIjoic2JldmU3MiIsImF1ZCI6ImNsaWVudCIsInNpZCI6MTcyNzU1NzMwMSwiZXhwIjoxNzU5MDkzMzAxfQ.tQLvDnKxVqYUGqO9KQ5_yHeX55FXCAs5BEZlBUGYM68
```


#### 3. /ops/upload
This endpoint allows operators to upload files to the server which can then downloaded easily by a valid client using the file's name. If the file's name is unknown by the client, the client may list it with __5. /client/files/<ops_username>__

In order to successfully finish the upload process, the user has to specify to upload the file as a file attachment to the server.
A curl request to do so may look as follows:
```
curl --location 'http://127.0.0.1:5000/ops/upload' --header 'Authorization: Bearer <token>' --form 'request_file=@"/home/sbavert/Downloads/file.pdf"'
```
and here is how an plain HTTP request packet may look like in plain text

```
POST /ops/upload HTTP/1.1
Host: 127.0.0.1:5000
Authorization: Bearer <token>
Content-Length: 207
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="request_file"; filename="file.pdf"
Content-Type: application/pdf

(data)
------WebKitFormBoundary7MA4YWxkTrZu0gW--

```

As before, replace `<token>` with an actual JWT.

#### 4. /logout
This endpoint does not require an argument but JWT bearer is expected in the `Authorization` header through which the session is discarded and future log-ins to the server with the same token is made impossible.

#### 5. /client/files/\<ops_username\>
As briefly mentioned before, this endpoint helps clients list all the files uploaded by `<ops_username>` (replaced with an actual username).  In order for the functionality to work, it expects a valid JWT bearer in the `Authorization` header that is of a valid session in the database.

#### 6. /client/files/\<ops_username\>/\<file_name\>
This endpoint is used by a client for downloading a file uploaded by an operator. Like the previous one, this also expects a JWT bearer token in order to work correctly. Additionally, it expects the name of the file to be downloaded by the client which must have been uploaded by the specified operator.
