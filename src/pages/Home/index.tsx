import React, { useState } from 'react';
import { StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { IUser } from '../../@types/model';
import { database } from '../../service/db';

export function Home( {navigation}){
    const [name, setName] = useState('');
    const [sobrenome, setSobrenome] = useState('');
    const [idade, setIdade] = useState('');


   async function handleRegister(){
        await database.write(async() => {
            await database.get('users').create((user: IUser) =>{
                user.name = name;
                user.sobrenome = sobrenome;
                user.idade = idade;
            });
        });
        setName('');
        setSobrenome('');
        setIdade('');
        navigation.navigate("Home")
    }

    function handleUsers(){
        navigation.navigate("Users")
    }




  return (
      <View style={styles.container}>
          <TextInput
          placeholder='Nome'
          value={name}
          keyboardType='default'
          onChangeText = {setName}
          style = {styles.input}
          />
          <TextInput
          placeholder='Sobrenome'
          keyboardType='default'
          value={sobrenome}
          onChangeText = {setSobrenome}
          style = {styles.input}
          />
          <TextInput
          placeholder='Idade'
          keyboardType='number-pad'
          value={idade}
          onChangeText = { setIdade}
          style = {styles.input}
          />
          <TouchableOpacity
            style={styles.button}
            onPress={handleRegister}
            activeOpacity={0.6}
          >
              <Text>Cadastrar Usuário</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.button2}
            onPress={handleUsers}
            activeOpacity={0.6}
          >
              <Text>Lista de Usuarios</Text>
          </TouchableOpacity>
      </View>
  )
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        flexDirection: 'column',
        justifyContent: 'center',
        height: 100,
        backgroundColor: '#cecece',
        margin: 8,
    },
    input: {
        margin: 10,
        borderRadius: 5,
        height: 50,
        padding: 5,
        backgroundColor: '#fff',
        marginRight: 8,
        color: '#222'
    },
    button: {
        backgroundColor: '#f89',
        height: 50,
        alignItems: 'center',
        justifyContent: 'center',
        padding: 5,
        borderRadius: 10,
        marginHorizontal: 40,
    },

    button2: {
        backgroundColor: '#00ced1',
        height: 50,
        alignItems: 'center',
        justifyContent: 'center',
        padding: 5,
        borderRadius: 10,
        marginHorizontal: 40,
        marginTop: 10,
    }
})
