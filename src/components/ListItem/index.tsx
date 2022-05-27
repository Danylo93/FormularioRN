import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { TouchableOpacity } from 'react-native-gesture-handler';
import { IUser } from '../../@types/model';
import { database } from '../../service/db';

interface Props {
  users: IUser;
}

export function ListItem({users}: Props) {

async function handleDeleteUser(){
   await database.write(async () => {
     const user = await database.get('users').find(users.id);
     await user.destroyPermanently();
   })
}

  return(
    <View style={styles.container}>
     <Text style={styles.title}>{users.name}</Text>
     
     <Text style={styles.title}>{users.sobrenome}</Text>
     <Text style={styles.title} >{users.idade}</Text>
     <View style={styles.buttons}>
       <TouchableOpacity
       style={styles.button}
       activeOpacity={0.6}
       onPress={handleDeleteUser}
       >
         <Text>Deletar</Text>
       </TouchableOpacity>
     </View>
   </View>
  );
}

const styles = StyleSheet.create({
  container: {
    height: 80,
    backgroundColor: '#fff',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    margin: 8,
    borderRadius: 5,
    flexDirection: 'row',
    alignContent: 'center',
    alignItems: 'center'
    
  },
  title:{
    color: '#000', fontSize: 16
  },
  button: {
    backgroundColor: '#dc3545',
    padding: 15,
    borderRadius: 10
  },
  button_text:{
    color: '#fff'
  },
  buttons: {
    flexDirection: 'row',
    alignContent: 'center'
  }
}) 
