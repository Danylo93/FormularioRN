import { appSchema,tableSchema } from "@nozbe/watermelondb/Schema";

export default appSchema({
    version: 1,
    tables: [
        tableSchema({
            name: 'users',
            columns: [
                {name: 'name', type: 'string'},
                {name: 'sobrenome', type: 'string'},
                {name: 'idade', type: 'string'}
            ],
        }),
    ],
});