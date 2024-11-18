# Desafio Neural Med Caio
  

## Project Folder Structure
```
desafio_neural_med_caio
│   README.md
│   docker-compose.yml    
│
└───front/
└───ml_service/
```

## Infra
-  **Front**: The frontend application used to send input messages, read output messages, query Redis, and query PostgreSQL.
-  **ML Service**: This service reads messages from the RabbitMQ queue, processes them with the NerModel, and saves the output to another queue, Redis, and PostgreSQL.
-  **Redis**: Acts as the hot storage for data.
-  **PostgreSQL**: Serves as the cold storage for data.
-  **RabbitMQ**: The main data integrator, from which the input is received and the output is sent.


## Architecture Diagram
![Architecture Diagram](diagram.png)


## Quick Tutorial: Running the Services
1.  **Install Docker and Docker Compose**: Ensure you have Docker and Docker Compose installed on your machine.

2.  **Clone the Repository**: Clone this repository to your local machine.
```bash
git clone <repository-url>

cd desafio_neural_med_caio
```  

3.  **Start the Services**: Use Docker Compose to start all services.
```bash
docker-compose up
``` 

4.  **Access the Services**:
-  **RabbitMQ Management UI**: Open your browser and go to `http://localhost:15672` (default user: `guest`, password: `guest`).
-  **Frontend Application**: Access the frontend at `http://localhost:8501`.
  

## Demonstration
![caption](demonstration.gif)