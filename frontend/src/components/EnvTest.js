import React from 'react';

const EnvTest = () => {
  const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
  const supabaseKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
      <h3 className="text-lg font-medium text-yellow-800 mb-2">Environment Variables Test</h3>
      <div className="space-y-1 text-sm">
        <p><strong>REACT_APP_SUPABASE_URL:</strong> {supabaseUrl || '❌ Not found'}</p>
        <p><strong>REACT_APP_SUPABASE_ANON_KEY:</strong> {supabaseKey ? '✅ Present' : '❌ Not found'}</p>
        <p><strong>All env vars loaded:</strong> {supabaseUrl && supabaseKey ? '✅ Yes' : '❌ No'}</p>
      </div>
    </div>
  );
};

export default EnvTest;
