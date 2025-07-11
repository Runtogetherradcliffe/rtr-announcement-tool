diff --git a/strava_utils.py b/strava_utils.py
index a6c8917a40461d2895d161c7cf617966230f3839..6f365fefd497a3fdf235175c2f2eb4ed9c51b1dc 100644
--- a/strava_utils.py
+++ b/strava_utils.py
@@ -1,47 +1,31 @@
-diff --git a/strava_utils.py b/strava_utils.py
-index e57bc2bdc029ecd0818b891eee761bbd1491ed0b..9955ec702da98dff8c87cb0be603685c16339bcc 100644
---- a/strava_utils.py
-+++ b/strava_utils.py
-@@ -1,25 +1,30 @@
- 
- import os
- import requests
--import json
- 
--# This function assumes you have your STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, and REFRESH_TOKEN set in the environment
--def get_strava_access_token():
--    STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
--    STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
--    REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
--
--    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET or not REFRESH_TOKEN:
--        raise ValueError("Strava credentials are missing from environment variables.")
-+def refresh_strava_token(client_id: str, client_secret: str, refresh_token: str) -> str:
-+    """Request a fresh Strava access token."""
- 
-     response = requests.post(
-         "https://www.strava.com/oauth/token",
-         data={
--            "client_id": STRAVA_CLIENT_ID,
--            "client_secret": STRAVA_CLIENT_SECRET,
-+            "client_id": client_id,
-+            "client_secret": client_secret,
-             "grant_type": "refresh_token",
--            "refresh_token": REFRESH_TOKEN,
-+            "refresh_token": refresh_token,
-         },
-     )
-     response.raise_for_status()
-     return response.json()["access_token"]
-+
-+
-+# This function assumes you have your STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, and REFRESH_TOKEN set in the environment
-+def get_strava_access_token():
-+    STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
-+    STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
-+    REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
-+
-+    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET or not REFRESH_TOKEN:
-+        raise ValueError("Strava credentials are missing from environment variables.")
-+
-+    return refresh_strava_token(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, REFRESH_TOKEN)
+import os
+import requests
+
+
+def refresh_strava_token(client_id: str, client_secret: str, refresh_token: str) -> str:
+    """Request a fresh Strava access token."""
+    response = requests.post(
+        "https://www.strava.com/oauth/token",
+        data={
+            "client_id": client_id,
+            "client_secret": client_secret,
+            "grant_type": "refresh_token",
+            "refresh_token": refresh_token,
+        },
+    )
+    response.raise_for_status()
+    return response.json()["access_token"]
+
+
+# This function assumes you have your STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET,
+# and REFRESH_TOKEN set in the environment
+
+def get_strava_access_token():
+    STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
+    STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
+    REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
+
+    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET or not REFRESH_TOKEN:
+        raise ValueError("Strava credentials are missing from environment variables.")
+
+    return refresh_strava_token(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, REFRESH_TOKEN)

+
