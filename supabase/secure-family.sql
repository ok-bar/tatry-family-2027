begin;
create schema if not exists tatry_private;
revoke all on schema tatry_private from public, anon, authenticated;
grant usage on schema tatry_private to authenticated;
create table if not exists tatry_private.allowed_emails (email text primary key check (email=lower(email)), can_create boolean not null default false);
alter table tatry_private.allowed_emails enable row level security;
revoke all on tatry_private.allowed_emails from public,anon,authenticated;
create or replace function tatry_private.approved() returns boolean language sql stable security definer set search_path='' as $$
 select exists(select 1 from auth.users u join tatry_private.allowed_emails a on lower(u.email)=a.email where u.id=auth.uid() and u.email_confirmed_at is not null)
$$;
create or replace function tatry_private.member(t uuid) returns boolean language sql stable security definer set search_path='' as $$
 select tatry_private.approved() and exists(select 1 from public.tatry_trip_members m where m.trip_id=t and m.user_id=auth.uid())
$$;
revoke all on function tatry_private.approved(),tatry_private.member(uuid) from public,anon;
grant execute on function tatry_private.approved(),tatry_private.member(uuid) to authenticated;
-- Replace recursive membership policies and check BOTH old and new rows on updates.
do $$ declare p record; t text; begin
 for p in select tablename,policyname from pg_policies where schemaname='public' and tablename in ('tatry_trips','tatry_trip_members','tatry_trip_visits','tatry_trip_expenses','tatry_trip_settings') loop
 execute format('drop policy %I on public.%I',p.policyname,p.tablename);
 end loop;
 for t in select unnest(array['tatry_trip_visits','tatry_trip_expenses','tatry_trip_settings']) loop
 execute format('create policy family_read on public.%I for select to authenticated using (tatry_private.member(trip_id))',t);
 execute format('create policy family_insert on public.%I for insert to authenticated with check (tatry_private.member(trip_id) and updated_by=auth.uid())',t);
 execute format('create policy family_update on public.%I for update to authenticated using (tatry_private.member(trip_id)) with check (tatry_private.member(trip_id) and updated_by=auth.uid())',t);
 execute format('create policy family_delete on public.%I for delete to authenticated using (tatry_private.member(trip_id))',t);
 end loop;
end $$;
create policy family_read on public.tatry_trips for select to authenticated using (tatry_private.member(id));
create policy family_read on public.tatry_trip_members for select to authenticated using (tatry_private.member(trip_id));
revoke insert,update,delete on public.tatry_trips,public.tatry_trip_members from authenticated,anon;
create or replace function public.tatry_access() returns boolean language sql stable security invoker set search_path='' as $$select tatry_private.approved()$$;
create or replace function public.tatry_create_trip(p_name text default 'הטיול שלנו') returns table(trip_id uuid,join_code text) language plpgsql security definer set search_path='' as $$
declare n uuid; c text; begin
 if not tatry_private.approved() or not exists(select 1 from tatry_private.allowed_emails a join auth.users u on lower(u.email)=a.email where u.id=auth.uid() and a.can_create) then raise exception 'not_approved' using errcode='42501'; end if;
 select t.id,t.join_code into n,c from public.tatry_trips t where t.owner_id=auth.uid() order by t.created_at limit 1;
 if n is null then
 c:=upper(substr(replace(gen_random_uuid()::text,'-',''),1,8));
 insert into public.tatry_trips(name,join_code,owner_id) values(left(coalesce(nullif(trim(p_name),''),'הטיול שלנו'),100),c,auth.uid()) returning id into n;
 insert into public.tatry_trip_members(trip_id,user_id,role) values(n,auth.uid(),'owner');
 end if;
 return query select n,c;
end $$;
create or replace function public.tatry_join_trip(p_join_code text) returns table(trip_id uuid,trip_name text) language plpgsql security definer set search_path='' as $$
declare t public.tatry_trips%rowtype; begin
 if not tatry_private.approved() then raise exception 'not_approved' using errcode='42501'; end if;
 select * into t from public.tatry_trips where public.tatry_trips.join_code=upper(trim(p_join_code));
 if t.id is null then raise exception 'trip_not_found'; end if;
 insert into public.tatry_trip_members(trip_id,user_id,role) values(t.id,auth.uid(),'member') on conflict do nothing;
 return query select t.id,t.name;
end $$;
revoke all on function public.tatry_access(),public.tatry_create_trip(text),public.tatry_join_trip(text) from public,anon;
grant execute on function public.tatry_access(),public.tatry_create_trip(text),public.tatry_join_trip(text) to authenticated;
-- Each independently editable item has its own row; tombstones propagate deletions.
create table public.tatry_shared_items (
 trip_id uuid not null references public.tatry_trips(id) on delete cascade,
 kind text not null check(kind in ('visit','check','expense','budget','file')),
 item_id text not null check(length(item_id) between 1 and 150),
 payload jsonb not null default '{}' check(jsonb_typeof(payload)='object' and octet_length(payload::text)<20000),
 deleted boolean not null default false,
 updated_by uuid not null references auth.users(id),
 updated_at timestamptz not null default now(),
 primary key(trip_id,kind,item_id)
);
alter table public.tatry_shared_items enable row level security;
revoke all on public.tatry_shared_items from anon;
grant select,insert,update on public.tatry_shared_items to authenticated;
create policy family_read on public.tatry_shared_items for select to authenticated using(tatry_private.member(trip_id));
create policy family_insert on public.tatry_shared_items for insert to authenticated with check(tatry_private.member(trip_id) and updated_by=auth.uid());
create policy family_update on public.tatry_shared_items for update to authenticated using(tatry_private.member(trip_id)) with check(tatry_private.member(trip_id) and updated_by=auth.uid());
create or replace function tatry_private.stamp() returns trigger language plpgsql set search_path='' as $$begin new.updated_at=clock_timestamp(); return new; end$$;
revoke all on function tatry_private.stamp() from public,anon,authenticated;
create trigger stamp before update on public.tatry_shared_items for each row execute function tatry_private.stamp();
create index tatry_shared_updated_by on public.tatry_shared_items(updated_by);
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types) values('tatry-tickets','tatry-tickets',false,20971520,array['application/pdf','image/jpeg','image/png','image/webp']) on conflict(id) do update set public=false,file_size_limit=excluded.file_size_limit,allowed_mime_types=excluded.allowed_mime_types;
create or replace function tatry_private.file_access(p text) returns boolean language plpgsql stable security invoker set search_path='' as $$begin
 if split_part(p,'/',1) !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' then return false; end if;
 return tatry_private.member(split_part(p,'/',1)::uuid);
end$$;
revoke all on function tatry_private.file_access(text) from public,anon;
grant execute on function tatry_private.file_access(text) to authenticated;
create policy tatry_ticket_read on storage.objects for select to authenticated using(bucket_id='tatry-tickets' and tatry_private.file_access(name));
create policy tatry_ticket_insert on storage.objects for insert to authenticated with check(bucket_id='tatry-tickets' and tatry_private.file_access(name));
create policy tatry_ticket_update on storage.objects for update to authenticated using(bucket_id='tatry-tickets' and tatry_private.file_access(name)) with check(bucket_id='tatry-tickets' and tatry_private.file_access(name));
create policy tatry_ticket_delete on storage.objects for delete to authenticated using(bucket_id='tatry-tickets' and tatry_private.file_access(name));
alter publication supabase_realtime add table public.tatry_shared_items;
commit;
