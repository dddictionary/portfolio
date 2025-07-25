#!/bin/bash
curl -X POST \
  -d "name=John Doe" \
  -d "email=john.doe@example.com" \
  -d "content=This is a test post from curl. Yay!" \
  http://mlhportfolio-aaron.duckdns.org:5000/api/timeline_post

response=$(curl http://mlhportfolio-aaron.duckdns.org:5000/api/timeline_post)
echo $response
exit 0
