-- Keep a log of any SQL queries you execute as you solve the mystery.
LOG 1 -- searched for the crime seen to find evidence
SELECT
  id,
  description
FROM
  crime_scene_reports
WHERE
  month = 7
  and day = 28
  and street = 'Humphrey Street';

-- evidence found
-- -time: 10:15am
-- -place:  the Humphrey Street bakery
-- -witnesses: 3
LOG 2 -- gets suspects names
-- gets the license_plate of pepole who exited after the crime within 10 min
SELECT
  name
FROM
  people
  join bakery_security_logs on bakery_security_logs.license_plate = people.license_plate
WHERE
  year = 2021
  and month = 7
  and day = 28
  and hour = 10
  and minute >= 15
  and minute <= 25
  and activity = 'exit';

-- current suspects
-- Vanessa
-- Barry
-- Iman
-- Sofia
-- Luca
-- Diana
-- Kelsey
-- Bruce
LOG 3 -- gets the witnesses interveiwes
SELECT
  name,
  transcript
FROM
  interviews
WHERE
  year = 2021
  and month = 7
  and day = 28 -- Sometime within ten minutes of the theft, I saw the thief get into a car in the bakery parking lot and drive away. If you have security footage from the bakery parking lot, you might want to look for cars that left the parking lot in that time frame.
  -- I don't know the thief's name, but it was someone I recognized. Earlier this morning, before I arrived at Emma's bakery, I was walking by the ATM on Leggett Street and saw the thief there withdrawing some money.
  -- As the thief was leaving the bakery, they called someone who talked to them for less than a minute. In the call, I heard the thief say that they were planning to take the earliest flight out of Fiftyville tomorrow. The thief then asked the person on the other end of the phone to purchase the flight ticket.
  LOG 4 -- selects suspects based on the atm evident and the car exit evident
select
  name
from
  people
where
  id in (
    -- selet person id of suspects
    select
      person_id
    from
      bank_accounts
      join atm_transactions on atm_transactions.account_number = bank_accounts.account_number
    WHERE
      year = 2021
      and month = 7
      and day = 28
      and atm_location = 'Leggett Street'
      and transaction_type = 'withdraw'
  ) -- matches the with the old suspects list
  and name in (
    SELECT
      name
    FROM
      people
      join bakery_security_logs on bakery_security_logs.license_plate = people.license_plate
    WHERE
      year = 2021
      and month = 7
      and day = 28
      and hour = 10
      and minute >= 15
      and minute <= 25
      and activity = 'exit'
  ) LOG 5 -- new list of suspects based on the three witness evidents
  -- made some refactoring to mimize the query
select
  name
from
  people
  join phone_calls on phone_calls.caller = people.phone_number
  join bank_accounts on bank_accounts.person_id = people.id
  join atm_transactions on atm_transactions.account_number = bank_accounts.account_number
  join bakery_security_logs on bakery_security_logs.license_plate = people.license_plate
WHERE
  phone_calls.year = 2021
  and phone_calls.month = 7
  and phone_calls.day = 28
  and phone_calls.duration <= 60
  and atm_transactions.year = 2021
  and atm_transactions.month = 7
  and atm_transactions.day = 28
  and atm_transactions.atm_location = 'Leggett Street'
  and atm_transactions.transaction_type = 'withdraw'
  and bakery_security_logs.year = 2021
  and bakery_security_logs.month = 7
  and bakery_security_logs.day = 28
  and bakery_security_logs.hour = 10
  and bakery_security_logs.minute >= 15
  and bakery_security_logs.minute <= 25
  and bakery_security_logs.activity = 'exit';

-- new list
-- Bruce
-- Diana
LOG 6 -- checking if bruce traveld the day after the crime
-- he had
-- he is heading to newYork
select
  *
from
  people
  join passengers on passengers.passport_number = people.passport_number
  join flights on flights.id = passengers.flight_id
  join airports on airports.id = flights.destination_airport_id
where
  name = 'Bruce' LOG 7 -- the number of the person bruce called on 27 of july
SELECT
  name,
  *
FROM
  people
  JOIN phone_calls ON people.phone_number = phone_calls.receiver
WHERE
  phone_calls.year = 2021
  AND phone_calls.month = 7
  AND phone_calls.day = 28
  AND phone_calls.duration <= 60
ORDER BY
  phone_calls.duration;

-- his name
SELECT
  name,
  *
FROM
  people
  JOIN phone_calls ON people.phone_number = phone_calls.receiver
WHERE
  phone_calls.year = 2021
  AND phone_calls.month = 7
  AND phone_calls.day = 28
  AND phone_calls.duration <= 60
  AND phone_calls.caller = '(367) 555-5533'
ORDER BY
  phone_calls.duration;

-- Robin