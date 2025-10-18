-- CREATE TABLE Airline (
--   Airline_ID SERIAL PRIMARY KEY,
--   Name VARCHAR(100),
--   Country VARCHAR(50)
-- );

-- CREATE TABLE Airport (
--   Airport_ID SERIAL PRIMARY KEY,
--   Name VARCHAR(100),
--   City VARCHAR(50),
--   Country VARCHAR(50)
-- );

-- CREATE TABLE Flight (
--   Flight_ID SERIAL PRIMARY KEY,
--   Airline_ID INT REFERENCES Airline(Airline_ID),
--   Source_Airport INT REFERENCES Airport(Airport_ID),
--   Destination_Airport INT REFERENCES Airport(Airport_ID),
--   Departure_Time TIMESTAMP,
--   Arrival_Time TIMESTAMP,
--   Price DECIMAL(10,2) CHECK (Price > 0)
-- );

-- CREATE TABLE Passenger (
--   Passenger_ID SERIAL PRIMARY KEY,
--   Name VARCHAR(100),
--   Email VARCHAR(100) UNIQUE,
--   Phone VARCHAR(20)
-- );

-- CREATE TABLE Booking (
--   Booking_ID SERIAL PRIMARY KEY,
--   Flight_ID INT REFERENCES Flight(Flight_ID),
--   Passenger_ID INT REFERENCES Passenger(Passenger_ID),
--   Booking_Date DATE,
--   Seat_No VARCHAR(10),
--   Status VARCHAR(20)
-- );

-- INSERT INTO Airline (Name, Country) VALUES ('Air India', 'India'), ('Emirates', 'UAE');

-- INSERT INTO Airport (Name, City, Country) VALUES ('Indira Gandhi International', 'Delhi', 'India'),
--        ('Dubai International', 'Dubai', 'UAE');

-- INSERT INTO Flight (Airline_ID, Source_Airport, Destination_Airport, Departure_Time, Arrival_Time, Price)
-- VALUES (1, 1, 2, '2025-10-08 10:00', '2025-10-08 13:00', 15000.00),
--        (2, 2, 1, '2025-10-09 15:00', '2025-10-09 18:30', 14000.00);

-- INSERT INTO Passenger (Name, Email, Phone)
-- VALUES ('Jisto Prakash', 'jisto@gmail.com', '9876543210'),
--        ('Romeo Mathew', 'romeo@gmail.com', '9876509876');

-- INSERT INTO Booking (Flight_ID, Passenger_ID, Booking_Date, Seat_No, Status)
-- VALUES (1, 1, '2025-10-07', '12A', 'Confirmed'),
--        (2, 2, '2025-10-07', '9C', 'Pending');

-- SELECT * FROM Booking;

-- UPDATE Booking SET status='Confirmed' WHERE passenger_id = 2;

-- SELECT
--   f.Flight_ID,
--   a.Name AS Airline_Name,
--   src.Name AS Source_Airport,
--   dest.Name AS Destination_Airport,
--   f.Departure_Time,
--   f.Price
-- FROM
--   Flight f
-- JOIN Airline a ON f.Airline_ID = a.Airline_ID
-- JOIN Airport src ON f.Source_Airport = src.Airport_ID
-- JOIN Airport dest ON f.Destination_Airport = dest.Airport_ID;

-- SELECT* FROM booking;

-- BEGIN; 
-- UPDATE Booking
-- SET Status = 'Cancelled'
-- WHERE Booking_ID = 1;
-- INSERT INTO Booking (Flight_ID, Passenger_ID, Booking_Date, Seat_No, Status)
-- VALUES (2, 1, '2025-10-07', '18B', 'Confirmed');
-- COMMIT;

-- SELECT* FROM booking;

-- INSERT INTO Passenger (Name, Email, Phone)
-- VALUES ('Jisto', 'jisto@gmail.com', '8969667');

INSERT INTO Booking (Flight_ID, Passenger_ID, Booking_Date, Seat_No, Status)
VALUES (596, 1, '2025-10-08', '3A', 'Confirmed');

