from app import create_app

app = create_app()

if __name__ == "__main__":
    # Required: run at port 8080 and on localhost or 0.0.0.0
    app.run(host="0.0.0.0", port=8080, debug=True,use_reloader = False)
