



CREATE DATABASE nc_plus_one;

\c nc_plus_one

DROP TABLE 
DROP TABLE 
DROP TABLE 
DROP TABLE 


CREATE TABLE events (
    title VARCHAR(30) UNIQUE NOT NULL,
    description VARCHAR(50),
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    organiser_id INT NOT NULL REFERENCES users(user_id),
    venue_id INT NOT NULL REFERENCES venues(venue_id);
)

CREATE TABLE rsvps (
    attendee_id INT NOT NULL REFERENCES users(user_id),
    event_id INT NOT NULL REFERENCES events(event_id);
)

CREATE TABLE users (
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL;
)

CREATE TABLE venues (
    name VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    capacity INT NOT NULL; 
)

