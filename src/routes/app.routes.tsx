import { createStackNavigator } from '@react-navigation/stack';
import { Home } from '../pages/Home';
import { Users } from '../pages/Users';
import React from 'react';
import { useNavigation } from '@react-navigation/native'

const Stack = createStackNavigator();

const AppRoutes: React.FC = () => {
    return (
        <Stack.Navigator>
          <Stack.Screen name="Home" component={Home} />
          <Stack.Screen name="Users" component={Users} />
        </Stack.Navigator>
      );

};

export default AppRoutes;


  
