# The backend of MyTherapy.
I led the development of the backend for MyTherapy, a mental health and therapy support platform 
submitted to the Bulgarian National IT Olympiad 2024. The project was awarded 5th place in the national rankings.

The backend is a monolithic FastAPI application designed with clear modularity and scalability in mind. It currently supports two core features
- User Management – authentication, registration, and OAuth2
- Call Scheduling – session managment between users and therapists

## Architecture
The project follows a clean separation of concerns with two main layers
- `applications/` – each feature (module) encapsulates its own business logic and database
- `routers/` – lightweight API endpoints that delegate to the feature layer
This design ensures maintainability while allowing for easy future expansion into a microservice architecture, if needed.

## Stack
FastAPI, TortoiseORM, bcrypt, Pydantic, Google Cloud Platform.

## Frontend
[Can be found here](https://github.com/ForceFinity/my-therapy/)
