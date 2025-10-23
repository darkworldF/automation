# 🎯 Two-Step Product Import Tool

**Perfect control over your product imports!**

## ✨ What You Asked For:

### 🔍 **Step 1: PREVIEW**
- Click → Fetch all products from engwe.com
- See everything in a beautiful visual preview
- Review products, images, prices, variants

### 🚀 **Step 2: IMPORT**  
- Click → Upload all products to your Shopify store
- Full control - only import what you've reviewed

---

## 🎮 **How to Use:**

### **Windows Users:**
```
1. Double-click: step1_fetch.bat
   → Fetches products & opens preview in browser
   
2. Review products in browser preview

3. Double-click: step2_upload.bat  
   → Uploads to your Shopify store
```

### **Mac/Linux Users:**
```bash
1. ./step1_fetch.sh
   → Fetches products & opens preview in browser
   
2. Review products in browser preview

3. ./step2_upload.sh
   → Uploads to your Shopify store
```

---

## 📋 **What Happens:**

### **Step 1 Results:**
- ✅ All products fetched from engwe.com
- 🌐 Beautiful HTML preview opens in your browser
- 📊 Statistics: total products, variants, images
- 💾 Data saved locally for Step 2

### **Step 2 Results:**
- 🚀 Products uploaded directly to Shopify
- 📝 Created as drafts for your review
- 🔍 Duplicate detection (skips existing products)
- 📈 Real-time progress and success statistics

---

## 🎨 **Preview Features:**

**Visual Product Cards showing:**
- 🖼️ Product images
- 💰 Pricing information  
- 📝 Descriptions
- 🎯 Variant counts
- 📊 Import statistics

**Responsive Design:**
- 💻 Works on desktop
- 📱 Mobile-friendly
- 🎨 Professional styling

---

## ⚙️ **Setup (One-time):**

1. **Configure API credentials** in `config.ini`:
   ```ini
   [SHOPIFY_API]
   store_url = nlebike.myshopify.com
   access_token = shpat_your_token_here
   api_key = your_api_key_here
   api_secret = your_api_secret_here
   ```

2. **Make scripts executable** (Mac/Linux only):
   ```bash
   chmod +x step1_fetch.sh step2_upload.sh
   ```

---

## 🎯 **Perfect Workflow:**

```
📥 STEP 1: Fetch & Preview
     ↓
👀 Review in Browser  
     ↓
✅ STEP 2: Upload to Shopify
     ↓  
🎉 Products in Your Store!
```

**This gives you complete control while maintaining full automation!**

---

## 📁 **Files Created:**

- `products_preview.json` - Raw product data
- `products_preview.html` - Visual preview (opens in browser)
- Import logs and statistics

## 🔒 **Security:**
- All data processed locally
- API credentials never shared
- Direct communication with your Shopify store only

---

**Ready to start?** Run Step 1 and see all your products! 🚀