"""Entry point for WatchTower KE."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n  WatchTower KE is running at http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
