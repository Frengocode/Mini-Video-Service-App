# 🚀 Meno - Video Service App

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-FCA121?style=for-the-badge&logo=python&logoColor=white)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://swagger.io/)
[![Pydantic](https://img.shields.io/badge/Pydantic-3776AB?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/latest/)
![Kafka](https://img.shields.io/badge/kafka-%23231F20.svg?style=for-the-badge&logo=apachekafka&logoColor=white)


## 📚 Features

- **User Authentication & Authorization**: Secure login, signup, and JWT-based token management.
- **Content Sharing**: Users can upload photos, reels, and interact with them through likes and comments.
- **Efficient Database Management**: Utilizing PostgreSQL with SQLAlchemy ORM and Alembic for migrations.
  
## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance framework for building APIs.
- **Database**: [PostgreSQL](https://www.postgresql.org/) - Powerful, open-source object-relational database.
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit and Object Relational Mapper.
- **Real-time Communication**: WebSocket for handling real-time notifications and updates.
- **Containerization**: [Docker](https://www.docker.com/) - Ensures the application runs smoothly in different environments.
- **Task Scheduling**: [Apscheduler](https://apscheduler.readthedocs.io/en/latest/) - Advanced Python scheduler.
  

## 🖥️ Installation

### Prerequisites

Ensure you have the following installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/) (for database management)
- ![Kafka](https://img.shields.io/badge/kafka-%23231F20.svg?style=for-the-badge&logo=apachekafka&logoColor=white)

### Clone the Repository and You need to specify DATABASE_URL in database/database.py 

```bash
git clone https://github.com/Frengocode/Meno.git
cd Meno
uvicorn main.main:app --reload

DATABASE_URL  = postgresql://username:password@localohost/Meno
