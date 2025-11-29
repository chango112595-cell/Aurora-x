
#!/bin/bash

# First, login as admin to get the access token
echo "Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Alebec95!"}')

# Extract the access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"accessToken":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to login. Please check the current password."
  exit 1
fi

echo "Login successful!"
echo "Enter new password for admin:"
read -s NEW_PASSWORD

# Change the password
curl -X POST http://localhost:5000/api/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{\"currentPassword\":\"Alebec95!\",\"newPassword\":\"$NEW_PASSWORD\"}"

echo ""
echo "Password change complete!"
