drop table if exists entries;
create table entries (
id integer primary key autoincrement,
time timestamp not null,
name text not null,
email text not null,
position text not null,
years text not null,
'task_1' text not null,
'task_2' text not null,
'task_3' text not null,
'sq_1' text not null,
'sq_2' text not null,
'sq_3' text not null,
comments text
);
