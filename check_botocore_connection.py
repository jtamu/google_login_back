from botocore.session import get_session

session = get_session()

client = session.create_client('dynamodb', 'ap-northeast-1', endpoint_url="http://dynamo-test:8000")

print(client.list_tables())
