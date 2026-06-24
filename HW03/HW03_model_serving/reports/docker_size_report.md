# HW03 Docker Image Size Report

| Repository | Tag | Size |
|---|---|---|
| qbc12-airbnb-serving | naive | 1.91GB |
| qbc12-airbnb-serving | optimized | 923MB |

## Analysis
The naive image (1.91GB) is about twice the size of the optimized image (923MB). It uses the full `python:3.11` base image and `COPY . .`, so the build context includes notebooks, reports, and other files that are not needed to run the API.
The optimized image uses `python:3.11-slim`, a multi-stage build, and a `.dockerignore` file. Dependencies are installed in a builder stage; only the installed packages and `src/` are copied into the final runtime image.
For production I would deploy the optimized image: it is smaller to pull and store, has a smaller attack surface, and runs the same FastAPI service with the model loaded from MLflow at startup.
