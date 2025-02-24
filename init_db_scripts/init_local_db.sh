docker stop resume_postgres
docker rm resume_postgres
docker network create mynet
docker run -d -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres --name resume_postgres --network mynet -p 5432:5432 postgres
docker cp ./data/resume_2.sql resume_postgres:/resume.sql
sleep 40
docker exec -i resume_postgres pg_restore -U postgres -d postgres /resume.sql
