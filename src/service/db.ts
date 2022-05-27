import { Database } from "@nozbe/watermelondb";
import SQLiteAdaptyer from '@nozbe/watermelondb/adapters/sqlite';

import schema from '../model/schema';
import migrations from '../model/migrations'

import Categories from '../model/users'

const adapter  = new SQLiteAdaptyer({
    schema,
    migrations,
    dbName: 'Teste',
});

export const database = new Database({
    adapter,
    modelClasses: [Categories],
})