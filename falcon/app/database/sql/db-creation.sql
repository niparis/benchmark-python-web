
create table users (
    user_id bigserial primary key,
    email varchar unique not null,
    full_name varchar not null,
    password varchar not null,
    is_active Boolean default true not null,
    is_superuser Boolean default false not null,
    created_date Timestamp default now() not null
)


