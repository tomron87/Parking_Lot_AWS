import json
import uuid
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ParkingLotTickets')

def lambda_handler(event, context):
    try:
        # Try to get from query params first
        plate = None
        parking_lot = None

        if event.get("queryStringParameters"):
            plate = event["queryStringParameters"].get("plate")
            parking_lot = event["queryStringParameters"].get("parkingLot")

        # If not found, try parsing JSON body
        if not plate or not parking_lot:
            try:
                body = json.loads(event.get("body", "{}"))
                plate = plate or body.get("plate")
                parking_lot = parking_lot or body.get("parkingLot")
            except json.JSONDecodeError:
                pass  # invalid JSON, will be caught below

        # Still missing?
        if not plate or not parking_lot:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameters: plate and parkingLot'
                })
            }

        ticket_id = str(uuid.uuid4())
        entry_time = datetime.now(timezone.utc).isoformat()

        table.put_item(
            Item={
                'ticketId': ticket_id,
                'plate': plate,
                'parkingLot': parking_lot,
                'entryTime': entry_time,
                'status': 'active'
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'ticketId': ticket_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }