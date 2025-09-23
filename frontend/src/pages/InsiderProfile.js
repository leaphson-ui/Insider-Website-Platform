import React from 'react';
import { useParams } from 'react-router-dom';
import InsiderPage from '../components/pages/InsiderPage';

const InsiderProfile = () => {
  const { traderId } = useParams();
  
  return <InsiderPage insiderId={parseInt(traderId)} />;
};

export default InsiderProfile;
