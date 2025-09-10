/*
  # Create security events table

  1. New Tables
    - `security_events`
      - `id` (uuid, primary key)
      - `ts` (timestamp, default now)
      - `ip` (text, client IP address)
      - `username` (text, attempted username)
      - `reason` (text, threat description)
      - `pattern` (text, matched pattern)
      - `snippet` (text, input snippet)
      - `user_agent` (text, client user agent)

  2. Security
    - Enable RLS on `security_events` table
    - Add policy for admins to read all security events
*/

CREATE TABLE IF NOT EXISTS security_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ts timestamptz DEFAULT now(),
  ip text,
  username text,
  reason text,
  pattern text,
  snippet text,
  user_agent text
);

ALTER TABLE security_events ENABLE ROW LEVEL SECURITY;

-- Policy for admins to read all security events
CREATE POLICY "Admins can read security events"
  ON security_events
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM users 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Policy for system to insert security events (service role)
CREATE POLICY "System can insert security events"
  ON security_events
  FOR INSERT
  TO service_role
  WITH CHECK (true);