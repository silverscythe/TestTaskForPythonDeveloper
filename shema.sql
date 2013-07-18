drop table if exists entries;
drop table if exists authors;
drop table if exists books;
drop table if exists authorsbooks;
create table authors (
  id integer primary key autoincrement,
  author text not null
);
create table books (
  id integer primary key autoincrement,
  book text not null
);
create table authorsbooks(
  idauthor integer,
  idbook integer 
);
create table entries (
  author text ,
  book text
);
