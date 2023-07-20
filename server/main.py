import uvicorn

if __name__ == "__main__":
    # Write a pump status switching task every 5 seconds

    # Run the FastAPI application
    uvicorn.run("app.app:app", host="0.0.0.0", port=3389)

