import uvicorn

uvicorn.run("gateway:app", host="0.0.0.0", port=4000)
