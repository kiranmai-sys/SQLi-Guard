@@ .. @@
 CREATE TABLE IF NOT EXISTS users (
   id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
   username text UNIQUE NOT NULL,
-  password text NOT NULL,
+  password text NOT NULL, -- This will store hashed passwords
   role text DEFAULT 'user' CHECK (role IN ('user', 'admin')),
   created_at timestamptz DEFAULT now()
 );