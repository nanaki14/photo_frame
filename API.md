# API Documentation

## Digital Photo Frame REST API

Complete API reference for the digital photo frame system running on Raspberry Pi Zero 2 WH with Waveshare e-ink display.

**Base URL:** `http://your-pi-ip:3000/api`

## 📋 API Overview

### Authentication
Currently, the API uses no authentication by default. For production deployment, consider implementing basic authentication (see [SECURITY.md](SECURITY.md)).

### Content Types
- **Requests**: `application/json` for data, `multipart/form-data` for file uploads
- **Responses**: `application/json`

### Response Format
All API responses follow this standard format:

```json
{
  "success": boolean,
  "data": object | null,
  "error": string | null
}
```

## 📸 Photo Management

### Upload Photo

Upload a new JPEG image to display on the e-ink screen.

**Endpoint:** `POST /api/photo`  
**Content-Type:** `multipart/form-data`

#### Request
```bash
curl -X POST \
  -F "photo=@your-image.jpg" \
  http://your-pi-ip:3000/api/photo
```

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| photo | File | Yes | JPEG image file (max 10MB) |

#### Response
```json
{
  "success": true,
  "filename": "photo_1640995200000.jpg",
  "uploadedAt": "2021-12-31T12:00:00.000Z",
  "width": 800,
  "height": 480
}
```

#### Error Responses
```json
// File too large
{
  "success": false,
  "error": "File size too large"
}

// Invalid file type
{
  "success": false,
  "error": "Only JPEG files are allowed"
}

// Corrupted image
{
  "success": false,
  "error": "Input buffer contains unsupported image format"
}
```

### Get Current Photo

Retrieve information about the currently displayed photo.

**Endpoint:** `GET /api/photo`

#### Request
```bash
curl http://your-pi-ip:3000/api/photo
```

#### Response
```json
{
  "success": true,
  "data": {
    "filename": "photo_1640995200000.jpg",
    "originalName": "photo_1640995200000.jpg",
    "size": 156789,
    "width": 800,
    "height": 480,
    "uploadedAt": "2021-12-31T12:00:00.000Z"
  }
}
```

#### No Photo Response
```json
{
  "success": true,
  "data": null
}
```

### Delete Current Photo

Remove the currently displayed photo and clear the display.

**Endpoint:** `DELETE /api/photo`

#### Request
```bash
curl -X DELETE http://your-pi-ip:3000/api/photo
```

#### Response
```json
{
  "success": true,
  "data": {
    "success": true
  }
}
```

## ⚙️ Settings Management

### Get Settings

Retrieve current system settings.

**Endpoint:** `GET /api/settings`

#### Request
```bash
curl http://your-pi-ip:3000/api/settings
```

#### Response
```json
{
  "success": true,
  "data": {
    "display": {
      "brightness": 100
    },
    "system": {
      "autoDisplayUpdate": true,
      "keepCurrentPhoto": true
    }
  }
}
```

### Update Settings

Modify system settings.

**Endpoint:** `PUT /api/settings`  
**Content-Type:** `application/json`

#### Request
```bash
curl -X PUT \
  -H "Content-Type: application/json" \
  -d '{"settings": {"display": {"brightness": 80}}}' \
  http://your-pi-ip:3000/api/settings
```

#### Request Body
```json
{
  "settings": {
    "display": {
      "brightness": 80
    },
    "system": {
      "autoDisplayUpdate": true,
      "keepCurrentPhoto": true
    }
  }
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "display": {
      "brightness": 80
    },
    "system": {
      "autoDisplayUpdate": true,
      "keepCurrentPhoto": true
    }
  }
}
```

## 📊 System Status

### Get System Status

Retrieve current system status including battery, storage, and display information.

**Endpoint:** `GET /api/status`

#### Request
```bash
curl http://your-pi-ip:3000/api/status
```

#### Response
```json
{
  "success": true,
  "data": {
    "battery": {
      "level": 100,
      "charging": false
    },
    "storage": {
      "used": 45678901,
      "total": 1000000000,
      "available": 954321099
    },
    "display": {
      "hasPhoto": true,
      "lastUpdate": "2021-12-31T12:00:00.000Z",
      "status": "active"
    }
  }
}
```

#### Status Field Values
| Field | Type | Description |
|-------|------|-------------|
| battery.level | number | Battery percentage (0-100) |
| battery.charging | boolean | Whether device is charging |
| storage.used | number | Used storage in bytes |
| storage.total | number | Total storage in bytes |
| storage.available | number | Available storage in bytes |
| display.hasPhoto | boolean | Whether a photo is currently displayed |
| display.lastUpdate | string | ISO timestamp of last display update |
| display.status | string | Display status: "active", "updating", or "error" |

## 📝 Usage Examples

### JavaScript/TypeScript
```typescript
// Upload photo
const uploadPhoto = async (file: File) => {
  const formData = new FormData();
  formData.append('photo', file);
  
  const response = await fetch('/api/photo', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};

// Get current photo
const getCurrentPhoto = async () => {
  const response = await fetch('/api/photo');
  return await response.json();
};

// Update settings
const updateSettings = async (settings) => {
  const response = await fetch('/api/settings', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ settings })
  });
  
  return await response.json();
};
```

