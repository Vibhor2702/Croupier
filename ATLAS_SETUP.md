# MongoDB Atlas Setup Guide

Follow these steps to set up MongoDB Atlas (cloud database) for Croupier:

## Step 1: Create MongoDB Atlas Account

1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Try Free" or "Sign In"
3. Create account (Google/GitHub sign-in available)

## Step 2: Create a Free Cluster

1. After login, click "Build a Database"
2. Choose **FREE** tier (M0 Sandbox)
3. Select cloud provider and region (choose closest to you)
4. Cluster name: `Croupier` (or keep default)
5. Click "Create"

Wait 1-3 minutes for cluster to deploy.

## Step 3: Create Database User

1. Click "Database Access" in left sidebar
2. Click "Add New Database User"
3. Authentication Method: **Password**
4. Username: `croupier_admin` (or your choice)
5. Password: Click "Autogenerate Secure Password" and **SAVE IT**
6. Database User Privileges: **Read and write to any database**
7. Click "Add User"

## Step 4: Configure Network Access

1. Click "Network Access" in left sidebar
2. Click "Add IP Address"
3. Choose one:
   - **Allow Access from Anywhere**: Click this button (sets 0.0.0.0/0)
   - Or add your current IP address
4. Click "Confirm"

**Note:** For production, restrict to specific IPs. For testing, "anywhere" is fine.

## Step 5: Get Connection String

1. Click "Database" in left sidebar
2. Click "Connect" button on your cluster
3. Choose "Connect your application"
4. Driver: **Python** / Version: **3.12 or later**
5. Copy the connection string - looks like:
   ```
   mongodb+srv://croupier_admin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. **Replace `<password>`** with the password you saved in Step 3

## Step 6: Update Your .env File

1. Open `.env` file in Croupier project (or create from `.env.example`)
2. Update the MONGODB_URL:
   ```env
   MONGODB_URL=mongodb+srv://croupier_admin:YOUR_ACTUAL_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DB_NAME=croupier_master
   JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
   ```

**Important:** Replace `YOUR_ACTUAL_PASSWORD` with your real password from Step 3.

## Step 7: Test Connection

Run this command to verify connection:

```powershell
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MongoClient(os.getenv('MONGODB_URL')); print('Connected!'); print('Databases:', client.list_database_names())"
```

If successful, you'll see "Connected!" and list of databases.

## Step 8: Run the Server

```powershell
uvicorn main:app --reload
```

Server should start at http://localhost:8000

## Step 9: Test the API

```powershell
python test_api.py
```

This will create a test organization and run through all operations.

---

## Troubleshooting

**Error: "Authentication failed"**
- Double-check password in `.env` file
- Ensure no special characters are URL-encoded (use %40 for @, %23 for #, etc.)

**Error: "Connection timeout"**
- Check Network Access settings in Atlas
- Ensure 0.0.0.0/0 is whitelisted or your IP is added

**Error: "Server selection timeout"**
- Verify connection string format
- Check internet connection
- Verify cluster is running (not paused)

**Check cluster status:**
- Go to Atlas dashboard
- If cluster shows "Paused", click "Resume"

---

## View Your Data in Atlas

1. In Atlas dashboard, click "Browse Collections"
2. You'll see:
   - `croupier_master` database
   - `organizations` collection (org metadata)
   - `admin_users` collection (admin accounts)
   - `org_<name>` collections (one per organization created)

## Next Steps

- Open http://localhost:8000/docs for Swagger UI
- Create organizations via API
- Monitor data in Atlas dashboard
- Check "Metrics" tab for performance stats
