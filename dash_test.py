from src.dash_app.create_app import dashboard

app = dashboard(enable_pages=False)

if __name__ == "__main__":
    app.run(debug=True)