### Python
```python
import requests

BASE_URL = "http://your-pi-ip:3000/api"

# Upload photo
def upload_photo(file_path):
    with open(file_path, 'rb') as f:
        files = {'photo': f}
        response = requests.post(f"{BASE_URL}/photo", files=files)
        return response.json()

# Get current photo
def get_current_photo():
    response = requests.get(f"{BASE_URL}/photo")
    return response.json()

# Get system status
def get_status():
    response = requests.get(f"{BASE_URL}/status")
    return response.json()

# Delete photo
def delete_photo():
    response = requests.delete(f"{BASE_URL}/photo")
    return response.json()
```

### Bash/cURL
```bash
#!/bin/bash

PI_IP="192.168.1.100"
BASE_URL="http://${PI_IP}:3000/api"

# Upload photo
upload_photo() {
    curl -X POST -F "photo=@$1" "${BASE_URL}/photo"
}

# Get current photo info
get_photo() {
    curl -s "${BASE_URL}/photo" | jq .
}

# Get system status
get_status() {
    curl -s "${BASE_URL}/status" | jq .
}

# Delete current photo
delete_photo() {
    curl -X DELETE "${BASE_URL}/photo"
}

# Update display brightness
set_brightness() {
    curl -X PUT \
      -H "Content-Type: application/json" \
      -d "{\"settings\": {\"display\": {\"brightness\": $1}}}" \
      "${BASE_URL}/settings"
}

# Usage examples
upload_photo "vacation.jpg"
get_status
set_brightness 80
```

## 🔄 Webhook Integration

While the current API doesn't support webhooks, you can implement polling for status changes:

```javascript
// Poll for photo changes
const pollForChanges = () => {
  let lastUpdate = null;
  
  setInterval(async () => {
    const status = await fetch('/api/status').then(r => r.json());
    
    if (status.data.display.lastUpdate !== lastUpdate) {
      lastUpdate = status.data.display.lastUpdate;
      console.log('Photo updated!', status.data.display);
      // Handle photo change
    }
  }, 5000); // Check every 5 seconds
};
```

## 🚨 Error Handling

### Common Error Codes
| HTTP Code | Description | Typical Cause |
|-----------|-------------|---------------|
| 400 | Bad Request | Invalid file type, size too large, malformed JSON |
| 404 | Not Found | Invalid endpoint |
| 429 | Too Many Requests | Rate limiting (if implemented) |
| 500 | Internal Server Error | Server processing error, display update failure |

### Error Response Examples
```json
// File validation error
{
  "success": false,
  "error": "Only JPEG files are allowed"
}

// Server error
{
  "success": false,
  "error": "Failed to process image"
}

// Network error (no response)
// Handle with try/catch in client code
```

### Best Practices for Error Handling
```javascript
const apiCall = async (url, options = {}) => {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'API call failed');
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};
```

## 📱 Mobile Integration

### React Native Example
```javascript
import { launchImageLibrary } from 'react-native-image-picker';

const PhotoUploadComponent = () => {
  const uploadPhoto = () => {
    launchImageLibrary({ mediaType: 'photo' }, (response) => {
      if (response.assets && response.assets[0]) {
        const asset = response.assets[0];
        
        const formData = new FormData();
        formData.append('photo', {
          uri: asset.uri,
          type: asset.type,
          name: asset.fileName || 'photo.jpg'
        });
        
        fetch('http://your-pi-ip:3000/api/photo', {
          method: 'POST',
          body: formData,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        .then(response => response.json())
        .then(data => console.log('Upload success:', data))
        .catch(error => console.error('Upload error:', error));
      }
    });
  };
  
  return (
    <Button title="Upload Photo" onPress={uploadPhoto} />
  );
};
```

## 🔧 Development Tools

### API Testing with Postman

1. **Import Collection**: Create a Postman collection with these endpoints
2. **Environment Variables**: Set `{{base_url}}` to your Pi's URL
3. **Test Scripts**: Add response validation scripts

### OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: Digital Photo Frame API
  version: 1.0.0
  description: REST API for Raspberry Pi digital photo frame
servers:
  - url: http://your-pi-ip:3000/api
paths:
  /photo:
    post:
      summary: Upload photo
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                photo:
                  type: string
                  format: binary
      responses:
        '200':
          description: Upload successful
    get:
      summary: Get current photo
      responses:
        '200':
          description: Photo information
    delete:
      summary: Delete current photo
      responses:
        '200':
          description: Photo deleted
  /status:
    get:
      summary: Get system status
      responses:
        '200':
          description: System status
  /settings:
    get:
      summary: Get settings
      responses:
        '200':
          description: Current settings
    put:
      summary: Update settings
      requestBody:
        content:
          application/json:
            schema:
              type: object
      responses:
        '200':
          description: Settings updated
```

## 📚 Additional Resources

- [Hono Framework Documentation](https://honojs.dev/)
- [Sharp Image Processing](https://sharp.pixelplumbing.com/)
- [React Query Guide](https://tanstack.com/query/latest)
- [Raspberry Pi API Development](https://www.raspberrypi.org/documentation/)

---

## Support

For API issues or questions:
1. Check the logs: `sudo journalctl -u photo-frame.service -f`
2. Verify service status: `systemctl status photo-frame.service`
3. Test endpoints with curl commands above
4. Review error responses for debugging information