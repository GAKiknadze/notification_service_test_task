from src import rest_app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(rest_app, host="0.0.0.0", port=8000, log_config=None)
