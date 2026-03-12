from app import app
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['role'] = 'admin'
        sess['user_id'] = 1
    response = client.get('/', follow_redirects=True)
    
    if b'categoryChart' in response.data:
        print("Chart rendered successfully")
    else:
        print("Chart not found")
        
    # extract script
    import re
    m = re.search(r'data:\s*\[.*?\]', response.data.decode('utf-8'))
    if m:
        print(m.group(0))
