import React from 'react';
import { FlatList, StyleSheet, Text, View } from 'react-native';
import { database } from '../../service/db';
import withObservables from '@nozbe/with-observables';
import { ListItem } from '../../components/ListItem';
import {  IUsers } from '../../@types/model';


const db = database.collections.get('users');
const observeUsers = () => db.query().observe();


const enhanceWithUsers = withObservables([], () => ({
    users: observeUsers(),
}));


const UsersList = ({ users }: IUsers) => (
    <FlatList
    style={styles.container}
     data={users}
     keyExtractor={item => item.id}
        showsVerticalScrollIndicator={false}
        renderItem={({item}) => <ListItem users={item} /> }
     />
);

const UsersListRender = enhanceWithUsers(UsersList);

export function Users({navigation}){
    
    return (
        <View>
            <UsersListRender />
        </View>
    
    );

}

const styles = StyleSheet.create({
    container: {
    backgroundColor: '#ed1',
    }
})