docker run -e POSTGRES_USER=myuser \
           -e POSTGRES_PASSWORD=mypassword \
           -e POSTGRES_DB=mydatabase \
           --name my_postgres \
           -p 5432:5432 \
           -v postgres_data:/var/lib/postgresql/data \
           -d pgvector/pgvector:pg17