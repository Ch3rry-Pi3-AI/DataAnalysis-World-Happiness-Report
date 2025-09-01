from src.dash_app.create_app import dashboard

app = dashboard()

if __name__ == "__main__":
    app.run(debug=True)