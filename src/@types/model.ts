import Model from "@nozbe/watermelondb/Model";

export interface IUser extends Model{
    id: string;
    name?: string;
    sobrenome?: string;
    idade?: string;
}

export interface IUsers{
    users: IUser[];
}