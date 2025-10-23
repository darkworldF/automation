# 🚀 API Setup Guide - Quick Configuration

## Step 1: Get Your API Credentials

After creating your "Product Import Tool" private app in Shopify:

1. **In your Shopify Admin** → Apps → App and sales channel settings
2. **Click on "Product Import Tool"** (the app you created)
3. **Copy these credentials:**

### Required Credentials:
- **Store URL**: `nlebike.myshopify.com`
- **Admin API access token**: Starts with `shpat_...`
- **API key**: Alphanumeric string
- **API secret**: Alphanumeric string

## Step 2: Update config.ini

Open `config.ini` and update the `[SHOPIFY_API]` section:

```ini
[SHOPIFY_API]
store_url = nlebike.myshopify.com
api_version = 2023-10
access_token = shpat_your_actual_access_token_here
api_key = your_actual_api_key_here
api_secret = your_actual_api_secret_here
```

## Step 3: Verify App Permissions

Make sure your private app has these permissions enabled:

- ✅ **write_products** - Create and update products
- ✅ **read_products** - Read existing products
- ✅ **write_product_listings** - Manage product visibility
- ✅ **read_inventory** - Read inventory levels
- ✅ **write_inventory** - Update inventory levels

## Step 4: Run the Import

**Windows:**
```
setup_and_run_api.bat
```

**Mac/Linux:**
```
./setup_and_run_api.sh
```

## 🛡️ Security Note

Your API credentials are stored locally and only sent directly to your Shopify store. Never share these credentials with anyone.

## 🎯 Expected Results

- Products will be created as **drafts** in your Shopify admin
- You can review before publishing
- Duplicates are automatically detected and skipped
- Progress is shown in real-time during import

## 🔍 Troubleshooting

If you get permission errors:
1. Check that all required scopes are enabled in your private app
2. Verify the API credentials are correctly copied
3. Make sure the store URL is correct (nlebike.myshopify.com)

---

**Ready to import?** Just run `setup_and_run_api.bat` (Windows) or `./setup_and_run_api.sh` (Mac/Linux)!