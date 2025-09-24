import { createClient } from '@supabase/supabase-js'

// Hardcoded values for now to test the dashboard
const supabaseUrl = 'https://sifpyksougtsklegphxf.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpZnB5a3NvdWd0c2tsZWdwaHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2NzI5OTUsImV4cCI6MjA3NDI0ODk5NX0.NDc6nd1w9SFhgYYJkRrAqD_3pO584tUrGcNrDErCq9Y'

console.log('Using hardcoded Supabase credentials for testing')

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
