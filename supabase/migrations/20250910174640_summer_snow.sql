/*
  # Create schedules table

  1. New Tables
    - `schedules`
      - `id` (uuid, primary key)
      - `title` (text, required)
      - `description` (text, optional)
      - `date` (date, required)
      - `start_time` (time, required)
      - `end_time` (time, required)
      - `created_by` (uuid, foreign key to users)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS on `schedules` table
    - Add policy for all authenticated users to read schedules
    - Add policy for admins to manage schedules
*/

CREATE TABLE IF NOT EXISTS schedules (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  description text DEFAULT '',
  date date NOT NULL,
  start_time time NOT NULL,
  end_time time NOT NULL,
  created_by uuid REFERENCES users(id),
  created_at timestamptz DEFAULT now()
);

ALTER TABLE schedules ENABLE ROW LEVEL SECURITY;

-- Policy for all authenticated users to read schedules
CREATE POLICY "All users can read schedules"
  ON schedules
  FOR SELECT
  TO authenticated
  USING (true);

-- Policy for admins to insert schedules
CREATE POLICY "Admins can insert schedules"
  ON schedules
  FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM users 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Policy for admins to update schedules
CREATE POLICY "Admins can update schedules"
  ON schedules
  FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM users 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Policy for admins to delete schedules
CREATE POLICY "Admins can delete schedules"
  ON schedules
  FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM users 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Insert sample schedules
INSERT INTO schedules (title, description, date, start_time, end_time, created_by) 
SELECT 
  'Team Meeting',
  'Weekly team sync and project updates',
  CURRENT_DATE,
  '09:00'::time,
  '10:00'::time,
  u.id
FROM users u WHERE u.username = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO schedules (title, description, date, start_time, end_time, created_by) 
SELECT 
  'Security Review',
  'Monthly security audit and vulnerability assessment',
  CURRENT_DATE + INTERVAL '1 day',
  '14:00'::time,
  '16:00'::time,
  u.id
FROM users u WHERE u.username = 'admin'
ON CONFLICT DO NOTHING;

INSERT INTO schedules (title, description, date, start_time, end_time, created_by) 
SELECT 
  'System Maintenance',
  'Scheduled database maintenance and updates',
  CURRENT_DATE + INTERVAL '7 days',
  '02:00'::time,
  '04:00'::time,
  u.id
FROM users u WHERE u.username = 'admin'
ON CONFLICT DO NOTHING;