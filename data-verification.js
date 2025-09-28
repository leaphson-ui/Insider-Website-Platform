const { createClient } = require('@supabase/supabase-js');

// Use the same Supabase credentials as your frontend
const supabaseUrl = 'https://sifpyksougtsklegphxf.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpZnB5a3NvdWd0c2tsZWdwaHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2NzI5OTUsImV4cCI6MjA3NDI0ODk5NX0.NDc6nd1w9SFhgYYJkRrAqD_3pO584tUrGcNrDErCq9Y';

const supabase = createClient(supabaseUrl, supabaseKey);

async function verifyLargestTransactions() {
  try {
    console.log('🔍 Verifying largest transactions in database...\n');
    
    // Query for the top 10 largest transactions by value
    const { data, error } = await supabase
      .from('insider_transactions')
      .select('insider_name, company_name, company_ticker, calculated_transaction_value, transaction_date, transaction_code')
      .order('calculated_transaction_value', { ascending: false })
      .limit(10);
    
    if (error) {
      console.error('Database error:', error);
      return;
    }
    
    console.log('📊 Top 10 Largest Transactions:');
    console.log('=====================================');
    
    data.forEach((transaction, index) => {
      const value = transaction.calculated_transaction_value;
      const formattedValue = value ? `$${value.toLocaleString()}` : 'N/A';
      
      console.log(`${index + 1}. ${formattedValue}`);
      console.log(`   Insider: ${transaction.insider_name || 'N/A'}`);
      console.log(`   Company: ${transaction.company_name || 'N/A'} (${transaction.company_ticker || 'N/A'})`);
      console.log(`   Date: ${transaction.transaction_date || 'N/A'}`);
      console.log(`   Type: ${transaction.transaction_code || 'N/A'}`);
      console.log('');
    });
    
    // Check if $372M is indeed the largest
    const largestValue = data[0]?.calculated_transaction_value;
    if (largestValue === 372150000) {
      console.log('✅ Confirmed: $372,150,000 is the largest transaction in the database');
    } else {
      console.log(`❌ Mismatch: Database shows largest as $${largestValue?.toLocaleString()}, not $372,150,000`);
    }
    
  } catch (error) {
    console.error('Verification failed:', error);
  }
}

verifyLargestTransactions();
