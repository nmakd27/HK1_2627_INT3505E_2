BEGIN TRANSACTION;
CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL
        );
INSERT INTO "books" VALUES(1,'Clean Code','Robert Martin');
INSERT INTO "books" VALUES(2,'The Pragmatic Programmer','Andrew Hunt');
INSERT INTO "books" VALUES(3,'Clean Arch','Robert Martin');
INSERT INTO "books" VALUES(4,'Animal Farm','George Orwell');
INSERT INTO "books" VALUES(5,'Head First Java','Kathy Sierra');
INSERT INTO "books" VALUES(6,'Design Patterns','Erich Gamma');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('books',6);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT NOT NULL,
    total REAL NOT NULL
);
INSERT INTO "orders" VALUES(1,'Alice',100.5);
INSERT INTO "orders" VALUES(2,'Bob',250.0);
INSERT INTO "orders" VALUES(3,'Charlie',75.5);
INSERT INTO "sqlite_sequence" VALUES('orders',3);
COMMIT;
