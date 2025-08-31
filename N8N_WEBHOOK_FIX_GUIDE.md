# 🔧 N8N Webhook Fix - Binary Data Error Resolution

## ❌ Error Encountered
```
Problem in node 'HTTP Request1'
This operation expects the node's input data to contain a binary file 'data', but none was found [item 0]
```

## ✅ Solution: Proper N8N HTTP Request Configuration

### Step 1: Ensure Binary Data is Available

Your workflow needs to have binary data available from a previous node. Common sources:
- **HTTP Request** (downloading image from URL)
- **Read Binary File** (local file)
- **Gmail/Outlook** (attachment)
- **WooCommerce** (product image)

### Step 2: Configure HTTP Request Node

#### Node Configuration:
```json
{
  "node": "HTTP Request",
  "method": "POST",
  "url": "https://media-converter-6.preview.emergentagent.com/api/webhook",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": []
  },
  "sendBody": true,
  "contentType": "multipart-form-data",
  "bodyParameters": {
    "parameters": [
      {
        "name": "image",
        "value": "",
        "parameterType": "formBinaryData",
        "inputDataFieldName": "data"
      },
      {
        "name": "json_data",
        "value": "={\"title\": \"{{ $json.title }}\", \"description\": \"{{ $json.description }}\", \"url\": \"{{ $json.url }}\", \"store\": \"gizmobbs\"}",
        "parameterType": "formData"
      }
    ]
  }
}
```

#### Key Settings:
1. **Content Type**: `multipart-form-data`
2. **Body Parameters**:
   - `image`: Set to **Form Binary Data** with field name `data`
   - `json_data`: Set to **Form Data** with JSON string

### Step 3: Complete Working Example

#### Example Workflow: WooCommerce → Instagram

```json
{
  "nodes": [
    {
      "name": "WooCommerce Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "woocommerce"
      }
    },
    {
      "name": "Download Product Image",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "={{ $json.image_url }}",
        "responseFormat": "file",
        "options": {}
      }
    },
    {
      "name": "Publish to Instagram",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://media-converter-6.preview.emergentagent.com/api/webhook",
        "sendHeaders": true,
        "sendBody": true,
        "contentType": "multipart-form-data",
        "bodyParameters": {
          "parameters": [
            {
              "name": "image",
              "parameterType": "formBinaryData",
              "inputDataFieldName": "data"
            },
            {
              "name": "json_data",
              "value": "={\"title\": \"{{ $json.product_name }}\", \"description\": \"{{ $json.product_description }}\", \"url\": \"{{ $json.product_url }}\", \"store\": \"gizmobbs\"}",
              "parameterType": "formData"
            }
          ]
        }
      }
    }
  ]
}
```

## 🔍 Debugging Steps

### 1. Check Binary Data Availability
Add a **Set** node before HTTP Request to debug:
```json
{
  "name": "Debug Binary Data",
  "type": "n8n-nodes-base.set",
  "parameters": {
    "values": {
      "binary": [
        {
          "name": "debug_data",
          "value": "={{ $binary.data }}"
        }
      ]
    }
  }
}
```

### 2. Test Binary Data Field Name
The most common issue is the wrong field name. Try these:
- `data` (most common)
- `attachment`
- `file`
- `image`

### 3. Alternative: Base64 Encoding
If binary data is not working, convert to base64:

```json
{
  "name": "Convert to Base64",
  "type": "n8n-nodes-base.set",
  "parameters": {
    "values": {
      "string": [
        {
          "name": "image_base64",
          "value": "={{ $binary.data.data }}"
        }
      ]
    }
  }
}
```

Then send as form data:
```json
{
  "name": "json_data",
  "value": "={\"title\": \"Test\", \"description\": \"Test\", \"url\": \"https://example.com\", \"image_base64\": \"{{ $json.image_base64 }}\"}",
  "parameterType": "formData"
}
```

## 📋 Quick Fix Checklist

- [ ] Binary data is available from previous node
- [ ] HTTP Request method is **POST**
- [ ] Content Type is **multipart-form-data**
- [ ] Image parameter type is **formBinaryData**
- [ ] Image field name is correct (usually `data`)
- [ ] JSON data is properly formatted string
- [ ] Store name is valid: `gizmobbs`, `outdoor`, `logicantiq`, `ma-boutique`

## 🧪 Test Your Fix

### Test cURL Command:
```bash
curl -X POST "https://media-converter-6.preview.emergentagent.com/api/webhook" \
  -F "image=@/path/to/your/image.jpg" \
  -F 'json_data={"title":"Test Product","description":"Test description","url":"https://example.com/product","store":"gizmobbs"}'
```

### Expected Response:
```json
{
  "status": "success",
  "message": "Webhook processed successfully",
  "data": {
    "image_filename": "webhook_xxxxx.jpg",
    "publication_results": [...]
  }
}
```

## 🎯 Instagram Publishing Results

After fixing the n8n configuration, you should see:
- ✅ Facebook post creation (immediate success)
- 📱 Instagram posting (requires authentication setup)
- 🖼️ Image optimization and EXIF correction
- 📊 Detailed publication results

## 🆘 Still Having Issues?

1. **Check n8n execution log** for detailed error messages
2. **Verify image URL** is accessible and valid format
3. **Test with static image** first before dynamic data
4. **Enable n8n debug mode** to see full request/response

---

Your n8n workflow should now properly send binary image data to the Instagram webhook! 🚀