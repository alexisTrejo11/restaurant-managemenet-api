--- Table 
CREATE TABLE tables (
    id SERIAL PRIMARY KEY,
    capacity INTEGER NOT NULL,
    number VARCHAR(255) UNIQUE NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table for 2 (small intimate table)
INSERT INTO tables (capacity, number, is_available) VALUES (2, 'T1', true);
-- Table for 4 (standard dining table)
INSERT INTO tables (capacity, number, is_available) VALUES (4, 'T2', true);
-- Table for 6 (larger group table)
INSERT INTO tables (capacity, number, is_available) VALUES (6, 'T3', true);
-- Window-side table for 2 with nice view
INSERT INTO tables (capacity, number, is_available) VALUES (2, 'Window-1', true);
-- Booth seating for 4 people
INSERT INTO tables (capacity, number, is_available) VALUES (4, 'Booth-A', true);
-- High-top table for 4 at the bar area
INSERT INTO tables (capacity, number, is_available) VALUES (4, 'Bar-1', true);
-- Large round table for 8 (for big groups)
INSERT INTO tables (capacity, number, is_available) VALUES (8, 'Round-1', true);
-- Outdoor patio table for 4
INSERT INTO tables (capacity, number, is_available) VALUES (4, 'Patio-3', true);
-- Private room table for 10 (for special events)
INSERT INTO tables (capacity, number, is_available) VALUES (10, 'Private-1', true);
-- Corner table for 2 (popular romantic spot)
INSERT INTO tables (capacity, number, is_available) VALUES (2, 'Corner-2', true);
