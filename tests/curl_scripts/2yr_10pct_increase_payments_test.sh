#!/bin/bash
# Create 24 monthly payments for a 2-year lease contract

echo "Creating payment 1 of 24 - Due: 2025-12-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2025-12-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 2 of 24 - Due: 2026-01-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-01-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 3 of 24 - Due: 2026-02-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-02-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 4 of 24 - Due: 2026-03-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-03-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 5 of 24 - Due: 2026-04-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-04-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 6 of 24 - Due: 2026-05-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-05-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 7 of 24 - Due: 2026-06-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-06-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 8 of 24 - Due: 2026-07-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-07-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 9 of 24 - Due: 2026-08-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-08-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 10 of 24 - Due: 2026-09-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-09-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 11 of 24 - Due: 2026-10-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-10-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 12 of 24 - Due: 2026-11-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1000,
  "due_date": "2026-11-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 13 of 24 - Due: 2026-12-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2026-12-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 14 of 24 - Due: 2027-01-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-01-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 15 of 24 - Due: 2027-02-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-02-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 16 of 24 - Due: 2027-03-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-03-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 17 of 24 - Due: 2027-04-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-04-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 18 of 24 - Due: 2027-05-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-05-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 19 of 24 - Due: 2027-06-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-06-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 20 of 24 - Due: 2027-07-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-07-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 21 of 24 - Due: 2027-08-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-08-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 22 of 24 - Due: 2027-09-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-09-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 23 of 24 - Due: 2027-10-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-10-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\nCreating payment 24 of 24 - Due: 2027-11-01"
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "contract_id": "Lease_2Yr_Payments",
  "amount": 1100,
  "due_date": "2027-11-01T04:07:28.711Z",
  "status": "Scheduled"
}'

echo -e "\n\n✅ All 24 payments created successfully!"
echo "To view summary: curl http://127.0.0.1:8000/api/v1/payments/contract/Lease_2Yr_Payments/summary"

