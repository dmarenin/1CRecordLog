from server import app

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 2034

    app.run(HOST, PORT, threaded=True) 

