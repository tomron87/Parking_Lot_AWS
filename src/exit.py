import json
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ParkingLotTickets')

def calculate_fee(entry_time, exit_time):
    entry = datetime.fromisoformat(entry_time)
    exit_dt = datetime.fromisoformat(exit_time)
    total_minutes = (exit_dt - entry).total_seconds() / 60
    increments = (total_minutes + 14) // 15
    fee = increments * 2.5
    return {
        'total_minutes': total_minutes,
        'fee': float(fee)
    }

def lambda_handler(event, context):
    try:
        ticket_id = None

        if event.get("queryStringParameters"):
            ticket_id = event["queryStringParameters"].get("ticketId")

        if not ticket_id:
            try:
                body = json.loads(event.get("body", "{}"))
                ticket_id = ticket_id or body.get("ticketId")
            except json.JSONDecodeError:
                pass

        if not ticket_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: ticketId'
                })
            }

        response = table.get_item(Key={'ticketId': ticket_id})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Ticket not found'
                })
            }

        ticket = response['Item']

        if ticket['status'] != 'active':
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Ticket already used'
                })
            }

        exit_time = datetime.now(timezone.utc).isoformat()
        fee_info = calculate_fee(ticket['entryTime'], exit_time)

        table.update_item(
            Key={'ticketId': ticket_id},
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'completed'}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'plate': ticket['plate'],
                'parkingLot': ticket['parkingLot'],
                'totalTimeMinutes': round(fee_info['total_minutes'], 2),
                'charge': fee_info['fee']
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }