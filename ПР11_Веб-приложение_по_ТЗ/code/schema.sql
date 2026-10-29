PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS role (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    code  VARCHAR(20) UNIQUE NOT NULL,
    name  VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS user (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    login          VARCHAR(50)  UNIQUE NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    fio            VARCHAR(150) NOT NULL,
    phone          VARCHAR(16)  NOT NULL,
    email          VARCHAR(100) NOT NULL,
    role_id        INTEGER      NOT NULL DEFAULT 1,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES role(id)
);

CREATE TABLE IF NOT EXISTS room (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         VARCHAR(100) UNIQUE NOT NULL,
    capacity     INTEGER      NOT NULL CHECK (capacity > 0),
    description  TEXT,
    image        VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS payment_method (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS status (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS request (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id            INTEGER  NOT NULL,
    room_id            INTEGER  NOT NULL,
    payment_method_id  INTEGER  NOT NULL,
    status_id          INTEGER  NOT NULL DEFAULT 1,
    start_at           DATETIME NOT NULL,
    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)           REFERENCES user(id)           ON DELETE CASCADE,
    FOREIGN KEY (room_id)           REFERENCES room(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(id),
    FOREIGN KEY (status_id)         REFERENCES status(id)
);

CREATE TABLE IF NOT EXISTS review (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id  INTEGER  UNIQUE NOT NULL,
    text        TEXT     NOT NULL,
    rating      INTEGER  NOT NULL CHECK (rating BETWEEN 1 AND 5),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES request(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_request_user   ON request(user_id);
CREATE INDEX IF NOT EXISTS idx_request_status ON request(status_id);
CREATE INDEX IF NOT EXISTS idx_request_room   ON request(room_id);

INSERT OR IGNORE INTO role (id, code, name) VALUES
    (1, 'user',  'Участник'),
    (2, 'admin', 'Администратор');

INSERT OR IGNORE INTO status (id, name) VALUES
    (1, 'Новая'),
    (2, 'Мероприятие назначено'),
    (3, 'Завершено');

INSERT OR IGNORE INTO payment_method (id, name) VALUES
    (1, 'При очном посещении'),
    (2, 'Перевод по СБП');
