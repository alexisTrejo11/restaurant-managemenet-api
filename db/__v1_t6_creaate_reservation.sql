CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(255) NOT NULL,
    customer_number INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL,
    table_id INTEGER NOT NULL,
    reservation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP WITH TIME ZONE, -- NULLable
    FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE RESTRICT,
    CONSTRAINT chk_reservation_status CHECK (status IN ('PENDING', 'BOOKED', 'ATTENDED', 'NOT_ATTENDED', 'CANCELLED'))
);

INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
VALUES (
    'John Smith',
    '+15551234567',
    4,
    'john.smith@example.com',
    (SELECT id FROM tables WHERE number = 'T2'),
    CURRENT_TIMESTAMP + INTERVAL '2 days 19:00',
    'BOOKED'
);


INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, created_at)
VALUES (
    'Emily Johnson',
    '+15559876543',
    2,
    'emily.j@example.com',
    (SELECT id FROM tables WHERE number = 'Window-1'),
    CURRENT_TIMESTAMP - INTERVAL '3 days 19:30',
    'ATTENDED',
    CURRENT_TIMESTAMP - INTERVAL '5 days'
);


INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, cancelled_at)
VALUES (
    'Michael Brown',
    '+15555551234',
    6,
    'michael.b@example.com',
    (SELECT id FROM tables WHERE number = 'Round-1'),
    CURRENT_TIMESTAMP + INTERVAL '1 day 20:00',
    'CANCELLED',
    CURRENT_TIMESTAMP - INTERVAL '2 hours'
);


INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
VALUES (
    'Sarah Wilson',
    '+15553334455',
    3,
    'sarah.w@example.com',
    (SELECT id FROM tables WHERE number = 'Booth-A'),
    CURRENT_TIMESTAMP - INTERVAL '1 day 18:45',
    'NOT_ATTENDED'
);


INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
VALUES (
    'Sarah Wilson',
    '+15553334455',
    3,
    'sarah.w@example.com',
    (SELECT id FROM tables WHERE number = 'Booth-A'),
    CURRENT_TIMESTAMP - INTERVAL '1 day 18:45',
    'NOT_ATTENDED'
);


INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
VALUES (
    'David Lee',
    '+15557778899',
    5,
    'david.lee@example.com',
    (SELECT id FROM tables WHERE number = 'Private-1'),
    CURRENT_TIMESTAMP + INTERVAL '3 days 20:30',
    'PENDING'
);

INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
VALUES (
    'Robert and Maria Garcia',
    '+15556667777',
    2,
    'garcia.family@example.com',
    (SELECT id FROM tables WHERE number = 'Corner-2'),
    CURRENT_TIMESTAMP + INTERVAL '1 week 19:00',
    'BOOKED'
);

INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, created_at)
VALUES (
    'TechSolutions Inc.',
    '+15552468013',
    4,
    'events@techsolutions.com',
    (SELECT id FROM tables WHERE number = 'T3'),
    CURRENT_TIMESTAMP - INTERVAL '5 hours',
    'ATTENDED',
    CURRENT_TIMESTAMP - INTERVAL '2 days'
);

INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, cancelled_at)
VALUES (
    'Jessica Taylor',
    '+15558765432',
    8,
    'jessica.t@example.com',
    (SELECT id FROM tables WHERE number = 'Round-1'),
    CURRENT_TIMESTAMP + INTERVAL '1 hour',
    'CANCELLED',
    CURRENT_TIMESTAMP - INTERVAL '30 minutes'
);


INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, created_at)
VALUES (
    'Thomas Anderson',
    '+15551231234',
    4,
    'thomas.a@example.com',
    (SELECT id FROM tables WHERE number = 'Window-1'),
    CURRENT_TIMESTAMP - INTERVAL '1 week 19:15',
    'ATTENDED',
    CURRENT_TIMESTAMP - INTERVAL '2 weeks'
);

INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
VALUES (
    'Smith Family Reunion',
    '+15554443322',
    12,
    'smith.family@example.com',
    (SELECT id FROM tables WHERE number = 'Private-1'),
    CURRENT_TIMESTAMP + INTERVAL '2 weeks 12:00',
    'BOOKED'
);