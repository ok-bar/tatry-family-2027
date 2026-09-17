begin;
do $test$
declare u uuid:=gen_random_uuid(); v uuid:=gen_random_uuid(); outsider uuid:=gen_random_uuid(); t uuid; code text; other uuid:=gen_random_uuid(); ok boolean;
begin
 insert into auth.users(id,email,email_confirmed_at) values (u,'tatry-test-owner@example.invalid',now()),(v,'tatry-test-member@example.invalid',now()),(outsider,'tatry-test-outsider@example.invalid',now());
 insert into tatry_private.allowed_emails(email,can_create) values ('tatry-test-owner@example.invalid',true),('tatry-test-member@example.invalid',false);
 perform set_config('request.jwt.claim.sub',u::text,true);
 execute 'set local role authenticated';
 select trip_id,join_code into t,code from public.tatry_create_trip('rollback security test');
 if not public.tatry_access() then raise exception 'owner denied'; end if;
 if not tatry_private.file_access(t::text||'/file/blob') then raise exception 'owner file denied'; end if;
 insert into public.tatry_shared_items(trip_id,kind,item_id,payload,updated_by) values(t,'budget','budget','{"value":1234}',u);
 perform set_config('request.jwt.claim.sub',v::text,true);
 perform public.tatry_join_trip(code);
 if (select count(*) from public.tatry_shared_items where trip_id=t)<>1 then raise exception 'member read failed';end if;
 update public.tatry_shared_items set payload='{"value":4321}',updated_by=v where trip_id=t;
 if not tatry_private.file_access(t::text||'/file/blob') then raise exception 'member file denied';end if;
 begin
 update public.tatry_shared_items set trip_id=other where trip_id=t;
 raise exception 'cross trip update was allowed';
 exception when insufficient_privilege then null;end;
 perform set_config('request.jwt.claim.sub',outsider::text,true);
 if public.tatry_access() then raise exception 'outsider access';end if;
 if (select count(*) from public.tatry_shared_items where trip_id=t)<>0 then raise exception 'outsider read';end if;
 if tatry_private.file_access(t::text||'/file/blob') then raise exception 'outsider file access';end if;
 begin perform public.tatry_join_trip(code);raise exception 'outsider joined';exception when insufficient_privilege then null;end;
 begin insert into public.tatry_shared_items(trip_id,kind,item_id,updated_by) values(t,'visit','bad',outsider);raise exception 'outsider wrote';exception when insufficient_privilege then null;end;
 execute 'reset role';
 delete from tatry_private.allowed_emails where email='tatry-test-member@example.invalid';
 perform set_config('request.jwt.claim.sub',v::text,true);execute 'set local role authenticated';
 if tatry_private.file_access(t::text||'/file/blob') then raise exception 'revoked member file access';end if;
 if (select count(*) from public.tatry_shared_items where trip_id=t)<>0 then raise exception 'revoked read';end if;
 execute 'reset role';
end $test$;
select 'PASS: owner/member reads and writes; outsider and revoked member denied; cross-trip reassignment denied; private-file policy checked' as result;
rollback;
