CREATE TABLE IF NOT EXISTS urls (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE,
    last_check DATE,
    status_code INT
);

CREATE TABLE IF NOT EXISTS url_checks (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    url_id INT,
    status_code INT,
    h1 varchar(255),
    title TEXT,
    description TEXT ,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE
);