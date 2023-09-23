
The goal of this project is to explore methods for improving the performance of web applications.
Python and FastApi will be used.

To start project
Build the image:
$ docker build -t fast-api-a .

Run a fast-api container:
$ docker run -p 8000:8000 fast-api-a

And access it through a browser:
127.0.0.1:8000/health/