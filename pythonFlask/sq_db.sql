create table if not exists mainmenu (
id integer primary key autoincrement,
title text not null,
url text not null
);

insert into mainmenu (id, title, url) values (1, 'Главная', '/' );
insert into mainmenu (id, title, url) values (2, 'Добавить статью', 'add_post');