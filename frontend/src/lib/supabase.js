import { createClient } from '@supabase/supabase-js'

// Use environment variables for production, fallback to hardcoded for development
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://sifpyksougtsklegphxf.supabase.co'
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpZnB5a3NvdWd0c2tsZWdwaHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2NzI5OTUsImV4cCI6MjA3NDI0ODk5NX0.NDc6nd1w9SFhgYYJkRrAqD_3pO584tUrGcNrDErCq9Y'

console.log('Supabase URL:', supabaseUrl)

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
