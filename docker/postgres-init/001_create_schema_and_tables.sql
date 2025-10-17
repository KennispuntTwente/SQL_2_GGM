-- Create a small demo schema and table in the default database (srcdb)
CREATE SCHEMA IF NOT EXISTS staging;

-- Source table in staging schema
DROP TABLE IF EXISTS staging.demotable;
CREATE TABLE staging.demotable (
  id   INTEGER PRIMARY KEY,
  val  VARCHAR(50)
);

INSERT INTO staging.demotable (id, val) VALUES (1, 'foo'), (2, 'bar');

-- Create a simple silver schema and target table for staging_to_silver smoke
CREATE SCHEMA IF NOT EXISTS silver;

DROP TABLE IF EXISTS silver.demo_silver;
CREATE TABLE silver.demo_silver (
  id   INTEGER PRIMARY KEY,
  val  VARCHAR(50)
);
