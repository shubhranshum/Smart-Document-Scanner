# Smart Document Scanner: Production Deployment Guide

> **Quick Answer:**  
> **Yes, you can deploy the Frontend on Vercel!** In fact, Vercel is the single best, fastest platform for the React + Vite frontend.  
> However, for the **Python/OpenCV Backend**, running on Vercel Serverless is **strongly discouraged** due to hard cloud limits (explained below). The recommended, industry-standard deployment is **100% free**:
> * **Frontend $\to$ Vercel** (Global Edge CDN, auto-builds from Git, custom domain, free HTTPS).
> * **Backend $\to$ Render.com or Railway.app** (Docker container running FastAPI + OpenCV without upload limits, free tier).

---

## 1. Why Decouple Frontend (Vercel) & Backend (Render/Railway)?

| Constraint / Feature | Vercel Serverless Python | Render / Railway / Fly.io (Container) |
| :--- | :--- | :--- |
| **Max Request Body (Upload Size)** | **Hard 4.5 MB limit** (Causes `413 Payload Too Large` on smartphone photos) | **No artificial limit** (Our app supports 15 MB high-res images) |
| **Heavy Libraries (`opencv`, `numpy`)**| 250 MB uncompressed Lambda limit (frequently crashes during build) | Native Docker environment with all OS dependencies (`libgl1`, `libglib2.0`) |
| **Execution Timeout** | Strict 10 seconds on Hobby tier | Unlimited / configurable process duration |
| **Cold Starts** | 3 to 5 second cold boot when OpenCV imports | Instant, warm response |
| **Cost** | Free tier | Free tier available |

---

## 2. Step-by-Step Deployment (100% Free Tier)

### Step 1: Push Code to GitHub
Make sure your workspace is committed to your GitHub repository:
```bash
git add .
git commit -m "Add Dockerfile, Vercel config, and deployment setup"
git push origin main
```

---

### Step 2: Deploy the Backend on Render.com (Free)
1. Go to [Render.com](https://render.com) and sign in with GitHub.
2. Click **New +** $\to$ **Web Service**.
3. Select your repository.
4. Fill in the following settings:
   * **Name:** `smart-document-scanner-api`
   * **Root Directory:** `smart-document-scanner/backend` (or leave blank if repository root contains backend)
   * **Language / Environment:** **Docker**
   * **Instance Type:** **Free**
5. Click **Deploy Web Service**.
6. Once deployed, Render will provide your public backend URL, for example:  
   `https://smart-document-scanner-api.onrender.com`
7. Test it by opening `https://smart-document-scanner-api.onrender.com/api/health` in your browser. It should return:
   ```json
   {"status":"healthy","opencv_version":"4.11.0","backend_version":"1.0.0"}
   ```

*(Alternative: You can use **Railway.app** or **Fly.io** using the same included `backend/Dockerfile` with one click.)*

---

### Step 3: Deploy the Frontend on Vercel (Free)
1. Go to [Vercel](https://vercel.com) and log in with GitHub.
2. Click **Add New...** $\to$ **Project**.
3. Import your GitHub repository.
4. Configure the project:
   * **Framework Preset:** `Vite`
   * **Root Directory:** Click *Edit* and select **`smart-document-scanner/frontend`**.
   * **Build Command:** `npm run build`
   * **Output Directory:** `dist`
5. **Add Environment Variable:**
   * **Name:** `VITE_API_BASE_URL`
   * **Value:** Your Render backend URL from Step 2 (e.g. `https://smart-document-scanner-api.onrender.com`)
   *(Note: Do not add a trailing slash)*
6. Click **Deploy**.

---

### Step 4: Verify Deployment
1. Vercel will build and assign you a global URL (e.g., `https://smart-document-scanner.vercel.app`).
2. Open the URL on your laptop or phone.
3. Upload a document photograph, run **Detect Document**, and test perspective correction and PDF export live!

---

## 3. Configuration Files Pre-Configured in the Codebase

All necessary configuration files have already been created for you:

1. **[`frontend/vercel.json`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/frontend/vercel.json):**  
   Configures Single Page Application (SPA) URL rewrites so refreshing the page on any tab (`/`, `/detection`, etc.) will not produce a 404 error.
2. **[`backend/Dockerfile`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/Dockerfile):**  
   A lightweight, production-ready Debian-slim image equipped with `libgl1` and `libglib2.0-0` for OpenCV headless.
3. **[`frontend/src/services/api.js`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/frontend/src/services/api.js):**  
   Automatically reads `import.meta.env.VITE_API_BASE_URL` in production, falling back to `http://localhost:8000` during local development.
4. **[`backend/app/config.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/config.py):**  
   Pre-configured with `allowed_origins = ["*"]` so browser requests from any Vercel domain are accepted without CORS blocking.
