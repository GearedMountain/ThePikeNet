from pikenet import create_app

app = create_app()

if __name__ == '__main__':
    socketio.run(debug=True)
