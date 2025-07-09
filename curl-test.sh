#!/bin/bash
curl --request POST http://localhost:5000/api/timeline_post -d 'name=Aaron&email=a@example.io&content=first test post'
response=$(curl http://localhost:5000/api/timeline_post)
echo $response
exit 0
