DROP TABLE IF EXISTS daily_journey_log;
DROP TABLE IF EXISTS dates;

DROP TABLE IF EXISTS terms;
DROP TABLE IF EXISTS journeystops;
--DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS journeys;
DROP TABLE IF EXISTS tt_revisions;
DROP TABLE IF EXISTS education_authorities;

CREATE TABLE education_authorities (id serial PRIMARY KEY, name VARCHAR(255));

CREATE TABLE tt_revisions(id serial PRIMARY KEY, dataset_id INT, date DATE);

CREATE TABLE journeys(id serial PRIMARY KEY, block_ref VARCHAR(255), analysed_block_ref VARCHAR(255), origin VARCHAR(255), destination VARCHAR(255), operator_name VARCHAR(255), route VARCHAR(255), deptime TIME WITHOUT TIME ZONE, run_days VARCHAR(255), termdays INT, holidays INT, direction VARCHAR(255), vehicle_today VARCHAR(255), rev_id INT, FOREIGN KEY (termdays) REFERENCES education_authorities(id), FOREIGN KEY (holidays) REFERENCES education_authorities(id), FOREIGN KEY (rev_id) REFERENCES tt_revisions(id));

--CREATE TABLE stops (id serial PRIMARY KEY, atco_code VARCHAR(255), naptan_code VARCHAR(255), common_name VARCHAR(255), lat FLOAT, lon FLOAT, street VARCHAR(255), locality_name VARCHAR(255), parent_locality_name VARCHAR(255));

CREATE TABLE journeystops (id serial PRIMARY KEY, journeyid INT, stopid INT, reltime INT, FOREIGN KEY (journeyid) REFERENCES journeys(id), FOREIGN KEY (stopid) REFERENCES stops(id));

CREATE TABLE terms (id serial PRIMARY KEY, edid INT, startdate DATE, enddate DATE, FOREIGN KEY (edid) REFERENCES education_authorities(id));

CREATE TABLE dates(id serial PRIMARY KEY, date DATE);

CREATE TABLE daily_journey_log(journeyid INT, block_ref VARCHAR(255), vehicle_today VARCHAR(255), dateid INT, FOREIGN KEY (dateid) REFERENCES dates(id));
