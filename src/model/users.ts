import { Model } from "@nozbe/watermelondb";
import { field } from "@nozbe/watermelondb/decorators"

export default class Users extends Model{
    static table = 'users';

    @field('name') name: any;
    @field('sobrenome') sobrenome: any;
    @field('idade') idade: any;
}