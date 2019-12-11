create database tezosIfttt
    with owner doadmin;

create table if not exists public.triggers
(
  id serial not null
    constraint triggers_pk
      primary key,
  trigger_type varchar not null,
  trigger_subtype varchar,
  data jsonb
);

alter table public.triggers owner to doadmin;

create table if not exists public.actions
(
  action_type varchar not null,
  action_subtype varchar,
  data jsonb,
  id serial not null
    constraint actions_pk
      primary key
);

alter table public.actions owner to doadmin;

create table if not exists public.triggers_actions
(
  id serial not null
    constraint trigger_action_links_pk
      primary key,
  trigger_id integer not null
    constraint trigger_fk
      references public.triggers,
  action_id integer not null
    constraint action_fk
      references public.actions,
  active boolean default true
  unique_id uuid not null
);

alter table public.triggers_actions owner to doadmin;


