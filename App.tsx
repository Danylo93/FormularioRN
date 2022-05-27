import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import AppRoutes from './src/routes/app.routes'
import { Home } from './src/pages/Home';
import { Users } from './src/pages/Users';


export default function App(){
  return(
      <NavigationContainer>
        <AppRoutes />
      </NavigationContainer>
  ) 
  
}
