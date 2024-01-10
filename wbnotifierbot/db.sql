create table bot_users (
  telegram_user_id bigint primary key,
  is_admin bool default false not null,
  created_at timestamp default current_timestamp not null
);

insert into bot_users (telegram_user_id, is_admin) values 
  (1676532442, true);
