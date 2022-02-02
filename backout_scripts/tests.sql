--undo_create_table
 DROP TABLE DUMMY_TABLE;

--undo_drop_table
 CREATE TABLE DUMMY_TABLE (
id INT NOT NULL DEFAULT 1,name VARCHAR NULL
);

--undo_add_column
 ALTER TABLE DUMMY_TABLE
DROP COLUMN description;

--undo_add_columns
 ALTER TABLE DUMMY_TABLE
DROP COLUMN name,description;

--undo_drop_column
 ALTER TABLE DUMMY_TABLE
ADD COLUMN id INT NOT NULL DEFAULT 1;

--undo_drop_columns
 ALTER TABLE DUMMY_TABLE
ADD COLUMN id INT NOT NULL DEFAULT 1,name VARCHAR NULL;
