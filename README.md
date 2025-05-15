# Parking Lot API - Cloud Deployment

A serverless parking‑lot management system on **AWS Lambda + API Gateway + DynamoDB**.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/entry` | POST   | Register a vehicle entering the lot |
| `/exit`  | POST   | Calculate fee & close the ticket |

---

## API Usage

### `/entry`

*Accepts either JSON body **or** query parameters.*

| Parameter | Type   | Required | Description          |
|-----------|--------|----------|----------------------|
| `plate`   | string | ✔        | Vehicle licence plate|
| `parkingLot` | string | ✔    | Lot identifier       |

#### Sample request (JSON)

```bash
curl -X POST https://<api‑id>.execute-api.<region>.amazonaws.com/Prod/entry   -H "Content-Type: application/json"   -d '{"plate":"1234567","parkingLot":"A1"}'
```

#### Sample response

```json
{ "ticketId": "uuid-1234" }
```

---

### `/exit`

| Parameter | Type   | Required | Description                   |
|-----------|--------|----------|-------------------------------|
| `ticketId`| string | ✔        | ID returned by `/entry` call  |

#### Sample request

```bash
curl -X POST https://<api‑id>.execute-api.<region>.amazonaws.com/Prod/exit   -H "Content-Type: application/json"   -d '{"ticketId":"uuid-1234"}'
```

#### Sample response

```json
{
  "plate": "1234567",
  "parkingLot": "A1",
  "totalTimeMinutes": 12.4,
  "charge": 2.5
}
```

---

##  Implementation Details

###  `entry.py` – Vehicle Entry Lambda

This function handles incoming `POST /entry` requests. It supports input through both **query parameters** and **JSON body**. Here's what it does:

1. Extracts `plate` and `parkingLot` parameters.
2. Generates a unique ticket ID (`uuid4`).
3. Records the current UTC timestamp as the **entry time**.
4. Writes the ticket data to a DynamoDB table named `ParkingLotTickets` with `status: active`.
5. Returns the generated `ticketId` as a response.

The Lambda ensures graceful handling of missing or malformed input and returns appropriate HTTP error codes.

---

###  `exit.py` – Vehicle Exit Lambda

This function processes `POST /exit` requests. It also accepts `ticketId` from either **query parameters** or **JSON body**. It works as follows:

1. Retrieves the corresponding ticket record from DynamoDB.
2. Validates that the ticket exists and is still `active`.
3. Calculates the time elapsed since `entryTime` using 15-minute increments.
4. Computes the fee at **$2.50 per 15 minutes**.
5. Updates the ticket `status` to `completed`.
6. Returns the total duration and charge to the user.

The logic ensures no reused or double-processed tickets and handles missing/invalid ticket IDs.

---

###  Infrastructure as Code (`template.yaml`)

The project is deployed using AWS SAM and is defined in a `template.yaml` file. It includes:

- **Two Lambda Functions**:
  - `ParkingLotEntryFunction` (handles `/entry`)
  - `ParkingLotExitFunction` (handles `/exit`)
- Both functions are granted **DynamoDB CRUD access** via `DynamoDBCrudPolicy`.
- **One DynamoDB Table**:  
  `ParkingLotTickets`, using `ticketId` as the partition key.
- **API Gateway Integration**:  
  Automatically created by SAM using the `Events` block under each function.
- **BillingMode**: `PAY_PER_REQUEST` is used to simplify management and avoid provisioning throughput.

Example output is exposed using the `Outputs` section to provide the base API URL post-deployment.

---

###  AWS Deployment Choices

- **Runtime**: `python3.9` is used for compatibility and maturity across AWS Lambda.
- **Region**: `eu-central-1 (Frankfurt)` was selected for low-latency testing from Israel.
- **IAM Role Management**:  
  All permissions were granted using SAM-managed IAM roles. No credentials are hardcoded.
- **S3 Bucket**:  
  A custom bucket `parking-lot-sam-artifacts` was used to avoid depending on SAM’s default stack, which had previously caused permission issues.
- **Stack Name**: `parking-lot-hw1` was used for clarity and relevance to the assignment.

---


##  Security Compliance

* **No** AWS access keys or secrets in source.  
* IAM roles are created automatically by SAM.  
* `.aws/credentials`, `samconfig.toml`, and other local files are excluded from version control.

---


##  Grader Quick Start

1. Make sure AWS CLI and SAM CLI are installed
2. Make sure your AWS user has permissions for: Lambda, API Gateway, DynamoDB, S3, CloudFormation, IAM permissions: `iam:CreateRole` and `iam:PassRole`.
2. Create an S3 bucket (e.g. `parking-lot-grader-bucket`)
3. From project root, run:

```bash
./deploy.sh
```

Once deployed, test with:

```bash
curl -X POST https://<api-id>.execute-api.eu-central-1.amazonaws.com/Prod/entry \
  -H "Content-Type: application/json" \
  -d '{"plate":"1234567","parkingLot":"A1"}'
```

If you want, you can also test using my already built API: 

```
Base API: https://l7f29dwscj.execute-api.eu-central-1.amazonaws.com/Prod/
```