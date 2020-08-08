
create table users (
    user_id bigserial primary key,
    email varchar unique,
    full_name varchar,
    password varchar,
    is_active Boolean default true not null,
    is_superuser Boolean default false not null,
    created_date Timestamp default now() not null
)


