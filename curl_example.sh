curl -X POST "http://localhost:8000/messages?session_id=<SESSION_ID>" \
     -H "Content-Type: application/json" \
     -d '{
           "jsonrpc": "2.0",
           "id": 1,
           "method": "tools/call",
           "params": {
             "name": "search_providers",
             "arguments": {
               "query": "Mayo Clinic",
               "state": "MN"
             }
           }
         }'
