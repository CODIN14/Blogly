from applicaton import create_app

app = create_app()

# Test comment to trigger GitHub Actions workflow
if __name__ == "__main__":
    app.run(debug=True)