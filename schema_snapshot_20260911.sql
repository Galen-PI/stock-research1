--
-- PostgreSQL database dump
--

\restrict v8JkyzkwOmGjn5QFRjWZBkZHHRH87JGbkyyo7gYQxa2BrFEDlbwU3augD8hoKDq

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.11 (Ubuntu 17.11-1.pgdg24.04+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: auth; Type: SCHEMA; Schema: -; Owner: supabase_admin
--

CREATE SCHEMA auth;


ALTER SCHEMA auth OWNER TO supabase_admin;

--
-- Name: extensions; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA extensions;


ALTER SCHEMA extensions OWNER TO postgres;

--
-- Name: graphql; Type: SCHEMA; Schema: -; Owner: supabase_admin
--

CREATE SCHEMA graphql;


ALTER SCHEMA graphql OWNER TO supabase_admin;

--
-- Name: graphql_public; Type: SCHEMA; Schema: -; Owner: supabase_admin
--

CREATE SCHEMA graphql_public;


ALTER SCHEMA graphql_public OWNER TO supabase_admin;

--
-- Name: pgbouncer; Type: SCHEMA; Schema: -; Owner: pgbouncer
--

CREATE SCHEMA pgbouncer;


ALTER SCHEMA pgbouncer OWNER TO pgbouncer;

--
-- Name: realtime; Type: SCHEMA; Schema: -; Owner: supabase_admin
--

CREATE SCHEMA realtime;


ALTER SCHEMA realtime OWNER TO supabase_admin;

--
-- Name: storage; Type: SCHEMA; Schema: -; Owner: supabase_admin
--

CREATE SCHEMA storage;


ALTER SCHEMA storage OWNER TO supabase_admin;

--
-- Name: vault; Type: SCHEMA; Schema: -; Owner: supabase_admin
--

CREATE SCHEMA vault;


ALTER SCHEMA vault OWNER TO supabase_admin;

--
-- Name: hypopg; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS hypopg WITH SCHEMA public;


--
-- Name: EXTENSION hypopg; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION hypopg IS 'Hypothetical indexes for PostgreSQL';


--
-- Name: index_advisor; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS index_advisor WITH SCHEMA public;


--
-- Name: EXTENSION index_advisor; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION index_advisor IS 'Query index advisor';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA extensions;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: supabase_vault; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS supabase_vault WITH SCHEMA vault;


--
-- Name: EXTENSION supabase_vault; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION supabase_vault IS 'Supabase Vault Extension';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA extensions;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: aal_level; Type: TYPE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TYPE auth.aal_level AS ENUM (
    'aal1',
    'aal2',
    'aal3'
);


ALTER TYPE auth.aal_level OWNER TO supabase_auth_admin;

--
-- Name: code_challenge_method; Type: TYPE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TYPE auth.code_challenge_method AS ENUM (
    's256',
    'plain'
);


ALTER TYPE auth.code_challenge_method OWNER TO supabase_auth_admin;

--
-- Name: factor_status; Type: TYPE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TYPE auth.factor_status AS ENUM (
    'unverified',
    'verified'
);


ALTER TYPE auth.factor_status OWNER TO supabase_auth_admin;

--
-- Name: factor_type; Type: TYPE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TYPE auth.factor_type AS ENUM (
    'totp',
    'webauthn',
    'phone'
);


ALTER TYPE auth.factor_type OWNER TO supabase_auth_admin;

--
-- Name: oauth_authorization_status; Type: TYPE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TYPE auth.oauth_authorization_status AS ENUM (
    'pending',
    'approved',
    'denied',
    'expired'
);


ALTER TYPE auth.oauth_authorization_status OWNER TO supabase_auth_admin;

--
-- Name: oauth_client_type; Type: TYPE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TYPE auth.oauth_client_type AS ENUM (
    'public',
    'confidential'
);


ALTER TYPE auth.oauth_client_type OWNER TO supabase_auth_admin;

--
-- Name: oauth_registration_type; Type: TYPE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TYPE auth.oauth_registration_type AS ENUM (
    'dynamic',
    'manual'
);


ALTER TYPE auth.oauth_registration_type OWNER TO supabase_auth_admin;

--
-- Name: oauth_response_type; Type: TYPE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TYPE auth.oauth_response_type AS ENUM (
    'code'
);


ALTER TYPE auth.oauth_response_type OWNER TO supabase_auth_admin;

--
-- Name: one_time_token_type; Type: TYPE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TYPE auth.one_time_token_type AS ENUM (
    'confirmation_token',
    'reauthentication_token',
    'recovery_token',
    'email_change_token_new',
    'email_change_token_current',
    'phone_change_token'
);


ALTER TYPE auth.one_time_token_type OWNER TO supabase_auth_admin;

--
-- Name: action; Type: TYPE; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE TYPE realtime.action AS ENUM (
    'INSERT',
    'UPDATE',
    'DELETE',
    'TRUNCATE',
    'ERROR'
);


ALTER TYPE realtime.action OWNER TO supabase_realtime_admin;

--
-- Name: equality_op; Type: TYPE; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE TYPE realtime.equality_op AS ENUM (
    'eq',
    'neq',
    'lt',
    'lte',
    'gt',
    'gte',
    'in',
    'like',
    'ilike',
    'is',
    'match',
    'imatch',
    'isdistinct'
);


ALTER TYPE realtime.equality_op OWNER TO supabase_realtime_admin;

--
-- Name: user_defined_filter; Type: TYPE; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE TYPE realtime.user_defined_filter AS (
	column_name text,
	op realtime.equality_op,
	value text,
	negate boolean
);


ALTER TYPE realtime.user_defined_filter OWNER TO supabase_realtime_admin;

--
-- Name: wal_column; Type: TYPE; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE TYPE realtime.wal_column AS (
	name text,
	type_name text,
	type_oid oid,
	value jsonb,
	is_pkey boolean,
	is_selectable boolean
);


ALTER TYPE realtime.wal_column OWNER TO supabase_realtime_admin;

--
-- Name: wal_rls; Type: TYPE; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE TYPE realtime.wal_rls AS (
	wal jsonb,
	is_rls_enabled boolean,
	subscription_ids uuid[],
	errors text[]
);


ALTER TYPE realtime.wal_rls OWNER TO supabase_realtime_admin;

--
-- Name: buckettype; Type: TYPE; Schema: storage; Owner: supabase_storage_admin
--

CREATE TYPE storage.buckettype AS ENUM (
    'STANDARD',
    'ANALYTICS',
    'VECTOR'
);


ALTER TYPE storage.buckettype OWNER TO supabase_storage_admin;

--
-- Name: email(); Type: FUNCTION; Schema: auth; Owner: supabase_auth_admin
--

CREATE FUNCTION auth.email() RETURNS text
    LANGUAGE sql STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.email', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'email')
  )::text
$$;


ALTER FUNCTION auth.email() OWNER TO supabase_auth_admin;

--
-- Name: FUNCTION email(); Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON FUNCTION auth.email() IS 'Deprecated. Use auth.jwt() -> ''email'' instead.';


--
-- Name: jwt(); Type: FUNCTION; Schema: auth; Owner: supabase_auth_admin
--

CREATE FUNCTION auth.jwt() RETURNS jsonb
    LANGUAGE sql STABLE
    AS $$
  select 
    coalesce(
        nullif(current_setting('request.jwt.claim', true), ''),
        nullif(current_setting('request.jwt.claims', true), '')
    )::jsonb
$$;


ALTER FUNCTION auth.jwt() OWNER TO supabase_auth_admin;

--
-- Name: role(); Type: FUNCTION; Schema: auth; Owner: supabase_auth_admin
--

CREATE FUNCTION auth.role() RETURNS text
    LANGUAGE sql STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.role', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role')
  )::text
$$;


ALTER FUNCTION auth.role() OWNER TO supabase_auth_admin;

--
-- Name: FUNCTION role(); Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON FUNCTION auth.role() IS 'Deprecated. Use auth.jwt() -> ''role'' instead.';


--
-- Name: uid(); Type: FUNCTION; Schema: auth; Owner: supabase_auth_admin
--

CREATE FUNCTION auth.uid() RETURNS uuid
    LANGUAGE sql STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.sub', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub')
  )::uuid
$$;


ALTER FUNCTION auth.uid() OWNER TO supabase_auth_admin;

--
-- Name: FUNCTION uid(); Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON FUNCTION auth.uid() IS 'Deprecated. Use auth.jwt() -> ''sub'' instead.';


--
-- Name: grant_pg_cron_access(); Type: FUNCTION; Schema: extensions; Owner: supabase_admin
--

CREATE FUNCTION extensions.grant_pg_cron_access() RETURNS event_trigger
    LANGUAGE plpgsql
    SET search_path TO ''
    AS $$
BEGIN
  IF EXISTS (
    SELECT
    FROM pg_event_trigger_ddl_commands() AS ev
    JOIN pg_extension AS ext
    ON ev.objid = ext.oid
    WHERE ext.extname = 'pg_cron'
  )
  THEN
    grant usage on schema cron to postgres with grant option;

    alter default privileges in schema cron grant all on tables to postgres with grant option;
    alter default privileges in schema cron grant all on functions to postgres with grant option;
    alter default privileges in schema cron grant all on sequences to postgres with grant option;

    alter default privileges for user supabase_admin in schema cron grant all
        on sequences to postgres with grant option;
    alter default privileges for user supabase_admin in schema cron grant all
        on tables to postgres with grant option;
    alter default privileges for user supabase_admin in schema cron grant all
        on functions to postgres with grant option;

    grant all privileges on all tables in schema cron to postgres with grant option;
    revoke all on table cron.job from postgres;
    grant select on table cron.job to postgres with grant option;
    revoke trigger on cron.job_run_details from postgres;
  END IF;
END;
$$;


ALTER FUNCTION extensions.grant_pg_cron_access() OWNER TO supabase_admin;

--
-- Name: FUNCTION grant_pg_cron_access(); Type: COMMENT; Schema: extensions; Owner: supabase_admin
--

COMMENT ON FUNCTION extensions.grant_pg_cron_access() IS 'Grants access to pg_cron';


--
-- Name: grant_pg_graphql_access(); Type: FUNCTION; Schema: extensions; Owner: supabase_admin
--

CREATE FUNCTION extensions.grant_pg_graphql_access() RETURNS event_trigger
    LANGUAGE plpgsql
    SET search_path TO ''
    AS $_$
begin
    if not exists (
        select 1
        from pg_catalog.pg_event_trigger_ddl_commands() ev
        join pg_catalog.pg_extension e on ev.objid = e.oid
        where e.extname = 'pg_graphql'
    ) then
        return;
    end if;

    drop function if exists graphql_public.graphql;
    create or replace function graphql_public.graphql(
        "operationName" text default null,
        query text default null,
        variables jsonb default null,
        extensions jsonb default null
    )
        returns jsonb
        language sql
    as $$
        select graphql.resolve(
            query := query,
            variables := coalesce(variables, '{}'),
            "operationName" := "operationName",
            extensions := extensions
        );
    $$;

    -- Attach the wrapper to the extension so DROP EXTENSION cascades to it,
    -- which in turn triggers set_graphql_placeholder to reinstall the "not enabled" stub.
    alter extension pg_graphql add function graphql_public.graphql(text, text, jsonb, jsonb);

    grant usage on schema graphql to postgres, anon, authenticated, service_role;
    grant execute on function graphql.resolve to postgres, anon, authenticated, service_role;
    grant usage on schema graphql to postgres with grant option;
    grant usage on schema graphql_public to postgres with grant option;
end;
$_$;


ALTER FUNCTION extensions.grant_pg_graphql_access() OWNER TO supabase_admin;

--
-- Name: FUNCTION grant_pg_graphql_access(); Type: COMMENT; Schema: extensions; Owner: supabase_admin
--

COMMENT ON FUNCTION extensions.grant_pg_graphql_access() IS 'Grants access to pg_graphql';


--
-- Name: grant_pg_net_access(); Type: FUNCTION; Schema: extensions; Owner: supabase_admin
--

CREATE FUNCTION extensions.grant_pg_net_access() RETURNS event_trigger
    LANGUAGE plpgsql
    SET search_path TO ''
    AS $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_event_trigger_ddl_commands() AS ev
    JOIN pg_extension AS ext
    ON ev.objid = ext.oid
    WHERE ext.extname = 'pg_net'
  )
  THEN
    IF NOT EXISTS (
      SELECT 1
      FROM pg_roles
      WHERE rolname = 'supabase_functions_admin'
    )
    THEN
      CREATE USER supabase_functions_admin NOINHERIT CREATEROLE LOGIN NOREPLICATION;
    END IF;

    GRANT USAGE ON SCHEMA net TO supabase_functions_admin, postgres, anon, authenticated, service_role;

    IF EXISTS (
      SELECT FROM pg_extension
      WHERE extname = 'pg_net'
      -- all versions in use on existing projects as of 2025-02-20
      -- version 0.12.0 onwards don't need these applied
      AND extversion IN ('0.2', '0.6', '0.7', '0.7.1', '0.8.0', '0.10.0', '0.11.0')
    ) THEN
      ALTER function net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;
      ALTER function net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;

      ALTER function net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net;
      ALTER function net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net;

      REVOKE ALL ON FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) FROM PUBLIC;
      REVOKE ALL ON FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) FROM PUBLIC;

      GRANT EXECUTE ON FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) TO supabase_functions_admin, postgres, anon, authenticated, service_role;
      GRANT EXECUTE ON FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) TO supabase_functions_admin, postgres, anon, authenticated, service_role;
    END IF;
  END IF;
END;
$$;


ALTER FUNCTION extensions.grant_pg_net_access() OWNER TO supabase_admin;

--
-- Name: FUNCTION grant_pg_net_access(); Type: COMMENT; Schema: extensions; Owner: supabase_admin
--

COMMENT ON FUNCTION extensions.grant_pg_net_access() IS 'Grants access to pg_net';


--
-- Name: pgrst_ddl_watch(); Type: FUNCTION; Schema: extensions; Owner: supabase_admin
--

CREATE FUNCTION extensions.pgrst_ddl_watch() RETURNS event_trigger
    LANGUAGE plpgsql
    SET search_path TO ''
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN SELECT * FROM pg_event_trigger_ddl_commands()
  LOOP
    IF cmd.command_tag IN (
      'CREATE SCHEMA', 'ALTER SCHEMA'
    , 'CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO', 'ALTER TABLE'
    , 'CREATE FOREIGN TABLE', 'ALTER FOREIGN TABLE'
    , 'CREATE VIEW', 'ALTER VIEW'
    , 'CREATE MATERIALIZED VIEW', 'ALTER MATERIALIZED VIEW'
    , 'CREATE FUNCTION', 'ALTER FUNCTION'
    , 'CREATE TRIGGER'
    , 'CREATE TYPE', 'ALTER TYPE'
    , 'CREATE RULE'
    , 'COMMENT'
    )
    -- don't notify in case of CREATE TEMP table or other objects created on pg_temp
    AND cmd.schema_name is distinct from 'pg_temp'
    THEN
      NOTIFY pgrst, 'reload schema';
    END IF;
  END LOOP;
END; $$;


ALTER FUNCTION extensions.pgrst_ddl_watch() OWNER TO supabase_admin;

--
-- Name: pgrst_drop_watch(); Type: FUNCTION; Schema: extensions; Owner: supabase_admin
--

CREATE FUNCTION extensions.pgrst_drop_watch() RETURNS event_trigger
    LANGUAGE plpgsql
    SET search_path TO ''
    AS $$
DECLARE
  obj record;
BEGIN
  FOR obj IN SELECT * FROM pg_event_trigger_dropped_objects()
  LOOP
    IF obj.object_type IN (
      'schema'
    , 'table'
    , 'foreign table'
    , 'view'
    , 'materialized view'
    , 'function'
    , 'trigger'
    , 'type'
    , 'rule'
    )
    AND obj.is_temporary IS false -- no pg_temp objects
    THEN
      NOTIFY pgrst, 'reload schema';
    END IF;
  END LOOP;
END; $$;


ALTER FUNCTION extensions.pgrst_drop_watch() OWNER TO supabase_admin;

--
-- Name: set_graphql_placeholder(); Type: FUNCTION; Schema: extensions; Owner: supabase_admin
--

CREATE FUNCTION extensions.set_graphql_placeholder() RETURNS event_trigger
    LANGUAGE plpgsql
    SET search_path TO ''
    AS $_$
    DECLARE
    graphql_is_dropped bool;
    BEGIN
    graphql_is_dropped = (
        SELECT ev.schema_name = 'graphql_public'
        FROM pg_event_trigger_dropped_objects() AS ev
        WHERE ev.schema_name = 'graphql_public'
    );

    IF graphql_is_dropped
    THEN
        create or replace function graphql_public.graphql(
            "operationName" text default null,
            query text default null,
            variables jsonb default null,
            extensions jsonb default null
        )
            returns jsonb
            language plpgsql
            set search_path to ''
        as $$
            DECLARE
                server_version float;
            BEGIN
                server_version = (SELECT (SPLIT_PART((select version()), ' ', 2))::float);

                IF server_version >= 14 THEN
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql extension is not enabled.'
                            )
                        )
                    );
                ELSE
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql is only available on projects running Postgres 14 onwards.'
                            )
                        )
                    );
                END IF;
            END;
        $$;
    END IF;

    END;
$_$;


ALTER FUNCTION extensions.set_graphql_placeholder() OWNER TO supabase_admin;

--
-- Name: FUNCTION set_graphql_placeholder(); Type: COMMENT; Schema: extensions; Owner: supabase_admin
--

COMMENT ON FUNCTION extensions.set_graphql_placeholder() IS 'Reintroduces placeholder function for graphql_public.graphql';


--
-- Name: graphql(text, text, jsonb, jsonb); Type: FUNCTION; Schema: graphql_public; Owner: supabase_admin
--

CREATE FUNCTION graphql_public.graphql("operationName" text DEFAULT NULL::text, query text DEFAULT NULL::text, variables jsonb DEFAULT NULL::jsonb, extensions jsonb DEFAULT NULL::jsonb) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
            DECLARE
                server_version float;
            BEGIN
                server_version = (SELECT (SPLIT_PART((select version()), ' ', 2))::float);

                IF server_version >= 14 THEN
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql extension is not enabled.'
                            )
                        )
                    );
                ELSE
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql is only available on projects running Postgres 14 onwards.'
                            )
                        )
                    );
                END IF;
            END;
        $$;


ALTER FUNCTION graphql_public.graphql("operationName" text, query text, variables jsonb, extensions jsonb) OWNER TO supabase_admin;

--
-- Name: get_auth(text); Type: FUNCTION; Schema: pgbouncer; Owner: supabase_admin
--

CREATE FUNCTION pgbouncer.get_auth(p_usename text) RETURNS TABLE(username text, password text)
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO ''
    AS $_$
  BEGIN
      RAISE DEBUG 'PgBouncer auth request: %', p_usename;

      RETURN QUERY
      SELECT
          rolname::text,
          CASE WHEN rolvaliduntil < now()
              THEN null
              ELSE rolpassword::text
          END
      FROM pg_authid
      WHERE rolname=$1 and rolcanlogin;
  END;
  $_$;


ALTER FUNCTION pgbouncer.get_auth(p_usename text) OWNER TO supabase_admin;

--
-- Name: find_duplicate_logs(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.find_duplicate_logs(p_ticker text) RETURNS TABLE(accession_number text, cnt bigint)
    LANGUAGE sql STABLE
    SET search_path TO 'public'
    AS $$
    SELECT accession_number, COUNT(*)
    FROM candidate_review_log
    WHERE security_id = (SELECT id FROM securities WHERE ticker = p_ticker) AND verdict = 'real_event'
    GROUP BY accession_number
    HAVING COUNT(*) > 1;
$$;


ALTER FUNCTION public.find_duplicate_logs(p_ticker text) OWNER TO postgres;

--
-- Name: find_phantom_filings(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.find_phantom_filings(p_ticker text) RETURNS TABLE(filing_date date, accession_number text)
    LANGUAGE sql STABLE
    SET search_path TO 'public'
    AS $$
    SELECT fac.filing_date, fac.accession_number
    FROM filing_ai_classifications fac
    WHERE fac.ticker = p_ticker AND fac.ai_verdict = 'real_event'
    AND fac.accession_number NOT IN (
        SELECT accession_number FROM candidate_review_log
        WHERE security_id = (SELECT id FROM securities WHERE ticker = p_ticker)
        AND verdict = 'real_event'
    );
$$;


ALTER FUNCTION public.find_phantom_filings(p_ticker text) OWNER TO postgres;

--
-- Name: apply_rls(jsonb, integer); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.apply_rls(wal jsonb, max_record_bytes integer DEFAULT (1024 * 1024)) RETURNS SETOF realtime.wal_rls
    LANGUAGE plpgsql
    AS $$
declare
    -- Regclass of the table e.g. public.notes
    entity_ regclass = (quote_ident(wal ->> 'schema') || '.' || quote_ident(wal ->> 'table'))::regclass;

    -- I, U, D, T: insert, update ...
    action realtime.action = (
        case wal ->> 'action'
            when 'I' then 'INSERT'
            when 'U' then 'UPDATE'
            when 'D' then 'DELETE'
            else 'ERROR'
        end
    );

    -- Is row level security enabled for the table
    is_rls_enabled bool = relrowsecurity from pg_class where oid = entity_;

    subscriptions realtime.subscription[] = array_agg(subs)
        from
            realtime.subscription subs
        where
            subs.entity = entity_
            -- Filter by action early - only get subscriptions interested in this action
            -- action_filter column can be: '*' (all), 'INSERT', 'UPDATE', or 'DELETE'
            and (subs.action_filter = '*' or subs.action_filter = action::text);

    -- Subscription vars
    working_role regrole;
    working_selected_columns text[];
    claimed_role regrole;
    claims jsonb;

    subscription_id uuid;
    subscription_has_access bool;
    visible_to_subscription_ids uuid[] = '{}';

    -- structured info for wal's columns
    columns realtime.wal_column[];
    -- previous identity values for update/delete
    old_columns realtime.wal_column[];

    error_record_exceeds_max_size boolean = octet_length(wal::text) > max_record_bytes;

    -- Primary jsonb output for record
    output jsonb;

    -- Loop record for iterating unique roles (outer loop)
    role_record record;
    -- Loop record for iterating unique selected_columns within a role (inner loop)
    cols_record record;
    -- Subscription ids visible at the role level (before fanning out by selected_columns)
    visible_role_sub_ids uuid[] = '{}';

begin
    perform set_config('role', null, true);

    columns =
        array_agg(
            (
                x->>'name',
                x->>'type',
                x->>'typeoid',
                realtime.cast(
                    (x->'value') #>> '{}',
                    coalesce(
                        (x->>'typeoid')::regtype, -- null when wal2json version <= 2.4
                        (x->>'type')::regtype
                    )
                ),
                (pks ->> 'name') is not null,
                true
            )::realtime.wal_column
        )
        from
            jsonb_array_elements(wal -> 'columns') x
            left join jsonb_array_elements(wal -> 'pk') pks
                on (x ->> 'name') = (pks ->> 'name');

    old_columns =
        array_agg(
            (
                x->>'name',
                x->>'type',
                x->>'typeoid',
                realtime.cast(
                    (x->'value') #>> '{}',
                    coalesce(
                        (x->>'typeoid')::regtype, -- null when wal2json version <= 2.4
                        (x->>'type')::regtype
                    )
                ),
                (pks ->> 'name') is not null,
                true
            )::realtime.wal_column
        )
        from
            jsonb_array_elements(wal -> 'identity') x
            left join jsonb_array_elements(wal -> 'pk') pks
                on (x ->> 'name') = (pks ->> 'name');

    for role_record in
        select claims_role
        from (select distinct claims_role from unnest(subscriptions)) t
        order by claims_role::text
    loop
        working_role := role_record.claims_role;

        -- Update `is_selectable` for columns and old_columns (once per role)
        columns =
            array_agg(
                (
                    c.name,
                    c.type_name,
                    c.type_oid,
                    c.value,
                    c.is_pkey,
                    pg_catalog.has_column_privilege(working_role, entity_, c.name, 'SELECT')
                )::realtime.wal_column
            )
            from
                unnest(columns) c;

        old_columns =
                array_agg(
                    (
                        c.name,
                        c.type_name,
                        c.type_oid,
                        c.value,
                        c.is_pkey,
                        pg_catalog.has_column_privilege(working_role, entity_, c.name, 'SELECT')
                    )::realtime.wal_column
                )
                from
                    unnest(old_columns) c;

        if action <> 'DELETE' and count(1) = 0 from unnest(columns) c where c.is_pkey then
            -- Fan out 400 error per distinct selected_columns for this role
            for cols_record in
                select selected_columns
                from (select distinct selected_columns from unnest(subscriptions) s where s.claims_role = working_role) t
                order by coalesce(array_to_string(selected_columns, ','), '')
            loop
                working_selected_columns := cols_record.selected_columns;
                return next (
                    jsonb_build_object(
                        'schema', wal ->> 'schema',
                        'table', wal ->> 'table',
                        'type', action
                    ),
                    is_rls_enabled,
                    (select array_agg(s.subscription_id) from unnest(subscriptions) as s where s.claims_role = working_role and (s.selected_columns is not distinct from working_selected_columns)),
                    array['Error 400: Bad Request, no primary key']
                )::realtime.wal_rls;
            end loop;

        -- The claims role does not have SELECT permission to the primary key of entity
        elsif action <> 'DELETE' and sum(c.is_selectable::int) <> count(1) from unnest(columns) c where c.is_pkey then
            -- Fan out 401 error per distinct selected_columns for this role
            for cols_record in
                select selected_columns
                from (select distinct selected_columns from unnest(subscriptions) s where s.claims_role = working_role) t
                order by coalesce(array_to_string(selected_columns, ','), '')
            loop
                working_selected_columns := cols_record.selected_columns;
                return next (
                    jsonb_build_object(
                        'schema', wal ->> 'schema',
                        'table', wal ->> 'table',
                        'type', action
                    ),
                    is_rls_enabled,
                    (select array_agg(s.subscription_id) from unnest(subscriptions) as s where s.claims_role = working_role and (s.selected_columns is not distinct from working_selected_columns)),
                    array['Error 401: Unauthorized']
                )::realtime.wal_rls;
            end loop;

        else
            -- Create the prepared statement (once per role)
            if is_rls_enabled and action <> 'DELETE' then
                if (select 1 from pg_prepared_statements where name = 'walrus_rls_stmt' limit 1) > 0 then
                    deallocate walrus_rls_stmt;
                end if;
                execute realtime.build_prepared_statement_sql('walrus_rls_stmt', entity_, columns);
            end if;

            -- Collect all visible subscription IDs for this role (filter check + RLS check)
            visible_role_sub_ids = '{}';

            for subscription_id, claims in (
                    select
                        subs.subscription_id,
                        subs.claims
                    from
                        unnest(subscriptions) subs
                    where
                        subs.entity = entity_
                        and subs.claims_role = working_role
                        and (
                            realtime.is_visible_through_filters(columns, subs.filters)
                            or (
                              action = 'DELETE'
                              and realtime.is_visible_through_filters(old_columns, subs.filters)
                            )
                        )
            ) loop

                if not is_rls_enabled or action = 'DELETE' then
                    visible_role_sub_ids = visible_role_sub_ids || subscription_id;
                else
                    -- Check if RLS allows the role to see the record
                    perform
                        -- Trim leading and trailing quotes from working_role because set_config
                        -- doesn't recognize the role as valid if they are included
                        set_config('role', trim(both '"' from working_role::text), true),
                        set_config('request.jwt.claims', claims::text, true);

                    execute 'execute walrus_rls_stmt' into subscription_has_access;

                    -- Reset the role on every FOR..LOOP batch execution.
                    -- The first batch of 10 rows is pre-fetched using the current connection role (PG internal behaviour)
                    -- then we have to reset it again otherwise it would use the role defined in the `set_config` above
                    -- to fetch the remaining rows when rows>10, which could be a user-defined role that lacks execution grants.
                    -- The flow is:
                    --   1. run batch with conn role
                    --   2. set_config working_role
                    --   3. execute walrus
                    --   4. reset role (revert)
                    --   5. repeat
                    perform set_config('role', null, true);

                    if subscription_has_access then
                        visible_role_sub_ids = visible_role_sub_ids || subscription_id;
                    end if;
                end if;
            end loop;

            perform set_config('role', null, true);

            -- Inner loop: per distinct selected_columns for this role
            for cols_record in
                select selected_columns
                from (select distinct selected_columns from unnest(subscriptions) s where s.claims_role = working_role) t
                order by coalesce(array_to_string(selected_columns, ','), '')
            loop
                working_selected_columns := cols_record.selected_columns;

                output = jsonb_build_object(
                    'schema', wal ->> 'schema',
                    'table', wal ->> 'table',
                    'type', action,
                    'commit_timestamp', to_char(
                        ((wal ->> 'timestamp')::timestamptz at time zone 'utc'),
                        'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'
                    ),
                    'columns', (
                        select
                            jsonb_agg(
                                jsonb_build_object(
                                    'name', pa.attname,
                                    'type', pt.typname
                                )
                                order by pa.attnum asc
                            )
                        from
                            pg_attribute pa
                            join pg_type pt
                                on pa.atttypid = pt.oid
                            left join (
                                select unnest(conkey) as pkey_attnum
                                from pg_constraint
                                where conrelid = entity_ and contype = 'p'
                            ) pk on pk.pkey_attnum = pa.attnum
                        where
                            attrelid = entity_
                            and attnum > 0
                            and pg_catalog.has_column_privilege(working_role, entity_, pa.attname, 'SELECT')
                            and (working_selected_columns is null or pa.attname = any(working_selected_columns) or pk.pkey_attnum is not null)
                    )
                )
                -- Add "record" key for insert and update
                || case
                    when action in ('INSERT', 'UPDATE') then
                        jsonb_build_object(
                            'record',
                            (
                                select
                                    jsonb_object_agg(
                                        -- if unchanged toast, get column name and value from old record
                                        coalesce((c).name, (oc).name),
                                        case
                                            when (c).name is null then (oc).value
                                            else (c).value
                                        end
                                    )
                                from
                                    unnest(columns) c
                                    full outer join unnest(old_columns) oc
                                        on (c).name = (oc).name
                                where
                                    coalesce((c).is_selectable, (oc).is_selectable)
                                    and (working_selected_columns is null or coalesce((c).name, (oc).name) = any(working_selected_columns) or coalesce((c).is_pkey, (oc).is_pkey))
                                    and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                            )
                        )
                    else '{}'::jsonb
                end
                -- Add "old_record" key for update and delete
                || case
                    when action = 'UPDATE' then
                        jsonb_build_object(
                                'old_record',
                                (
                                    select jsonb_object_agg((c).name, (c).value)
                                    from unnest(old_columns) c
                                    where
                                        (c).is_selectable
                                        and (working_selected_columns is null or (c).name = any(working_selected_columns) or (c).is_pkey)
                                        and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                                )
                            )
                    when action = 'DELETE' then
                        jsonb_build_object(
                            'old_record',
                            (
                                select jsonb_object_agg((c).name, (c).value)
                                from unnest(old_columns) c
                                where
                                    (c).is_selectable
                                    and (working_selected_columns is null or (c).name = any(working_selected_columns) or (c).is_pkey)
                                    and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                                    and ( not is_rls_enabled or (c).is_pkey ) -- if RLS enabled, we can't secure deletes so filter to pkey
                            )
                        )
                    else '{}'::jsonb
                end;

                -- Filter visible_role_sub_ids to those matching the current selected_columns group
                visible_to_subscription_ids = coalesce(
                    (
                        select array_agg(s.subscription_id)
                        from unnest(subscriptions) s
                        where s.claims_role = working_role
                          and (s.selected_columns is not distinct from working_selected_columns)
                          and s.subscription_id = any(visible_role_sub_ids)
                    ),
                    '{}'::uuid[]
                );

                return next (
                    output,
                    is_rls_enabled,
                    visible_to_subscription_ids,
                    case
                        when error_record_exceeds_max_size then array['Error 413: Payload Too Large']
                        else '{}'
                    end
                )::realtime.wal_rls;
            end loop;

        end if;
    end loop;

    perform set_config('role', null, true);
end;
$$;


ALTER FUNCTION realtime.apply_rls(wal jsonb, max_record_bytes integer) OWNER TO supabase_realtime_admin;

--
-- Name: broadcast_changes(text, text, text, text, text, record, record, text); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.broadcast_changes(topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text DEFAULT 'ROW'::text) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    -- Declare a variable to hold the JSONB representation of the row
    row_data jsonb := '{}'::jsonb;
BEGIN
    IF level = 'STATEMENT' THEN
        RAISE EXCEPTION 'function can only be triggered for each row, not for each statement';
    END IF;
    -- Check the operation type and handle accordingly
    IF operation = 'INSERT' OR operation = 'UPDATE' OR operation = 'DELETE' THEN
        row_data := jsonb_build_object('old_record', OLD, 'record', NEW, 'operation', operation, 'table', table_name, 'schema', table_schema);
        PERFORM realtime.send (row_data, event_name, topic_name);
    ELSE
        RAISE EXCEPTION 'Unexpected operation type: %', operation;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to process the row: %', SQLERRM;
END;

$$;


ALTER FUNCTION realtime.broadcast_changes(topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text) OWNER TO supabase_realtime_admin;

--
-- Name: build_prepared_statement_sql(text, regclass, realtime.wal_column[]); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]) RETURNS text
    LANGUAGE sql
    AS $$
      /*
      Builds a sql string that, if executed, creates a prepared statement to
      tests retrive a row from *entity* by its primary key columns.
      Example
          select realtime.build_prepared_statement_sql('public.notes', '{"id"}'::text[], '{"bigint"}'::text[])
      */
          select
      'prepare ' || prepared_statement_name || ' as
          select
              exists(
                  select
                      1
                  from
                      ' || entity || '
                  where
                      ' || string_agg(quote_ident(pkc.name) || '=' || quote_nullable(pkc.value #>> '{}') , ' and ') || '
              )'
          from
              unnest(columns) pkc
          where
              pkc.is_pkey
          group by
              entity
      $$;


ALTER FUNCTION realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]) OWNER TO supabase_realtime_admin;

--
-- Name: cast(text, regtype); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime."cast"(val text, type_ regtype) RETURNS jsonb
    LANGUAGE plpgsql IMMUTABLE
    AS $$
declare
  res jsonb;
begin
  if type_::text = 'bytea' then
    return to_jsonb(val);
  end if;
  execute format('select to_jsonb(%L::'|| type_::text || ')', val) into res;
  return res;
end
$$;


ALTER FUNCTION realtime."cast"(val text, type_ regtype) OWNER TO supabase_realtime_admin;

--
-- Name: check_equality_op(realtime.equality_op, regtype, text, text); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text) RETURNS boolean
    LANGUAGE plpgsql IMMUTABLE
    AS $$
/*
Casts *val_1* and *val_2* as type *type_* and check the *op* condition for truthiness
*/
declare
    op_symbol text = (
        case
            when op = 'eq' then '='
            when op = 'neq' then '!='
            when op = 'lt' then '<'
            when op = 'lte' then '<='
            when op = 'gt' then '>'
            when op = 'gte' then '>='
            when op = 'in' then '= any'
            else 'UNKNOWN OP'
        end
    );
    res boolean;
begin
    execute format(
        'select %L::'|| type_::text || ' ' || op_symbol
        || ' ( %L::'
        || (
            case
                when op = 'in' then type_::text || '[]'
                else type_::text end
        )
        || ')', val_1, val_2) into res;
    return res;
end;
$$;


ALTER FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text) OWNER TO supabase_realtime_admin;

--
-- Name: check_equality_op(realtime.equality_op, regtype, text, text, boolean); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text, negate boolean) RETURNS boolean
    LANGUAGE plpgsql STABLE
    AS $$
declare
    op_symbol text;
    res boolean;
begin
    -- IS DISTINCT FROM / IS NOT DISTINCT FROM: infix, both sides typed literals
    if op = 'isdistinct' then
        execute format(
            'select %L::%s %s %L::%s',
            val_1,
            type_::text,
            case when negate then 'IS NOT DISTINCT FROM' else 'IS DISTINCT FROM' end,
            val_2,
            type_::text
        ) into res;
        return res;
    end if;

    -- IS requires a keyword RHS (NULL, TRUE, FALSE, UNKNOWN), not a typed literal
    if op = 'is' then
        if val_2 not in ('null', 'true', 'false', 'unknown') then
            raise exception 'invalid value for is filter: must be null, true, false, or unknown';
        end if;
        execute format(
            'select %L::%s %s %s',
            val_1,
            type_::text,
            case when negate then 'IS NOT' else 'IS' end,
            upper(val_2)
        ) into res;
        return res;
    end if;

    op_symbol = case
        when op = 'eq'    then '='
        when op = 'neq'   then '!='
        when op = 'lt'    then '<'
        when op = 'lte'   then '<='
        when op = 'gt'    then '>'
        when op = 'gte'   then '>='
        when op = 'in'    then '= any'
        when op = 'like'   then 'LIKE'
        when op = 'ilike'  then 'ILIKE'
        when op = 'match'  then '~'
        when op = 'imatch' then '~*'
        else null
    end;

    if op_symbol is null then
        raise exception 'unsupported equality operator: %', op::text;
    end if;

    execute format(
        'select %L::%s %s (%L::%s)',
        val_1,
        type_::text,
        op_symbol,
        val_2,
        case when op = 'in' then type_::text || '[]' else type_::text end
    ) into res;

    return case when negate then not res else res end;
end;
$$;


ALTER FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text, negate boolean) OWNER TO supabase_realtime_admin;

--
-- Name: is_visible_through_filters(realtime.wal_column[], realtime.user_defined_filter[]); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]) RETURNS boolean
    LANGUAGE sql STABLE
    AS $$
    select
        filters is null
        or array_length(filters, 1) is null
        or coalesce(
            count(col.name) = count(1)
            and sum(
                realtime.check_equality_op(
                    op:=f.op,
                    type_:=coalesce(col.type_oid::regtype, col.type_name::regtype),
                    val_1:=col.value #>> '{}',
                    val_2:=f.value,
                    negate:=coalesce(f.negate, false)
                )::int
            ) filter (where col.name is not null) = count(col.name),
            false
        )
    from
        unnest(filters) f
        left join unnest(columns) col
            on f.column_name = col.name;
$$;


ALTER FUNCTION realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]) OWNER TO supabase_realtime_admin;

--
-- Name: list_changes(name, name, integer, integer); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.list_changes(publication name, slot_name name, max_changes integer, max_record_bytes integer) RETURNS TABLE(wal jsonb, is_rls_enabled boolean, subscription_ids uuid[], errors text[], slot_changes_count bigint)
    LANGUAGE sql
    SET log_min_messages TO 'fatal'
    AS $$
  WITH pub AS (
    SELECT
      concat_ws(
        ',',
        CASE WHEN bool_or(pubinsert) THEN 'insert' ELSE NULL END,
        CASE WHEN bool_or(pubupdate) THEN 'update' ELSE NULL END,
        CASE WHEN bool_or(pubdelete) THEN 'delete' ELSE NULL END
      ) AS w2j_actions,
      coalesce(
        string_agg(
          realtime.quote_wal2json(format('%I.%I', schemaname, tablename)::regclass),
          ','
        ) filter (WHERE ppt.tablename IS NOT NULL),
        ''
      ) AS w2j_add_tables
    FROM pg_publication pp
    LEFT JOIN pg_publication_tables ppt ON pp.pubname = ppt.pubname
    WHERE pp.pubname = publication
    GROUP BY pp.pubname
    LIMIT 1
  ),
  -- MATERIALIZED ensures pg_logical_slot_get_changes is called exactly once
  w2j AS MATERIALIZED (
    SELECT x.*, pub.w2j_add_tables
    FROM pub,
         pg_logical_slot_get_changes(
           slot_name, null, max_changes,
           'include-pk', 'true',
           'include-transaction', 'false',
           'include-timestamp', 'true',
           'include-type-oids', 'true',
           'format-version', '2',
           'actions', pub.w2j_actions,
           'add-tables', pub.w2j_add_tables
         ) x
  ),
  slot_count AS (
    SELECT count(*)::bigint AS cnt
    FROM w2j
    WHERE w2j.w2j_add_tables <> ''
  ),
  rls_filtered AS (
    SELECT xyz.wal, xyz.is_rls_enabled, xyz.subscription_ids, xyz.errors
    FROM w2j,
         realtime.apply_rls(
           wal := w2j.data::jsonb,
           max_record_bytes := max_record_bytes
         ) xyz(wal, is_rls_enabled, subscription_ids, errors)
    WHERE w2j.w2j_add_tables <> ''
      AND xyz.subscription_ids[1] IS NOT NULL
  )
  SELECT rf.wal, rf.is_rls_enabled, rf.subscription_ids, rf.errors, sc.cnt
  FROM rls_filtered rf, slot_count sc

  UNION ALL

  SELECT null, null, null, null, sc.cnt
  FROM slot_count sc
  WHERE NOT EXISTS (SELECT 1 FROM rls_filtered)
$$;


ALTER FUNCTION realtime.list_changes(publication name, slot_name name, max_changes integer, max_record_bytes integer) OWNER TO supabase_realtime_admin;

--
-- Name: quote_wal2json(regclass); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.quote_wal2json(entity regclass) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
  SELECT
    realtime.wal2json_escape_identifier(nsp.nspname::text)
    || '.'
    || realtime.wal2json_escape_identifier(pc.relname::text)
  FROM pg_class pc
  JOIN pg_namespace nsp ON pc.relnamespace = nsp.oid
  WHERE pc.oid = entity
$$;


ALTER FUNCTION realtime.quote_wal2json(entity regclass) OWNER TO supabase_realtime_admin;

--
-- Name: send(jsonb, text, text, boolean); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.send(payload jsonb, event text, topic text, private boolean DEFAULT true) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
  generated_id uuid;
  final_payload jsonb;
BEGIN
  BEGIN
    generated_id := gen_random_uuid();

    -- Check if payload has an 'id' key, if not, add the generated UUID
    IF payload ? 'id' THEN
      final_payload := payload;
    ELSE
      final_payload := jsonb_set(payload, '{id}', to_jsonb(generated_id));
    END IF;

    -- Set the topic configuration
    EXECUTE format('SET LOCAL realtime.topic TO %L', topic);

    INSERT INTO realtime.messages (id, payload, event, topic, private, extension)
    VALUES (generated_id, final_payload, event, topic, private, 'broadcast');
  EXCEPTION
    WHEN OTHERS THEN
      RAISE WARNING 'WarnSendingBroadcastMessage: %', SQLERRM;
  END;
END;
$$;


ALTER FUNCTION realtime.send(payload jsonb, event text, topic text, private boolean) OWNER TO supabase_realtime_admin;

--
-- Name: send_binary(bytea, text, text, boolean); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.send_binary(payload bytea, event text, topic text, private boolean DEFAULT true) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
  generated_id uuid;
BEGIN
  BEGIN
    generated_id := gen_random_uuid();

    EXECUTE format('SET LOCAL realtime.topic TO %L', topic);

    INSERT INTO realtime.messages (id, binary_payload, event, topic, private, extension)
    VALUES (generated_id, payload, event, topic, private, 'broadcast');
  EXCEPTION
    WHEN OTHERS THEN
      RAISE WARNING 'WarnSendingBroadcastMessage: %', SQLERRM;
  END;
END;
$$;


ALTER FUNCTION realtime.send_binary(payload bytea, event text, topic text, private boolean) OWNER TO supabase_realtime_admin;

--
-- Name: subscription_check_filters(); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.subscription_check_filters() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
declare
    col_names text[] = coalesce(
            array_agg(a.attname order by a.attnum),
            '{}'::text[]
        )
        from
            pg_catalog.pg_attribute a
        where
            a.attrelid = new.entity
            and a.attnum > 0
            and not a.attisdropped
            and pg_catalog.has_column_privilege(
                (new.claims ->> 'role'),
                a.attrelid,
                a.attnum,
                'SELECT'
            );
    filter realtime.user_defined_filter;
    col_type regtype;
    in_val jsonb;
    selected_col text;
begin
    for filter in select * from unnest(new.filters) loop
        if not filter.column_name = any(col_names) then
            raise exception 'invalid column for filter %', filter.column_name;
        end if;

        col_type = (
            select atttypid::regtype
            from pg_catalog.pg_attribute
            where attrelid = new.entity
                  and attname = filter.column_name
        );
        if col_type is null then
            raise exception 'failed to lookup type for column %', filter.column_name;
        end if;

        if filter.op = 'in'::realtime.equality_op then
            in_val = realtime.cast(filter.value, (col_type::text || '[]')::regtype);
            if coalesce(jsonb_array_length(in_val), 0) > 100 then
                raise exception 'too many values for `in` filter. Maximum 100';
            end if;
        elsif filter.op = 'is'::realtime.equality_op then
            -- `is` requires a keyword RHS rather than a typed literal
            if filter.value not in ('null', 'true', 'false', 'unknown') then
                raise exception 'invalid value for is filter: must be null, true, false, or unknown';
            end if;
            -- IS NULL works for any type, but IS TRUE/FALSE/UNKNOWN require a boolean
            -- operand. Reject the non-null keywords on non-boolean columns here so they
            -- don't abort apply_rls at WAL time.
            if filter.value <> 'null' and col_type <> 'boolean'::regtype then
                raise exception 'is % filter requires a boolean column, got %', filter.value, col_type::text;
            end if;
        elsif filter.op in ('like'::realtime.equality_op, 'ilike'::realtime.equality_op) then
            -- like/ilike apply the text pattern operator (~~); reject column types that
            -- have no such operator instead of failing at WAL time
            if not exists (
                select 1 from pg_catalog.pg_operator
                where oprname = '~~' and oprleft = col_type
            ) then
                raise exception 'operator % requires a text-compatible column type, got %', filter.op::text, col_type::text;
            end if;
        elsif filter.op in ('match'::realtime.equality_op, 'imatch'::realtime.equality_op) then
            -- match/imatch apply the regex operators ~ / ~*; reject column types that have
            -- no such operator (e.g. integer) instead of failing at WAL time, mirroring the
            -- like/ilike guard above.
            if not exists (
                select 1 from pg_catalog.pg_operator
                where oprname = case when filter.op = 'imatch'::realtime.equality_op then '~*' else '~' end
                  and oprleft = col_type
                  and oprright = col_type
                  and oprresult = 'boolean'::regtype
            ) then
                raise exception 'operator % requires a text-compatible column type, got %', filter.op::text, col_type::text;
            end if;
            -- validate the regex eagerly so a bad pattern is rejected here, not inside
            -- apply_rls where it would abort the WAL stream for the entity
            begin
                perform '' ~ filter.value;
            exception when others then
                raise exception 'invalid regular expression for % filter: %', filter.op::text, sqlerrm;
            end;
        else
            -- eq/neq/lt/lte/gt/gte: value must be coercable to the type
            perform realtime.cast(filter.value, col_type);
        end if;
    end loop;

    if new.selected_columns is not null then
        for selected_col in select * from unnest(new.selected_columns) loop
            if not selected_col = any(col_names) then
                raise exception 'invalid column for select %', selected_col;
            end if;
        end loop;
    end if;

    -- Apply consistent order to filters so the unique constraint can't be tricked by a
    -- different filter order. negate is part of the sort key.
    new.filters = coalesce(
        array_agg(f order by f.column_name, f.op, f.value, f.negate),
        '{}'
    ) from unnest(new.filters) f;

    new.selected_columns = (
        select array_agg(c order by c)
        from unnest(new.selected_columns) c
    );

    return new;
end;
$$;


ALTER FUNCTION realtime.subscription_check_filters() OWNER TO supabase_realtime_admin;

--
-- Name: to_regrole(text); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.to_regrole(role_name text) RETURNS regrole
    LANGUAGE sql IMMUTABLE
    AS $$ select role_name::regrole $$;


ALTER FUNCTION realtime.to_regrole(role_name text) OWNER TO supabase_realtime_admin;

--
-- Name: topic(); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.topic() RETURNS text
    LANGUAGE sql STABLE
    AS $$
select nullif(current_setting('realtime.topic', true), '')::text;
$$;


ALTER FUNCTION realtime.topic() OWNER TO supabase_realtime_admin;

--
-- Name: wal2json_escape_identifier(text); Type: FUNCTION; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE FUNCTION realtime.wal2json_escape_identifier(name text) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
  -- Prefix `\`, `,`, `.`, and any whitespace with `\`
  SELECT regexp_replace(name, '([\\,.[:space:]])', '\\\1', 'g')
$$;


ALTER FUNCTION realtime.wal2json_escape_identifier(name text) OWNER TO supabase_realtime_admin;

--
-- Name: allow_any_operation(text[]); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.allow_any_operation(expected_operations text[]) RETURNS boolean
    LANGUAGE sql STABLE
    AS $$
  WITH current_operation AS (
    SELECT storage.operation() AS raw_operation
  ),
  normalized AS (
    SELECT CASE
      WHEN raw_operation LIKE 'storage.%' THEN substr(raw_operation, 9)
      ELSE raw_operation
    END AS current_operation
    FROM current_operation
  )
  SELECT EXISTS (
    SELECT 1
    FROM normalized n
    CROSS JOIN LATERAL unnest(expected_operations) AS expected_operation
    WHERE expected_operation IS NOT NULL
      AND expected_operation <> ''
      AND n.current_operation = CASE
        WHEN expected_operation LIKE 'storage.%' THEN substr(expected_operation, 9)
        ELSE expected_operation
      END
  );
$$;


ALTER FUNCTION storage.allow_any_operation(expected_operations text[]) OWNER TO supabase_storage_admin;

--
-- Name: allow_only_operation(text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.allow_only_operation(expected_operation text) RETURNS boolean
    LANGUAGE sql STABLE
    AS $$
  WITH current_operation AS (
    SELECT storage.operation() AS raw_operation
  ),
  normalized AS (
    SELECT
      CASE
        WHEN raw_operation LIKE 'storage.%' THEN substr(raw_operation, 9)
        ELSE raw_operation
      END AS current_operation,
      CASE
        WHEN expected_operation LIKE 'storage.%' THEN substr(expected_operation, 9)
        ELSE expected_operation
      END AS requested_operation
    FROM current_operation
  )
  SELECT CASE
    WHEN requested_operation IS NULL OR requested_operation = '' THEN FALSE
    ELSE COALESCE(current_operation = requested_operation, FALSE)
  END
  FROM normalized;
$$;


ALTER FUNCTION storage.allow_only_operation(expected_operation text) OWNER TO supabase_storage_admin;

--
-- Name: can_insert_object(text, text, uuid, jsonb); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.can_insert_object(bucketid text, name text, owner uuid, metadata jsonb) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  INSERT INTO "storage"."objects" ("bucket_id", "name", "owner", "metadata") VALUES (bucketid, name, owner, metadata);
  -- hack to rollback the successful insert
  RAISE sqlstate 'PT200' using
  message = 'ROLLBACK',
  detail = 'rollback successful insert';
END
$$;


ALTER FUNCTION storage.can_insert_object(bucketid text, name text, owner uuid, metadata jsonb) OWNER TO supabase_storage_admin;

--
-- Name: enforce_bucket_name_length(); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.enforce_bucket_name_length() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
    if length(new.name) > 100 then
        raise exception 'bucket name "%" is too long (% characters). Max is 100.', new.name, length(new.name);
    end if;
    return new;
end;
$$;


ALTER FUNCTION storage.enforce_bucket_name_length() OWNER TO supabase_storage_admin;

--
-- Name: extension(text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.extension(name text) RETURNS text
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    _parts text[];
    _filename text;
BEGIN
    -- Split on "/" to get path segments
    SELECT string_to_array(name, '/') INTO _parts;
    -- Get the last path segment (the actual filename)
    SELECT _parts[array_length(_parts, 1)] INTO _filename;
    -- Extract extension: reverse, split on '.', then reverse again
    RETURN reverse(split_part(reverse(_filename), '.', 1));
END
$$;


ALTER FUNCTION storage.extension(name text) OWNER TO supabase_storage_admin;

--
-- Name: filename(text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.filename(name text) RETURNS text
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    _parts text[];
BEGIN
    SELECT string_to_array(name, '/') INTO _parts;
    RETURN _parts[array_length(_parts, 1)];
END
$$;


ALTER FUNCTION storage.filename(name text) OWNER TO supabase_storage_admin;

--
-- Name: foldername(text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.foldername(name text) RETURNS text[]
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    _parts text[];
BEGIN
    -- Split on "/" to get path segments
    SELECT string_to_array(name, '/') INTO _parts;
    -- Return everything except the last segment
    RETURN _parts[1 : array_length(_parts,1) - 1];
END
$$;


ALTER FUNCTION storage.foldername(name text) OWNER TO supabase_storage_admin;

--
-- Name: get_common_prefix(text, text, text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.get_common_prefix(p_key text, p_prefix text, p_delimiter text) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $$
SELECT CASE
    WHEN position(p_delimiter IN substring(p_key FROM length(p_prefix) + 1)) > 0
    THEN left(p_key, length(p_prefix) + position(p_delimiter IN substring(p_key FROM length(p_prefix) + 1)))
    ELSE NULL
END;
$$;


ALTER FUNCTION storage.get_common_prefix(p_key text, p_prefix text, p_delimiter text) OWNER TO supabase_storage_admin;

--
-- Name: get_size_by_bucket(); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.get_size_by_bucket() RETURNS TABLE(size bigint, bucket_id text)
    LANGUAGE plpgsql STABLE
    AS $$
BEGIN
    return query
        select sum((metadata->>'size')::bigint)::bigint as size, obj.bucket_id
        from "storage".objects as obj
        group by obj.bucket_id;
END
$$;


ALTER FUNCTION storage.get_size_by_bucket() OWNER TO supabase_storage_admin;

--
-- Name: list_multipart_uploads_with_delimiter(text, text, text, integer, text, text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.list_multipart_uploads_with_delimiter(bucket_id text, prefix_param text, delimiter_param text, max_keys integer DEFAULT 100, next_key_token text DEFAULT ''::text, next_upload_token text DEFAULT ''::text) RETURNS TABLE(key text, id text, created_at timestamp with time zone)
    LANGUAGE plpgsql
    AS $_$
BEGIN
    RETURN QUERY EXECUTE
        'SELECT DISTINCT ON(key COLLATE "C") * from (
            SELECT
                CASE
                    WHEN position($2 IN substring(key from length($1) + 1)) > 0 THEN
                        substring(key from 1 for length($1) + position($2 IN substring(key from length($1) + 1)))
                    ELSE
                        key
                END AS key, id, created_at
            FROM
                storage.s3_multipart_uploads
            WHERE
                bucket_id = $5 AND
                key ILIKE $1 || ''%'' AND
                CASE
                    WHEN $4 != '''' AND $6 = '''' THEN
                        CASE
                            WHEN position($2 IN substring(key from length($1) + 1)) > 0 THEN
                                substring(key from 1 for length($1) + position($2 IN substring(key from length($1) + 1))) COLLATE "C" > $4
                            ELSE
                                key COLLATE "C" > $4
                            END
                    ELSE
                        true
                END AND
                CASE
                    WHEN $6 != '''' THEN
                        id COLLATE "C" > $6
                    ELSE
                        true
                    END
            ORDER BY
                key COLLATE "C" ASC, created_at ASC) as e order by key COLLATE "C" LIMIT $3'
        USING prefix_param, delimiter_param, max_keys, next_key_token, bucket_id, next_upload_token;
END;
$_$;


ALTER FUNCTION storage.list_multipart_uploads_with_delimiter(bucket_id text, prefix_param text, delimiter_param text, max_keys integer, next_key_token text, next_upload_token text) OWNER TO supabase_storage_admin;

--
-- Name: list_objects_with_delimiter(text, text, text, integer, text, text, text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.list_objects_with_delimiter(_bucket_id text, prefix_param text, delimiter_param text, max_keys integer DEFAULT 100, start_after text DEFAULT ''::text, next_token text DEFAULT ''::text, sort_order text DEFAULT 'asc'::text) RETURNS TABLE(name text, id uuid, metadata jsonb, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone)
    LANGUAGE plpgsql STABLE
    AS $_$
DECLARE
    v_peek_name TEXT;
    v_current RECORD;
    v_common_prefix TEXT;

    -- Configuration
    v_is_asc BOOLEAN;
    v_prefix TEXT;
    v_start TEXT;
    v_upper_bound TEXT;
    v_file_batch_size INT;

    -- Seek state
    v_next_seek TEXT;
    v_count INT := 0;

    -- Dynamic SQL for batch query only
    v_batch_query TEXT;

BEGIN
    -- ========================================================================
    -- INITIALIZATION
    -- ========================================================================
    v_is_asc := lower(coalesce(sort_order, 'asc')) = 'asc';
    v_prefix := coalesce(prefix_param, '');
    v_start := CASE WHEN coalesce(next_token, '') <> '' THEN next_token ELSE coalesce(start_after, '') END;
    v_file_batch_size := LEAST(GREATEST(max_keys * 2, 100), 1000);

    -- Calculate upper bound for prefix filtering (bytewise, using COLLATE "C")
    IF v_prefix = '' THEN
        v_upper_bound := NULL;
    ELSIF right(v_prefix, 1) = delimiter_param THEN
        v_upper_bound := left(v_prefix, -1) || chr(ascii(delimiter_param) + 1);
    ELSE
        v_upper_bound := left(v_prefix, -1) || chr(ascii(right(v_prefix, 1)) + 1);
    END IF;

    -- Build batch query (dynamic SQL - called infrequently, amortized over many rows)
    IF v_is_asc THEN
        IF v_upper_bound IS NOT NULL THEN
            v_batch_query := 'SELECT o.name, o.id, o.updated_at, o.created_at, o.last_accessed_at, o.metadata ' ||
                'FROM storage.objects o WHERE o.bucket_id = $1 AND o.name COLLATE "C" >= $2 ' ||
                'AND o.name COLLATE "C" < $3 ORDER BY o.name COLLATE "C" ASC LIMIT $4';
        ELSE
            v_batch_query := 'SELECT o.name, o.id, o.updated_at, o.created_at, o.last_accessed_at, o.metadata ' ||
                'FROM storage.objects o WHERE o.bucket_id = $1 AND o.name COLLATE "C" >= $2 ' ||
                'ORDER BY o.name COLLATE "C" ASC LIMIT $4';
        END IF;
    ELSE
        IF v_upper_bound IS NOT NULL THEN
            v_batch_query := 'SELECT o.name, o.id, o.updated_at, o.created_at, o.last_accessed_at, o.metadata ' ||
                'FROM storage.objects o WHERE o.bucket_id = $1 AND o.name COLLATE "C" < $2 ' ||
                'AND o.name COLLATE "C" >= $3 ORDER BY o.name COLLATE "C" DESC LIMIT $4';
        ELSE
            v_batch_query := 'SELECT o.name, o.id, o.updated_at, o.created_at, o.last_accessed_at, o.metadata ' ||
                'FROM storage.objects o WHERE o.bucket_id = $1 AND o.name COLLATE "C" < $2 ' ||
                'ORDER BY o.name COLLATE "C" DESC LIMIT $4';
        END IF;
    END IF;

    -- ========================================================================
    -- SEEK INITIALIZATION: Determine starting position
    -- ========================================================================
    IF v_start = '' THEN
        IF v_is_asc THEN
            v_next_seek := v_prefix;
        ELSE
            -- DESC without cursor: find the last item in range
            IF v_upper_bound IS NOT NULL THEN
                SELECT o.name INTO v_next_seek FROM storage.objects o
                WHERE o.bucket_id = _bucket_id AND o.name COLLATE "C" >= v_prefix AND o.name COLLATE "C" < v_upper_bound
                ORDER BY o.name COLLATE "C" DESC LIMIT 1;
            ELSIF v_prefix <> '' THEN
                SELECT o.name INTO v_next_seek FROM storage.objects o
                WHERE o.bucket_id = _bucket_id AND o.name COLLATE "C" >= v_prefix
                ORDER BY o.name COLLATE "C" DESC LIMIT 1;
            ELSE
                SELECT o.name INTO v_next_seek FROM storage.objects o
                WHERE o.bucket_id = _bucket_id
                ORDER BY o.name COLLATE "C" DESC LIMIT 1;
            END IF;

            IF v_next_seek IS NOT NULL THEN
                v_next_seek := v_next_seek || delimiter_param;
            ELSE
                RETURN;
            END IF;
        END IF;
    ELSE
        -- Cursor provided: determine if it refers to a folder or leaf
        IF EXISTS (
            SELECT 1 FROM storage.objects o
            WHERE o.bucket_id = _bucket_id
              AND o.name COLLATE "C" LIKE v_start || delimiter_param || '%'
            LIMIT 1
        ) THEN
            -- Cursor refers to a folder
            IF v_is_asc THEN
                v_next_seek := v_start || chr(ascii(delimiter_param) + 1);
            ELSE
                v_next_seek := v_start || delimiter_param;
            END IF;
        ELSE
            -- Cursor refers to a leaf object
            IF v_is_asc THEN
                v_next_seek := v_start || delimiter_param;
            ELSE
                v_next_seek := v_start;
            END IF;
        END IF;
    END IF;

    -- ========================================================================
    -- MAIN LOOP: Hybrid peek-then-batch algorithm
    -- Uses STATIC SQL for peek (hot path) and DYNAMIC SQL for batch
    -- ========================================================================
    LOOP
        EXIT WHEN v_count >= max_keys;

        -- STEP 1: PEEK using STATIC SQL (plan cached, very fast)
        IF v_is_asc THEN
            IF v_upper_bound IS NOT NULL THEN
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = _bucket_id AND o.name COLLATE "C" >= v_next_seek AND o.name COLLATE "C" < v_upper_bound
                ORDER BY o.name COLLATE "C" ASC LIMIT 1;
            ELSE
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = _bucket_id AND o.name COLLATE "C" >= v_next_seek
                ORDER BY o.name COLLATE "C" ASC LIMIT 1;
            END IF;
        ELSE
            IF v_upper_bound IS NOT NULL THEN
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = _bucket_id AND o.name COLLATE "C" < v_next_seek AND o.name COLLATE "C" >= v_prefix
                ORDER BY o.name COLLATE "C" DESC LIMIT 1;
            ELSIF v_prefix <> '' THEN
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = _bucket_id AND o.name COLLATE "C" < v_next_seek AND o.name COLLATE "C" >= v_prefix
                ORDER BY o.name COLLATE "C" DESC LIMIT 1;
            ELSE
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = _bucket_id AND o.name COLLATE "C" < v_next_seek
                ORDER BY o.name COLLATE "C" DESC LIMIT 1;
            END IF;
        END IF;

        EXIT WHEN v_peek_name IS NULL;

        -- STEP 2: Check if this is a FOLDER or FILE
        v_common_prefix := storage.get_common_prefix(v_peek_name, v_prefix, delimiter_param);

        IF v_common_prefix IS NOT NULL THEN
            -- FOLDER: Emit and skip to next folder (no heap access needed)
            name := rtrim(v_common_prefix, delimiter_param);
            id := NULL;
            updated_at := NULL;
            created_at := NULL;
            last_accessed_at := NULL;
            metadata := NULL;
            RETURN NEXT;
            v_count := v_count + 1;

            -- Advance seek past the folder range
            IF v_is_asc THEN
                v_next_seek := left(v_common_prefix, -1) || chr(ascii(delimiter_param) + 1);
            ELSE
                v_next_seek := v_common_prefix;
            END IF;
        ELSE
            -- FILE: Batch fetch using DYNAMIC SQL (overhead amortized over many rows)
            -- For ASC: upper_bound is the exclusive upper limit (< condition)
            -- For DESC: prefix is the inclusive lower limit (>= condition)
            FOR v_current IN EXECUTE v_batch_query USING _bucket_id, v_next_seek,
                CASE WHEN v_is_asc THEN COALESCE(v_upper_bound, v_prefix) ELSE v_prefix END, v_file_batch_size
            LOOP
                v_common_prefix := storage.get_common_prefix(v_current.name, v_prefix, delimiter_param);

                IF v_common_prefix IS NOT NULL THEN
                    -- Hit a folder: exit batch, let peek handle it
                    v_next_seek := v_current.name;
                    EXIT;
                END IF;

                -- Emit file
                name := v_current.name;
                id := v_current.id;
                updated_at := v_current.updated_at;
                created_at := v_current.created_at;
                last_accessed_at := v_current.last_accessed_at;
                metadata := v_current.metadata;
                RETURN NEXT;
                v_count := v_count + 1;

                -- Advance seek past this file
                IF v_is_asc THEN
                    v_next_seek := v_current.name || delimiter_param;
                ELSE
                    v_next_seek := v_current.name;
                END IF;

                EXIT WHEN v_count >= max_keys;
            END LOOP;
        END IF;
    END LOOP;
END;
$_$;


ALTER FUNCTION storage.list_objects_with_delimiter(_bucket_id text, prefix_param text, delimiter_param text, max_keys integer, start_after text, next_token text, sort_order text) OWNER TO supabase_storage_admin;

--
-- Name: operation(); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.operation() RETURNS text
    LANGUAGE plpgsql STABLE
    AS $$
BEGIN
    RETURN current_setting('storage.operation', true);
END;
$$;


ALTER FUNCTION storage.operation() OWNER TO supabase_storage_admin;

--
-- Name: protect_delete(); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.protect_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Check if storage.allow_delete_query is set to 'true'
    IF COALESCE(current_setting('storage.allow_delete_query', true), 'false') != 'true' THEN
        RAISE EXCEPTION 'Direct deletion from storage tables is not allowed. Use the Storage API instead.'
            USING HINT = 'This prevents accidental data loss from orphaned objects.',
                  ERRCODE = '42501';
    END IF;
    RETURN NULL;
END;
$$;


ALTER FUNCTION storage.protect_delete() OWNER TO supabase_storage_admin;

--
-- Name: search(text, text, integer, integer, integer, text, text, text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.search(prefix text, bucketname text, limits integer DEFAULT 100, levels integer DEFAULT 1, offsets integer DEFAULT 0, search text DEFAULT ''::text, sortcolumn text DEFAULT 'name'::text, sortorder text DEFAULT 'asc'::text) RETURNS TABLE(name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql STABLE
    AS $_$
DECLARE
    v_peek_name TEXT;
    v_current RECORD;
    v_common_prefix TEXT;
    v_delimiter CONSTANT TEXT := '/';

    -- Configuration
    v_limit INT;
    v_prefix TEXT;
    v_prefix_lower TEXT;
    v_prefix_len INT;
    v_prefix_start INT;
    v_combined_levels INT;
    v_is_asc BOOLEAN;
    v_order_by TEXT;
    v_sort_order TEXT;
    v_upper_bound TEXT;
    v_file_batch_size INT;

    -- Dynamic SQL for batch query only
    v_batch_query TEXT;

    -- Seek state
    v_next_seek TEXT;
    v_count INT := 0;
    v_skipped INT := 0;
BEGIN
    -- ========================================================================
    -- INITIALIZATION
    -- ========================================================================
    v_limit := LEAST(coalesce(limits, 100), 1500);
    v_prefix := coalesce(prefix, '') || coalesce(search, '');
    v_prefix_lower := lower(v_prefix);
    v_prefix_len := length(coalesce(prefix, ''));
    v_prefix_start := coalesce(array_length(string_to_array(coalesce(prefix, ''), v_delimiter), 1), 1);
    v_combined_levels := coalesce(array_length(string_to_array(v_prefix, v_delimiter), 1), 1);
    v_is_asc := lower(coalesce(sortorder, 'asc')) = 'asc';
    v_file_batch_size := LEAST(GREATEST(v_limit * 2, 100), 1000);

    -- Validate sort column
    CASE lower(coalesce(sortcolumn, 'name'))
        WHEN 'name' THEN v_order_by := 'name';
        WHEN 'updated_at' THEN v_order_by := 'updated_at';
        WHEN 'created_at' THEN v_order_by := 'created_at';
        WHEN 'last_accessed_at' THEN v_order_by := 'last_accessed_at';
        ELSE v_order_by := 'name';
    END CASE;

    v_sort_order := CASE WHEN v_is_asc THEN 'asc' ELSE 'desc' END;

    -- ========================================================================
    -- NON-NAME SORTING: Use path_tokens approach
    -- ========================================================================
    IF v_order_by != 'name' THEN
        RETURN QUERY EXECUTE format(
            $sql$
            WITH folders AS (
                SELECT array_to_string(path_tokens[$1:$2], '/') AS folder
                FROM storage.objects
                WHERE objects.name ILIKE $3 || '%%'
                  AND bucket_id = $4
                  AND array_length(objects.path_tokens, 1) <> $2
                GROUP BY folder
                ORDER BY folder %s
            )
            (SELECT folder AS "name",
                   NULL::uuid AS id,
                   NULL::timestamptz AS updated_at,
                   NULL::timestamptz AS created_at,
                   NULL::timestamptz AS last_accessed_at,
                   NULL::jsonb AS metadata FROM folders)
            UNION ALL
            (SELECT array_to_string(path_tokens[$1:$2], '/') AS "name",
                   id, updated_at, created_at, last_accessed_at, metadata
             FROM storage.objects
             WHERE objects.name ILIKE $3 || '%%'
               AND bucket_id = $4
               AND array_length(objects.path_tokens, 1) = $2
             ORDER BY %I %s)
            LIMIT $5 OFFSET $6
            $sql$, v_sort_order, v_order_by, v_sort_order
        ) USING v_prefix_start, v_combined_levels, v_prefix, bucketname, v_limit, offsets;
        RETURN;
    END IF;

    -- ========================================================================
    -- NAME SORTING: Hybrid skip-scan with batch optimization
    -- ========================================================================

    -- Calculate upper bound for prefix filtering
    IF v_prefix_lower = '' THEN
        v_upper_bound := NULL;
    ELSIF right(v_prefix_lower, 1) = v_delimiter THEN
        v_upper_bound := left(v_prefix_lower, -1) || chr(ascii(v_delimiter) + 1);
    ELSE
        v_upper_bound := left(v_prefix_lower, -1) || chr(ascii(right(v_prefix_lower, 1)) + 1);
    END IF;

    -- Build batch query (dynamic SQL - called infrequently, amortized over many rows)
    IF v_is_asc THEN
        IF v_upper_bound IS NOT NULL THEN
            v_batch_query := 'SELECT o.name, o.id, o.updated_at, o.created_at, o.last_accessed_at, o.metadata ' ||
                'FROM storage.objects o WHERE o.bucket_id = $1 AND lower(o.name) COLLATE "C" >= $2 ' ||
                'AND lower(o.name) COLLATE "C" < $3 ORDER BY lower(o.name) COLLATE "C" ASC LIMIT $4';
        ELSE
            v_batch_query := 'SELECT o.name, o.id, o.updated_at, o.created_at, o.last_accessed_at, o.metadata ' ||
                'FROM storage.objects o WHERE o.bucket_id = $1 AND lower(o.name) COLLATE "C" >= $2 ' ||
                'ORDER BY lower(o.name) COLLATE "C" ASC LIMIT $4';
        END IF;
    ELSE
        IF v_upper_bound IS NOT NULL THEN
            v_batch_query := 'SELECT o.name, o.id, o.updated_at, o.created_at, o.last_accessed_at, o.metadata ' ||
                'FROM storage.objects o WHERE o.bucket_id = $1 AND lower(o.name) COLLATE "C" < $2 ' ||
                'AND lower(o.name) COLLATE "C" >= $3 ORDER BY lower(o.name) COLLATE "C" DESC LIMIT $4';
        ELSE
            v_batch_query := 'SELECT o.name, o.id, o.updated_at, o.created_at, o.last_accessed_at, o.metadata ' ||
                'FROM storage.objects o WHERE o.bucket_id = $1 AND lower(o.name) COLLATE "C" < $2 ' ||
                'ORDER BY lower(o.name) COLLATE "C" DESC LIMIT $4';
        END IF;
    END IF;

    -- Initialize seek position
    IF v_is_asc THEN
        v_next_seek := v_prefix_lower;
    ELSE
        -- DESC: find the last item in range first (static SQL)
        IF v_upper_bound IS NOT NULL THEN
            SELECT o.name INTO v_peek_name FROM storage.objects o
            WHERE o.bucket_id = bucketname AND lower(o.name) COLLATE "C" >= v_prefix_lower AND lower(o.name) COLLATE "C" < v_upper_bound
            ORDER BY lower(o.name) COLLATE "C" DESC LIMIT 1;
        ELSIF v_prefix_lower <> '' THEN
            SELECT o.name INTO v_peek_name FROM storage.objects o
            WHERE o.bucket_id = bucketname AND lower(o.name) COLLATE "C" >= v_prefix_lower
            ORDER BY lower(o.name) COLLATE "C" DESC LIMIT 1;
        ELSE
            SELECT o.name INTO v_peek_name FROM storage.objects o
            WHERE o.bucket_id = bucketname
            ORDER BY lower(o.name) COLLATE "C" DESC LIMIT 1;
        END IF;

        IF v_peek_name IS NOT NULL THEN
            v_next_seek := lower(v_peek_name) || v_delimiter;
        ELSE
            RETURN;
        END IF;
    END IF;

    -- ========================================================================
    -- MAIN LOOP: Hybrid peek-then-batch algorithm
    -- Uses STATIC SQL for peek (hot path) and DYNAMIC SQL for batch
    -- ========================================================================
    LOOP
        EXIT WHEN v_count >= v_limit;

        -- STEP 1: PEEK using STATIC SQL (plan cached, very fast)
        IF v_is_asc THEN
            IF v_upper_bound IS NOT NULL THEN
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = bucketname AND lower(o.name) COLLATE "C" >= v_next_seek AND lower(o.name) COLLATE "C" < v_upper_bound
                ORDER BY lower(o.name) COLLATE "C" ASC LIMIT 1;
            ELSE
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = bucketname AND lower(o.name) COLLATE "C" >= v_next_seek
                ORDER BY lower(o.name) COLLATE "C" ASC LIMIT 1;
            END IF;
        ELSE
            IF v_upper_bound IS NOT NULL THEN
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = bucketname AND lower(o.name) COLLATE "C" < v_next_seek AND lower(o.name) COLLATE "C" >= v_prefix_lower
                ORDER BY lower(o.name) COLLATE "C" DESC LIMIT 1;
            ELSIF v_prefix_lower <> '' THEN
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = bucketname AND lower(o.name) COLLATE "C" < v_next_seek AND lower(o.name) COLLATE "C" >= v_prefix_lower
                ORDER BY lower(o.name) COLLATE "C" DESC LIMIT 1;
            ELSE
                SELECT o.name INTO v_peek_name FROM storage.objects o
                WHERE o.bucket_id = bucketname AND lower(o.name) COLLATE "C" < v_next_seek
                ORDER BY lower(o.name) COLLATE "C" DESC LIMIT 1;
            END IF;
        END IF;

        EXIT WHEN v_peek_name IS NULL;

        -- STEP 2: Check if this is a FOLDER or FILE
        v_common_prefix := storage.get_common_prefix(lower(v_peek_name), v_prefix_lower, v_delimiter);

        IF v_common_prefix IS NOT NULL THEN
            -- FOLDER: Handle offset, emit if needed, skip to next folder
            IF v_skipped < offsets THEN
                v_skipped := v_skipped + 1;
            ELSE
                name := substring(rtrim(storage.get_common_prefix(v_peek_name, v_prefix, v_delimiter), v_delimiter) from v_prefix_len + 1);
                id := NULL;
                updated_at := NULL;
                created_at := NULL;
                last_accessed_at := NULL;
                metadata := NULL;
                RETURN NEXT;
                v_count := v_count + 1;
            END IF;

            -- Advance seek past the folder range
            IF v_is_asc THEN
                v_next_seek := lower(left(v_common_prefix, -1)) || chr(ascii(v_delimiter) + 1);
            ELSE
                v_next_seek := lower(v_common_prefix);
            END IF;
        ELSE
            -- FILE: Batch fetch using DYNAMIC SQL (overhead amortized over many rows)
            -- For ASC: upper_bound is the exclusive upper limit (< condition)
            -- For DESC: prefix_lower is the inclusive lower limit (>= condition)
            FOR v_current IN EXECUTE v_batch_query
                USING bucketname, v_next_seek,
                    CASE WHEN v_is_asc THEN COALESCE(v_upper_bound, v_prefix_lower) ELSE v_prefix_lower END, v_file_batch_size
            LOOP
                v_common_prefix := storage.get_common_prefix(lower(v_current.name), v_prefix_lower, v_delimiter);

                IF v_common_prefix IS NOT NULL THEN
                    -- Hit a folder: exit batch, let peek handle it
                    v_next_seek := lower(v_current.name);
                    EXIT;
                END IF;

                -- Handle offset skipping
                IF v_skipped < offsets THEN
                    v_skipped := v_skipped + 1;
                ELSE
                    -- Emit file
                    name := substring(v_current.name from v_prefix_len + 1);
                    id := v_current.id;
                    updated_at := v_current.updated_at;
                    created_at := v_current.created_at;
                    last_accessed_at := v_current.last_accessed_at;
                    metadata := v_current.metadata;
                    RETURN NEXT;
                    v_count := v_count + 1;
                END IF;

                -- Advance seek past this file
                IF v_is_asc THEN
                    v_next_seek := lower(v_current.name) || v_delimiter;
                ELSE
                    v_next_seek := lower(v_current.name);
                END IF;

                EXIT WHEN v_count >= v_limit;
            END LOOP;
        END IF;
    END LOOP;
END;
$_$;


ALTER FUNCTION storage.search(prefix text, bucketname text, limits integer, levels integer, offsets integer, search text, sortcolumn text, sortorder text) OWNER TO supabase_storage_admin;

--
-- Name: search_by_timestamp(text, text, integer, integer, text, text, text, text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.search_by_timestamp(p_prefix text, p_bucket_id text, p_limit integer, p_level integer, p_start_after text, p_sort_order text, p_sort_column text, p_sort_column_after text) RETURNS TABLE(key text, name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql STABLE
    AS $_$
DECLARE
    v_cursor_op text;
    v_query text;
    v_prefix text;
    v_sort_order text;
    v_sort_column text;
BEGIN
    v_prefix := coalesce(p_prefix, '');

    -- Defense-in-depth: this function is independently reachable and must
    -- not trust p_sort_order/p_sort_column to already be validated by a
    -- caller. Normalize to the same strict allow-list storage.search_v2
    -- uses before interpolating anything into dynamic SQL below.
    v_sort_order := lower(coalesce(p_sort_order, 'asc'));
    IF v_sort_order NOT IN ('asc', 'desc') THEN
        v_sort_order := 'asc';
    END IF;

    v_sort_column := lower(coalesce(p_sort_column, 'updated_at'));
    IF v_sort_column NOT IN ('updated_at', 'created_at') THEN
        v_sort_column := 'updated_at';
    END IF;

    IF v_sort_order = 'asc' THEN
        v_cursor_op := '>';
    ELSE
        v_cursor_op := '<';
    END IF;

    v_query := format($sql$
        WITH raw_objects AS (
            SELECT
                o.name AS obj_name,
                o.id AS obj_id,
                o.updated_at AS obj_updated_at,
                o.created_at AS obj_created_at,
                o.last_accessed_at AS obj_last_accessed_at,
                o.metadata AS obj_metadata,
                storage.get_common_prefix(o.name, $1, '/') AS common_prefix
            FROM storage.objects o
            WHERE o.bucket_id = $2
              AND o.name COLLATE "C" LIKE $1 || '%%'
        ),
        -- Aggregate common prefixes (folders)
        -- Both created_at and updated_at use MIN(obj_created_at) to match the old prefixes table behavior
        aggregated_prefixes AS (
            SELECT
                rtrim(common_prefix, '/') AS name,
                NULL::uuid AS id,
                MIN(obj_created_at) AS updated_at,
                MIN(obj_created_at) AS created_at,
                NULL::timestamptz AS last_accessed_at,
                NULL::jsonb AS metadata,
                TRUE AS is_prefix
            FROM raw_objects
            WHERE common_prefix IS NOT NULL
            GROUP BY common_prefix
        ),
        leaf_objects AS (
            SELECT
                obj_name AS name,
                obj_id AS id,
                obj_updated_at AS updated_at,
                obj_created_at AS created_at,
                obj_last_accessed_at AS last_accessed_at,
                obj_metadata AS metadata,
                FALSE AS is_prefix
            FROM raw_objects
            WHERE common_prefix IS NULL
        ),
        combined AS (
            SELECT * FROM aggregated_prefixes
            UNION ALL
            SELECT * FROM leaf_objects
        ),
        filtered AS (
            SELECT *
            FROM combined
            WHERE (
                $5 = ''
                OR ROW(
                    date_trunc('milliseconds', %I),
                    name COLLATE "C"
                ) %s ROW(
                    COALESCE(NULLIF($6, '')::timestamptz, 'epoch'::timestamptz),
                    $5
                )
            )
        )
        SELECT
            split_part(name, '/', $3) AS key,
            name,
            id,
            updated_at,
            created_at,
            last_accessed_at,
            metadata
        FROM filtered
        ORDER BY
            COALESCE(date_trunc('milliseconds', %I), 'epoch'::timestamptz) %s,
            name COLLATE "C" %s
        LIMIT $4
    $sql$,
        v_sort_column,
        v_cursor_op,
        v_sort_column,
        v_sort_order,
        v_sort_order
    );

    RETURN QUERY EXECUTE v_query
    USING v_prefix, p_bucket_id, p_level, p_limit, p_start_after, p_sort_column_after;
END;
$_$;


ALTER FUNCTION storage.search_by_timestamp(p_prefix text, p_bucket_id text, p_limit integer, p_level integer, p_start_after text, p_sort_order text, p_sort_column text, p_sort_column_after text) OWNER TO supabase_storage_admin;

--
-- Name: search_v2(text, text, integer, integer, text, text, text, text); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.search_v2(prefix text, bucket_name text, limits integer DEFAULT 100, levels integer DEFAULT 1, start_after text DEFAULT ''::text, sort_order text DEFAULT 'asc'::text, sort_column text DEFAULT 'name'::text, sort_column_after text DEFAULT ''::text) RETURNS TABLE(key text, name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql STABLE
    AS $$
DECLARE
    v_sort_col text;
    v_sort_ord text;
    v_limit int;
BEGIN
    -- Cap limit to maximum of 1500 records
    v_limit := LEAST(coalesce(limits, 100), 1500);

    -- Validate and normalize sort_order
    v_sort_ord := lower(coalesce(sort_order, 'asc'));
    IF v_sort_ord NOT IN ('asc', 'desc') THEN
        v_sort_ord := 'asc';
    END IF;

    -- Validate and normalize sort_column
    v_sort_col := lower(coalesce(sort_column, 'name'));
    IF v_sort_col NOT IN ('name', 'updated_at', 'created_at') THEN
        v_sort_col := 'name';
    END IF;

    -- Route to appropriate implementation
    IF v_sort_col = 'name' THEN
        -- Use list_objects_with_delimiter for name sorting (most efficient: O(k * log n))
        RETURN QUERY
        SELECT
            split_part(l.name, '/', levels) AS key,
            l.name AS name,
            l.id,
            l.updated_at,
            l.created_at,
            l.last_accessed_at,
            l.metadata
        FROM storage.list_objects_with_delimiter(
            bucket_name,
            coalesce(prefix, ''),
            '/',
            v_limit,
            start_after,
            '',
            v_sort_ord
        ) l;
    ELSE
        -- Use aggregation approach for timestamp sorting
        -- Not efficient for large datasets but supports correct pagination
        RETURN QUERY SELECT * FROM storage.search_by_timestamp(
            prefix, bucket_name, v_limit, levels, start_after,
            v_sort_ord, v_sort_col, sort_column_after
        );
    END IF;
END;
$$;


ALTER FUNCTION storage.search_v2(prefix text, bucket_name text, limits integer, levels integer, start_after text, sort_order text, sort_column text, sort_column_after text) OWNER TO supabase_storage_admin;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: storage; Owner: supabase_storage_admin
--

CREATE FUNCTION storage.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW; 
END;
$$;


ALTER FUNCTION storage.update_updated_at_column() OWNER TO supabase_storage_admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_log_entries; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.audit_log_entries (
    instance_id uuid,
    id uuid NOT NULL,
    payload json,
    created_at timestamp with time zone,
    ip_address character varying(64) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE auth.audit_log_entries OWNER TO supabase_auth_admin;

--
-- Name: TABLE audit_log_entries; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.audit_log_entries IS 'Auth: Audit trail for user actions.';


--
-- Name: custom_oauth_providers; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.custom_oauth_providers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    provider_type text NOT NULL,
    identifier text NOT NULL,
    name text NOT NULL,
    client_id text NOT NULL,
    client_secret text NOT NULL,
    acceptable_client_ids text[] DEFAULT '{}'::text[] NOT NULL,
    scopes text[] DEFAULT '{}'::text[] NOT NULL,
    pkce_enabled boolean DEFAULT true NOT NULL,
    attribute_mapping jsonb DEFAULT '{}'::jsonb NOT NULL,
    authorization_params jsonb DEFAULT '{}'::jsonb NOT NULL,
    enabled boolean DEFAULT true NOT NULL,
    email_optional boolean DEFAULT false NOT NULL,
    issuer text,
    discovery_url text,
    skip_nonce_check boolean DEFAULT false NOT NULL,
    cached_discovery jsonb,
    discovery_cached_at timestamp with time zone,
    authorization_url text,
    token_url text,
    userinfo_url text,
    jwks_uri text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    custom_claims_allowlist text[] DEFAULT '{}'::text[] NOT NULL,
    CONSTRAINT custom_oauth_providers_authorization_url_https CHECK (((authorization_url IS NULL) OR (authorization_url ~~ 'https://%'::text))),
    CONSTRAINT custom_oauth_providers_authorization_url_length CHECK (((authorization_url IS NULL) OR (char_length(authorization_url) <= 2048))),
    CONSTRAINT custom_oauth_providers_client_id_length CHECK (((char_length(client_id) >= 1) AND (char_length(client_id) <= 512))),
    CONSTRAINT custom_oauth_providers_discovery_url_length CHECK (((discovery_url IS NULL) OR (char_length(discovery_url) <= 2048))),
    CONSTRAINT custom_oauth_providers_identifier_format CHECK ((identifier ~ '^[a-z0-9][a-z0-9:-]{0,48}[a-z0-9]$'::text)),
    CONSTRAINT custom_oauth_providers_issuer_length CHECK (((issuer IS NULL) OR ((char_length(issuer) >= 1) AND (char_length(issuer) <= 2048)))),
    CONSTRAINT custom_oauth_providers_jwks_uri_https CHECK (((jwks_uri IS NULL) OR (jwks_uri ~~ 'https://%'::text))),
    CONSTRAINT custom_oauth_providers_jwks_uri_length CHECK (((jwks_uri IS NULL) OR (char_length(jwks_uri) <= 2048))),
    CONSTRAINT custom_oauth_providers_name_length CHECK (((char_length(name) >= 1) AND (char_length(name) <= 100))),
    CONSTRAINT custom_oauth_providers_oauth2_requires_endpoints CHECK (((provider_type <> 'oauth2'::text) OR ((authorization_url IS NOT NULL) AND (token_url IS NOT NULL) AND (userinfo_url IS NOT NULL)))),
    CONSTRAINT custom_oauth_providers_oidc_discovery_url_https CHECK (((provider_type <> 'oidc'::text) OR (discovery_url IS NULL) OR (discovery_url ~~ 'https://%'::text))),
    CONSTRAINT custom_oauth_providers_oidc_issuer_https CHECK (((provider_type <> 'oidc'::text) OR (issuer IS NULL) OR (issuer ~~ 'https://%'::text))),
    CONSTRAINT custom_oauth_providers_oidc_requires_issuer CHECK (((provider_type <> 'oidc'::text) OR (issuer IS NOT NULL))),
    CONSTRAINT custom_oauth_providers_provider_type_check CHECK ((provider_type = ANY (ARRAY['oauth2'::text, 'oidc'::text]))),
    CONSTRAINT custom_oauth_providers_token_url_https CHECK (((token_url IS NULL) OR (token_url ~~ 'https://%'::text))),
    CONSTRAINT custom_oauth_providers_token_url_length CHECK (((token_url IS NULL) OR (char_length(token_url) <= 2048))),
    CONSTRAINT custom_oauth_providers_userinfo_url_https CHECK (((userinfo_url IS NULL) OR (userinfo_url ~~ 'https://%'::text))),
    CONSTRAINT custom_oauth_providers_userinfo_url_length CHECK (((userinfo_url IS NULL) OR (char_length(userinfo_url) <= 2048)))
);


ALTER TABLE auth.custom_oauth_providers OWNER TO supabase_auth_admin;

--
-- Name: flow_state; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.flow_state (
    id uuid NOT NULL,
    user_id uuid,
    auth_code text,
    code_challenge_method auth.code_challenge_method,
    code_challenge text,
    provider_type text NOT NULL,
    provider_access_token text,
    provider_refresh_token text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    authentication_method text NOT NULL,
    auth_code_issued_at timestamp with time zone,
    invite_token text,
    referrer text,
    oauth_client_state_id uuid,
    linking_target_id uuid,
    email_optional boolean DEFAULT false NOT NULL
);


ALTER TABLE auth.flow_state OWNER TO supabase_auth_admin;

--
-- Name: TABLE flow_state; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.flow_state IS 'Stores metadata for all OAuth/SSO login flows';


--
-- Name: identities; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.identities (
    provider_id text NOT NULL,
    user_id uuid NOT NULL,
    identity_data jsonb NOT NULL,
    provider text NOT NULL,
    last_sign_in_at timestamp with time zone,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    email text GENERATED ALWAYS AS (lower((identity_data ->> 'email'::text))) STORED,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE auth.identities OWNER TO supabase_auth_admin;

--
-- Name: TABLE identities; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.identities IS 'Auth: Stores identities associated to a user.';


--
-- Name: COLUMN identities.email; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON COLUMN auth.identities.email IS 'Auth: Email is a generated column that references the optional email property in the identity_data';


--
-- Name: instances; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.instances (
    id uuid NOT NULL,
    uuid uuid,
    raw_base_config text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE auth.instances OWNER TO supabase_auth_admin;

--
-- Name: TABLE instances; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.instances IS 'Auth: Manages users across multiple sites.';


--
-- Name: mfa_amr_claims; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.mfa_amr_claims (
    session_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    authentication_method text NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE auth.mfa_amr_claims OWNER TO supabase_auth_admin;

--
-- Name: TABLE mfa_amr_claims; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.mfa_amr_claims IS 'auth: stores authenticator method reference claims for multi factor authentication';


--
-- Name: mfa_challenges; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.mfa_challenges (
    id uuid NOT NULL,
    factor_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    verified_at timestamp with time zone,
    ip_address inet NOT NULL,
    otp_code text,
    web_authn_session_data jsonb
);


ALTER TABLE auth.mfa_challenges OWNER TO supabase_auth_admin;

--
-- Name: TABLE mfa_challenges; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.mfa_challenges IS 'auth: stores metadata about challenge requests made';


--
-- Name: mfa_factors; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.mfa_factors (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    friendly_name text,
    factor_type auth.factor_type NOT NULL,
    status auth.factor_status NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    secret text,
    phone text,
    last_challenged_at timestamp with time zone,
    web_authn_credential jsonb,
    web_authn_aaguid uuid,
    last_webauthn_challenge_data jsonb
);


ALTER TABLE auth.mfa_factors OWNER TO supabase_auth_admin;

--
-- Name: TABLE mfa_factors; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.mfa_factors IS 'auth: stores metadata about factors';


--
-- Name: COLUMN mfa_factors.last_webauthn_challenge_data; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON COLUMN auth.mfa_factors.last_webauthn_challenge_data IS 'Stores the latest WebAuthn challenge data including attestation/assertion for customer verification';


--
-- Name: oauth_authorizations; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.oauth_authorizations (
    id uuid NOT NULL,
    authorization_id text NOT NULL,
    client_id uuid NOT NULL,
    user_id uuid,
    redirect_uri text NOT NULL,
    scope text NOT NULL,
    state text,
    resource text,
    code_challenge text,
    code_challenge_method auth.code_challenge_method,
    response_type auth.oauth_response_type DEFAULT 'code'::auth.oauth_response_type NOT NULL,
    status auth.oauth_authorization_status DEFAULT 'pending'::auth.oauth_authorization_status NOT NULL,
    authorization_code text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone DEFAULT (now() + '00:03:00'::interval) NOT NULL,
    approved_at timestamp with time zone,
    nonce text,
    CONSTRAINT oauth_authorizations_authorization_code_length CHECK ((char_length(authorization_code) <= 255)),
    CONSTRAINT oauth_authorizations_code_challenge_length CHECK ((char_length(code_challenge) <= 128)),
    CONSTRAINT oauth_authorizations_expires_at_future CHECK ((expires_at > created_at)),
    CONSTRAINT oauth_authorizations_nonce_length CHECK ((char_length(nonce) <= 255)),
    CONSTRAINT oauth_authorizations_redirect_uri_length CHECK ((char_length(redirect_uri) <= 2048)),
    CONSTRAINT oauth_authorizations_resource_length CHECK ((char_length(resource) <= 2048)),
    CONSTRAINT oauth_authorizations_scope_length CHECK ((char_length(scope) <= 4096)),
    CONSTRAINT oauth_authorizations_state_length CHECK ((char_length(state) <= 4096))
);


ALTER TABLE auth.oauth_authorizations OWNER TO supabase_auth_admin;

--
-- Name: oauth_client_states; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.oauth_client_states (
    id uuid NOT NULL,
    provider_type text NOT NULL,
    code_verifier text,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE auth.oauth_client_states OWNER TO supabase_auth_admin;

--
-- Name: TABLE oauth_client_states; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.oauth_client_states IS 'Stores OAuth states for third-party provider authentication flows where Supabase acts as the OAuth client.';


--
-- Name: oauth_clients; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.oauth_clients (
    id uuid NOT NULL,
    client_secret_hash text,
    registration_type auth.oauth_registration_type NOT NULL,
    redirect_uris text NOT NULL,
    grant_types text NOT NULL,
    client_name text,
    client_uri text,
    logo_uri text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    client_type auth.oauth_client_type DEFAULT 'confidential'::auth.oauth_client_type NOT NULL,
    token_endpoint_auth_method text NOT NULL,
    CONSTRAINT oauth_clients_client_name_length CHECK ((char_length(client_name) <= 1024)),
    CONSTRAINT oauth_clients_client_uri_length CHECK ((char_length(client_uri) <= 2048)),
    CONSTRAINT oauth_clients_logo_uri_length CHECK ((char_length(logo_uri) <= 2048)),
    CONSTRAINT oauth_clients_token_endpoint_auth_method_check CHECK ((token_endpoint_auth_method = ANY (ARRAY['client_secret_basic'::text, 'client_secret_post'::text, 'none'::text])))
);


ALTER TABLE auth.oauth_clients OWNER TO supabase_auth_admin;

--
-- Name: oauth_consents; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.oauth_consents (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    client_id uuid NOT NULL,
    scopes text NOT NULL,
    granted_at timestamp with time zone DEFAULT now() NOT NULL,
    revoked_at timestamp with time zone,
    CONSTRAINT oauth_consents_revoked_after_granted CHECK (((revoked_at IS NULL) OR (revoked_at >= granted_at))),
    CONSTRAINT oauth_consents_scopes_length CHECK ((char_length(scopes) <= 2048)),
    CONSTRAINT oauth_consents_scopes_not_empty CHECK ((char_length(TRIM(BOTH FROM scopes)) > 0))
);


ALTER TABLE auth.oauth_consents OWNER TO supabase_auth_admin;

--
-- Name: one_time_tokens; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.one_time_tokens (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    token_type auth.one_time_token_type NOT NULL,
    token_hash text NOT NULL,
    relates_to text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT one_time_tokens_token_hash_check CHECK ((char_length(token_hash) > 0))
);


ALTER TABLE auth.one_time_tokens OWNER TO supabase_auth_admin;

--
-- Name: refresh_tokens; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.refresh_tokens (
    instance_id uuid,
    id bigint NOT NULL,
    token character varying(255),
    user_id character varying(255),
    revoked boolean,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    parent character varying(255),
    session_id uuid
);


ALTER TABLE auth.refresh_tokens OWNER TO supabase_auth_admin;

--
-- Name: TABLE refresh_tokens; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.refresh_tokens IS 'Auth: Store of tokens used to refresh JWT tokens once they expire.';


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: auth; Owner: supabase_auth_admin
--

CREATE SEQUENCE auth.refresh_tokens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.refresh_tokens_id_seq OWNER TO supabase_auth_admin;

--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: supabase_auth_admin
--

ALTER SEQUENCE auth.refresh_tokens_id_seq OWNED BY auth.refresh_tokens.id;


--
-- Name: saml_providers; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.saml_providers (
    id uuid NOT NULL,
    sso_provider_id uuid NOT NULL,
    entity_id text NOT NULL,
    metadata_xml text NOT NULL,
    metadata_url text,
    attribute_mapping jsonb,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    name_id_format text,
    CONSTRAINT "entity_id not empty" CHECK ((char_length(entity_id) > 0)),
    CONSTRAINT "metadata_url not empty" CHECK (((metadata_url = NULL::text) OR (char_length(metadata_url) > 0))),
    CONSTRAINT "metadata_xml not empty" CHECK ((char_length(metadata_xml) > 0))
);


ALTER TABLE auth.saml_providers OWNER TO supabase_auth_admin;

--
-- Name: TABLE saml_providers; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.saml_providers IS 'Auth: Manages SAML Identity Provider connections.';


--
-- Name: saml_relay_states; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.saml_relay_states (
    id uuid NOT NULL,
    sso_provider_id uuid NOT NULL,
    request_id text NOT NULL,
    for_email text,
    redirect_to text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    flow_state_id uuid,
    CONSTRAINT "request_id not empty" CHECK ((char_length(request_id) > 0))
);


ALTER TABLE auth.saml_relay_states OWNER TO supabase_auth_admin;

--
-- Name: TABLE saml_relay_states; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.saml_relay_states IS 'Auth: Contains SAML Relay State information for each Service Provider initiated login.';


--
-- Name: schema_migrations; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.schema_migrations (
    version character varying(255) NOT NULL
);


ALTER TABLE auth.schema_migrations OWNER TO supabase_auth_admin;

--
-- Name: TABLE schema_migrations; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.schema_migrations IS 'Auth: Manages updates to the auth system.';


--
-- Name: sessions; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.sessions (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    factor_id uuid,
    aal auth.aal_level,
    not_after timestamp with time zone,
    refreshed_at timestamp without time zone,
    user_agent text,
    ip inet,
    tag text,
    oauth_client_id uuid,
    refresh_token_hmac_key text,
    refresh_token_counter bigint,
    scopes text,
    CONSTRAINT sessions_scopes_length CHECK ((char_length(scopes) <= 4096))
);


ALTER TABLE auth.sessions OWNER TO supabase_auth_admin;

--
-- Name: TABLE sessions; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.sessions IS 'Auth: Stores session data associated to a user.';


--
-- Name: COLUMN sessions.not_after; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON COLUMN auth.sessions.not_after IS 'Auth: Not after is a nullable column that contains a timestamp after which the session should be regarded as expired.';


--
-- Name: COLUMN sessions.refresh_token_hmac_key; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON COLUMN auth.sessions.refresh_token_hmac_key IS 'Holds a HMAC-SHA256 key used to sign refresh tokens for this session.';


--
-- Name: COLUMN sessions.refresh_token_counter; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON COLUMN auth.sessions.refresh_token_counter IS 'Holds the ID (counter) of the last issued refresh token.';


--
-- Name: sso_domains; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.sso_domains (
    id uuid NOT NULL,
    sso_provider_id uuid NOT NULL,
    domain text NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    CONSTRAINT "domain not empty" CHECK ((char_length(domain) > 0))
);


ALTER TABLE auth.sso_domains OWNER TO supabase_auth_admin;

--
-- Name: TABLE sso_domains; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.sso_domains IS 'Auth: Manages SSO email address domain mapping to an SSO Identity Provider.';


--
-- Name: sso_providers; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.sso_providers (
    id uuid NOT NULL,
    resource_id text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    disabled boolean,
    CONSTRAINT "resource_id not empty" CHECK (((resource_id = NULL::text) OR (char_length(resource_id) > 0)))
);


ALTER TABLE auth.sso_providers OWNER TO supabase_auth_admin;

--
-- Name: TABLE sso_providers; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.sso_providers IS 'Auth: Manages SSO identity provider information; see saml_providers for SAML.';


--
-- Name: COLUMN sso_providers.resource_id; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON COLUMN auth.sso_providers.resource_id IS 'Auth: Uniquely identifies a SSO provider according to a user-chosen resource ID (case insensitive), useful in infrastructure as code.';


--
-- Name: users; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.users (
    instance_id uuid,
    id uuid NOT NULL,
    aud character varying(255),
    role character varying(255),
    email character varying(255),
    encrypted_password character varying(255),
    email_confirmed_at timestamp with time zone,
    invited_at timestamp with time zone,
    confirmation_token character varying(255),
    confirmation_sent_at timestamp with time zone,
    recovery_token character varying(255),
    recovery_sent_at timestamp with time zone,
    email_change_token_new character varying(255),
    email_change character varying(255),
    email_change_sent_at timestamp with time zone,
    last_sign_in_at timestamp with time zone,
    raw_app_meta_data jsonb,
    raw_user_meta_data jsonb,
    is_super_admin boolean,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    phone text DEFAULT NULL::character varying,
    phone_confirmed_at timestamp with time zone,
    phone_change text DEFAULT ''::character varying,
    phone_change_token character varying(255) DEFAULT ''::character varying,
    phone_change_sent_at timestamp with time zone,
    confirmed_at timestamp with time zone GENERATED ALWAYS AS (LEAST(email_confirmed_at, phone_confirmed_at)) STORED,
    email_change_token_current character varying(255) DEFAULT ''::character varying,
    email_change_confirm_status smallint DEFAULT 0,
    banned_until timestamp with time zone,
    reauthentication_token character varying(255) DEFAULT ''::character varying,
    reauthentication_sent_at timestamp with time zone,
    is_sso_user boolean DEFAULT false NOT NULL,
    deleted_at timestamp with time zone,
    is_anonymous boolean DEFAULT false NOT NULL,
    CONSTRAINT users_email_change_confirm_status_check CHECK (((email_change_confirm_status >= 0) AND (email_change_confirm_status <= 2)))
);


ALTER TABLE auth.users OWNER TO supabase_auth_admin;

--
-- Name: TABLE users; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON TABLE auth.users IS 'Auth: Stores user login data within a secure schema.';


--
-- Name: COLUMN users.is_sso_user; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON COLUMN auth.users.is_sso_user IS 'Auth: Set this column to true when the account comes from SSO. These accounts can have duplicate emails.';


--
-- Name: webauthn_challenges; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.webauthn_challenges (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    challenge_type text NOT NULL,
    session_data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    CONSTRAINT webauthn_challenges_challenge_type_check CHECK ((challenge_type = ANY (ARRAY['signup'::text, 'registration'::text, 'authentication'::text])))
);


ALTER TABLE auth.webauthn_challenges OWNER TO supabase_auth_admin;

--
-- Name: webauthn_credentials; Type: TABLE; Schema: auth; Owner: supabase_auth_admin
--

CREATE TABLE auth.webauthn_credentials (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    credential_id bytea NOT NULL,
    public_key bytea NOT NULL,
    attestation_type text DEFAULT ''::text NOT NULL,
    aaguid uuid,
    sign_count bigint DEFAULT 0 NOT NULL,
    transports jsonb DEFAULT '[]'::jsonb NOT NULL,
    backup_eligible boolean DEFAULT false NOT NULL,
    backed_up boolean DEFAULT false NOT NULL,
    friendly_name text DEFAULT ''::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    last_used_at timestamp with time zone
);


ALTER TABLE auth.webauthn_credentials OWNER TO supabase_auth_admin;

--
-- Name: sec_8k_filings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sec_8k_filings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    security_id uuid NOT NULL,
    accession_number text NOT NULL,
    filing_date date,
    item_codes text,
    primary_document_url text,
    source text DEFAULT 'SEC'::text,
    promoted_to_event boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.sec_8k_filings OWNER TO postgres;

--
-- Name: securities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.securities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id uuid NOT NULL,
    ticker text NOT NULL,
    exchange text NOT NULL,
    security_type text NOT NULL,
    currency text NOT NULL,
    sector text
);


ALTER TABLE public.securities OWNER TO postgres;

--
-- Name: TABLE securities; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.securities IS 'Tradable financial instruments associated with entities and used for market price tracking.';


--
-- Name: candidate_8k_events; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.candidate_8k_events WITH (security_invoker='true') AS
 SELECT s.ticker,
    f.filing_date,
    f.item_codes,
    f.accession_number,
    f.primary_document_url,
    f.promoted_to_event,
        CASE
            WHEN (f.item_codes ~~ '%5.02%'::text) THEN 'Officer/Director departure or appointment'::text
            WHEN (f.item_codes ~~ '%1.01%'::text) THEN 'Material definitive agreement'::text
            WHEN (f.item_codes ~~ '%2.01%'::text) THEN 'Completion of acquisition/disposition'::text
            WHEN (f.item_codes ~~ '%2.05%'::text) THEN 'Costs associated with exit/disposal (restructuring/layoffs)'::text
            WHEN (f.item_codes ~~ '%2.06%'::text) THEN 'Material impairment'::text
            WHEN (f.item_codes ~~ '%4.01%'::text) THEN 'Auditor change'::text
            WHEN (f.item_codes ~~ '%4.02%'::text) THEN 'Non-reliance on previous financials (restatement)'::text
            WHEN (f.item_codes ~~ '%1.02%'::text) THEN 'Termination of material agreement'::text
            WHEN (f.item_codes ~~ '%1.05%'::text) THEN 'Material cybersecurity incident'::text
            WHEN (f.item_codes ~~ '%3.01%'::text) THEN 'Notice of delisting/non-compliance'::text
            WHEN (f.item_codes ~~ '%8.01%'::text) THEN 'Other events (needs manual review — mixed signal)'::text
            ELSE 'Other high-signal code'::text
        END AS item_code_label
   FROM (public.sec_8k_filings f
     JOIN public.securities s ON ((s.id = f.security_id)))
  WHERE (f.item_codes ~ '(5\.02|1\.01|2\.01|2\.05|2\.06|4\.01|4\.02|1\.02|1\.05|3\.01|8\.01)'::text)
  ORDER BY s.ticker, f.filing_date;


ALTER VIEW public.candidate_8k_events OWNER TO postgres;

--
-- Name: candidate_8k_events_legacy; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.candidate_8k_events_legacy WITH (security_invoker='true') AS
 SELECT s.ticker,
    f.filing_date,
    f.item_codes,
    f.accession_number,
    f.primary_document_url,
    f.promoted_to_event,
        CASE
            WHEN (f.item_codes ~ '(^|,)1(,|$)'::text) THEN 'Changes in Control of Registrant (legacy item 1)'::text
            WHEN (f.item_codes ~ '(^|,)2(,|$)'::text) THEN 'Acquisition or Disposition of Assets (legacy item 2)'::text
            WHEN (f.item_codes ~ '(^|,)4(,|$)'::text) THEN 'Changes in Certifying Accountant (legacy item 4)'::text
            WHEN (f.item_codes ~ '(^|,)5(,|$)'::text) THEN 'Other Events -- needs manual review, mixed signal, may include leadership changes (legacy item 5)'::text
            ELSE 'Other legacy high-signal code'::text
        END AS item_code_label
   FROM (public.sec_8k_filings f
     JOIN public.securities s ON ((s.id = f.security_id)))
  WHERE ((f.filing_date < '2004-08-01'::date) AND (f.item_codes ~ '(^|,)(1|2|4|5)(,|$)'::text))
  ORDER BY s.ticker, f.filing_date;


ALTER VIEW public.candidate_8k_events_legacy OWNER TO postgres;

--
-- Name: financial_growth_classified; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.financial_growth_classified (
    security_id uuid,
    ticker text,
    period_type text,
    fiscal_year integer,
    fiscal_quarter integer,
    period_end date,
    net_income_yoy_growth numeric,
    net_income_growth_type text,
    net_income_growth_label text,
    fcf_yoy_growth numeric,
    fcf_growth_type text,
    fcf_growth_label text,
    revenue_yoy_growth numeric,
    revenue_growth_type text,
    calculated_at timestamp with time zone
);


ALTER TABLE public.financial_growth_classified OWNER TO postgres;

--
-- Name: financial_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.financial_metrics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    financial_statement_id uuid,
    security_id uuid NOT NULL,
    period_type text NOT NULL,
    period_end date NOT NULL,
    fiscal_year integer NOT NULL,
    fiscal_quarter integer,
    revenue_growth numeric,
    revenue_yoy_growth numeric,
    gross_margin numeric,
    operating_margin numeric,
    net_margin numeric,
    net_income_growth numeric,
    net_income_yoy_growth numeric,
    fcf_margin numeric,
    fcf_growth numeric,
    fcf_yoy_growth numeric,
    operating_cash_flow_margin numeric,
    capex_revenue_ratio numeric,
    calculated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT financial_metrics_period_type_check CHECK ((period_type = ANY (ARRAY['annual'::text, 'quarterly'::text])))
);


ALTER TABLE public.financial_metrics OWNER TO postgres;

--
-- Name: financial_statements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.financial_statements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    security_id uuid NOT NULL,
    statement_type text NOT NULL,
    period_type text NOT NULL,
    period_end date NOT NULL,
    fiscal_year integer,
    fiscal_quarter integer,
    filed_date date,
    revenue numeric,
    gross_profit numeric,
    operating_income numeric,
    net_income numeric,
    eps_basic numeric,
    eps_diluted numeric,
    total_assets numeric,
    total_liabilities numeric,
    total_equity numeric,
    cash_and_equivalents numeric,
    operating_cash_flow numeric,
    capital_expenditures numeric,
    free_cash_flow numeric,
    source text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.financial_statements OWNER TO postgres;

--
-- Name: market_prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_prices (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    security_id uuid NOT NULL,
    price_date date NOT NULL,
    open numeric NOT NULL,
    high numeric NOT NULL,
    low numeric NOT NULL,
    close numeric NOT NULL,
    adjusted_close numeric NOT NULL,
    volume bigint NOT NULL
);


ALTER TABLE public.market_prices OWNER TO postgres;

--
-- Name: TABLE market_prices; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.market_prices IS 'Historical daily market data for tradable securities.';


--
-- Name: sec_filings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sec_filings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    security_id uuid NOT NULL,
    accession_number text NOT NULL,
    form_type text NOT NULL,
    filing_date date NOT NULL,
    period_end date,
    fiscal_year integer,
    fiscal_quarter integer,
    filing_url text,
    source text DEFAULT 'SEC'::text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.sec_filings OWNER TO postgres;

--
-- Name: financial_market_reactions; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.financial_market_reactions WITH (security_invoker='true') AS
 SELECT fs.id AS financial_statement_id,
    fs.security_id,
    s.ticker,
    fs.period_end,
    COALESCE(sf.filing_date, fs.filed_date) AS filed_date,
    fm.period_type,
    fm.fiscal_year,
    fm.fiscal_quarter,
    fm.revenue_growth,
    fm.revenue_yoy_growth,
    fm.net_income_yoy_growth,
    fm.gross_margin,
    fm.operating_margin,
    fm.net_margin,
    fm.fcf_margin,
    fm.fcf_yoy_growth,
    fm.operating_cash_flow_margin,
    fm.capex_revenue_ratio,
    prior_price.price_date AS prior_price_date,
    prior_price.close AS prior_close,
    event_price.price_date AS event_price_date,
    event_price.open AS event_open,
    event_price.close AS event_close,
    day_1.price_date AS day_1_date,
    day_1.close AS day_1_close,
    day_5.price_date AS day_5_date,
    day_5.close AS day_5_close,
    day_20.price_date AS day_20_date,
    day_20.close AS day_20_close,
        CASE
            WHEN ((prior_price.close IS NOT NULL) AND (event_price.close IS NOT NULL)) THEN ((event_price.close / prior_price.close) - (1)::numeric)
            ELSE NULL::numeric
        END AS filing_day_return,
        CASE
            WHEN ((event_price.close IS NOT NULL) AND (day_1.close IS NOT NULL)) THEN ((day_1.close / event_price.close) - (1)::numeric)
            ELSE NULL::numeric
        END AS return_1d,
        CASE
            WHEN ((event_price.close IS NOT NULL) AND (day_5.close IS NOT NULL)) THEN ((day_5.close / event_price.close) - (1)::numeric)
            ELSE NULL::numeric
        END AS return_5d,
        CASE
            WHEN ((event_price.close IS NOT NULL) AND (day_20.close IS NOT NULL)) THEN ((day_20.close / event_price.close) - (1)::numeric)
            ELSE NULL::numeric
        END AS return_20d,
    spy_prior.close AS spy_prior_close,
    spy_event.close AS spy_event_close,
    spy_day1.close AS spy_day1_close,
    spy_day5.close AS spy_day5_close,
    spy_day20.close AS spy_day20_close,
        CASE
            WHEN ((spy_prior.close IS NOT NULL) AND (spy_event.close IS NOT NULL)) THEN ((spy_event.close / spy_prior.close) - (1)::numeric)
            ELSE NULL::numeric
        END AS spy_filing_day_return,
        CASE
            WHEN ((spy_event.close IS NOT NULL) AND (spy_day1.close IS NOT NULL)) THEN ((spy_day1.close / spy_event.close) - (1)::numeric)
            ELSE NULL::numeric
        END AS spy_return_1d,
        CASE
            WHEN ((spy_event.close IS NOT NULL) AND (spy_day5.close IS NOT NULL)) THEN ((spy_day5.close / spy_event.close) - (1)::numeric)
            ELSE NULL::numeric
        END AS spy_return_5d,
        CASE
            WHEN ((spy_event.close IS NOT NULL) AND (spy_day20.close IS NOT NULL)) THEN ((spy_day20.close / spy_event.close) - (1)::numeric)
            ELSE NULL::numeric
        END AS spy_return_20d,
        CASE
            WHEN ((prior_price.close IS NOT NULL) AND (event_price.close IS NOT NULL) AND (spy_prior.close IS NOT NULL) AND (spy_event.close IS NOT NULL)) THEN (((event_price.close / prior_price.close) - (1)::numeric) - ((spy_event.close / spy_prior.close) - (1)::numeric))
            ELSE NULL::numeric
        END AS abnormal_filing_day_return,
        CASE
            WHEN ((event_price.close IS NOT NULL) AND (day_1.close IS NOT NULL) AND (spy_event.close IS NOT NULL) AND (spy_day1.close IS NOT NULL)) THEN (((day_1.close / event_price.close) - (1)::numeric) - ((spy_day1.close / spy_event.close) - (1)::numeric))
            ELSE NULL::numeric
        END AS abnormal_return_1d,
        CASE
            WHEN ((event_price.close IS NOT NULL) AND (day_5.close IS NOT NULL) AND (spy_event.close IS NOT NULL) AND (spy_day5.close IS NOT NULL)) THEN (((day_5.close / event_price.close) - (1)::numeric) - ((spy_day5.close / spy_event.close) - (1)::numeric))
            ELSE NULL::numeric
        END AS abnormal_return_5d,
        CASE
            WHEN ((event_price.close IS NOT NULL) AND (day_20.close IS NOT NULL) AND (spy_event.close IS NOT NULL) AND (spy_day20.close IS NOT NULL)) THEN (((day_20.close / event_price.close) - (1)::numeric) - ((spy_day20.close / spy_event.close) - (1)::numeric))
            ELSE NULL::numeric
        END AS abnormal_return_20d
   FROM (((((((((((((public.financial_statements fs
     JOIN public.securities s ON ((s.id = fs.security_id)))
     LEFT JOIN public.financial_metrics fm ON (((fm.security_id = fs.security_id) AND (fm.period_end = fs.period_end) AND (fm.period_type = fs.period_type))))
     LEFT JOIN LATERAL ( SELECT sec.filing_date
           FROM public.sec_filings sec
          WHERE ((sec.security_id = fs.security_id) AND (sec.period_end = fs.period_end) AND (sec.form_type =
                CASE
                    WHEN (fs.period_type = 'annual'::text) THEN '10-K'::text
                    WHEN (fs.fiscal_quarter = 4) THEN '10-K'::text
                    ELSE '10-Q'::text
                END))
          ORDER BY sec.filing_date
         LIMIT 1) sf ON (true))
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = fs.security_id) AND (mp.price_date < COALESCE(sf.filing_date, fs.filed_date)))
          ORDER BY mp.price_date DESC
         LIMIT 1) prior_price ON (true))
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.open,
            mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = fs.security_id) AND (mp.price_date > COALESCE(sf.filing_date, fs.filed_date)))
          ORDER BY mp.price_date
         LIMIT 1) event_price ON (true))
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = fs.security_id) AND (mp.price_date > event_price.price_date))
          ORDER BY mp.price_date
         LIMIT 1) day_1 ON (true))
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = fs.security_id) AND (mp.price_date > event_price.price_date))
          ORDER BY mp.price_date
         OFFSET 4
         LIMIT 1) day_5 ON (true))
     LEFT JOIN LATERAL ( SELECT mp.price_date,
            mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = fs.security_id) AND (mp.price_date > event_price.price_date))
          ORDER BY mp.price_date
         OFFSET 19
         LIMIT 1) day_20 ON (true))
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = prior_price.price_date))
         LIMIT 1) spy_prior ON (true))
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = event_price.price_date))
         LIMIT 1) spy_event ON (true))
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = day_1.price_date))
         LIMIT 1) spy_day1 ON (true))
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = day_5.price_date))
         LIMIT 1) spy_day5 ON (true))
     LEFT JOIN LATERAL ( SELECT mp.close
           FROM public.market_prices mp
          WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = day_20.price_date))
         LIMIT 1) spy_day20 ON (true));


ALTER VIEW public.financial_market_reactions OWNER TO postgres;

--
-- Name: candidate_financial_events; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.candidate_financial_events WITH (security_invoker='true') AS
 WITH company_baseline AS (
         SELECT financial_growth_classified.security_id,
            financial_growth_classified.period_type,
            percentile_cont((0.5)::double precision) WITHIN GROUP (ORDER BY ((abs(financial_growth_classified.net_income_yoy_growth))::double precision)) AS median_abs_growth
           FROM public.financial_growth_classified
          WHERE ((financial_growth_classified.net_income_growth_type = 'normal'::text) AND (financial_growth_classified.net_income_yoy_growth IS NOT NULL))
          GROUP BY financial_growth_classified.security_id, financial_growth_classified.period_type
        )
 SELECT gc.ticker,
    gc.period_type,
    gc.fiscal_year,
    gc.fiscal_quarter,
    gc.period_end,
    mr.filed_date,
    gc.net_income_yoy_growth,
    gc.net_income_growth_type,
    gc.net_income_growth_label,
    gc.revenue_yoy_growth,
    gc.fcf_yoy_growth,
    mr.prior_close,
    mr.event_open,
    mr.event_close,
    mr.day_5_close,
    mr.day_20_close,
    mr.filing_day_return,
    mr.return_5d,
    mr.return_20d,
    cb.median_abs_growth AS company_typical_swing,
    GREATEST((cb.median_abs_growth * (3)::double precision), (0.35)::double precision) AS relative_threshold_used,
        CASE
            WHEN (gc.net_income_growth_type = ANY (ARRAY['turned_positive'::text, 'turned_negative'::text])) THEN 'sign_transition'::text
            WHEN ((abs(gc.net_income_yoy_growth))::double precision >= GREATEST((COALESCE(cb.median_abs_growth, (0)::double precision) * (3)::double precision), (0.35)::double precision)) THEN 'large_relative_magnitude'::text
            ELSE 'other'::text
        END AS flag_reason
   FROM ((public.financial_growth_classified gc
     JOIN public.financial_market_reactions mr ON (((mr.security_id = gc.security_id) AND (mr.period_end = gc.period_end) AND (mr.period_type = gc.period_type))))
     LEFT JOIN company_baseline cb ON (((cb.security_id = gc.security_id) AND (cb.period_type = gc.period_type))))
  WHERE ((gc.net_income_growth_type = ANY (ARRAY['turned_positive'::text, 'turned_negative'::text])) OR ((gc.net_income_yoy_growth IS NOT NULL) AND ((abs(gc.net_income_yoy_growth))::double precision >= GREATEST((COALESCE(cb.median_abs_growth, (0)::double precision) * (3)::double precision), (0.35)::double precision))))
  ORDER BY gc.ticker, gc.period_end;


ALTER VIEW public.candidate_financial_events OWNER TO postgres;

--
-- Name: candidate_review_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.candidate_review_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    security_id uuid NOT NULL,
    filing_date date NOT NULL,
    accession_number text,
    item_codes text,
    verdict text NOT NULL,
    reason text NOT NULL,
    linked_event_id uuid,
    reviewed_at timestamp with time zone DEFAULT now(),
    CONSTRAINT candidate_review_log_verdict_check CHECK ((verdict = ANY (ARRAY['real_event'::text, 'rejected_noise'::text])))
);


ALTER TABLE public.candidate_review_log OWNER TO postgres;

--
-- Name: classification_corrections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classification_corrections (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ticker text NOT NULL,
    filing_date date NOT NULL,
    accession_number text,
    original_verdict text NOT NULL,
    corrected_verdict text NOT NULL,
    original_confidence numeric,
    error_category text NOT NULL,
    correction_reasoning text NOT NULL,
    linked_event_id uuid,
    corrected_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.classification_corrections OWNER TO postgres;

--
-- Name: event_entity_relationships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_entity_relationships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_id uuid NOT NULL,
    entity_id uuid NOT NULL,
    relationship_type text NOT NULL,
    impact_direction text
);


ALTER TABLE public.event_entity_relationships OWNER TO postgres;

--
-- Name: TABLE event_entity_relationships; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.event_entity_relationships IS 'Connections between real-world events and the entities involved in, affected by, or otherwise related to those events.';


--
-- Name: event_market_reactions_corrected; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_market_reactions_corrected (
    event_id uuid NOT NULL,
    title text,
    ticker text,
    event_date date,
    prior_price_date date,
    prior_close numeric,
    event_price_date date,
    event_close numeric,
    day_1_close numeric,
    day_5_close numeric,
    day_20_close numeric,
    return_0d numeric,
    return_1d numeric,
    return_5d numeric,
    return_20d numeric,
    spy_prior_close numeric,
    spy_event_close numeric,
    spy_day1_close numeric,
    spy_day5_close numeric,
    spy_day20_close numeric,
    abnormal_return_0d numeric,
    abnormal_return_1d numeric,
    abnormal_return_5d numeric,
    abnormal_return_20d numeric,
    date_was_corrected boolean DEFAULT false,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.event_market_reactions_corrected OWNER TO postgres;

--
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_date timestamp with time zone NOT NULL,
    title text DEFAULT ''::text NOT NULL,
    description text NOT NULL,
    event_time_precision text DEFAULT '''exact'''::text NOT NULL
);


ALTER TABLE public.events OWNER TO postgres;

--
-- Name: TABLE events; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.events IS 'Real-world events that may affect companies, markets, sectors, or other entities.';


--
-- Name: event_market_reactions; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.event_market_reactions WITH (security_invoker='true') AS
 WITH event_entities AS (
         SELECT ev.id AS event_id,
            ev.title,
            ev.event_date,
            s.id AS security_id,
            s.ticker
           FROM ((public.events ev
             JOIN public.event_entity_relationships eer ON ((eer.event_id = ev.id)))
             JOIN public.securities s ON ((s.entity_id = eer.entity_id)))
          WHERE (eer.relationship_type <> 'actor'::text)
        ), live_computed AS (
         SELECT ee.event_id,
            ee.title,
            ee.ticker,
            ee.event_date,
            prior_price.price_date AS prior_price_date,
            prior_price.close AS prior_close,
            event_price.price_date AS event_price_date,
            event_price.close AS event_close,
            day_1.close AS day_1_close,
            day_5.close AS day_5_close,
            day_20.close AS day_20_close,
                CASE
                    WHEN ((prior_price.close IS NOT NULL) AND (event_price.close IS NOT NULL)) THEN ((event_price.close / prior_price.close) - (1)::numeric)
                    ELSE NULL::numeric
                END AS return_0d,
                CASE
                    WHEN ((event_price.close IS NOT NULL) AND (day_1.close IS NOT NULL)) THEN ((day_1.close / event_price.close) - (1)::numeric)
                    ELSE NULL::numeric
                END AS return_1d,
                CASE
                    WHEN ((event_price.close IS NOT NULL) AND (day_5.close IS NOT NULL)) THEN ((day_5.close / event_price.close) - (1)::numeric)
                    ELSE NULL::numeric
                END AS return_5d,
                CASE
                    WHEN ((event_price.close IS NOT NULL) AND (day_20.close IS NOT NULL)) THEN ((day_20.close / event_price.close) - (1)::numeric)
                    ELSE NULL::numeric
                END AS return_20d,
            spy_prior.close AS spy_prior_close,
            spy_event.close AS spy_event_close,
            spy_day1.close AS spy_day1_close,
            spy_day5.close AS spy_day5_close,
            spy_day20.close AS spy_day20_close,
                CASE
                    WHEN ((prior_price.close IS NOT NULL) AND (event_price.close IS NOT NULL) AND (spy_prior.close IS NOT NULL) AND (spy_event.close IS NOT NULL)) THEN (((event_price.close / prior_price.close) - (1)::numeric) - ((spy_event.close / spy_prior.close) - (1)::numeric))
                    ELSE NULL::numeric
                END AS abnormal_return_0d,
                CASE
                    WHEN ((event_price.close IS NOT NULL) AND (day_1.close IS NOT NULL) AND (spy_event.close IS NOT NULL) AND (spy_day1.close IS NOT NULL)) THEN (((day_1.close / event_price.close) - (1)::numeric) - ((spy_day1.close / spy_event.close) - (1)::numeric))
                    ELSE NULL::numeric
                END AS abnormal_return_1d,
                CASE
                    WHEN ((event_price.close IS NOT NULL) AND (day_5.close IS NOT NULL) AND (spy_event.close IS NOT NULL) AND (spy_day5.close IS NOT NULL)) THEN (((day_5.close / event_price.close) - (1)::numeric) - ((spy_day5.close / spy_event.close) - (1)::numeric))
                    ELSE NULL::numeric
                END AS abnormal_return_5d,
                CASE
                    WHEN ((event_price.close IS NOT NULL) AND (day_20.close IS NOT NULL) AND (spy_event.close IS NOT NULL) AND (spy_day20.close IS NOT NULL)) THEN (((day_20.close / event_price.close) - (1)::numeric) - ((spy_day20.close / spy_event.close) - (1)::numeric))
                    ELSE NULL::numeric
                END AS abnormal_return_20d
           FROM ((((((((((event_entities ee
             LEFT JOIN LATERAL ( SELECT mp.price_date,
                    mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = ee.security_id) AND (mp.price_date < ee.event_date))
                  ORDER BY mp.price_date DESC
                 LIMIT 1) prior_price ON (true))
             LEFT JOIN LATERAL ( SELECT mp.price_date,
                    mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = ee.security_id) AND (mp.price_date > ee.event_date))
                  ORDER BY mp.price_date
                 LIMIT 1) event_price ON (true))
             LEFT JOIN LATERAL ( SELECT mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = ee.security_id) AND (mp.price_date > event_price.price_date))
                  ORDER BY mp.price_date
                 LIMIT 1) day_1 ON (true))
             LEFT JOIN LATERAL ( SELECT mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = ee.security_id) AND (mp.price_date > event_price.price_date))
                  ORDER BY mp.price_date
                 OFFSET 4
                 LIMIT 1) day_5 ON (true))
             LEFT JOIN LATERAL ( SELECT mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = ee.security_id) AND (mp.price_date > event_price.price_date))
                  ORDER BY mp.price_date
                 OFFSET 19
                 LIMIT 1) day_20 ON (true))
             LEFT JOIN LATERAL ( SELECT mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = prior_price.price_date))
                 LIMIT 1) spy_prior ON (true))
             LEFT JOIN LATERAL ( SELECT mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = event_price.price_date))
                 LIMIT 1) spy_event ON (true))
             LEFT JOIN LATERAL ( SELECT mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = ( SELECT mp2.price_date
                           FROM public.market_prices mp2
                          WHERE ((mp2.security_id = ee.security_id) AND (mp2.price_date > event_price.price_date))
                          ORDER BY mp2.price_date
                         LIMIT 1)))
                 LIMIT 1) spy_day1 ON (true))
             LEFT JOIN LATERAL ( SELECT mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = ( SELECT mp2.price_date
                           FROM public.market_prices mp2
                          WHERE ((mp2.security_id = ee.security_id) AND (mp2.price_date > event_price.price_date))
                          ORDER BY mp2.price_date
                         OFFSET 4
                         LIMIT 1)))
                 LIMIT 1) spy_day5 ON (true))
             LEFT JOIN LATERAL ( SELECT mp.close
                   FROM public.market_prices mp
                  WHERE ((mp.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (mp.price_date = ( SELECT mp2.price_date
                           FROM public.market_prices mp2
                          WHERE ((mp2.security_id = ee.security_id) AND (mp2.price_date > event_price.price_date))
                          ORDER BY mp2.price_date
                         OFFSET 19
                         LIMIT 1)))
                 LIMIT 1) spy_day20 ON (true))
        )
 SELECT lc.event_id,
    lc.title,
    lc.ticker,
    COALESCE((c.event_date)::timestamp with time zone, lc.event_date) AS event_date,
    COALESCE(c.prior_price_date, lc.prior_price_date) AS prior_price_date,
    COALESCE(c.prior_close, lc.prior_close) AS prior_close,
    COALESCE(c.event_price_date, lc.event_price_date) AS event_price_date,
    COALESCE(c.event_close, lc.event_close) AS event_close,
    COALESCE(c.day_1_close, lc.day_1_close) AS day_1_close,
    COALESCE(c.day_5_close, lc.day_5_close) AS day_5_close,
    COALESCE(c.day_20_close, lc.day_20_close) AS day_20_close,
    COALESCE(c.return_0d, lc.return_0d) AS return_0d,
    COALESCE(c.return_1d, lc.return_1d) AS return_1d,
    COALESCE(c.return_5d, lc.return_5d) AS return_5d,
    COALESCE(c.return_20d, lc.return_20d) AS return_20d,
    COALESCE(c.spy_prior_close, lc.spy_prior_close) AS spy_prior_close,
    COALESCE(c.spy_event_close, lc.spy_event_close) AS spy_event_close,
    COALESCE(c.spy_day1_close, lc.spy_day1_close) AS spy_day1_close,
    COALESCE(c.spy_day5_close, lc.spy_day5_close) AS spy_day5_close,
    COALESCE(c.spy_day20_close, lc.spy_day20_close) AS spy_day20_close,
    COALESCE(c.abnormal_return_0d, lc.abnormal_return_0d) AS abnormal_return_0d,
    COALESCE(c.abnormal_return_1d, lc.abnormal_return_1d) AS abnormal_return_1d,
    COALESCE(c.abnormal_return_5d, lc.abnormal_return_5d) AS abnormal_return_5d,
    COALESCE(c.abnormal_return_20d, lc.abnormal_return_20d) AS abnormal_return_20d,
    COALESCE(c.date_was_corrected, false) AS date_was_corrected
   FROM (live_computed lc
     LEFT JOIN public.event_market_reactions_corrected c ON ((c.event_id = lc.event_id)));


ALTER VIEW public.event_market_reactions OWNER TO postgres;

--
-- Name: filing_ai_classifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.filing_ai_classifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ticker text NOT NULL,
    filing_date date NOT NULL,
    accession_number text NOT NULL,
    item_codes text,
    primary_document_url text,
    ai_verdict text NOT NULL,
    ai_confidence numeric NOT NULL,
    ai_reasoning text NOT NULL,
    ai_suggested_title text,
    ai_suggested_description text,
    ai_suggested_event_type text,
    ai_matched_known_template text,
    model_version text NOT NULL,
    prompt_version text NOT NULL,
    classified_at timestamp with time zone DEFAULT now(),
    flagged_for_review boolean NOT NULL,
    flag_reason text NOT NULL,
    human_reviewed_at timestamp with time zone,
    human_verdict text,
    human_agreed_with_ai boolean,
    linked_event_id uuid,
    CONSTRAINT filing_ai_classifications_ai_confidence_check CHECK (((ai_confidence >= (0)::numeric) AND (ai_confidence <= (1)::numeric))),
    CONSTRAINT filing_ai_classifications_ai_verdict_check CHECK ((ai_verdict = ANY (ARRAY['real_event'::text, 'likely_noise'::text, 'uncertain'::text]))),
    CONSTRAINT filing_ai_classifications_human_verdict_check CHECK ((human_verdict = ANY (ARRAY['real_event'::text, 'rejected_noise'::text, 'unverifiable'::text])))
);


ALTER TABLE public.filing_ai_classifications OWNER TO postgres;

--
-- Name: classifier_confidence_calibration; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.classifier_confidence_calibration WITH (security_invoker='true') AS
 SELECT
        CASE
            WHEN (sub.avg_confidence >= 0.9) THEN 'high (0.9+)'::text
            WHEN (sub.avg_confidence >= 0.8) THEN 'medium (0.8-0.9)'::text
            ELSE 'lower (<0.8)'::text
        END AS confidence_bucket,
    count(*) AS n,
    avg(abs(emr.abnormal_return_5d)) AS avg_abs_move_5d,
    avg(abs(emr.abnormal_return_20d)) AS avg_abs_move_20d
   FROM (( SELECT crl.linked_event_id,
            avg(fac.ai_confidence) AS avg_confidence
           FROM (public.candidate_review_log crl
             JOIN public.filing_ai_classifications fac ON ((fac.accession_number = crl.accession_number)))
          WHERE (crl.verdict = 'real_event'::text)
          GROUP BY crl.linked_event_id) sub
     JOIN public.event_market_reactions emr ON ((emr.event_id = sub.linked_event_id)))
  WHERE (emr.abnormal_return_5d IS NOT NULL)
  GROUP BY
        CASE
            WHEN (sub.avg_confidence >= 0.9) THEN 'high (0.9+)'::text
            WHEN (sub.avg_confidence >= 0.8) THEN 'medium (0.8-0.9)'::text
            ELSE 'lower (<0.8)'::text
        END;


ALTER VIEW public.classifier_confidence_calibration OWNER TO postgres;

--
-- Name: company_sentiment_timeline; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_sentiment_timeline (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id uuid NOT NULL,
    date date NOT NULL,
    article_count integer NOT NULL,
    avg_tone numeric,
    source text DEFAULT 'gdelt'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.company_sentiment_timeline OWNER TO postgres;

--
-- Name: event_relationships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_relationships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_event_id uuid NOT NULL,
    target_event_id uuid NOT NULL,
    relationship_type text NOT NULL,
    days_between integer,
    confidence numeric,
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.event_relationships OWNER TO postgres;

--
-- Name: cross_entity_web; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.cross_entity_web WITH (security_invoker='true') AS
 SELECT DISTINCT s1.ticker AS company_a,
    e1.title AS event_a,
    e1.event_date AS date_a,
    er.relationship_type,
    er.confidence,
    s2.ticker AS company_b,
    e2.title AS event_b,
    e2.event_date AS date_b,
    er.notes
   FROM ((((public.event_relationships er
     JOIN public.events e1 ON ((e1.id = er.source_event_id)))
     JOIN public.events e2 ON ((e2.id = er.target_event_id)))
     JOIN LATERAL ( SELECT s.ticker,
            s.entity_id
           FROM (public.event_entity_relationships eer
             JOIN public.securities s ON ((s.entity_id = eer.entity_id)))
          WHERE (eer.event_id = e1.id)
          ORDER BY (e1.title ~~* (('%'::text || s.ticker) || '%'::text)) DESC, s.ticker
         LIMIT 1) s1 ON (true))
     JOIN LATERAL ( SELECT s.ticker,
            s.entity_id
           FROM (public.event_entity_relationships eer
             JOIN public.securities s ON ((s.entity_id = eer.entity_id)))
          WHERE (eer.event_id = e2.id)
          ORDER BY (e2.title ~~* (('%'::text || s.ticker) || '%'::text)) DESC, s.ticker
         LIMIT 1) s2 ON (true))
  WHERE (s1.ticker <> s2.ticker)
  ORDER BY er.confidence DESC, e1.event_date;


ALTER VIEW public.cross_entity_web OWNER TO postgres;

--
-- Name: cross_entity_web_v2; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.cross_entity_web_v2 WITH (security_invoker='true') AS
 SELECT e.title AS shared_event,
    e.event_date,
    array_agg(DISTINCT s.ticker ORDER BY s.ticker) AS companies_linked
   FROM ((public.events e
     JOIN public.event_entity_relationships eer ON ((eer.event_id = e.id)))
     JOIN public.securities s ON ((s.entity_id = eer.entity_id)))
  GROUP BY e.id, e.title, e.event_date
 HAVING (count(DISTINCT s.ticker) > 1);


ALTER VIEW public.cross_entity_web_v2 OWNER TO postgres;

--
-- Name: entities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    entity_type text NOT NULL,
    description text,
    ticker text
);


ALTER TABLE public.entities OWNER TO postgres;

--
-- Name: TABLE entities; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.entities IS 'Companies, governments, organizations, countries, industries, commodities, and other entities involved in or affected by events.';


--
-- Name: event_article_relationships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_article_relationships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_id uuid NOT NULL,
    article_id uuid NOT NULL,
    relationship_type text NOT NULL
);


ALTER TABLE public.event_article_relationships OWNER TO postgres;

--
-- Name: TABLE event_article_relationships; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.event_article_relationships IS 'Connections between events and the source articles or documents that provide evidence about those events.';


--
-- Name: event_candidate_triage; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.event_candidate_triage WITH (security_invoker='true') AS
 WITH ranked_prices AS (
         SELECT market_prices.security_id,
            market_prices.price_date,
            market_prices.close,
            row_number() OVER (PARTITION BY market_prices.security_id ORDER BY market_prices.price_date) AS rn
           FROM public.market_prices
        ), all_filings AS (
         SELECT f.security_id,
            s.ticker,
            ent.name AS company_name,
            f.filing_date,
            f.accession_number,
            f.primary_document_url,
            f.item_codes
           FROM ((public.sec_8k_filings f
             JOIN public.securities s ON ((s.id = f.security_id)))
             JOIN public.entities ent ON ((ent.id = s.entity_id)))
          WHERE (f.filing_date IS NOT NULL)
        ), prior_day AS (
         SELECT DISTINCT ON (af_1.security_id, af_1.filing_date) af_1.security_id,
            af_1.filing_date,
            rp.close AS prior_close,
            rp.price_date AS prior_date
           FROM (all_filings af_1
             JOIN ranked_prices rp ON (((rp.security_id = af_1.security_id) AND (rp.price_date < af_1.filing_date))))
          ORDER BY af_1.security_id, af_1.filing_date, rp.price_date DESC
        ), event_day AS (
         SELECT DISTINCT ON (af_1.security_id, af_1.filing_date) af_1.security_id,
            af_1.filing_date,
            rp.rn AS event_rn,
            rp.price_date AS event_date_actual
           FROM (all_filings af_1
             JOIN ranked_prices rp ON (((rp.security_id = af_1.security_id) AND (rp.price_date >= af_1.filing_date))))
          ORDER BY af_1.security_id, af_1.filing_date, rp.price_date
        ), day5 AS (
         SELECT ed.security_id,
            ed.filing_date,
            rp.close AS day5_close,
            rp.price_date AS day5_date
           FROM (event_day ed
             JOIN ranked_prices rp ON (((rp.security_id = ed.security_id) AND (rp.rn = (ed.event_rn + 5)))))
        ), spy_returns AS (
         SELECT pd_1.security_id,
            pd_1.filing_date,
            spy_prior.close AS spy_prior_close,
            spy_day5.close AS spy_day5_close
           FROM ((((prior_day pd_1
             JOIN event_day ed ON (((ed.security_id = pd_1.security_id) AND (ed.filing_date = pd_1.filing_date))))
             JOIN day5 d5_1 ON (((d5_1.security_id = pd_1.security_id) AND (d5_1.filing_date = pd_1.filing_date))))
             LEFT JOIN LATERAL ( SELECT market_prices.close
                   FROM public.market_prices
                  WHERE ((market_prices.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (market_prices.price_date = pd_1.prior_date))) spy_prior ON (true))
             LEFT JOIN LATERAL ( SELECT market_prices.close
                   FROM public.market_prices
                  WHERE ((market_prices.security_id = '09e39bb1-7b36-406d-b5d1-db755e37ad54'::uuid) AND (market_prices.price_date = d5_1.day5_date))) spy_day5 ON (true))
        ), company_typical_swing AS (
         SELECT af_1.security_id,
            percentile_cont((0.5)::double precision) WITHIN GROUP (ORDER BY ((abs((((d5_1.day5_close - pd_1.prior_close) / pd_1.prior_close) - ((sr_1.spy_day5_close - sr_1.spy_prior_close) / sr_1.spy_prior_close))))::double precision)) AS median_abnormal_swing
           FROM (((all_filings af_1
             JOIN prior_day pd_1 ON (((pd_1.security_id = af_1.security_id) AND (pd_1.filing_date = af_1.filing_date))))
             JOIN day5 d5_1 ON (((d5_1.security_id = af_1.security_id) AND (d5_1.filing_date = af_1.filing_date))))
             JOIN spy_returns sr_1 ON (((sr_1.security_id = af_1.security_id) AND (sr_1.filing_date = af_1.filing_date))))
          WHERE ((pd_1.prior_close IS NOT NULL) AND (d5_1.day5_close IS NOT NULL) AND (sr_1.spy_prior_close IS NOT NULL) AND (sr_1.spy_day5_close IS NOT NULL))
          GROUP BY af_1.security_id
        ), hit_rates AS (
         SELECT candidate_review_log.item_codes,
            count(*) AS times_reviewed,
            count(*) FILTER (WHERE (candidate_review_log.verdict = 'real_event'::text)) AS real_event_count,
            round(((100.0 * (count(*) FILTER (WHERE (candidate_review_log.verdict = 'real_event'::text)))::numeric) / (count(*))::numeric), 1) AS hit_rate_pct
           FROM public.candidate_review_log
          GROUP BY candidate_review_log.item_codes
        )
 SELECT af.ticker,
    af.company_name,
    af.filing_date,
    af.item_codes,
    round((((d5.day5_close - pd.prior_close) / pd.prior_close) * (100)::numeric), 2) AS raw_return_5d_pct,
    round(((((d5.day5_close - pd.prior_close) / pd.prior_close) - ((sr.spy_day5_close - sr.spy_prior_close) / sr.spy_prior_close)) * (100)::numeric), 2) AS abnormal_return_5d_pct,
    round(((cts.median_abnormal_swing * (100)::double precision))::numeric, 2) AS company_typical_swing_pct,
        CASE
            WHEN (cts.median_abnormal_swing IS NULL) THEN NULL::boolean
            WHEN ((abs((((d5.day5_close - pd.prior_close) / pd.prior_close) - ((sr.spy_day5_close - sr.spy_prior_close) / sr.spy_prior_close))))::double precision > ((2)::double precision * cts.median_abnormal_swing)) THEN true
            ELSE false
        END AS large_relative_to_company_norm,
        CASE
            WHEN ((af.filing_date >= '2008-01-01'::date) AND (af.filing_date <= '2009-06-30'::date)) THEN true
            WHEN ((af.filing_date >= '2020-02-15'::date) AND (af.filing_date <= '2020-04-15'::date)) THEN true
            WHEN ((af.filing_date >= '2022-02-24'::date) AND (af.filing_date <= '2022-03-15'::date)) THEN true
            ELSE false
        END AS in_known_confound_window,
        CASE
            WHEN (af.item_codes !~ ','::text) THEN true
            ELSE false
        END AS single_item_code,
        CASE
            WHEN (af.item_codes ~~ '%2.02%'::text) THEN true
            WHEN (af.item_codes ~ '(^|,)(9|12)(,|$)'::text) THEN true
            ELSE false
        END AS bundled_with_earnings,
    (EXISTS ( SELECT 1
           FROM public.financial_statements fs
          WHERE ((fs.security_id = af.security_id) AND (fs.filed_date IS NOT NULL) AND ((af.filing_date >= (fs.filed_date - 45)) AND (af.filing_date <= (fs.filed_date + 3)))))) AS near_known_earnings_date,
    hr.times_reviewed AS pattern_times_reviewed,
    hr.hit_rate_pct AS pattern_hit_rate_pct,
    af.accession_number,
    af.primary_document_url
   FROM (((((all_filings af
     JOIN prior_day pd ON (((pd.security_id = af.security_id) AND (pd.filing_date = af.filing_date))))
     JOIN day5 d5 ON (((d5.security_id = af.security_id) AND (d5.filing_date = af.filing_date))))
     JOIN spy_returns sr ON (((sr.security_id = af.security_id) AND (sr.filing_date = af.filing_date))))
     LEFT JOIN company_typical_swing cts ON ((cts.security_id = af.security_id)))
     LEFT JOIN hit_rates hr ON ((hr.item_codes = af.item_codes)))
  WHERE ((pd.prior_close IS NOT NULL) AND (d5.day5_close IS NOT NULL) AND (sr.spy_prior_close IS NOT NULL) AND (sr.spy_day5_close IS NOT NULL));


ALTER VIEW public.event_candidate_triage OWNER TO postgres;

--
-- Name: event_component_dates; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.event_component_dates WITH (security_invoker='true') AS
 SELECT e.id AS event_id,
    e.title,
    e.event_date AS event_summary_date,
    crl.filing_date AS real_component_date,
    crl.accession_number,
    s.ticker
   FROM ((public.events e
     JOIN public.candidate_review_log crl ON ((crl.linked_event_id = e.id)))
     JOIN public.securities s ON ((s.id = crl.security_id)))
  WHERE (crl.verdict = 'real_event'::text);


ALTER VIEW public.event_component_dates OWNER TO postgres;

--
-- Name: event_pre_context; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_pre_context (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_id uuid NOT NULL,
    entity_id uuid NOT NULL,
    firm_state_label text,
    firm_state_as_of_period date,
    regime_id uuid,
    market_cap_at_event numeric,
    size_bucket text,
    surprise_vs_consensus text,
    surprise_data_source text DEFAULT 'NOT_AVAILABLE_no_consensus_data_ingested'::text,
    computed_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.event_pre_context OWNER TO postgres;

--
-- Name: event_tag_suggestions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_tag_suggestions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_id uuid NOT NULL,
    suggested_tag_name text NOT NULL,
    ai_confidence numeric NOT NULL,
    ai_reasoning text NOT NULL,
    model_version text NOT NULL,
    prompt_version text NOT NULL,
    suggested_at timestamp with time zone DEFAULT now(),
    flagged_for_review boolean NOT NULL,
    flag_reason text NOT NULL,
    human_reviewed_at timestamp with time zone,
    human_decision text,
    CONSTRAINT event_tag_suggestions_ai_confidence_check CHECK (((ai_confidence >= (0)::numeric) AND (ai_confidence <= (1)::numeric))),
    CONSTRAINT event_tag_suggestions_human_decision_check CHECK ((human_decision = ANY (ARRAY['confirmed'::text, 'rejected'::text])))
);


ALTER TABLE public.event_tag_suggestions OWNER TO postgres;

--
-- Name: event_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_tags (
    event_id uuid NOT NULL,
    tag_id uuid NOT NULL
);


ALTER TABLE public.event_tags OWNER TO postgres;

--
-- Name: event_type_relationships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_type_relationships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_id uuid NOT NULL,
    event_type_id uuid NOT NULL,
    confidence numeric DEFAULT 1.0 NOT NULL
);


ALTER TABLE public.event_type_relationships OWNER TO postgres;

--
-- Name: TABLE event_type_relationships; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.event_type_relationships IS 'Connections between events and the classifications that describe them.';


--
-- Name: event_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_types (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    description text NOT NULL,
    category text NOT NULL
);


ALTER TABLE public.event_types OWNER TO postgres;

--
-- Name: TABLE event_types; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.event_types IS 'Classification tags describing the nature, category, and characteristics of real-world events.';


--
-- Name: financial_analysis; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.financial_analysis WITH (security_invoker='true') AS
 SELECT s.id AS security_id,
    s.ticker,
    s.exchange,
    s.security_type,
    s.currency,
    fm.period_end,
    fm.period_type,
    fm.fiscal_year,
    fm.fiscal_quarter,
    fm.revenue_growth,
    fm.revenue_yoy_growth,
    fm.net_income_yoy_growth,
    fm.gross_margin,
    fm.operating_margin,
    fm.net_margin,
    fm.fcf_margin,
    fm.fcf_yoy_growth,
    fm.operating_cash_flow_margin,
    fm.capex_revenue_ratio
   FROM (public.financial_metrics fm
     JOIN public.securities s ON ((s.id = fm.security_id)));


ALTER VIEW public.financial_analysis OWNER TO postgres;

--
-- Name: financial_analysis_clean; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.financial_analysis_clean WITH (security_invoker='true') AS
 SELECT fs.security_id,
    s.ticker,
    fs.period_type,
    fs.period_end,
    fs.fiscal_year,
    fs.fiscal_quarter,
    fs.filed_date,
    fs.revenue,
    fs.gross_profit,
    fs.operating_income,
    fs.net_income,
    fs.eps_basic,
    fs.eps_diluted,
    fs.total_assets,
    fs.total_liabilities,
    fs.total_equity,
    fs.cash_and_equivalents,
    fs.operating_cash_flow,
    fs.capital_expenditures,
    fs.free_cash_flow,
    fm.revenue_growth AS revenue_growth_pct,
    fm.revenue_yoy_growth AS revenue_yoy_pct,
    fm.net_income_growth AS net_income_growth_pct,
    fm.net_income_yoy_growth AS net_income_yoy_pct,
    fm.gross_margin AS gross_margin_pct,
    fm.operating_margin AS operating_margin_pct,
    fm.net_margin AS net_margin_pct,
    fm.fcf_margin AS fcf_margin_pct,
    fm.operating_cash_flow_margin AS operating_cash_flow_margin_pct,
    fm.fcf_growth AS fcf_growth_pct,
    fm.fcf_yoy_growth AS fcf_yoy_growth_pct,
    fm.capex_revenue_ratio AS capex_revenue_ratio_pct,
    fs.source,
    fm.calculated_at
   FROM ((public.financial_statements fs
     JOIN public.securities s ON ((s.id = fs.security_id)))
     LEFT JOIN public.financial_metrics fm ON (((fm.financial_statement_id = fs.id) AND (fm.security_id = fs.security_id) AND (fm.period_type = fs.period_type) AND (fm.period_end = fs.period_end))));


ALTER VIEW public.financial_analysis_clean OWNER TO postgres;

--
-- Name: financial_health_snapshot; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.financial_health_snapshot WITH (security_invoker='true') AS
 WITH quarterly_metrics AS (
         SELECT financial_analysis_clean.security_id,
            financial_analysis_clean.ticker,
            financial_analysis_clean.period_type,
            financial_analysis_clean.period_end,
            financial_analysis_clean.fiscal_year,
            financial_analysis_clean.fiscal_quarter,
            financial_analysis_clean.filed_date,
            financial_analysis_clean.revenue,
            financial_analysis_clean.gross_profit,
            financial_analysis_clean.operating_income,
            financial_analysis_clean.net_income,
            financial_analysis_clean.eps_basic,
            financial_analysis_clean.eps_diluted,
            financial_analysis_clean.total_assets,
            financial_analysis_clean.total_liabilities,
            financial_analysis_clean.total_equity,
            financial_analysis_clean.cash_and_equivalents,
            financial_analysis_clean.operating_cash_flow,
            financial_analysis_clean.capital_expenditures,
            financial_analysis_clean.free_cash_flow,
            financial_analysis_clean.revenue_growth_pct,
            financial_analysis_clean.revenue_yoy_pct,
            financial_analysis_clean.net_income_growth_pct,
            financial_analysis_clean.net_income_yoy_pct,
            financial_analysis_clean.gross_margin_pct,
            financial_analysis_clean.operating_margin_pct,
            financial_analysis_clean.net_margin_pct,
            financial_analysis_clean.fcf_margin_pct,
            financial_analysis_clean.operating_cash_flow_margin_pct,
            financial_analysis_clean.fcf_growth_pct,
            financial_analysis_clean.fcf_yoy_growth_pct,
            financial_analysis_clean.capex_revenue_ratio_pct,
            financial_analysis_clean.source,
            financial_analysis_clean.calculated_at,
            lag(financial_analysis_clean.revenue_yoy_pct) OVER (PARTITION BY financial_analysis_clean.security_id ORDER BY financial_analysis_clean.period_end) AS previous_revenue_yoy_pct,
            lag(financial_analysis_clean.gross_margin_pct) OVER (PARTITION BY financial_analysis_clean.security_id ORDER BY financial_analysis_clean.period_end) AS previous_gross_margin_pct,
            lag(financial_analysis_clean.operating_margin_pct) OVER (PARTITION BY financial_analysis_clean.security_id ORDER BY financial_analysis_clean.period_end) AS previous_operating_margin_pct,
            lag(financial_analysis_clean.net_margin_pct) OVER (PARTITION BY financial_analysis_clean.security_id ORDER BY financial_analysis_clean.period_end) AS previous_net_margin_pct,
            lag(financial_analysis_clean.fcf_margin_pct) OVER (PARTITION BY financial_analysis_clean.security_id ORDER BY financial_analysis_clean.period_end) AS previous_fcf_margin_pct,
            lag(financial_analysis_clean.capex_revenue_ratio_pct) OVER (PARTITION BY financial_analysis_clean.security_id ORDER BY financial_analysis_clean.period_end) AS previous_capex_revenue_ratio_pct
           FROM public.financial_analysis_clean
          WHERE (financial_analysis_clean.period_type = 'quarterly'::text)
        )
 SELECT security_id,
    ticker,
    period_end,
    fiscal_year,
    fiscal_quarter,
    revenue,
    net_income,
    free_cash_flow,
    revenue_yoy_pct,
    gross_margin_pct,
    operating_margin_pct,
    net_margin_pct,
    fcf_margin_pct,
    fcf_yoy_growth_pct,
    capex_revenue_ratio_pct,
    (revenue_yoy_pct - previous_revenue_yoy_pct) AS revenue_growth_change,
    (gross_margin_pct - previous_gross_margin_pct) AS gross_margin_change,
    (operating_margin_pct - previous_operating_margin_pct) AS operating_margin_change,
    (net_margin_pct - previous_net_margin_pct) AS net_margin_change,
    (fcf_margin_pct - previous_fcf_margin_pct) AS fcf_margin_change,
    (capex_revenue_ratio_pct - previous_capex_revenue_ratio_pct) AS capex_intensity_change
   FROM quarterly_metrics;


ALTER VIEW public.financial_health_snapshot OWNER TO postgres;

--
-- Name: fundamental_signals; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.fundamental_signals WITH (security_invoker='true') AS
 SELECT ticker,
    security_id,
    fiscal_year,
    fiscal_quarter,
    period_end,
    revenue_yoy_pct,
    revenue_growth_change,
    gross_margin_pct,
    gross_margin_change,
    operating_margin_pct,
    operating_margin_change,
    net_margin_pct,
    net_margin_change,
    fcf_margin_pct,
    fcf_margin_change,
    fcf_yoy_growth_pct,
    capex_revenue_ratio_pct,
    capex_intensity_change,
        CASE
            WHEN (revenue_growth_change > 0.02) THEN 'accelerating'::text
            WHEN (revenue_growth_change < '-0.02'::numeric) THEN 'decelerating'::text
            ELSE 'stable'::text
        END AS revenue_momentum,
        CASE
            WHEN (gross_margin_change > 0.01) THEN 'improving'::text
            WHEN (gross_margin_change < '-0.01'::numeric) THEN 'deteriorating'::text
            ELSE 'stable'::text
        END AS gross_margin_trend,
        CASE
            WHEN (operating_margin_change > 0.01) THEN 'improving'::text
            WHEN (operating_margin_change < '-0.01'::numeric) THEN 'deteriorating'::text
            ELSE 'stable'::text
        END AS operating_margin_trend,
        CASE
            WHEN (fcf_yoy_growth_pct > 0.10) THEN 'strong_growth'::text
            WHEN (fcf_yoy_growth_pct < '-0.10'::numeric) THEN 'declining'::text
            ELSE 'stable'::text
        END AS fcf_trend
   FROM public.financial_health_snapshot;


ALTER VIEW public.fundamental_signals OWNER TO postgres;

--
-- Name: financial_condition_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.financial_condition_summary WITH (security_invoker='true') AS
 SELECT security_id,
    ticker,
    fiscal_year,
    fiscal_quarter,
    period_end,
    revenue_momentum,
    gross_margin_trend,
    operating_margin_trend,
    fcf_trend,
    (((((revenue_momentum = 'accelerating'::text))::integer + ((gross_margin_trend = 'improving'::text))::integer) + ((operating_margin_trend = 'improving'::text))::integer) + ((fcf_trend = 'strong_growth'::text))::integer) AS positive_count,
    (((((revenue_momentum = 'decelerating'::text))::integer + ((gross_margin_trend = 'deteriorating'::text))::integer) + ((operating_margin_trend = 'deteriorating'::text))::integer) + ((fcf_trend = 'declining'::text))::integer) AS negative_count,
        CASE
            WHEN (((((((revenue_momentum = 'accelerating'::text))::integer + ((gross_margin_trend = 'improving'::text))::integer) + ((operating_margin_trend = 'improving'::text))::integer) + ((fcf_trend = 'strong_growth'::text))::integer) >= 3) AND ((((((revenue_momentum = 'decelerating'::text))::integer + ((gross_margin_trend = 'deteriorating'::text))::integer) + ((operating_margin_trend = 'deteriorating'::text))::integer) + ((fcf_trend = 'declining'::text))::integer) = 0)) THEN 'Strong'::text
            WHEN (((((((revenue_momentum = 'decelerating'::text))::integer + ((gross_margin_trend = 'deteriorating'::text))::integer) + ((operating_margin_trend = 'deteriorating'::text))::integer) + ((fcf_trend = 'declining'::text))::integer) >= 3) AND ((((((revenue_momentum = 'accelerating'::text))::integer + ((gross_margin_trend = 'improving'::text))::integer) + ((operating_margin_trend = 'improving'::text))::integer) + ((fcf_trend = 'strong_growth'::text))::integer) = 0)) THEN 'Deteriorating'::text
            WHEN (((((((revenue_momentum = 'accelerating'::text))::integer + ((gross_margin_trend = 'improving'::text))::integer) + ((operating_margin_trend = 'improving'::text))::integer) + ((fcf_trend = 'strong_growth'::text))::integer) > (((((revenue_momentum = 'decelerating'::text))::integer + ((gross_margin_trend = 'deteriorating'::text))::integer) + ((operating_margin_trend = 'deteriorating'::text))::integer) + ((fcf_trend = 'declining'::text))::integer)) AND ((((((revenue_momentum = 'decelerating'::text))::integer + ((gross_margin_trend = 'deteriorating'::text))::integer) + ((operating_margin_trend = 'deteriorating'::text))::integer) + ((fcf_trend = 'declining'::text))::integer) <= 1)) THEN 'Healthy'::text
            WHEN (((((((revenue_momentum = 'decelerating'::text))::integer + ((gross_margin_trend = 'deteriorating'::text))::integer) + ((operating_margin_trend = 'deteriorating'::text))::integer) + ((fcf_trend = 'declining'::text))::integer) > (((((revenue_momentum = 'accelerating'::text))::integer + ((gross_margin_trend = 'improving'::text))::integer) + ((operating_margin_trend = 'improving'::text))::integer) + ((fcf_trend = 'strong_growth'::text))::integer)) AND ((((((revenue_momentum = 'accelerating'::text))::integer + ((gross_margin_trend = 'improving'::text))::integer) + ((operating_margin_trend = 'improving'::text))::integer) + ((fcf_trend = 'strong_growth'::text))::integer) <= 1)) THEN 'Weak'::text
            ELSE 'Mixed'::text
        END AS overall_condition
   FROM public.fundamental_signals;


ALTER VIEW public.financial_condition_summary OWNER TO postgres;

--
-- Name: financial_filing_events; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.financial_filing_events WITH (security_invoker='true') AS
 SELECT s.id AS security_id,
    s.ticker,
    s.exchange,
    s.security_type,
    s.currency,
    fs.filed_date,
    latest.period_end,
    latest.fiscal_year,
    latest.fiscal_quarter,
    q.revenue_growth AS quarterly_revenue_growth,
    q.revenue_yoy_growth AS quarterly_revenue_yoy_growth,
    q.net_income_yoy_growth AS quarterly_net_income_yoy_growth,
    q.gross_margin AS quarterly_gross_margin,
    q.operating_margin AS quarterly_operating_margin,
    q.net_margin AS quarterly_net_margin,
    q.fcf_margin AS quarterly_fcf_margin,
    q.fcf_yoy_growth AS quarterly_fcf_yoy_growth,
    q.operating_cash_flow_margin AS quarterly_operating_cash_flow_margin,
    q.capex_revenue_ratio AS quarterly_capex_revenue_ratio,
    a.revenue_growth AS annual_revenue_growth,
    a.revenue_yoy_growth AS annual_revenue_yoy_growth,
    a.net_income_yoy_growth AS annual_net_income_yoy_growth,
    a.gross_margin AS annual_gross_margin,
    a.operating_margin AS annual_operating_margin,
    a.net_margin AS annual_net_margin,
    a.fcf_margin AS annual_fcf_margin,
    a.fcf_yoy_growth AS annual_fcf_yoy_growth,
    a.operating_cash_flow_margin AS annual_operating_cash_flow_margin,
    a.capex_revenue_ratio AS annual_capex_revenue_ratio
   FROM ((((public.securities s
     JOIN ( SELECT financial_statements.security_id,
            financial_statements.filed_date
           FROM public.financial_statements
          GROUP BY financial_statements.security_id, financial_statements.filed_date) fs ON ((fs.security_id = s.id)))
     LEFT JOIN LATERAL ( SELECT f.period_end,
            f.fiscal_year,
            f.fiscal_quarter
           FROM public.financial_statements f
          WHERE ((f.security_id = fs.security_id) AND (f.filed_date = fs.filed_date))
          ORDER BY f.period_end DESC
         LIMIT 1) latest ON (true))
     LEFT JOIN public.financial_metrics q ON (((q.security_id = fs.security_id) AND (q.period_end = latest.period_end) AND (q.period_type = 'quarterly'::text))))
     LEFT JOIN public.financial_metrics a ON (((a.security_id = fs.security_id) AND (a.period_end = latest.period_end) AND (a.period_type = 'annual'::text))));


ALTER VIEW public.financial_filing_events OWNER TO postgres;

--
-- Name: macro_data_releases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.macro_data_releases (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    series_id text NOT NULL,
    event_type_hint text NOT NULL,
    release_date date NOT NULL,
    period_covered text,
    revision_marker text,
    value numeric,
    previous_value numeric,
    change_from_previous numeric,
    company_relative_threshold_flag boolean,
    median_abs_change_for_series numeric,
    fetched_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.macro_data_releases OWNER TO postgres;

--
-- Name: market_regimes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_regimes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    start_date date NOT NULL,
    end_date date,
    description text NOT NULL
);


ALTER TABLE public.market_regimes OWNER TO postgres;

--
-- Name: news_ai_classifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.news_ai_classifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    article_id uuid NOT NULL,
    ticker text NOT NULL,
    match_score numeric,
    ai_verdict text NOT NULL,
    ai_confidence numeric NOT NULL,
    ai_reasoning text NOT NULL,
    ai_suggested_title text,
    ai_suggested_description text,
    ai_suggested_event_type text,
    ai_flagged_possible_duplicate_of text,
    model_version text NOT NULL,
    prompt_version text NOT NULL,
    classified_at timestamp with time zone DEFAULT now(),
    flagged_for_review boolean NOT NULL,
    flag_reason text NOT NULL,
    human_reviewed_at timestamp with time zone,
    human_verdict text,
    human_agreed_with_ai boolean,
    linked_event_id uuid,
    CONSTRAINT news_ai_classifications_ai_confidence_check CHECK (((ai_confidence >= (0)::numeric) AND (ai_confidence <= (1)::numeric))),
    CONSTRAINT news_ai_classifications_ai_verdict_check CHECK ((ai_verdict = ANY (ARRAY['real_event'::text, 'likely_noise'::text, 'uncertain'::text]))),
    CONSTRAINT news_ai_classifications_human_verdict_check CHECK ((human_verdict = ANY (ARRAY['real_event'::text, 'rejected_noise'::text, 'unverifiable'::text])))
);


ALTER TABLE public.news_ai_classifications OWNER TO postgres;

--
-- Name: news_article_entities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.news_article_entities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    article_id uuid NOT NULL,
    ticker text NOT NULL,
    match_score numeric,
    sentiment_score numeric,
    fetched_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.news_article_entities OWNER TO postgres;

--
-- Name: news_articles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.news_articles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    published_at timestamp with time zone NOT NULL,
    title text NOT NULL,
    source_name text NOT NULL,
    url text NOT NULL,
    content text NOT NULL,
    source_type text NOT NULL
);


ALTER TABLE public.news_articles OWNER TO postgres;

--
-- Name: TABLE news_articles; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.news_articles IS 'Source articles and documents used as evidence for identifying and analyzing real-world events.';


--
-- Name: news_candidate_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.news_candidate_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    article_id uuid NOT NULL,
    ticker text NOT NULL,
    match_score numeric,
    verdict text NOT NULL,
    reason text NOT NULL,
    linked_event_id uuid,
    reviewed_at timestamp with time zone DEFAULT now(),
    CONSTRAINT news_candidate_events_verdict_check CHECK ((verdict = ANY (ARRAY['real_event'::text, 'rejected_noise'::text, 'unverifiable'::text])))
);


ALTER TABLE public.news_candidate_events OWNER TO postgres;

--
-- Name: pattern_significance_tests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pattern_significance_tests (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tag_name text NOT NULL,
    n integer NOT NULL,
    muted_count integer,
    punished_count integer,
    rewarded_count integer,
    chi2_statistic numeric,
    p_value numeric,
    is_significant boolean,
    dominant_reaction text,
    tested_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.pattern_significance_tests OWNER TO postgres;

--
-- Name: recoverable_rejected_noise; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.recoverable_rejected_noise WITH (security_invoker='true') AS
 SELECT crl.security_id,
    s.ticker,
    crl.filing_date,
    crl.accession_number,
    crl.verdict
   FROM ((public.candidate_review_log crl
     JOIN public.securities s ON ((s.id = crl.security_id)))
     JOIN public.filing_ai_classifications fac ON (((fac.accession_number = crl.accession_number) AND (fac.ticker = s.ticker))))
  WHERE ((crl.verdict = 'rejected_noise'::text) AND (fac.ai_verdict = 'real_event'::text));


ALTER VIEW public.recoverable_rejected_noise OWNER TO postgres;

--
-- Name: tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    tier1_category text NOT NULL,
    description text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.tags OWNER TO postgres;

--
-- Name: same_entity_sequence_chain_position; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.same_entity_sequence_chain_position WITH (security_invoker='true') AS
 WITH chained_events AS (
         SELECT e.id AS event_id,
            e.title,
            e.event_date,
            s.ticker
           FROM (((public.events e
             JOIN public.event_tags et ON (((et.event_id = e.id) AND (et.tag_id = ( SELECT tags.id
                   FROM public.tags
                  WHERE (tags.name = 'same_entity_sequence'::text))))))
             JOIN public.event_entity_relationships eer ON ((eer.event_id = e.id)))
             JOIN public.securities s ON ((s.entity_id = eer.entity_id)))
        ), ranked AS (
         SELECT chained_events.event_id,
            chained_events.title,
            chained_events.event_date,
            chained_events.ticker,
            row_number() OVER (PARTITION BY chained_events.ticker ORDER BY chained_events.event_date) AS rank_asc,
            count(*) OVER (PARTITION BY chained_events.ticker) AS total_for_ticker
           FROM chained_events
        )
 SELECT event_id,
    title,
    event_date,
    ticker,
    rank_asc,
    total_for_ticker,
        CASE
            WHEN (total_for_ticker = 1) THEN 'only_one'::text
            WHEN (rank_asc = 1) THEN 'opening'::text
            WHEN (rank_asc = total_for_ticker) THEN 'closing'::text
            ELSE 'middle'::text
        END AS chain_position
   FROM ranked;


ALTER VIEW public.same_entity_sequence_chain_position OWNER TO postgres;

--
-- Name: messages; Type: TABLE; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE TABLE realtime.messages (
    topic text NOT NULL,
    extension text NOT NULL,
    payload jsonb,
    event text,
    private boolean DEFAULT false,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    inserted_at timestamp without time zone DEFAULT now() NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    binary_payload bytea,
    skip_broadcast boolean DEFAULT false NOT NULL
)
PARTITION BY RANGE (inserted_at);


ALTER TABLE realtime.messages OWNER TO supabase_realtime_admin;

--
-- Name: schema_migrations; Type: TABLE; Schema: realtime; Owner: supabase_admin
--

CREATE TABLE realtime.schema_migrations (
    version bigint NOT NULL,
    inserted_at timestamp(0) without time zone DEFAULT now()
);


ALTER TABLE realtime.schema_migrations OWNER TO supabase_admin;

--
-- Name: subscription; Type: TABLE; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE TABLE realtime.subscription (
    id bigint NOT NULL,
    subscription_id uuid NOT NULL,
    entity regclass NOT NULL,
    filters realtime.user_defined_filter[] DEFAULT '{}'::realtime.user_defined_filter[] NOT NULL,
    claims jsonb NOT NULL,
    claims_role regrole GENERATED ALWAYS AS (realtime.to_regrole((claims ->> 'role'::text))) STORED NOT NULL,
    created_at timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    action_filter text DEFAULT '*'::text,
    selected_columns text[],
    CONSTRAINT subscription_action_filter_check CHECK ((action_filter = ANY (ARRAY['*'::text, 'INSERT'::text, 'UPDATE'::text, 'DELETE'::text])))
);


ALTER TABLE realtime.subscription OWNER TO supabase_realtime_admin;

--
-- Name: subscription_id_seq; Type: SEQUENCE; Schema: realtime; Owner: supabase_realtime_admin
--

ALTER TABLE realtime.subscription ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME realtime.subscription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: buckets; Type: TABLE; Schema: storage; Owner: supabase_storage_admin
--

CREATE TABLE storage.buckets (
    id text NOT NULL,
    name text NOT NULL,
    owner uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    public boolean DEFAULT false,
    avif_autodetection boolean DEFAULT false,
    file_size_limit bigint,
    allowed_mime_types text[],
    owner_id text,
    type storage.buckettype DEFAULT 'STANDARD'::storage.buckettype NOT NULL,
    versioning_status text DEFAULT 'DISABLED'::text NOT NULL,
    CONSTRAINT buckets_versioning_dark_check CHECK ((versioning_status = 'DISABLED'::text)),
    CONSTRAINT buckets_versioning_standard_only_check CHECK (((type = 'STANDARD'::storage.buckettype) OR (versioning_status = 'DISABLED'::text))),
    CONSTRAINT buckets_versioning_status_check CHECK ((versioning_status = ANY (ARRAY['DISABLED'::text, 'ENABLED'::text, 'SUSPENDED'::text])))
);


ALTER TABLE storage.buckets OWNER TO supabase_storage_admin;

--
-- Name: COLUMN buckets.owner; Type: COMMENT; Schema: storage; Owner: supabase_storage_admin
--

COMMENT ON COLUMN storage.buckets.owner IS 'Field is deprecated, use owner_id instead';


--
-- Name: buckets_analytics; Type: TABLE; Schema: storage; Owner: supabase_storage_admin
--

CREATE TABLE storage.buckets_analytics (
    name text NOT NULL,
    type storage.buckettype DEFAULT 'ANALYTICS'::storage.buckettype NOT NULL,
    format text DEFAULT 'ICEBERG'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE storage.buckets_analytics OWNER TO supabase_storage_admin;

--
-- Name: buckets_vectors; Type: TABLE; Schema: storage; Owner: supabase_storage_admin
--

CREATE TABLE storage.buckets_vectors (
    id text NOT NULL,
    type storage.buckettype DEFAULT 'VECTOR'::storage.buckettype NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE storage.buckets_vectors OWNER TO supabase_storage_admin;

--
-- Name: migrations; Type: TABLE; Schema: storage; Owner: supabase_storage_admin
--

CREATE TABLE storage.migrations (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    hash character varying(40) NOT NULL,
    executed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE storage.migrations OWNER TO supabase_storage_admin;

--
-- Name: objects; Type: TABLE; Schema: storage; Owner: supabase_storage_admin
--

CREATE TABLE storage.objects (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    bucket_id text,
    name text,
    owner uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_accessed_at timestamp with time zone DEFAULT now(),
    metadata jsonb,
    path_tokens text[] GENERATED ALWAYS AS (string_to_array(name, '/'::text)) STORED,
    version text,
    owner_id text,
    user_metadata jsonb,
    archived_at timestamp with time zone,
    is_delete_marker boolean DEFAULT false NOT NULL,
    is_versioned boolean DEFAULT false NOT NULL
);


ALTER TABLE storage.objects OWNER TO supabase_storage_admin;

--
-- Name: COLUMN objects.owner; Type: COMMENT; Schema: storage; Owner: supabase_storage_admin
--

COMMENT ON COLUMN storage.objects.owner IS 'Field is deprecated, use owner_id instead';


--
-- Name: s3_multipart_uploads; Type: TABLE; Schema: storage; Owner: supabase_storage_admin
--

CREATE TABLE storage.s3_multipart_uploads (
    id text NOT NULL,
    in_progress_size bigint DEFAULT 0 NOT NULL,
    upload_signature text NOT NULL,
    bucket_id text NOT NULL,
    key text NOT NULL COLLATE pg_catalog."C",
    version text NOT NULL,
    owner_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_metadata jsonb,
    metadata jsonb
);


ALTER TABLE storage.s3_multipart_uploads OWNER TO supabase_storage_admin;

--
-- Name: s3_multipart_uploads_parts; Type: TABLE; Schema: storage; Owner: supabase_storage_admin
--

CREATE TABLE storage.s3_multipart_uploads_parts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    upload_id text NOT NULL,
    size bigint DEFAULT 0 NOT NULL,
    part_number integer NOT NULL,
    bucket_id text NOT NULL,
    key text NOT NULL COLLATE pg_catalog."C",
    etag text NOT NULL,
    owner_id text,
    version text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE storage.s3_multipart_uploads_parts OWNER TO supabase_storage_admin;

--
-- Name: vector_indexes; Type: TABLE; Schema: storage; Owner: supabase_storage_admin
--

CREATE TABLE storage.vector_indexes (
    id text DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL COLLATE pg_catalog."C",
    bucket_id text NOT NULL,
    data_type text NOT NULL,
    dimension integer NOT NULL,
    distance_metric text NOT NULL,
    metadata_configuration jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE storage.vector_indexes OWNER TO supabase_storage_admin;

--
-- Name: refresh_tokens id; Type: DEFAULT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('auth.refresh_tokens_id_seq'::regclass);


--
-- Name: mfa_amr_claims amr_id_pk; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.mfa_amr_claims
    ADD CONSTRAINT amr_id_pk PRIMARY KEY (id);


--
-- Name: audit_log_entries audit_log_entries_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.audit_log_entries
    ADD CONSTRAINT audit_log_entries_pkey PRIMARY KEY (id);


--
-- Name: custom_oauth_providers custom_oauth_providers_identifier_key; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.custom_oauth_providers
    ADD CONSTRAINT custom_oauth_providers_identifier_key UNIQUE (identifier);


--
-- Name: custom_oauth_providers custom_oauth_providers_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.custom_oauth_providers
    ADD CONSTRAINT custom_oauth_providers_pkey PRIMARY KEY (id);


--
-- Name: flow_state flow_state_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.flow_state
    ADD CONSTRAINT flow_state_pkey PRIMARY KEY (id);


--
-- Name: identities identities_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.identities
    ADD CONSTRAINT identities_pkey PRIMARY KEY (id);


--
-- Name: identities identities_provider_id_provider_unique; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.identities
    ADD CONSTRAINT identities_provider_id_provider_unique UNIQUE (provider_id, provider);


--
-- Name: instances instances_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.instances
    ADD CONSTRAINT instances_pkey PRIMARY KEY (id);


--
-- Name: mfa_amr_claims mfa_amr_claims_session_id_authentication_method_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.mfa_amr_claims
    ADD CONSTRAINT mfa_amr_claims_session_id_authentication_method_pkey UNIQUE (session_id, authentication_method);


--
-- Name: mfa_challenges mfa_challenges_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.mfa_challenges
    ADD CONSTRAINT mfa_challenges_pkey PRIMARY KEY (id);


--
-- Name: mfa_factors mfa_factors_last_challenged_at_key; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.mfa_factors
    ADD CONSTRAINT mfa_factors_last_challenged_at_key UNIQUE (last_challenged_at);


--
-- Name: mfa_factors mfa_factors_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.mfa_factors
    ADD CONSTRAINT mfa_factors_pkey PRIMARY KEY (id);


--
-- Name: oauth_authorizations oauth_authorizations_authorization_code_key; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_authorization_code_key UNIQUE (authorization_code);


--
-- Name: oauth_authorizations oauth_authorizations_authorization_id_key; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_authorization_id_key UNIQUE (authorization_id);


--
-- Name: oauth_authorizations oauth_authorizations_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_pkey PRIMARY KEY (id);


--
-- Name: oauth_client_states oauth_client_states_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_client_states
    ADD CONSTRAINT oauth_client_states_pkey PRIMARY KEY (id);


--
-- Name: oauth_clients oauth_clients_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_clients
    ADD CONSTRAINT oauth_clients_pkey PRIMARY KEY (id);


--
-- Name: oauth_consents oauth_consents_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_pkey PRIMARY KEY (id);


--
-- Name: oauth_consents oauth_consents_user_client_unique; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_user_client_unique UNIQUE (user_id, client_id);


--
-- Name: one_time_tokens one_time_tokens_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.one_time_tokens
    ADD CONSTRAINT one_time_tokens_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_token_unique; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.refresh_tokens
    ADD CONSTRAINT refresh_tokens_token_unique UNIQUE (token);


--
-- Name: saml_providers saml_providers_entity_id_key; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.saml_providers
    ADD CONSTRAINT saml_providers_entity_id_key UNIQUE (entity_id);


--
-- Name: saml_providers saml_providers_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.saml_providers
    ADD CONSTRAINT saml_providers_pkey PRIMARY KEY (id);


--
-- Name: saml_relay_states saml_relay_states_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.saml_relay_states
    ADD CONSTRAINT saml_relay_states_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: sso_domains sso_domains_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.sso_domains
    ADD CONSTRAINT sso_domains_pkey PRIMARY KEY (id);


--
-- Name: sso_providers sso_providers_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.sso_providers
    ADD CONSTRAINT sso_providers_pkey PRIMARY KEY (id);


--
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.users
    ADD CONSTRAINT users_phone_key UNIQUE (phone);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: webauthn_challenges webauthn_challenges_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.webauthn_challenges
    ADD CONSTRAINT webauthn_challenges_pkey PRIMARY KEY (id);


--
-- Name: webauthn_credentials webauthn_credentials_pkey; Type: CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.webauthn_credentials
    ADD CONSTRAINT webauthn_credentials_pkey PRIMARY KEY (id);


--
-- Name: events Events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT "Events_pkey" PRIMARY KEY (id);


--
-- Name: candidate_review_log candidate_review_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_review_log
    ADD CONSTRAINT candidate_review_log_pkey PRIMARY KEY (id);


--
-- Name: candidate_review_log candidate_review_log_unique_filing; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_review_log
    ADD CONSTRAINT candidate_review_log_unique_filing UNIQUE (security_id, filing_date, accession_number);


--
-- Name: classification_corrections classification_corrections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classification_corrections
    ADD CONSTRAINT classification_corrections_pkey PRIMARY KEY (id);


--
-- Name: company_sentiment_timeline company_sentiment_timeline_entity_id_date_source_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_sentiment_timeline
    ADD CONSTRAINT company_sentiment_timeline_entity_id_date_source_key UNIQUE (entity_id, date, source);


--
-- Name: company_sentiment_timeline company_sentiment_timeline_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_sentiment_timeline
    ADD CONSTRAINT company_sentiment_timeline_pkey PRIMARY KEY (id);


--
-- Name: entities entities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT entities_pkey PRIMARY KEY (id);


--
-- Name: event_article_relationships event_article_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_article_relationships
    ADD CONSTRAINT event_article_relationships_pkey PRIMARY KEY (id);


--
-- Name: event_entity_relationships event_entity_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_entity_relationships
    ADD CONSTRAINT event_entity_relationships_pkey PRIMARY KEY (id);


--
-- Name: event_market_reactions_corrected event_market_reactions_corrected_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_market_reactions_corrected
    ADD CONSTRAINT event_market_reactions_corrected_pkey PRIMARY KEY (event_id);


--
-- Name: event_pre_context event_pre_context_event_id_entity_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_pre_context
    ADD CONSTRAINT event_pre_context_event_id_entity_id_key UNIQUE (event_id, entity_id);


--
-- Name: event_pre_context event_pre_context_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_pre_context
    ADD CONSTRAINT event_pre_context_pkey PRIMARY KEY (id);


--
-- Name: event_relationships event_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_relationships
    ADD CONSTRAINT event_relationships_pkey PRIMARY KEY (id);


--
-- Name: event_relationships event_relationships_source_event_id_target_event_id_relatio_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_relationships
    ADD CONSTRAINT event_relationships_source_event_id_target_event_id_relatio_key UNIQUE (source_event_id, target_event_id, relationship_type);


--
-- Name: event_tag_suggestions event_tag_suggestions_event_id_suggested_tag_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_tag_suggestions
    ADD CONSTRAINT event_tag_suggestions_event_id_suggested_tag_name_key UNIQUE (event_id, suggested_tag_name);


--
-- Name: event_tag_suggestions event_tag_suggestions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_tag_suggestions
    ADD CONSTRAINT event_tag_suggestions_pkey PRIMARY KEY (id);


--
-- Name: event_tags event_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_tags
    ADD CONSTRAINT event_tags_pkey PRIMARY KEY (event_id, tag_id);


--
-- Name: event_type_relationships event_type_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_type_relationships
    ADD CONSTRAINT event_type_relationships_pkey PRIMARY KEY (id);


--
-- Name: event_types event_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_types
    ADD CONSTRAINT event_types_pkey PRIMARY KEY (id);


--
-- Name: filing_ai_classifications filing_ai_classifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.filing_ai_classifications
    ADD CONSTRAINT filing_ai_classifications_pkey PRIMARY KEY (id);


--
-- Name: filing_ai_classifications filing_ai_classifications_ticker_filing_date_accession_numb_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.filing_ai_classifications
    ADD CONSTRAINT filing_ai_classifications_ticker_filing_date_accession_numb_key UNIQUE (ticker, filing_date, accession_number);


--
-- Name: financial_metrics financial_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_metrics
    ADD CONSTRAINT financial_metrics_pkey PRIMARY KEY (id);


--
-- Name: financial_metrics financial_metrics_security_id_period_type_period_end_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_metrics
    ADD CONSTRAINT financial_metrics_security_id_period_type_period_end_key UNIQUE (security_id, period_type, period_end);


--
-- Name: financial_statements financial_statements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_statements
    ADD CONSTRAINT financial_statements_pkey PRIMARY KEY (id);


--
-- Name: financial_statements financial_statements_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_statements
    ADD CONSTRAINT financial_statements_unique UNIQUE (security_id, statement_type, period_type, period_end);


--
-- Name: macro_data_releases macro_data_releases_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.macro_data_releases
    ADD CONSTRAINT macro_data_releases_pkey PRIMARY KEY (id);


--
-- Name: macro_data_releases macro_data_releases_unique_period; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.macro_data_releases
    ADD CONSTRAINT macro_data_releases_unique_period UNIQUE (series_id, period_covered, revision_marker);


--
-- Name: market_prices market_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_prices
    ADD CONSTRAINT market_prices_pkey PRIMARY KEY (id);


--
-- Name: market_prices market_prices_security_date_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_prices
    ADD CONSTRAINT market_prices_security_date_unique UNIQUE (security_id, price_date);


--
-- Name: market_regimes market_regimes_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_regimes
    ADD CONSTRAINT market_regimes_name_key UNIQUE (name);


--
-- Name: market_regimes market_regimes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_regimes
    ADD CONSTRAINT market_regimes_pkey PRIMARY KEY (id);


--
-- Name: news_ai_classifications news_ai_classifications_article_id_ticker_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_ai_classifications
    ADD CONSTRAINT news_ai_classifications_article_id_ticker_key UNIQUE (article_id, ticker);


--
-- Name: news_ai_classifications news_ai_classifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_ai_classifications
    ADD CONSTRAINT news_ai_classifications_pkey PRIMARY KEY (id);


--
-- Name: news_article_entities news_article_entities_article_id_ticker_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_article_entities
    ADD CONSTRAINT news_article_entities_article_id_ticker_key UNIQUE (article_id, ticker);


--
-- Name: news_article_entities news_article_entities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_article_entities
    ADD CONSTRAINT news_article_entities_pkey PRIMARY KEY (id);


--
-- Name: news_articles news_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_articles
    ADD CONSTRAINT news_articles_pkey PRIMARY KEY (id);


--
-- Name: news_candidate_events news_candidate_events_article_id_ticker_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_candidate_events
    ADD CONSTRAINT news_candidate_events_article_id_ticker_key UNIQUE (article_id, ticker);


--
-- Name: news_candidate_events news_candidate_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_candidate_events
    ADD CONSTRAINT news_candidate_events_pkey PRIMARY KEY (id);


--
-- Name: pattern_significance_tests pattern_significance_tests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pattern_significance_tests
    ADD CONSTRAINT pattern_significance_tests_pkey PRIMARY KEY (id);


--
-- Name: pattern_significance_tests pattern_significance_tests_tag_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pattern_significance_tests
    ADD CONSTRAINT pattern_significance_tests_tag_name_key UNIQUE (tag_name);


--
-- Name: sec_8k_filings sec_8k_filings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sec_8k_filings
    ADD CONSTRAINT sec_8k_filings_pkey PRIMARY KEY (id);


--
-- Name: sec_8k_filings sec_8k_filings_security_id_accession_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sec_8k_filings
    ADD CONSTRAINT sec_8k_filings_security_id_accession_number_key UNIQUE (security_id, accession_number);


--
-- Name: sec_filings sec_filings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sec_filings
    ADD CONSTRAINT sec_filings_pkey PRIMARY KEY (id);


--
-- Name: sec_filings sec_filings_security_id_accession_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sec_filings
    ADD CONSTRAINT sec_filings_security_id_accession_number_key UNIQUE (security_id, accession_number);


--
-- Name: securities securities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.securities
    ADD CONSTRAINT securities_pkey PRIMARY KEY (id);


--
-- Name: securities securities_ticker_exchange_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.securities
    ADD CONSTRAINT securities_ticker_exchange_unique UNIQUE (ticker, exchange);


--
-- Name: tags tags_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_name_key UNIQUE (name);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: messages messages_payload_exclusive; Type: CHECK CONSTRAINT; Schema: realtime; Owner: supabase_realtime_admin
--

ALTER TABLE realtime.messages
    ADD CONSTRAINT messages_payload_exclusive CHECK (((payload IS NULL) OR (binary_payload IS NULL))) NOT VALID;


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: realtime; Owner: supabase_realtime_admin
--

ALTER TABLE ONLY realtime.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id, inserted_at);


--
-- Name: subscription pk_subscription; Type: CONSTRAINT; Schema: realtime; Owner: supabase_realtime_admin
--

ALTER TABLE ONLY realtime.subscription
    ADD CONSTRAINT pk_subscription PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: realtime; Owner: supabase_admin
--

ALTER TABLE ONLY realtime.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: buckets_analytics buckets_analytics_pkey; Type: CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.buckets_analytics
    ADD CONSTRAINT buckets_analytics_pkey PRIMARY KEY (id);


--
-- Name: buckets buckets_pkey; Type: CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.buckets
    ADD CONSTRAINT buckets_pkey PRIMARY KEY (id);


--
-- Name: buckets_vectors buckets_vectors_pkey; Type: CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.buckets_vectors
    ADD CONSTRAINT buckets_vectors_pkey PRIMARY KEY (id);


--
-- Name: migrations migrations_name_key; Type: CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.migrations
    ADD CONSTRAINT migrations_name_key UNIQUE (name);


--
-- Name: migrations migrations_pkey; Type: CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.migrations
    ADD CONSTRAINT migrations_pkey PRIMARY KEY (id);


--
-- Name: objects objects_pkey; Type: CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.objects
    ADD CONSTRAINT objects_pkey PRIMARY KEY (id);


--
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_pkey; Type: CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.s3_multipart_uploads_parts
    ADD CONSTRAINT s3_multipart_uploads_parts_pkey PRIMARY KEY (id);


--
-- Name: s3_multipart_uploads s3_multipart_uploads_pkey; Type: CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.s3_multipart_uploads
    ADD CONSTRAINT s3_multipart_uploads_pkey PRIMARY KEY (id);


--
-- Name: vector_indexes vector_indexes_pkey; Type: CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.vector_indexes
    ADD CONSTRAINT vector_indexes_pkey PRIMARY KEY (id);


--
-- Name: audit_logs_instance_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX audit_logs_instance_id_idx ON auth.audit_log_entries USING btree (instance_id);


--
-- Name: confirmation_token_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX confirmation_token_idx ON auth.users USING btree (confirmation_token) WHERE ((confirmation_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: custom_oauth_providers_created_at_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX custom_oauth_providers_created_at_idx ON auth.custom_oauth_providers USING btree (created_at);


--
-- Name: custom_oauth_providers_enabled_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX custom_oauth_providers_enabled_idx ON auth.custom_oauth_providers USING btree (enabled);


--
-- Name: custom_oauth_providers_identifier_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX custom_oauth_providers_identifier_idx ON auth.custom_oauth_providers USING btree (identifier);


--
-- Name: custom_oauth_providers_provider_type_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX custom_oauth_providers_provider_type_idx ON auth.custom_oauth_providers USING btree (provider_type);


--
-- Name: email_change_token_current_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX email_change_token_current_idx ON auth.users USING btree (email_change_token_current) WHERE ((email_change_token_current)::text !~ '^[0-9 ]*$'::text);


--
-- Name: email_change_token_new_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX email_change_token_new_idx ON auth.users USING btree (email_change_token_new) WHERE ((email_change_token_new)::text !~ '^[0-9 ]*$'::text);


--
-- Name: factor_id_created_at_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX factor_id_created_at_idx ON auth.mfa_factors USING btree (user_id, created_at);


--
-- Name: flow_state_created_at_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX flow_state_created_at_idx ON auth.flow_state USING btree (created_at DESC);


--
-- Name: identities_email_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX identities_email_idx ON auth.identities USING btree (email text_pattern_ops);


--
-- Name: INDEX identities_email_idx; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON INDEX auth.identities_email_idx IS 'Auth: Ensures indexed queries on the email column';


--
-- Name: identities_user_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX identities_user_id_idx ON auth.identities USING btree (user_id);


--
-- Name: idx_auth_code; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX idx_auth_code ON auth.flow_state USING btree (auth_code);


--
-- Name: idx_oauth_client_states_created_at; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX idx_oauth_client_states_created_at ON auth.oauth_client_states USING btree (created_at);


--
-- Name: idx_user_id_auth_method; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX idx_user_id_auth_method ON auth.flow_state USING btree (user_id, authentication_method);


--
-- Name: idx_users_created_at_desc; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX idx_users_created_at_desc ON auth.users USING btree (created_at DESC);


--
-- Name: idx_users_email; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX idx_users_email ON auth.users USING btree (email);


--
-- Name: idx_users_last_sign_in_at_desc; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX idx_users_last_sign_in_at_desc ON auth.users USING btree (last_sign_in_at DESC);


--
-- Name: idx_users_name; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX idx_users_name ON auth.users USING btree (((raw_user_meta_data ->> 'name'::text))) WHERE ((raw_user_meta_data ->> 'name'::text) IS NOT NULL);


--
-- Name: mfa_challenge_created_at_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX mfa_challenge_created_at_idx ON auth.mfa_challenges USING btree (created_at DESC);


--
-- Name: mfa_factors_user_friendly_name_unique; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX mfa_factors_user_friendly_name_unique ON auth.mfa_factors USING btree (friendly_name, user_id) WHERE (TRIM(BOTH FROM friendly_name) <> ''::text);


--
-- Name: mfa_factors_user_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX mfa_factors_user_id_idx ON auth.mfa_factors USING btree (user_id);


--
-- Name: oauth_auth_pending_exp_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX oauth_auth_pending_exp_idx ON auth.oauth_authorizations USING btree (expires_at) WHERE (status = 'pending'::auth.oauth_authorization_status);


--
-- Name: oauth_clients_deleted_at_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX oauth_clients_deleted_at_idx ON auth.oauth_clients USING btree (deleted_at);


--
-- Name: oauth_consents_active_client_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX oauth_consents_active_client_idx ON auth.oauth_consents USING btree (client_id) WHERE (revoked_at IS NULL);


--
-- Name: oauth_consents_active_user_client_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX oauth_consents_active_user_client_idx ON auth.oauth_consents USING btree (user_id, client_id) WHERE (revoked_at IS NULL);


--
-- Name: oauth_consents_user_order_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX oauth_consents_user_order_idx ON auth.oauth_consents USING btree (user_id, granted_at DESC);


--
-- Name: one_time_tokens_relates_to_hash_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX one_time_tokens_relates_to_hash_idx ON auth.one_time_tokens USING hash (relates_to);


--
-- Name: one_time_tokens_token_hash_hash_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX one_time_tokens_token_hash_hash_idx ON auth.one_time_tokens USING hash (token_hash);


--
-- Name: one_time_tokens_user_id_token_type_key; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX one_time_tokens_user_id_token_type_key ON auth.one_time_tokens USING btree (user_id, token_type);


--
-- Name: reauthentication_token_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX reauthentication_token_idx ON auth.users USING btree (reauthentication_token) WHERE ((reauthentication_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: recovery_token_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX recovery_token_idx ON auth.users USING btree (recovery_token) WHERE ((recovery_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: refresh_tokens_instance_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX refresh_tokens_instance_id_idx ON auth.refresh_tokens USING btree (instance_id);


--
-- Name: refresh_tokens_instance_id_user_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX refresh_tokens_instance_id_user_id_idx ON auth.refresh_tokens USING btree (instance_id, user_id);


--
-- Name: refresh_tokens_parent_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX refresh_tokens_parent_idx ON auth.refresh_tokens USING btree (parent);


--
-- Name: refresh_tokens_session_id_revoked_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX refresh_tokens_session_id_revoked_idx ON auth.refresh_tokens USING btree (session_id, revoked);


--
-- Name: refresh_tokens_updated_at_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX refresh_tokens_updated_at_idx ON auth.refresh_tokens USING btree (updated_at DESC);


--
-- Name: saml_providers_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX saml_providers_sso_provider_id_idx ON auth.saml_providers USING btree (sso_provider_id);


--
-- Name: saml_relay_states_created_at_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX saml_relay_states_created_at_idx ON auth.saml_relay_states USING btree (created_at DESC);


--
-- Name: saml_relay_states_for_email_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX saml_relay_states_for_email_idx ON auth.saml_relay_states USING btree (for_email);


--
-- Name: saml_relay_states_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX saml_relay_states_sso_provider_id_idx ON auth.saml_relay_states USING btree (sso_provider_id);


--
-- Name: sessions_not_after_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX sessions_not_after_idx ON auth.sessions USING btree (not_after DESC);


--
-- Name: sessions_oauth_client_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX sessions_oauth_client_id_idx ON auth.sessions USING btree (oauth_client_id);


--
-- Name: sessions_user_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX sessions_user_id_idx ON auth.sessions USING btree (user_id);


--
-- Name: sso_domains_domain_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX sso_domains_domain_idx ON auth.sso_domains USING btree (lower(domain));


--
-- Name: sso_domains_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX sso_domains_sso_provider_id_idx ON auth.sso_domains USING btree (sso_provider_id);


--
-- Name: sso_providers_resource_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX sso_providers_resource_id_idx ON auth.sso_providers USING btree (lower(resource_id));


--
-- Name: sso_providers_resource_id_pattern_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX sso_providers_resource_id_pattern_idx ON auth.sso_providers USING btree (resource_id text_pattern_ops);


--
-- Name: unique_phone_factor_per_user; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX unique_phone_factor_per_user ON auth.mfa_factors USING btree (user_id, phone);


--
-- Name: user_id_created_at_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX user_id_created_at_idx ON auth.sessions USING btree (user_id, created_at);


--
-- Name: users_email_partial_key; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX users_email_partial_key ON auth.users USING btree (email) WHERE (is_sso_user = false);


--
-- Name: INDEX users_email_partial_key; Type: COMMENT; Schema: auth; Owner: supabase_auth_admin
--

COMMENT ON INDEX auth.users_email_partial_key IS 'Auth: A partial unique index that applies only when is_sso_user is false';


--
-- Name: users_instance_id_email_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX users_instance_id_email_idx ON auth.users USING btree (instance_id, lower((email)::text));


--
-- Name: users_instance_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX users_instance_id_idx ON auth.users USING btree (instance_id);


--
-- Name: users_is_anonymous_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX users_is_anonymous_idx ON auth.users USING btree (is_anonymous);


--
-- Name: webauthn_challenges_expires_at_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX webauthn_challenges_expires_at_idx ON auth.webauthn_challenges USING btree (expires_at);


--
-- Name: webauthn_challenges_user_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX webauthn_challenges_user_id_idx ON auth.webauthn_challenges USING btree (user_id);


--
-- Name: webauthn_credentials_credential_id_key; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE UNIQUE INDEX webauthn_credentials_credential_id_key ON auth.webauthn_credentials USING btree (credential_id);


--
-- Name: webauthn_credentials_user_id_idx; Type: INDEX; Schema: auth; Owner: supabase_auth_admin
--

CREATE INDEX webauthn_credentials_user_id_idx ON auth.webauthn_credentials USING btree (user_id);


--
-- Name: event_tags_tag_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX event_tags_tag_id_idx ON public.event_tags USING btree (tag_id);


--
-- Name: idx_ai_class_flagged; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ai_class_flagged ON public.news_ai_classifications USING btree (flagged_for_review) WHERE (flagged_for_review = true);


--
-- Name: idx_ai_class_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ai_class_ticker ON public.news_ai_classifications USING btree (ticker);


--
-- Name: idx_crl_accession; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crl_accession ON public.candidate_review_log USING btree (accession_number, verdict);


--
-- Name: idx_eer_entity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eer_entity ON public.event_entity_relationships USING btree (entity_id);


--
-- Name: idx_eer_event; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eer_event ON public.event_entity_relationships USING btree (event_id);


--
-- Name: idx_event_relationships_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_event_relationships_source ON public.event_relationships USING btree (source_event_id);


--
-- Name: idx_event_relationships_target; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_event_relationships_target ON public.event_relationships USING btree (target_event_id);


--
-- Name: idx_filing_class_flagged; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_filing_class_flagged ON public.filing_ai_classifications USING btree (flagged_for_review) WHERE (flagged_for_review = true);


--
-- Name: idx_filing_class_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_filing_class_ticker ON public.filing_ai_classifications USING btree (ticker);


--
-- Name: idx_financial_metrics_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_financial_metrics_period ON public.financial_metrics USING btree (period_end);


--
-- Name: idx_financial_metrics_security; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_financial_metrics_security ON public.financial_metrics USING btree (security_id);


--
-- Name: idx_financial_metrics_security_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_financial_metrics_security_period ON public.financial_metrics USING btree (security_id, period_type, period_end);


--
-- Name: idx_growth_classified_security_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_growth_classified_security_period ON public.financial_growth_classified USING btree (security_id, period_type, fiscal_year, fiscal_quarter);


--
-- Name: idx_growth_classified_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_growth_classified_ticker ON public.financial_growth_classified USING btree (ticker);


--
-- Name: idx_macro_data_releases_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_macro_data_releases_date ON public.macro_data_releases USING btree (release_date);


--
-- Name: idx_macro_data_releases_series; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_macro_data_releases_series ON public.macro_data_releases USING btree (series_id);


--
-- Name: idx_news_article_entities_match_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_news_article_entities_match_score ON public.news_article_entities USING btree (match_score);


--
-- Name: idx_news_article_entities_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_news_article_entities_ticker ON public.news_article_entities USING btree (ticker);


--
-- Name: idx_news_candidate_events_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_news_candidate_events_ticker ON public.news_candidate_events USING btree (ticker);


--
-- Name: idx_news_candidate_events_verdict; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_news_candidate_events_verdict ON public.news_candidate_events USING btree (verdict);


--
-- Name: idx_pre_context_firm_state; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pre_context_firm_state ON public.event_pre_context USING btree (firm_state_label);


--
-- Name: idx_pre_context_regime; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pre_context_regime ON public.event_pre_context USING btree (regime_id);


--
-- Name: idx_sec_8k_filing_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sec_8k_filing_date ON public.sec_8k_filings USING btree (filing_date);


--
-- Name: idx_sec_8k_promoted; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sec_8k_promoted ON public.sec_8k_filings USING btree (promoted_to_event);


--
-- Name: idx_sec_8k_security; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sec_8k_security ON public.sec_8k_filings USING btree (security_id);


--
-- Name: idx_sec_filings_accession; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sec_filings_accession ON public.sec_filings USING btree (accession_number);


--
-- Name: idx_sec_filings_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sec_filings_period ON public.sec_filings USING btree (security_id, period_end);


--
-- Name: idx_sec_filings_security_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sec_filings_security_date ON public.sec_filings USING btree (security_id, filing_date);


--
-- Name: idx_sentiment_entity_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sentiment_entity_date ON public.company_sentiment_timeline USING btree (entity_id, date);


--
-- Name: idx_tag_sugg_flagged; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tag_sugg_flagged ON public.event_tag_suggestions USING btree (flagged_for_review) WHERE (flagged_for_review = true);


--
-- Name: securities_ticker_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX securities_ticker_idx ON public.securities USING btree (ticker);


--
-- Name: ix_realtime_subscription_entity; Type: INDEX; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE INDEX ix_realtime_subscription_entity ON realtime.subscription USING btree (entity);


--
-- Name: messages_inserted_at_topic_index; Type: INDEX; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE INDEX messages_inserted_at_topic_index ON ONLY realtime.messages USING btree (inserted_at DESC, topic) WHERE ((extension = 'broadcast'::text) AND (private IS TRUE));


--
-- Name: subscription_subscription_id_entity_filters_action_filter_selec; Type: INDEX; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE UNIQUE INDEX subscription_subscription_id_entity_filters_action_filter_selec ON realtime.subscription USING btree (subscription_id, entity, filters, action_filter, COALESCE(selected_columns, '{}'::text[]));


--
-- Name: bname; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE UNIQUE INDEX bname ON storage.buckets USING btree (name);


--
-- Name: bucketid_objname; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE UNIQUE INDEX bucketid_objname ON storage.objects USING btree (bucket_id, name);


--
-- Name: buckets_analytics_unique_name_idx; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE UNIQUE INDEX buckets_analytics_unique_name_idx ON storage.buckets_analytics USING btree (name) WHERE (deleted_at IS NULL);


--
-- Name: idx_multipart_uploads_list; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE INDEX idx_multipart_uploads_list ON storage.s3_multipart_uploads USING btree (bucket_id, key, created_at);


--
-- Name: idx_objects_bucket_id_name; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE INDEX idx_objects_bucket_id_name ON storage.objects USING btree (bucket_id, name COLLATE "C");


--
-- Name: idx_objects_bucket_id_name_lower; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE INDEX idx_objects_bucket_id_name_lower ON storage.objects USING btree (bucket_id, lower(name) COLLATE "C");


--
-- Name: idx_objects_current_version; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE UNIQUE INDEX idx_objects_current_version ON storage.objects USING btree (bucket_id, name COLLATE "C") WHERE (archived_at IS NULL);


--
-- Name: idx_objects_null_version; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE UNIQUE INDEX idx_objects_null_version ON storage.objects USING btree (bucket_id, name COLLATE "C") WHERE (NOT is_versioned);


--
-- Name: name_prefix_search; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE INDEX name_prefix_search ON storage.objects USING btree (name text_pattern_ops);


--
-- Name: objects_bucket_id_name_version_key; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE UNIQUE INDEX objects_bucket_id_name_version_key ON storage.objects USING btree (bucket_id, name COLLATE "C", version) NULLS NOT DISTINCT;


--
-- Name: vector_indexes_name_bucket_id_idx; Type: INDEX; Schema: storage; Owner: supabase_storage_admin
--

CREATE UNIQUE INDEX vector_indexes_name_bucket_id_idx ON storage.vector_indexes USING btree (name, bucket_id);


--
-- Name: subscription tr_check_filters; Type: TRIGGER; Schema: realtime; Owner: supabase_realtime_admin
--

CREATE TRIGGER tr_check_filters BEFORE INSERT OR UPDATE ON realtime.subscription FOR EACH ROW EXECUTE FUNCTION realtime.subscription_check_filters();


--
-- Name: buckets enforce_bucket_name_length_trigger; Type: TRIGGER; Schema: storage; Owner: supabase_storage_admin
--

CREATE TRIGGER enforce_bucket_name_length_trigger BEFORE INSERT OR UPDATE OF name ON storage.buckets FOR EACH ROW EXECUTE FUNCTION storage.enforce_bucket_name_length();


--
-- Name: buckets protect_buckets_delete; Type: TRIGGER; Schema: storage; Owner: supabase_storage_admin
--

CREATE TRIGGER protect_buckets_delete BEFORE DELETE ON storage.buckets FOR EACH STATEMENT EXECUTE FUNCTION storage.protect_delete();


--
-- Name: objects protect_objects_delete; Type: TRIGGER; Schema: storage; Owner: supabase_storage_admin
--

CREATE TRIGGER protect_objects_delete BEFORE DELETE ON storage.objects FOR EACH STATEMENT EXECUTE FUNCTION storage.protect_delete();


--
-- Name: objects update_objects_updated_at; Type: TRIGGER; Schema: storage; Owner: supabase_storage_admin
--

CREATE TRIGGER update_objects_updated_at BEFORE UPDATE ON storage.objects FOR EACH ROW EXECUTE FUNCTION storage.update_updated_at_column();


--
-- Name: identities identities_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.identities
    ADD CONSTRAINT identities_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: mfa_amr_claims mfa_amr_claims_session_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.mfa_amr_claims
    ADD CONSTRAINT mfa_amr_claims_session_id_fkey FOREIGN KEY (session_id) REFERENCES auth.sessions(id) ON DELETE CASCADE;


--
-- Name: mfa_challenges mfa_challenges_auth_factor_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.mfa_challenges
    ADD CONSTRAINT mfa_challenges_auth_factor_id_fkey FOREIGN KEY (factor_id) REFERENCES auth.mfa_factors(id) ON DELETE CASCADE;


--
-- Name: mfa_factors mfa_factors_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.mfa_factors
    ADD CONSTRAINT mfa_factors_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: oauth_authorizations oauth_authorizations_client_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_client_id_fkey FOREIGN KEY (client_id) REFERENCES auth.oauth_clients(id) ON DELETE CASCADE;


--
-- Name: oauth_authorizations oauth_authorizations_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: oauth_consents oauth_consents_client_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_client_id_fkey FOREIGN KEY (client_id) REFERENCES auth.oauth_clients(id) ON DELETE CASCADE;


--
-- Name: oauth_consents oauth_consents_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: one_time_tokens one_time_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.one_time_tokens
    ADD CONSTRAINT one_time_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: refresh_tokens refresh_tokens_session_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.refresh_tokens
    ADD CONSTRAINT refresh_tokens_session_id_fkey FOREIGN KEY (session_id) REFERENCES auth.sessions(id) ON DELETE CASCADE;


--
-- Name: saml_providers saml_providers_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.saml_providers
    ADD CONSTRAINT saml_providers_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE;


--
-- Name: saml_relay_states saml_relay_states_flow_state_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.saml_relay_states
    ADD CONSTRAINT saml_relay_states_flow_state_id_fkey FOREIGN KEY (flow_state_id) REFERENCES auth.flow_state(id) ON DELETE CASCADE;


--
-- Name: saml_relay_states saml_relay_states_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.saml_relay_states
    ADD CONSTRAINT saml_relay_states_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_oauth_client_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.sessions
    ADD CONSTRAINT sessions_oauth_client_id_fkey FOREIGN KEY (oauth_client_id) REFERENCES auth.oauth_clients(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: sso_domains sso_domains_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.sso_domains
    ADD CONSTRAINT sso_domains_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE;


--
-- Name: webauthn_challenges webauthn_challenges_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.webauthn_challenges
    ADD CONSTRAINT webauthn_challenges_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: webauthn_credentials webauthn_credentials_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE ONLY auth.webauthn_credentials
    ADD CONSTRAINT webauthn_credentials_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: candidate_review_log candidate_review_log_linked_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_review_log
    ADD CONSTRAINT candidate_review_log_linked_event_id_fkey FOREIGN KEY (linked_event_id) REFERENCES public.events(id);


--
-- Name: candidate_review_log candidate_review_log_security_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidate_review_log
    ADD CONSTRAINT candidate_review_log_security_id_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id);


--
-- Name: classification_corrections classification_corrections_linked_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classification_corrections
    ADD CONSTRAINT classification_corrections_linked_event_id_fkey FOREIGN KEY (linked_event_id) REFERENCES public.events(id);


--
-- Name: company_sentiment_timeline company_sentiment_timeline_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_sentiment_timeline
    ADD CONSTRAINT company_sentiment_timeline_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id);


--
-- Name: event_article_relationships event_article_relationships_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_article_relationships
    ADD CONSTRAINT event_article_relationships_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.news_articles(id);


--
-- Name: event_article_relationships event_article_relationships_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_article_relationships
    ADD CONSTRAINT event_article_relationships_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: event_entity_relationships event_entity_relationships_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_entity_relationships
    ADD CONSTRAINT event_entity_relationships_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id);


--
-- Name: event_entity_relationships event_entity_relationships_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_entity_relationships
    ADD CONSTRAINT event_entity_relationships_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: event_market_reactions_corrected event_market_reactions_corrected_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_market_reactions_corrected
    ADD CONSTRAINT event_market_reactions_corrected_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: event_pre_context event_pre_context_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_pre_context
    ADD CONSTRAINT event_pre_context_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id);


--
-- Name: event_pre_context event_pre_context_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_pre_context
    ADD CONSTRAINT event_pre_context_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: event_pre_context event_pre_context_regime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_pre_context
    ADD CONSTRAINT event_pre_context_regime_id_fkey FOREIGN KEY (regime_id) REFERENCES public.market_regimes(id);


--
-- Name: event_relationships event_relationships_source_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_relationships
    ADD CONSTRAINT event_relationships_source_event_id_fkey FOREIGN KEY (source_event_id) REFERENCES public.events(id);


--
-- Name: event_relationships event_relationships_target_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_relationships
    ADD CONSTRAINT event_relationships_target_event_id_fkey FOREIGN KEY (target_event_id) REFERENCES public.events(id);


--
-- Name: event_tag_suggestions event_tag_suggestions_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_tag_suggestions
    ADD CONSTRAINT event_tag_suggestions_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: event_tags event_tags_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_tags
    ADD CONSTRAINT event_tags_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id) ON DELETE CASCADE;


--
-- Name: event_tags event_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_tags
    ADD CONSTRAINT event_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id) ON DELETE CASCADE;


--
-- Name: event_type_relationships event_type_relationships_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_type_relationships
    ADD CONSTRAINT event_type_relationships_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: event_type_relationships event_type_relationships_event_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_type_relationships
    ADD CONSTRAINT event_type_relationships_event_type_id_fkey FOREIGN KEY (event_type_id) REFERENCES public.event_types(id);


--
-- Name: filing_ai_classifications filing_ai_classifications_linked_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.filing_ai_classifications
    ADD CONSTRAINT filing_ai_classifications_linked_event_id_fkey FOREIGN KEY (linked_event_id) REFERENCES public.events(id);


--
-- Name: financial_metrics financial_metrics_financial_statement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_metrics
    ADD CONSTRAINT financial_metrics_financial_statement_id_fkey FOREIGN KEY (financial_statement_id) REFERENCES public.financial_statements(id) ON DELETE CASCADE;


--
-- Name: financial_metrics financial_metrics_security_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_metrics
    ADD CONSTRAINT financial_metrics_security_id_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id) ON DELETE CASCADE;


--
-- Name: financial_statements financial_statements_security_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.financial_statements
    ADD CONSTRAINT financial_statements_security_id_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id);


--
-- Name: market_prices market_prices_security_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_prices
    ADD CONSTRAINT market_prices_security_id_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id);


--
-- Name: news_ai_classifications news_ai_classifications_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_ai_classifications
    ADD CONSTRAINT news_ai_classifications_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.news_articles(id);


--
-- Name: news_ai_classifications news_ai_classifications_linked_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_ai_classifications
    ADD CONSTRAINT news_ai_classifications_linked_event_id_fkey FOREIGN KEY (linked_event_id) REFERENCES public.events(id);


--
-- Name: news_article_entities news_article_entities_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_article_entities
    ADD CONSTRAINT news_article_entities_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.news_articles(id) ON DELETE CASCADE;


--
-- Name: news_candidate_events news_candidate_events_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_candidate_events
    ADD CONSTRAINT news_candidate_events_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.news_articles(id);


--
-- Name: news_candidate_events news_candidate_events_linked_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news_candidate_events
    ADD CONSTRAINT news_candidate_events_linked_event_id_fkey FOREIGN KEY (linked_event_id) REFERENCES public.events(id);


--
-- Name: sec_8k_filings sec_8k_filings_security_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sec_8k_filings
    ADD CONSTRAINT sec_8k_filings_security_id_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id);


--
-- Name: sec_filings sec_filings_security_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sec_filings
    ADD CONSTRAINT sec_filings_security_id_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id);


--
-- Name: securities securities_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.securities
    ADD CONSTRAINT securities_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id);


--
-- Name: objects objects_bucketId_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.objects
    ADD CONSTRAINT "objects_bucketId_fkey" FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: s3_multipart_uploads s3_multipart_uploads_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.s3_multipart_uploads
    ADD CONSTRAINT s3_multipart_uploads_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.s3_multipart_uploads_parts
    ADD CONSTRAINT s3_multipart_uploads_parts_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_upload_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.s3_multipart_uploads_parts
    ADD CONSTRAINT s3_multipart_uploads_parts_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES storage.s3_multipart_uploads(id) ON DELETE CASCADE;


--
-- Name: vector_indexes vector_indexes_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE ONLY storage.vector_indexes
    ADD CONSTRAINT vector_indexes_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets_vectors(id);


--
-- Name: audit_log_entries; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.audit_log_entries ENABLE ROW LEVEL SECURITY;

--
-- Name: flow_state; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.flow_state ENABLE ROW LEVEL SECURITY;

--
-- Name: identities; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.identities ENABLE ROW LEVEL SECURITY;

--
-- Name: instances; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.instances ENABLE ROW LEVEL SECURITY;

--
-- Name: mfa_amr_claims; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.mfa_amr_claims ENABLE ROW LEVEL SECURITY;

--
-- Name: mfa_challenges; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.mfa_challenges ENABLE ROW LEVEL SECURITY;

--
-- Name: mfa_factors; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.mfa_factors ENABLE ROW LEVEL SECURITY;

--
-- Name: one_time_tokens; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.one_time_tokens ENABLE ROW LEVEL SECURITY;

--
-- Name: refresh_tokens; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.refresh_tokens ENABLE ROW LEVEL SECURITY;

--
-- Name: saml_providers; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.saml_providers ENABLE ROW LEVEL SECURITY;

--
-- Name: saml_relay_states; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.saml_relay_states ENABLE ROW LEVEL SECURITY;

--
-- Name: schema_migrations; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.schema_migrations ENABLE ROW LEVEL SECURITY;

--
-- Name: sessions; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.sessions ENABLE ROW LEVEL SECURITY;

--
-- Name: sso_domains; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.sso_domains ENABLE ROW LEVEL SECURITY;

--
-- Name: sso_providers; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.sso_providers ENABLE ROW LEVEL SECURITY;

--
-- Name: users; Type: ROW SECURITY; Schema: auth; Owner: supabase_auth_admin
--

ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

--
-- Name: candidate_review_log; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.candidate_review_log ENABLE ROW LEVEL SECURITY;

--
-- Name: classification_corrections; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.classification_corrections ENABLE ROW LEVEL SECURITY;

--
-- Name: company_sentiment_timeline; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.company_sentiment_timeline ENABLE ROW LEVEL SECURITY;

--
-- Name: entities; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.entities ENABLE ROW LEVEL SECURITY;

--
-- Name: event_article_relationships; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.event_article_relationships ENABLE ROW LEVEL SECURITY;

--
-- Name: event_entity_relationships; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.event_entity_relationships ENABLE ROW LEVEL SECURITY;

--
-- Name: event_market_reactions_corrected; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.event_market_reactions_corrected ENABLE ROW LEVEL SECURITY;

--
-- Name: event_pre_context; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.event_pre_context ENABLE ROW LEVEL SECURITY;

--
-- Name: event_relationships; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.event_relationships ENABLE ROW LEVEL SECURITY;

--
-- Name: event_tag_suggestions; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.event_tag_suggestions ENABLE ROW LEVEL SECURITY;

--
-- Name: event_tags; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.event_tags ENABLE ROW LEVEL SECURITY;

--
-- Name: event_type_relationships; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.event_type_relationships ENABLE ROW LEVEL SECURITY;

--
-- Name: event_types; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.event_types ENABLE ROW LEVEL SECURITY;

--
-- Name: events; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;

--
-- Name: filing_ai_classifications; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.filing_ai_classifications ENABLE ROW LEVEL SECURITY;

--
-- Name: financial_growth_classified; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.financial_growth_classified ENABLE ROW LEVEL SECURITY;

--
-- Name: financial_metrics; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.financial_metrics ENABLE ROW LEVEL SECURITY;

--
-- Name: financial_statements; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.financial_statements ENABLE ROW LEVEL SECURITY;

--
-- Name: macro_data_releases; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.macro_data_releases ENABLE ROW LEVEL SECURITY;

--
-- Name: market_prices; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.market_prices ENABLE ROW LEVEL SECURITY;

--
-- Name: market_regimes; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.market_regimes ENABLE ROW LEVEL SECURITY;

--
-- Name: news_ai_classifications; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.news_ai_classifications ENABLE ROW LEVEL SECURITY;

--
-- Name: news_article_entities; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.news_article_entities ENABLE ROW LEVEL SECURITY;

--
-- Name: news_articles; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.news_articles ENABLE ROW LEVEL SECURITY;

--
-- Name: news_candidate_events; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.news_candidate_events ENABLE ROW LEVEL SECURITY;

--
-- Name: pattern_significance_tests; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.pattern_significance_tests ENABLE ROW LEVEL SECURITY;

--
-- Name: sec_8k_filings; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.sec_8k_filings ENABLE ROW LEVEL SECURITY;

--
-- Name: sec_filings; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.sec_filings ENABLE ROW LEVEL SECURITY;

--
-- Name: securities; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.securities ENABLE ROW LEVEL SECURITY;

--
-- Name: tags; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.tags ENABLE ROW LEVEL SECURITY;

--
-- Name: messages; Type: ROW SECURITY; Schema: realtime; Owner: supabase_realtime_admin
--

ALTER TABLE realtime.messages ENABLE ROW LEVEL SECURITY;

--
-- Name: buckets; Type: ROW SECURITY; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE storage.buckets ENABLE ROW LEVEL SECURITY;

--
-- Name: buckets_analytics; Type: ROW SECURITY; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE storage.buckets_analytics ENABLE ROW LEVEL SECURITY;

--
-- Name: buckets_vectors; Type: ROW SECURITY; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE storage.buckets_vectors ENABLE ROW LEVEL SECURITY;

--
-- Name: migrations; Type: ROW SECURITY; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE storage.migrations ENABLE ROW LEVEL SECURITY;

--
-- Name: objects; Type: ROW SECURITY; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

--
-- Name: s3_multipart_uploads; Type: ROW SECURITY; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE storage.s3_multipart_uploads ENABLE ROW LEVEL SECURITY;

--
-- Name: s3_multipart_uploads_parts; Type: ROW SECURITY; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE storage.s3_multipart_uploads_parts ENABLE ROW LEVEL SECURITY;

--
-- Name: vector_indexes; Type: ROW SECURITY; Schema: storage; Owner: supabase_storage_admin
--

ALTER TABLE storage.vector_indexes ENABLE ROW LEVEL SECURITY;

--
-- Name: supabase_realtime; Type: PUBLICATION; Schema: -; Owner: postgres
--

CREATE PUBLICATION supabase_realtime WITH (publish = 'insert, update, delete, truncate');


ALTER PUBLICATION supabase_realtime OWNER TO postgres;

--
-- Name: SCHEMA auth; Type: ACL; Schema: -; Owner: supabase_admin
--

GRANT USAGE ON SCHEMA auth TO anon;
GRANT USAGE ON SCHEMA auth TO authenticated;
GRANT USAGE ON SCHEMA auth TO service_role;
GRANT ALL ON SCHEMA auth TO supabase_auth_admin;
GRANT ALL ON SCHEMA auth TO dashboard_user;
GRANT USAGE ON SCHEMA auth TO postgres;


--
-- Name: SCHEMA extensions; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA extensions TO anon;
GRANT USAGE ON SCHEMA extensions TO authenticated;
GRANT USAGE ON SCHEMA extensions TO service_role;
GRANT ALL ON SCHEMA extensions TO dashboard_user;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO postgres;
GRANT USAGE ON SCHEMA public TO anon;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO service_role;


--
-- Name: SCHEMA realtime; Type: ACL; Schema: -; Owner: supabase_admin
--

GRANT USAGE ON SCHEMA realtime TO postgres WITH GRANT OPTION;
GRANT USAGE ON SCHEMA realtime TO anon;
GRANT USAGE ON SCHEMA realtime TO service_role;
GRANT ALL ON SCHEMA realtime TO supabase_realtime_admin WITH GRANT OPTION;
GRANT USAGE ON SCHEMA realtime TO authenticated;


--
-- Name: SCHEMA storage; Type: ACL; Schema: -; Owner: supabase_admin
--

GRANT USAGE ON SCHEMA storage TO postgres WITH GRANT OPTION;
GRANT USAGE ON SCHEMA storage TO anon;
GRANT USAGE ON SCHEMA storage TO authenticated;
GRANT USAGE ON SCHEMA storage TO service_role;
GRANT ALL ON SCHEMA storage TO supabase_storage_admin WITH GRANT OPTION;
GRANT ALL ON SCHEMA storage TO dashboard_user;


--
-- Name: SCHEMA vault; Type: ACL; Schema: -; Owner: supabase_admin
--

GRANT USAGE ON SCHEMA vault TO postgres WITH GRANT OPTION;
GRANT USAGE ON SCHEMA vault TO service_role;


--
-- Name: FUNCTION gtrgm_in(cstring); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_in(cstring) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_in(cstring) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_in(cstring) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_in(cstring) TO service_role;


--
-- Name: FUNCTION gtrgm_out(public.gtrgm); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_out(public.gtrgm) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_out(public.gtrgm) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_out(public.gtrgm) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_out(public.gtrgm) TO service_role;


--
-- Name: FUNCTION halfvec_in(cstring, oid, integer); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_in(cstring, oid, integer) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_in(cstring, oid, integer) TO anon;
GRANT ALL ON FUNCTION public.halfvec_in(cstring, oid, integer) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_in(cstring, oid, integer) TO service_role;


--
-- Name: FUNCTION halfvec_out(public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_out(public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_out(public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_out(public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_out(public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_recv(internal, oid, integer); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_recv(internal, oid, integer) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_recv(internal, oid, integer) TO anon;
GRANT ALL ON FUNCTION public.halfvec_recv(internal, oid, integer) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_recv(internal, oid, integer) TO service_role;


--
-- Name: FUNCTION halfvec_send(public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_send(public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_send(public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_send(public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_send(public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_typmod_in(cstring[]); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_typmod_in(cstring[]) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_typmod_in(cstring[]) TO anon;
GRANT ALL ON FUNCTION public.halfvec_typmod_in(cstring[]) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_typmod_in(cstring[]) TO service_role;


--
-- Name: FUNCTION sparsevec_in(cstring, oid, integer); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_in(cstring, oid, integer) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_in(cstring, oid, integer) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_in(cstring, oid, integer) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_in(cstring, oid, integer) TO service_role;


--
-- Name: FUNCTION sparsevec_out(public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_out(public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_out(public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_out(public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_out(public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_recv(internal, oid, integer); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_recv(internal, oid, integer) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_recv(internal, oid, integer) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_recv(internal, oid, integer) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_recv(internal, oid, integer) TO service_role;


--
-- Name: FUNCTION sparsevec_send(public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_send(public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_send(public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_send(public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_send(public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_typmod_in(cstring[]); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_typmod_in(cstring[]) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_typmod_in(cstring[]) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_typmod_in(cstring[]) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_typmod_in(cstring[]) TO service_role;


--
-- Name: FUNCTION vector_in(cstring, oid, integer); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_in(cstring, oid, integer) TO postgres;
GRANT ALL ON FUNCTION public.vector_in(cstring, oid, integer) TO anon;
GRANT ALL ON FUNCTION public.vector_in(cstring, oid, integer) TO authenticated;
GRANT ALL ON FUNCTION public.vector_in(cstring, oid, integer) TO service_role;


--
-- Name: FUNCTION vector_out(public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_out(public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_out(public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_out(public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_out(public.vector) TO service_role;


--
-- Name: FUNCTION vector_recv(internal, oid, integer); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_recv(internal, oid, integer) TO postgres;
GRANT ALL ON FUNCTION public.vector_recv(internal, oid, integer) TO anon;
GRANT ALL ON FUNCTION public.vector_recv(internal, oid, integer) TO authenticated;
GRANT ALL ON FUNCTION public.vector_recv(internal, oid, integer) TO service_role;


--
-- Name: FUNCTION vector_send(public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_send(public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_send(public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_send(public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_send(public.vector) TO service_role;


--
-- Name: FUNCTION vector_typmod_in(cstring[]); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_typmod_in(cstring[]) TO postgres;
GRANT ALL ON FUNCTION public.vector_typmod_in(cstring[]) TO anon;
GRANT ALL ON FUNCTION public.vector_typmod_in(cstring[]) TO authenticated;
GRANT ALL ON FUNCTION public.vector_typmod_in(cstring[]) TO service_role;


--
-- Name: FUNCTION array_to_halfvec(real[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_halfvec(real[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_halfvec(real[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_halfvec(real[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_halfvec(real[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_sparsevec(real[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_sparsevec(real[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_sparsevec(real[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_sparsevec(real[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_sparsevec(real[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_vector(real[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_vector(real[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_vector(real[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_vector(real[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_vector(real[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_halfvec(double precision[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_halfvec(double precision[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_halfvec(double precision[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_halfvec(double precision[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_halfvec(double precision[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_sparsevec(double precision[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_sparsevec(double precision[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_sparsevec(double precision[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_sparsevec(double precision[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_sparsevec(double precision[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_vector(double precision[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_vector(double precision[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_vector(double precision[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_vector(double precision[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_vector(double precision[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_halfvec(integer[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_halfvec(integer[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_halfvec(integer[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_halfvec(integer[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_halfvec(integer[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_sparsevec(integer[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_sparsevec(integer[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_sparsevec(integer[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_sparsevec(integer[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_sparsevec(integer[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_vector(integer[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_vector(integer[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_vector(integer[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_vector(integer[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_vector(integer[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_halfvec(numeric[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_halfvec(numeric[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_halfvec(numeric[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_halfvec(numeric[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_halfvec(numeric[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_sparsevec(numeric[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_sparsevec(numeric[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_sparsevec(numeric[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_sparsevec(numeric[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_sparsevec(numeric[], integer, boolean) TO service_role;


--
-- Name: FUNCTION array_to_vector(numeric[], integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.array_to_vector(numeric[], integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.array_to_vector(numeric[], integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.array_to_vector(numeric[], integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.array_to_vector(numeric[], integer, boolean) TO service_role;


--
-- Name: FUNCTION halfvec_to_float4(public.halfvec, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_to_float4(public.halfvec, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_to_float4(public.halfvec, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.halfvec_to_float4(public.halfvec, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_to_float4(public.halfvec, integer, boolean) TO service_role;


--
-- Name: FUNCTION halfvec(public.halfvec, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec(public.halfvec, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.halfvec(public.halfvec, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.halfvec(public.halfvec, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec(public.halfvec, integer, boolean) TO service_role;


--
-- Name: FUNCTION halfvec_to_sparsevec(public.halfvec, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_to_sparsevec(public.halfvec, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_to_sparsevec(public.halfvec, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.halfvec_to_sparsevec(public.halfvec, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_to_sparsevec(public.halfvec, integer, boolean) TO service_role;


--
-- Name: FUNCTION halfvec_to_vector(public.halfvec, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_to_vector(public.halfvec, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_to_vector(public.halfvec, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.halfvec_to_vector(public.halfvec, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_to_vector(public.halfvec, integer, boolean) TO service_role;


--
-- Name: FUNCTION sparsevec_to_halfvec(public.sparsevec, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_to_halfvec(public.sparsevec, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_to_halfvec(public.sparsevec, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_to_halfvec(public.sparsevec, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_to_halfvec(public.sparsevec, integer, boolean) TO service_role;


--
-- Name: FUNCTION sparsevec(public.sparsevec, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec(public.sparsevec, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec(public.sparsevec, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.sparsevec(public.sparsevec, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec(public.sparsevec, integer, boolean) TO service_role;


--
-- Name: FUNCTION sparsevec_to_vector(public.sparsevec, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_to_vector(public.sparsevec, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_to_vector(public.sparsevec, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_to_vector(public.sparsevec, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_to_vector(public.sparsevec, integer, boolean) TO service_role;


--
-- Name: FUNCTION vector_to_float4(public.vector, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_to_float4(public.vector, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.vector_to_float4(public.vector, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.vector_to_float4(public.vector, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.vector_to_float4(public.vector, integer, boolean) TO service_role;


--
-- Name: FUNCTION vector_to_halfvec(public.vector, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_to_halfvec(public.vector, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.vector_to_halfvec(public.vector, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.vector_to_halfvec(public.vector, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.vector_to_halfvec(public.vector, integer, boolean) TO service_role;


--
-- Name: FUNCTION vector_to_sparsevec(public.vector, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_to_sparsevec(public.vector, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.vector_to_sparsevec(public.vector, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.vector_to_sparsevec(public.vector, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.vector_to_sparsevec(public.vector, integer, boolean) TO service_role;


--
-- Name: FUNCTION vector(public.vector, integer, boolean); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector(public.vector, integer, boolean) TO postgres;
GRANT ALL ON FUNCTION public.vector(public.vector, integer, boolean) TO anon;
GRANT ALL ON FUNCTION public.vector(public.vector, integer, boolean) TO authenticated;
GRANT ALL ON FUNCTION public.vector(public.vector, integer, boolean) TO service_role;


--
-- Name: FUNCTION email(); Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON FUNCTION auth.email() TO dashboard_user;


--
-- Name: FUNCTION jwt(); Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON FUNCTION auth.jwt() TO postgres;
GRANT ALL ON FUNCTION auth.jwt() TO dashboard_user;


--
-- Name: FUNCTION role(); Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON FUNCTION auth.role() TO dashboard_user;


--
-- Name: FUNCTION uid(); Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON FUNCTION auth.uid() TO dashboard_user;


--
-- Name: FUNCTION armor(bytea); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.armor(bytea) FROM postgres;
GRANT ALL ON FUNCTION extensions.armor(bytea) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.armor(bytea) TO dashboard_user;


--
-- Name: FUNCTION armor(bytea, text[], text[]); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.armor(bytea, text[], text[]) FROM postgres;
GRANT ALL ON FUNCTION extensions.armor(bytea, text[], text[]) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.armor(bytea, text[], text[]) TO dashboard_user;


--
-- Name: FUNCTION crypt(text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.crypt(text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.crypt(text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.crypt(text, text) TO dashboard_user;


--
-- Name: FUNCTION dearmor(text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.dearmor(text) FROM postgres;
GRANT ALL ON FUNCTION extensions.dearmor(text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.dearmor(text) TO dashboard_user;


--
-- Name: FUNCTION decrypt(bytea, bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.decrypt(bytea, bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.decrypt(bytea, bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.decrypt(bytea, bytea, text) TO dashboard_user;


--
-- Name: FUNCTION decrypt_iv(bytea, bytea, bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.decrypt_iv(bytea, bytea, bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.decrypt_iv(bytea, bytea, bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.decrypt_iv(bytea, bytea, bytea, text) TO dashboard_user;


--
-- Name: FUNCTION digest(bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.digest(bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.digest(bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.digest(bytea, text) TO dashboard_user;


--
-- Name: FUNCTION digest(text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.digest(text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.digest(text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.digest(text, text) TO dashboard_user;


--
-- Name: FUNCTION encrypt(bytea, bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.encrypt(bytea, bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.encrypt(bytea, bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.encrypt(bytea, bytea, text) TO dashboard_user;


--
-- Name: FUNCTION encrypt_iv(bytea, bytea, bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.encrypt_iv(bytea, bytea, bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.encrypt_iv(bytea, bytea, bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.encrypt_iv(bytea, bytea, bytea, text) TO dashboard_user;


--
-- Name: FUNCTION gen_random_bytes(integer); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.gen_random_bytes(integer) FROM postgres;
GRANT ALL ON FUNCTION extensions.gen_random_bytes(integer) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.gen_random_bytes(integer) TO dashboard_user;


--
-- Name: FUNCTION gen_random_uuid(); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.gen_random_uuid() FROM postgres;
GRANT ALL ON FUNCTION extensions.gen_random_uuid() TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.gen_random_uuid() TO dashboard_user;


--
-- Name: FUNCTION gen_salt(text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.gen_salt(text) FROM postgres;
GRANT ALL ON FUNCTION extensions.gen_salt(text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.gen_salt(text) TO dashboard_user;


--
-- Name: FUNCTION gen_salt(text, integer); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.gen_salt(text, integer) FROM postgres;
GRANT ALL ON FUNCTION extensions.gen_salt(text, integer) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.gen_salt(text, integer) TO dashboard_user;


--
-- Name: FUNCTION grant_pg_cron_access(); Type: ACL; Schema: extensions; Owner: supabase_admin
--

REVOKE ALL ON FUNCTION extensions.grant_pg_cron_access() FROM supabase_admin;
GRANT ALL ON FUNCTION extensions.grant_pg_cron_access() TO supabase_admin WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.grant_pg_cron_access() TO dashboard_user;


--
-- Name: FUNCTION grant_pg_graphql_access(); Type: ACL; Schema: extensions; Owner: supabase_admin
--

GRANT ALL ON FUNCTION extensions.grant_pg_graphql_access() TO postgres WITH GRANT OPTION;


--
-- Name: FUNCTION grant_pg_net_access(); Type: ACL; Schema: extensions; Owner: supabase_admin
--

REVOKE ALL ON FUNCTION extensions.grant_pg_net_access() FROM supabase_admin;
GRANT ALL ON FUNCTION extensions.grant_pg_net_access() TO supabase_admin WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.grant_pg_net_access() TO dashboard_user;


--
-- Name: FUNCTION hmac(bytea, bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.hmac(bytea, bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.hmac(bytea, bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.hmac(bytea, bytea, text) TO dashboard_user;


--
-- Name: FUNCTION hmac(text, text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.hmac(text, text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.hmac(text, text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.hmac(text, text, text) TO dashboard_user;


--
-- Name: FUNCTION pg_stat_statements(showtext boolean, OUT userid oid, OUT dbid oid, OUT toplevel boolean, OUT queryid bigint, OUT query text, OUT plans bigint, OUT total_plan_time double precision, OUT min_plan_time double precision, OUT max_plan_time double precision, OUT mean_plan_time double precision, OUT stddev_plan_time double precision, OUT calls bigint, OUT total_exec_time double precision, OUT min_exec_time double precision, OUT max_exec_time double precision, OUT mean_exec_time double precision, OUT stddev_exec_time double precision, OUT rows bigint, OUT shared_blks_hit bigint, OUT shared_blks_read bigint, OUT shared_blks_dirtied bigint, OUT shared_blks_written bigint, OUT local_blks_hit bigint, OUT local_blks_read bigint, OUT local_blks_dirtied bigint, OUT local_blks_written bigint, OUT temp_blks_read bigint, OUT temp_blks_written bigint, OUT shared_blk_read_time double precision, OUT shared_blk_write_time double precision, OUT local_blk_read_time double precision, OUT local_blk_write_time double precision, OUT temp_blk_read_time double precision, OUT temp_blk_write_time double precision, OUT wal_records bigint, OUT wal_fpi bigint, OUT wal_bytes numeric, OUT jit_functions bigint, OUT jit_generation_time double precision, OUT jit_inlining_count bigint, OUT jit_inlining_time double precision, OUT jit_optimization_count bigint, OUT jit_optimization_time double precision, OUT jit_emission_count bigint, OUT jit_emission_time double precision, OUT jit_deform_count bigint, OUT jit_deform_time double precision, OUT stats_since timestamp with time zone, OUT minmax_stats_since timestamp with time zone); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pg_stat_statements(showtext boolean, OUT userid oid, OUT dbid oid, OUT toplevel boolean, OUT queryid bigint, OUT query text, OUT plans bigint, OUT total_plan_time double precision, OUT min_plan_time double precision, OUT max_plan_time double precision, OUT mean_plan_time double precision, OUT stddev_plan_time double precision, OUT calls bigint, OUT total_exec_time double precision, OUT min_exec_time double precision, OUT max_exec_time double precision, OUT mean_exec_time double precision, OUT stddev_exec_time double precision, OUT rows bigint, OUT shared_blks_hit bigint, OUT shared_blks_read bigint, OUT shared_blks_dirtied bigint, OUT shared_blks_written bigint, OUT local_blks_hit bigint, OUT local_blks_read bigint, OUT local_blks_dirtied bigint, OUT local_blks_written bigint, OUT temp_blks_read bigint, OUT temp_blks_written bigint, OUT shared_blk_read_time double precision, OUT shared_blk_write_time double precision, OUT local_blk_read_time double precision, OUT local_blk_write_time double precision, OUT temp_blk_read_time double precision, OUT temp_blk_write_time double precision, OUT wal_records bigint, OUT wal_fpi bigint, OUT wal_bytes numeric, OUT jit_functions bigint, OUT jit_generation_time double precision, OUT jit_inlining_count bigint, OUT jit_inlining_time double precision, OUT jit_optimization_count bigint, OUT jit_optimization_time double precision, OUT jit_emission_count bigint, OUT jit_emission_time double precision, OUT jit_deform_count bigint, OUT jit_deform_time double precision, OUT stats_since timestamp with time zone, OUT minmax_stats_since timestamp with time zone) FROM postgres;
GRANT ALL ON FUNCTION extensions.pg_stat_statements(showtext boolean, OUT userid oid, OUT dbid oid, OUT toplevel boolean, OUT queryid bigint, OUT query text, OUT plans bigint, OUT total_plan_time double precision, OUT min_plan_time double precision, OUT max_plan_time double precision, OUT mean_plan_time double precision, OUT stddev_plan_time double precision, OUT calls bigint, OUT total_exec_time double precision, OUT min_exec_time double precision, OUT max_exec_time double precision, OUT mean_exec_time double precision, OUT stddev_exec_time double precision, OUT rows bigint, OUT shared_blks_hit bigint, OUT shared_blks_read bigint, OUT shared_blks_dirtied bigint, OUT shared_blks_written bigint, OUT local_blks_hit bigint, OUT local_blks_read bigint, OUT local_blks_dirtied bigint, OUT local_blks_written bigint, OUT temp_blks_read bigint, OUT temp_blks_written bigint, OUT shared_blk_read_time double precision, OUT shared_blk_write_time double precision, OUT local_blk_read_time double precision, OUT local_blk_write_time double precision, OUT temp_blk_read_time double precision, OUT temp_blk_write_time double precision, OUT wal_records bigint, OUT wal_fpi bigint, OUT wal_bytes numeric, OUT jit_functions bigint, OUT jit_generation_time double precision, OUT jit_inlining_count bigint, OUT jit_inlining_time double precision, OUT jit_optimization_count bigint, OUT jit_optimization_time double precision, OUT jit_emission_count bigint, OUT jit_emission_time double precision, OUT jit_deform_count bigint, OUT jit_deform_time double precision, OUT stats_since timestamp with time zone, OUT minmax_stats_since timestamp with time zone) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pg_stat_statements(showtext boolean, OUT userid oid, OUT dbid oid, OUT toplevel boolean, OUT queryid bigint, OUT query text, OUT plans bigint, OUT total_plan_time double precision, OUT min_plan_time double precision, OUT max_plan_time double precision, OUT mean_plan_time double precision, OUT stddev_plan_time double precision, OUT calls bigint, OUT total_exec_time double precision, OUT min_exec_time double precision, OUT max_exec_time double precision, OUT mean_exec_time double precision, OUT stddev_exec_time double precision, OUT rows bigint, OUT shared_blks_hit bigint, OUT shared_blks_read bigint, OUT shared_blks_dirtied bigint, OUT shared_blks_written bigint, OUT local_blks_hit bigint, OUT local_blks_read bigint, OUT local_blks_dirtied bigint, OUT local_blks_written bigint, OUT temp_blks_read bigint, OUT temp_blks_written bigint, OUT shared_blk_read_time double precision, OUT shared_blk_write_time double precision, OUT local_blk_read_time double precision, OUT local_blk_write_time double precision, OUT temp_blk_read_time double precision, OUT temp_blk_write_time double precision, OUT wal_records bigint, OUT wal_fpi bigint, OUT wal_bytes numeric, OUT jit_functions bigint, OUT jit_generation_time double precision, OUT jit_inlining_count bigint, OUT jit_inlining_time double precision, OUT jit_optimization_count bigint, OUT jit_optimization_time double precision, OUT jit_emission_count bigint, OUT jit_emission_time double precision, OUT jit_deform_count bigint, OUT jit_deform_time double precision, OUT stats_since timestamp with time zone, OUT minmax_stats_since timestamp with time zone) TO dashboard_user;


--
-- Name: FUNCTION pg_stat_statements_info(OUT dealloc bigint, OUT stats_reset timestamp with time zone); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pg_stat_statements_info(OUT dealloc bigint, OUT stats_reset timestamp with time zone) FROM postgres;
GRANT ALL ON FUNCTION extensions.pg_stat_statements_info(OUT dealloc bigint, OUT stats_reset timestamp with time zone) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pg_stat_statements_info(OUT dealloc bigint, OUT stats_reset timestamp with time zone) TO dashboard_user;


--
-- Name: FUNCTION pg_stat_statements_reset(userid oid, dbid oid, queryid bigint, minmax_only boolean); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint, minmax_only boolean) FROM postgres;
GRANT ALL ON FUNCTION extensions.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint, minmax_only boolean) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint, minmax_only boolean) TO dashboard_user;


--
-- Name: FUNCTION pgp_armor_headers(text, OUT key text, OUT value text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_armor_headers(text, OUT key text, OUT value text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_armor_headers(text, OUT key text, OUT value text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_armor_headers(text, OUT key text, OUT value text) TO dashboard_user;


--
-- Name: FUNCTION pgp_key_id(bytea); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_key_id(bytea) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_key_id(bytea) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_key_id(bytea) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_decrypt(bytea, bytea); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_decrypt(bytea, bytea) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt(bytea, bytea) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt(bytea, bytea) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_decrypt(bytea, bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_decrypt(bytea, bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt(bytea, bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt(bytea, bytea, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_decrypt(bytea, bytea, text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_decrypt(bytea, bytea, text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt(bytea, bytea, text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt(bytea, bytea, text, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_decrypt_bytea(bytea, bytea); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_decrypt_bytea(bytea, bytea) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt_bytea(bytea, bytea) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt_bytea(bytea, bytea) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_decrypt_bytea(bytea, bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_decrypt_bytea(bytea, bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt_bytea(bytea, bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt_bytea(bytea, bytea, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_decrypt_bytea(bytea, bytea, text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_decrypt_bytea(bytea, bytea, text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt_bytea(bytea, bytea, text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_decrypt_bytea(bytea, bytea, text, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_encrypt(text, bytea); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_encrypt(text, bytea) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_encrypt(text, bytea) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_encrypt(text, bytea) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_encrypt(text, bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_encrypt(text, bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_encrypt(text, bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_encrypt(text, bytea, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_encrypt_bytea(bytea, bytea); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_encrypt_bytea(bytea, bytea) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_encrypt_bytea(bytea, bytea) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_encrypt_bytea(bytea, bytea) TO dashboard_user;


--
-- Name: FUNCTION pgp_pub_encrypt_bytea(bytea, bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_pub_encrypt_bytea(bytea, bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_pub_encrypt_bytea(bytea, bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_pub_encrypt_bytea(bytea, bytea, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_sym_decrypt(bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_sym_decrypt(bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_sym_decrypt(bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_sym_decrypt(bytea, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_sym_decrypt(bytea, text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_sym_decrypt(bytea, text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_sym_decrypt(bytea, text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_sym_decrypt(bytea, text, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_sym_decrypt_bytea(bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_sym_decrypt_bytea(bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_sym_decrypt_bytea(bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_sym_decrypt_bytea(bytea, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_sym_decrypt_bytea(bytea, text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_sym_decrypt_bytea(bytea, text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_sym_decrypt_bytea(bytea, text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_sym_decrypt_bytea(bytea, text, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_sym_encrypt(text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_sym_encrypt(text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_sym_encrypt(text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_sym_encrypt(text, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_sym_encrypt(text, text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_sym_encrypt(text, text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_sym_encrypt(text, text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_sym_encrypt(text, text, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_sym_encrypt_bytea(bytea, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_sym_encrypt_bytea(bytea, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_sym_encrypt_bytea(bytea, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_sym_encrypt_bytea(bytea, text) TO dashboard_user;


--
-- Name: FUNCTION pgp_sym_encrypt_bytea(bytea, text, text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.pgp_sym_encrypt_bytea(bytea, text, text) FROM postgres;
GRANT ALL ON FUNCTION extensions.pgp_sym_encrypt_bytea(bytea, text, text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.pgp_sym_encrypt_bytea(bytea, text, text) TO dashboard_user;


--
-- Name: FUNCTION pgrst_ddl_watch(); Type: ACL; Schema: extensions; Owner: supabase_admin
--

GRANT ALL ON FUNCTION extensions.pgrst_ddl_watch() TO postgres WITH GRANT OPTION;


--
-- Name: FUNCTION pgrst_drop_watch(); Type: ACL; Schema: extensions; Owner: supabase_admin
--

GRANT ALL ON FUNCTION extensions.pgrst_drop_watch() TO postgres WITH GRANT OPTION;


--
-- Name: FUNCTION set_graphql_placeholder(); Type: ACL; Schema: extensions; Owner: supabase_admin
--

GRANT ALL ON FUNCTION extensions.set_graphql_placeholder() TO postgres WITH GRANT OPTION;


--
-- Name: FUNCTION uuid_generate_v1(); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_generate_v1() FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_generate_v1() TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_generate_v1() TO dashboard_user;


--
-- Name: FUNCTION uuid_generate_v1mc(); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_generate_v1mc() FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_generate_v1mc() TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_generate_v1mc() TO dashboard_user;


--
-- Name: FUNCTION uuid_generate_v3(namespace uuid, name text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_generate_v3(namespace uuid, name text) FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_generate_v3(namespace uuid, name text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_generate_v3(namespace uuid, name text) TO dashboard_user;


--
-- Name: FUNCTION uuid_generate_v4(); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_generate_v4() FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_generate_v4() TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_generate_v4() TO dashboard_user;


--
-- Name: FUNCTION uuid_generate_v5(namespace uuid, name text); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_generate_v5(namespace uuid, name text) FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_generate_v5(namespace uuid, name text) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_generate_v5(namespace uuid, name text) TO dashboard_user;


--
-- Name: FUNCTION uuid_nil(); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_nil() FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_nil() TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_nil() TO dashboard_user;


--
-- Name: FUNCTION uuid_ns_dns(); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_ns_dns() FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_ns_dns() TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_ns_dns() TO dashboard_user;


--
-- Name: FUNCTION uuid_ns_oid(); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_ns_oid() FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_ns_oid() TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_ns_oid() TO dashboard_user;


--
-- Name: FUNCTION uuid_ns_url(); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_ns_url() FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_ns_url() TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_ns_url() TO dashboard_user;


--
-- Name: FUNCTION uuid_ns_x500(); Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON FUNCTION extensions.uuid_ns_x500() FROM postgres;
GRANT ALL ON FUNCTION extensions.uuid_ns_x500() TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION extensions.uuid_ns_x500() TO dashboard_user;


--
-- Name: FUNCTION graphql("operationName" text, query text, variables jsonb, extensions jsonb); Type: ACL; Schema: graphql_public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION graphql_public.graphql("operationName" text, query text, variables jsonb, extensions jsonb) TO postgres;
GRANT ALL ON FUNCTION graphql_public.graphql("operationName" text, query text, variables jsonb, extensions jsonb) TO anon;
GRANT ALL ON FUNCTION graphql_public.graphql("operationName" text, query text, variables jsonb, extensions jsonb) TO authenticated;
GRANT ALL ON FUNCTION graphql_public.graphql("operationName" text, query text, variables jsonb, extensions jsonb) TO service_role;


--
-- Name: FUNCTION pg_reload_conf(); Type: ACL; Schema: pg_catalog; Owner: supabase_admin
--

GRANT ALL ON FUNCTION pg_catalog.pg_reload_conf() TO postgres WITH GRANT OPTION;


--
-- Name: FUNCTION get_auth(p_usename text); Type: ACL; Schema: pgbouncer; Owner: supabase_admin
--

REVOKE ALL ON FUNCTION pgbouncer.get_auth(p_usename text) FROM PUBLIC;
GRANT ALL ON FUNCTION pgbouncer.get_auth(p_usename text) TO pgbouncer;


--
-- Name: FUNCTION binary_quantize(public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.binary_quantize(public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.binary_quantize(public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.binary_quantize(public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.binary_quantize(public.halfvec) TO service_role;


--
-- Name: FUNCTION binary_quantize(public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.binary_quantize(public.vector) TO postgres;
GRANT ALL ON FUNCTION public.binary_quantize(public.vector) TO anon;
GRANT ALL ON FUNCTION public.binary_quantize(public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.binary_quantize(public.vector) TO service_role;


--
-- Name: FUNCTION cosine_distance(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.cosine_distance(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.cosine_distance(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.cosine_distance(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.cosine_distance(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION cosine_distance(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.cosine_distance(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.cosine_distance(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.cosine_distance(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.cosine_distance(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION cosine_distance(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.cosine_distance(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.cosine_distance(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.cosine_distance(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.cosine_distance(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION find_duplicate_logs(p_ticker text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.find_duplicate_logs(p_ticker text) TO anon;
GRANT ALL ON FUNCTION public.find_duplicate_logs(p_ticker text) TO authenticated;
GRANT ALL ON FUNCTION public.find_duplicate_logs(p_ticker text) TO service_role;


--
-- Name: FUNCTION find_phantom_filings(p_ticker text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.find_phantom_filings(p_ticker text) TO anon;
GRANT ALL ON FUNCTION public.find_phantom_filings(p_ticker text) TO authenticated;
GRANT ALL ON FUNCTION public.find_phantom_filings(p_ticker text) TO service_role;


--
-- Name: FUNCTION gin_extract_query_trgm(text, internal, smallint, internal, internal, internal, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gin_extract_query_trgm(text, internal, smallint, internal, internal, internal, internal) TO postgres;
GRANT ALL ON FUNCTION public.gin_extract_query_trgm(text, internal, smallint, internal, internal, internal, internal) TO anon;
GRANT ALL ON FUNCTION public.gin_extract_query_trgm(text, internal, smallint, internal, internal, internal, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gin_extract_query_trgm(text, internal, smallint, internal, internal, internal, internal) TO service_role;


--
-- Name: FUNCTION gin_extract_value_trgm(text, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gin_extract_value_trgm(text, internal) TO postgres;
GRANT ALL ON FUNCTION public.gin_extract_value_trgm(text, internal) TO anon;
GRANT ALL ON FUNCTION public.gin_extract_value_trgm(text, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gin_extract_value_trgm(text, internal) TO service_role;


--
-- Name: FUNCTION gin_trgm_consistent(internal, smallint, text, integer, internal, internal, internal, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gin_trgm_consistent(internal, smallint, text, integer, internal, internal, internal, internal) TO postgres;
GRANT ALL ON FUNCTION public.gin_trgm_consistent(internal, smallint, text, integer, internal, internal, internal, internal) TO anon;
GRANT ALL ON FUNCTION public.gin_trgm_consistent(internal, smallint, text, integer, internal, internal, internal, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gin_trgm_consistent(internal, smallint, text, integer, internal, internal, internal, internal) TO service_role;


--
-- Name: FUNCTION gin_trgm_triconsistent(internal, smallint, text, integer, internal, internal, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gin_trgm_triconsistent(internal, smallint, text, integer, internal, internal, internal) TO postgres;
GRANT ALL ON FUNCTION public.gin_trgm_triconsistent(internal, smallint, text, integer, internal, internal, internal) TO anon;
GRANT ALL ON FUNCTION public.gin_trgm_triconsistent(internal, smallint, text, integer, internal, internal, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gin_trgm_triconsistent(internal, smallint, text, integer, internal, internal, internal) TO service_role;


--
-- Name: FUNCTION gtrgm_compress(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_compress(internal) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_compress(internal) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_compress(internal) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_compress(internal) TO service_role;


--
-- Name: FUNCTION gtrgm_consistent(internal, text, smallint, oid, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_consistent(internal, text, smallint, oid, internal) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_consistent(internal, text, smallint, oid, internal) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_consistent(internal, text, smallint, oid, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_consistent(internal, text, smallint, oid, internal) TO service_role;


--
-- Name: FUNCTION gtrgm_decompress(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_decompress(internal) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_decompress(internal) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_decompress(internal) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_decompress(internal) TO service_role;


--
-- Name: FUNCTION gtrgm_distance(internal, text, smallint, oid, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_distance(internal, text, smallint, oid, internal) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_distance(internal, text, smallint, oid, internal) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_distance(internal, text, smallint, oid, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_distance(internal, text, smallint, oid, internal) TO service_role;


--
-- Name: FUNCTION gtrgm_options(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_options(internal) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_options(internal) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_options(internal) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_options(internal) TO service_role;


--
-- Name: FUNCTION gtrgm_penalty(internal, internal, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_penalty(internal, internal, internal) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_penalty(internal, internal, internal) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_penalty(internal, internal, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_penalty(internal, internal, internal) TO service_role;


--
-- Name: FUNCTION gtrgm_picksplit(internal, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_picksplit(internal, internal) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_picksplit(internal, internal) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_picksplit(internal, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_picksplit(internal, internal) TO service_role;


--
-- Name: FUNCTION gtrgm_same(public.gtrgm, public.gtrgm, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_same(public.gtrgm, public.gtrgm, internal) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_same(public.gtrgm, public.gtrgm, internal) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_same(public.gtrgm, public.gtrgm, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_same(public.gtrgm, public.gtrgm, internal) TO service_role;


--
-- Name: FUNCTION gtrgm_union(internal, internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.gtrgm_union(internal, internal) TO postgres;
GRANT ALL ON FUNCTION public.gtrgm_union(internal, internal) TO anon;
GRANT ALL ON FUNCTION public.gtrgm_union(internal, internal) TO authenticated;
GRANT ALL ON FUNCTION public.gtrgm_union(internal, internal) TO service_role;


--
-- Name: FUNCTION halfvec_accum(double precision[], public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_accum(double precision[], public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_accum(double precision[], public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_accum(double precision[], public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_accum(double precision[], public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_add(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_add(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_add(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_add(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_add(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_avg(double precision[]); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_avg(double precision[]) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_avg(double precision[]) TO anon;
GRANT ALL ON FUNCTION public.halfvec_avg(double precision[]) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_avg(double precision[]) TO service_role;


--
-- Name: FUNCTION halfvec_cmp(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_cmp(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_cmp(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_cmp(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_cmp(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_combine(double precision[], double precision[]); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_combine(double precision[], double precision[]) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_combine(double precision[], double precision[]) TO anon;
GRANT ALL ON FUNCTION public.halfvec_combine(double precision[], double precision[]) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_combine(double precision[], double precision[]) TO service_role;


--
-- Name: FUNCTION halfvec_concat(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_concat(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_concat(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_concat(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_concat(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_eq(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_eq(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_eq(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_eq(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_eq(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_ge(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_ge(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_ge(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_ge(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_ge(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_gt(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_gt(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_gt(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_gt(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_gt(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_l2_squared_distance(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_l2_squared_distance(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_l2_squared_distance(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_l2_squared_distance(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_l2_squared_distance(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_le(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_le(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_le(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_le(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_le(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_lt(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_lt(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_lt(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_lt(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_lt(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_mul(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_mul(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_mul(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_mul(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_mul(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_ne(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_ne(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_ne(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_ne(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_ne(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_negative_inner_product(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_negative_inner_product(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_negative_inner_product(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_negative_inner_product(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_negative_inner_product(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_spherical_distance(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_spherical_distance(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_spherical_distance(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_spherical_distance(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_spherical_distance(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION halfvec_sub(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.halfvec_sub(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.halfvec_sub(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.halfvec_sub(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.halfvec_sub(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION hamming_distance(bit, bit); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hamming_distance(bit, bit) TO postgres;
GRANT ALL ON FUNCTION public.hamming_distance(bit, bit) TO anon;
GRANT ALL ON FUNCTION public.hamming_distance(bit, bit) TO authenticated;
GRANT ALL ON FUNCTION public.hamming_distance(bit, bit) TO service_role;


--
-- Name: FUNCTION hnsw_bit_support(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hnsw_bit_support(internal) TO postgres;
GRANT ALL ON FUNCTION public.hnsw_bit_support(internal) TO anon;
GRANT ALL ON FUNCTION public.hnsw_bit_support(internal) TO authenticated;
GRANT ALL ON FUNCTION public.hnsw_bit_support(internal) TO service_role;


--
-- Name: FUNCTION hnsw_halfvec_support(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hnsw_halfvec_support(internal) TO postgres;
GRANT ALL ON FUNCTION public.hnsw_halfvec_support(internal) TO anon;
GRANT ALL ON FUNCTION public.hnsw_halfvec_support(internal) TO authenticated;
GRANT ALL ON FUNCTION public.hnsw_halfvec_support(internal) TO service_role;


--
-- Name: FUNCTION hnsw_sparsevec_support(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hnsw_sparsevec_support(internal) TO postgres;
GRANT ALL ON FUNCTION public.hnsw_sparsevec_support(internal) TO anon;
GRANT ALL ON FUNCTION public.hnsw_sparsevec_support(internal) TO authenticated;
GRANT ALL ON FUNCTION public.hnsw_sparsevec_support(internal) TO service_role;


--
-- Name: FUNCTION hnswhandler(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hnswhandler(internal) TO postgres;
GRANT ALL ON FUNCTION public.hnswhandler(internal) TO anon;
GRANT ALL ON FUNCTION public.hnswhandler(internal) TO authenticated;
GRANT ALL ON FUNCTION public.hnswhandler(internal) TO service_role;


--
-- Name: FUNCTION hypopg(OUT indexname text, OUT indexrelid oid, OUT indrelid oid, OUT innatts integer, OUT indisunique boolean, OUT indkey int2vector, OUT indcollation oidvector, OUT indclass oidvector, OUT indoption oidvector, OUT indexprs pg_node_tree, OUT indpred pg_node_tree, OUT amid oid); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg(OUT indexname text, OUT indexrelid oid, OUT indrelid oid, OUT innatts integer, OUT indisunique boolean, OUT indkey int2vector, OUT indcollation oidvector, OUT indclass oidvector, OUT indoption oidvector, OUT indexprs pg_node_tree, OUT indpred pg_node_tree, OUT amid oid) TO postgres;
GRANT ALL ON FUNCTION public.hypopg(OUT indexname text, OUT indexrelid oid, OUT indrelid oid, OUT innatts integer, OUT indisunique boolean, OUT indkey int2vector, OUT indcollation oidvector, OUT indclass oidvector, OUT indoption oidvector, OUT indexprs pg_node_tree, OUT indpred pg_node_tree, OUT amid oid) TO anon;
GRANT ALL ON FUNCTION public.hypopg(OUT indexname text, OUT indexrelid oid, OUT indrelid oid, OUT innatts integer, OUT indisunique boolean, OUT indkey int2vector, OUT indcollation oidvector, OUT indclass oidvector, OUT indoption oidvector, OUT indexprs pg_node_tree, OUT indpred pg_node_tree, OUT amid oid) TO authenticated;
GRANT ALL ON FUNCTION public.hypopg(OUT indexname text, OUT indexrelid oid, OUT indrelid oid, OUT innatts integer, OUT indisunique boolean, OUT indkey int2vector, OUT indcollation oidvector, OUT indclass oidvector, OUT indoption oidvector, OUT indexprs pg_node_tree, OUT indpred pg_node_tree, OUT amid oid) TO service_role;


--
-- Name: FUNCTION hypopg_create_index(sql_order text, OUT indexrelid oid, OUT indexname text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_create_index(sql_order text, OUT indexrelid oid, OUT indexname text) TO postgres;
GRANT ALL ON FUNCTION public.hypopg_create_index(sql_order text, OUT indexrelid oid, OUT indexname text) TO anon;
GRANT ALL ON FUNCTION public.hypopg_create_index(sql_order text, OUT indexrelid oid, OUT indexname text) TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_create_index(sql_order text, OUT indexrelid oid, OUT indexname text) TO service_role;


--
-- Name: FUNCTION hypopg_drop_index(indexid oid); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_drop_index(indexid oid) TO postgres;
GRANT ALL ON FUNCTION public.hypopg_drop_index(indexid oid) TO anon;
GRANT ALL ON FUNCTION public.hypopg_drop_index(indexid oid) TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_drop_index(indexid oid) TO service_role;


--
-- Name: FUNCTION hypopg_get_indexdef(indexid oid); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_get_indexdef(indexid oid) TO postgres;
GRANT ALL ON FUNCTION public.hypopg_get_indexdef(indexid oid) TO anon;
GRANT ALL ON FUNCTION public.hypopg_get_indexdef(indexid oid) TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_get_indexdef(indexid oid) TO service_role;


--
-- Name: FUNCTION hypopg_hidden_indexes(); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_hidden_indexes() TO postgres;
GRANT ALL ON FUNCTION public.hypopg_hidden_indexes() TO anon;
GRANT ALL ON FUNCTION public.hypopg_hidden_indexes() TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_hidden_indexes() TO service_role;


--
-- Name: FUNCTION hypopg_hide_index(indexid oid); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_hide_index(indexid oid) TO postgres;
GRANT ALL ON FUNCTION public.hypopg_hide_index(indexid oid) TO anon;
GRANT ALL ON FUNCTION public.hypopg_hide_index(indexid oid) TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_hide_index(indexid oid) TO service_role;


--
-- Name: FUNCTION hypopg_relation_size(indexid oid); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_relation_size(indexid oid) TO postgres;
GRANT ALL ON FUNCTION public.hypopg_relation_size(indexid oid) TO anon;
GRANT ALL ON FUNCTION public.hypopg_relation_size(indexid oid) TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_relation_size(indexid oid) TO service_role;


--
-- Name: FUNCTION hypopg_reset(); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_reset() TO postgres;
GRANT ALL ON FUNCTION public.hypopg_reset() TO anon;
GRANT ALL ON FUNCTION public.hypopg_reset() TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_reset() TO service_role;


--
-- Name: FUNCTION hypopg_reset_index(); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_reset_index() TO postgres;
GRANT ALL ON FUNCTION public.hypopg_reset_index() TO anon;
GRANT ALL ON FUNCTION public.hypopg_reset_index() TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_reset_index() TO service_role;


--
-- Name: FUNCTION hypopg_unhide_all_indexes(); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_unhide_all_indexes() TO postgres;
GRANT ALL ON FUNCTION public.hypopg_unhide_all_indexes() TO anon;
GRANT ALL ON FUNCTION public.hypopg_unhide_all_indexes() TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_unhide_all_indexes() TO service_role;


--
-- Name: FUNCTION hypopg_unhide_index(indexid oid); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.hypopg_unhide_index(indexid oid) TO postgres;
GRANT ALL ON FUNCTION public.hypopg_unhide_index(indexid oid) TO anon;
GRANT ALL ON FUNCTION public.hypopg_unhide_index(indexid oid) TO authenticated;
GRANT ALL ON FUNCTION public.hypopg_unhide_index(indexid oid) TO service_role;


--
-- Name: FUNCTION index_advisor(query text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.index_advisor(query text) TO postgres;
GRANT ALL ON FUNCTION public.index_advisor(query text) TO anon;
GRANT ALL ON FUNCTION public.index_advisor(query text) TO authenticated;
GRANT ALL ON FUNCTION public.index_advisor(query text) TO service_role;


--
-- Name: FUNCTION inner_product(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.inner_product(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.inner_product(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.inner_product(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.inner_product(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION inner_product(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.inner_product(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.inner_product(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.inner_product(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.inner_product(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION inner_product(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.inner_product(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.inner_product(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.inner_product(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.inner_product(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION ivfflat_bit_support(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.ivfflat_bit_support(internal) TO postgres;
GRANT ALL ON FUNCTION public.ivfflat_bit_support(internal) TO anon;
GRANT ALL ON FUNCTION public.ivfflat_bit_support(internal) TO authenticated;
GRANT ALL ON FUNCTION public.ivfflat_bit_support(internal) TO service_role;


--
-- Name: FUNCTION ivfflat_halfvec_support(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.ivfflat_halfvec_support(internal) TO postgres;
GRANT ALL ON FUNCTION public.ivfflat_halfvec_support(internal) TO anon;
GRANT ALL ON FUNCTION public.ivfflat_halfvec_support(internal) TO authenticated;
GRANT ALL ON FUNCTION public.ivfflat_halfvec_support(internal) TO service_role;


--
-- Name: FUNCTION ivfflathandler(internal); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.ivfflathandler(internal) TO postgres;
GRANT ALL ON FUNCTION public.ivfflathandler(internal) TO anon;
GRANT ALL ON FUNCTION public.ivfflathandler(internal) TO authenticated;
GRANT ALL ON FUNCTION public.ivfflathandler(internal) TO service_role;


--
-- Name: FUNCTION jaccard_distance(bit, bit); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.jaccard_distance(bit, bit) TO postgres;
GRANT ALL ON FUNCTION public.jaccard_distance(bit, bit) TO anon;
GRANT ALL ON FUNCTION public.jaccard_distance(bit, bit) TO authenticated;
GRANT ALL ON FUNCTION public.jaccard_distance(bit, bit) TO service_role;


--
-- Name: FUNCTION l1_distance(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l1_distance(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.l1_distance(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.l1_distance(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.l1_distance(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION l1_distance(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l1_distance(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.l1_distance(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.l1_distance(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.l1_distance(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION l1_distance(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l1_distance(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.l1_distance(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.l1_distance(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.l1_distance(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION l2_distance(public.halfvec, public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l2_distance(public.halfvec, public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.l2_distance(public.halfvec, public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.l2_distance(public.halfvec, public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.l2_distance(public.halfvec, public.halfvec) TO service_role;


--
-- Name: FUNCTION l2_distance(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l2_distance(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.l2_distance(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.l2_distance(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.l2_distance(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION l2_distance(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l2_distance(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.l2_distance(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.l2_distance(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.l2_distance(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION l2_norm(public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l2_norm(public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.l2_norm(public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.l2_norm(public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.l2_norm(public.halfvec) TO service_role;


--
-- Name: FUNCTION l2_norm(public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l2_norm(public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.l2_norm(public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.l2_norm(public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.l2_norm(public.sparsevec) TO service_role;


--
-- Name: FUNCTION l2_normalize(public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l2_normalize(public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.l2_normalize(public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.l2_normalize(public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.l2_normalize(public.halfvec) TO service_role;


--
-- Name: FUNCTION l2_normalize(public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l2_normalize(public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.l2_normalize(public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.l2_normalize(public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.l2_normalize(public.sparsevec) TO service_role;


--
-- Name: FUNCTION l2_normalize(public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.l2_normalize(public.vector) TO postgres;
GRANT ALL ON FUNCTION public.l2_normalize(public.vector) TO anon;
GRANT ALL ON FUNCTION public.l2_normalize(public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.l2_normalize(public.vector) TO service_role;


--
-- Name: FUNCTION set_limit(real); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.set_limit(real) TO postgres;
GRANT ALL ON FUNCTION public.set_limit(real) TO anon;
GRANT ALL ON FUNCTION public.set_limit(real) TO authenticated;
GRANT ALL ON FUNCTION public.set_limit(real) TO service_role;


--
-- Name: FUNCTION show_limit(); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.show_limit() TO postgres;
GRANT ALL ON FUNCTION public.show_limit() TO anon;
GRANT ALL ON FUNCTION public.show_limit() TO authenticated;
GRANT ALL ON FUNCTION public.show_limit() TO service_role;


--
-- Name: FUNCTION show_trgm(text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.show_trgm(text) TO postgres;
GRANT ALL ON FUNCTION public.show_trgm(text) TO anon;
GRANT ALL ON FUNCTION public.show_trgm(text) TO authenticated;
GRANT ALL ON FUNCTION public.show_trgm(text) TO service_role;


--
-- Name: FUNCTION similarity(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.similarity(text, text) TO postgres;
GRANT ALL ON FUNCTION public.similarity(text, text) TO anon;
GRANT ALL ON FUNCTION public.similarity(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.similarity(text, text) TO service_role;


--
-- Name: FUNCTION similarity_dist(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.similarity_dist(text, text) TO postgres;
GRANT ALL ON FUNCTION public.similarity_dist(text, text) TO anon;
GRANT ALL ON FUNCTION public.similarity_dist(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.similarity_dist(text, text) TO service_role;


--
-- Name: FUNCTION similarity_op(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.similarity_op(text, text) TO postgres;
GRANT ALL ON FUNCTION public.similarity_op(text, text) TO anon;
GRANT ALL ON FUNCTION public.similarity_op(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.similarity_op(text, text) TO service_role;


--
-- Name: FUNCTION sparsevec_cmp(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_cmp(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_cmp(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_cmp(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_cmp(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_eq(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_eq(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_eq(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_eq(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_eq(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_ge(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_ge(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_ge(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_ge(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_ge(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_gt(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_gt(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_gt(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_gt(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_gt(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_l2_squared_distance(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_l2_squared_distance(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_l2_squared_distance(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_l2_squared_distance(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_l2_squared_distance(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_le(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_le(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_le(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_le(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_le(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_lt(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_lt(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_lt(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_lt(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_lt(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_ne(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_ne(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_ne(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_ne(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_ne(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION sparsevec_negative_inner_product(public.sparsevec, public.sparsevec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sparsevec_negative_inner_product(public.sparsevec, public.sparsevec) TO postgres;
GRANT ALL ON FUNCTION public.sparsevec_negative_inner_product(public.sparsevec, public.sparsevec) TO anon;
GRANT ALL ON FUNCTION public.sparsevec_negative_inner_product(public.sparsevec, public.sparsevec) TO authenticated;
GRANT ALL ON FUNCTION public.sparsevec_negative_inner_product(public.sparsevec, public.sparsevec) TO service_role;


--
-- Name: FUNCTION strict_word_similarity(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.strict_word_similarity(text, text) TO postgres;
GRANT ALL ON FUNCTION public.strict_word_similarity(text, text) TO anon;
GRANT ALL ON FUNCTION public.strict_word_similarity(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.strict_word_similarity(text, text) TO service_role;


--
-- Name: FUNCTION strict_word_similarity_commutator_op(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.strict_word_similarity_commutator_op(text, text) TO postgres;
GRANT ALL ON FUNCTION public.strict_word_similarity_commutator_op(text, text) TO anon;
GRANT ALL ON FUNCTION public.strict_word_similarity_commutator_op(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.strict_word_similarity_commutator_op(text, text) TO service_role;


--
-- Name: FUNCTION strict_word_similarity_dist_commutator_op(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.strict_word_similarity_dist_commutator_op(text, text) TO postgres;
GRANT ALL ON FUNCTION public.strict_word_similarity_dist_commutator_op(text, text) TO anon;
GRANT ALL ON FUNCTION public.strict_word_similarity_dist_commutator_op(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.strict_word_similarity_dist_commutator_op(text, text) TO service_role;


--
-- Name: FUNCTION strict_word_similarity_dist_op(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.strict_word_similarity_dist_op(text, text) TO postgres;
GRANT ALL ON FUNCTION public.strict_word_similarity_dist_op(text, text) TO anon;
GRANT ALL ON FUNCTION public.strict_word_similarity_dist_op(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.strict_word_similarity_dist_op(text, text) TO service_role;


--
-- Name: FUNCTION strict_word_similarity_op(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.strict_word_similarity_op(text, text) TO postgres;
GRANT ALL ON FUNCTION public.strict_word_similarity_op(text, text) TO anon;
GRANT ALL ON FUNCTION public.strict_word_similarity_op(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.strict_word_similarity_op(text, text) TO service_role;


--
-- Name: FUNCTION subvector(public.halfvec, integer, integer); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.subvector(public.halfvec, integer, integer) TO postgres;
GRANT ALL ON FUNCTION public.subvector(public.halfvec, integer, integer) TO anon;
GRANT ALL ON FUNCTION public.subvector(public.halfvec, integer, integer) TO authenticated;
GRANT ALL ON FUNCTION public.subvector(public.halfvec, integer, integer) TO service_role;


--
-- Name: FUNCTION subvector(public.vector, integer, integer); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.subvector(public.vector, integer, integer) TO postgres;
GRANT ALL ON FUNCTION public.subvector(public.vector, integer, integer) TO anon;
GRANT ALL ON FUNCTION public.subvector(public.vector, integer, integer) TO authenticated;
GRANT ALL ON FUNCTION public.subvector(public.vector, integer, integer) TO service_role;


--
-- Name: FUNCTION vector_accum(double precision[], public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_accum(double precision[], public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_accum(double precision[], public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_accum(double precision[], public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_accum(double precision[], public.vector) TO service_role;


--
-- Name: FUNCTION vector_add(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_add(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_add(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_add(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_add(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_avg(double precision[]); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_avg(double precision[]) TO postgres;
GRANT ALL ON FUNCTION public.vector_avg(double precision[]) TO anon;
GRANT ALL ON FUNCTION public.vector_avg(double precision[]) TO authenticated;
GRANT ALL ON FUNCTION public.vector_avg(double precision[]) TO service_role;


--
-- Name: FUNCTION vector_cmp(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_cmp(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_cmp(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_cmp(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_cmp(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_combine(double precision[], double precision[]); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_combine(double precision[], double precision[]) TO postgres;
GRANT ALL ON FUNCTION public.vector_combine(double precision[], double precision[]) TO anon;
GRANT ALL ON FUNCTION public.vector_combine(double precision[], double precision[]) TO authenticated;
GRANT ALL ON FUNCTION public.vector_combine(double precision[], double precision[]) TO service_role;


--
-- Name: FUNCTION vector_concat(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_concat(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_concat(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_concat(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_concat(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_dims(public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_dims(public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.vector_dims(public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.vector_dims(public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.vector_dims(public.halfvec) TO service_role;


--
-- Name: FUNCTION vector_dims(public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_dims(public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_dims(public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_dims(public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_dims(public.vector) TO service_role;


--
-- Name: FUNCTION vector_eq(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_eq(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_eq(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_eq(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_eq(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_ge(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_ge(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_ge(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_ge(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_ge(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_gt(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_gt(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_gt(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_gt(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_gt(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_l2_squared_distance(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_l2_squared_distance(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_l2_squared_distance(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_l2_squared_distance(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_l2_squared_distance(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_le(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_le(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_le(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_le(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_le(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_lt(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_lt(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_lt(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_lt(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_lt(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_mul(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_mul(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_mul(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_mul(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_mul(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_ne(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_ne(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_ne(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_ne(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_ne(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_negative_inner_product(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_negative_inner_product(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_negative_inner_product(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_negative_inner_product(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_negative_inner_product(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_norm(public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_norm(public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_norm(public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_norm(public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_norm(public.vector) TO service_role;


--
-- Name: FUNCTION vector_spherical_distance(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_spherical_distance(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_spherical_distance(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_spherical_distance(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_spherical_distance(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION vector_sub(public.vector, public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.vector_sub(public.vector, public.vector) TO postgres;
GRANT ALL ON FUNCTION public.vector_sub(public.vector, public.vector) TO anon;
GRANT ALL ON FUNCTION public.vector_sub(public.vector, public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.vector_sub(public.vector, public.vector) TO service_role;


--
-- Name: FUNCTION word_similarity(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.word_similarity(text, text) TO postgres;
GRANT ALL ON FUNCTION public.word_similarity(text, text) TO anon;
GRANT ALL ON FUNCTION public.word_similarity(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.word_similarity(text, text) TO service_role;


--
-- Name: FUNCTION word_similarity_commutator_op(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.word_similarity_commutator_op(text, text) TO postgres;
GRANT ALL ON FUNCTION public.word_similarity_commutator_op(text, text) TO anon;
GRANT ALL ON FUNCTION public.word_similarity_commutator_op(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.word_similarity_commutator_op(text, text) TO service_role;


--
-- Name: FUNCTION word_similarity_dist_commutator_op(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.word_similarity_dist_commutator_op(text, text) TO postgres;
GRANT ALL ON FUNCTION public.word_similarity_dist_commutator_op(text, text) TO anon;
GRANT ALL ON FUNCTION public.word_similarity_dist_commutator_op(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.word_similarity_dist_commutator_op(text, text) TO service_role;


--
-- Name: FUNCTION word_similarity_dist_op(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.word_similarity_dist_op(text, text) TO postgres;
GRANT ALL ON FUNCTION public.word_similarity_dist_op(text, text) TO anon;
GRANT ALL ON FUNCTION public.word_similarity_dist_op(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.word_similarity_dist_op(text, text) TO service_role;


--
-- Name: FUNCTION word_similarity_op(text, text); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.word_similarity_op(text, text) TO postgres;
GRANT ALL ON FUNCTION public.word_similarity_op(text, text) TO anon;
GRANT ALL ON FUNCTION public.word_similarity_op(text, text) TO authenticated;
GRANT ALL ON FUNCTION public.word_similarity_op(text, text) TO service_role;


--
-- Name: FUNCTION apply_rls(wal jsonb, max_record_bytes integer); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.apply_rls(wal jsonb, max_record_bytes integer) TO postgres;
GRANT ALL ON FUNCTION realtime.apply_rls(wal jsonb, max_record_bytes integer) TO dashboard_user;
GRANT ALL ON FUNCTION realtime.apply_rls(wal jsonb, max_record_bytes integer) TO anon;
GRANT ALL ON FUNCTION realtime.apply_rls(wal jsonb, max_record_bytes integer) TO authenticated;
GRANT ALL ON FUNCTION realtime.apply_rls(wal jsonb, max_record_bytes integer) TO service_role;


--
-- Name: FUNCTION broadcast_changes(topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.broadcast_changes(topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text) TO postgres;
GRANT ALL ON FUNCTION realtime.broadcast_changes(topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text) TO dashboard_user;


--
-- Name: FUNCTION build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]) TO postgres;
GRANT ALL ON FUNCTION realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]) TO dashboard_user;
GRANT ALL ON FUNCTION realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]) TO anon;
GRANT ALL ON FUNCTION realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]) TO authenticated;
GRANT ALL ON FUNCTION realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]) TO service_role;


--
-- Name: FUNCTION "cast"(val text, type_ regtype); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime."cast"(val text, type_ regtype) TO postgres;
GRANT ALL ON FUNCTION realtime."cast"(val text, type_ regtype) TO dashboard_user;
GRANT ALL ON FUNCTION realtime."cast"(val text, type_ regtype) TO anon;
GRANT ALL ON FUNCTION realtime."cast"(val text, type_ regtype) TO authenticated;
GRANT ALL ON FUNCTION realtime."cast"(val text, type_ regtype) TO service_role;


--
-- Name: FUNCTION check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text) TO postgres;
GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text) TO dashboard_user;
GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text) TO anon;
GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text) TO authenticated;
GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text) TO service_role;


--
-- Name: FUNCTION check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text, negate boolean); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text, negate boolean) TO postgres;
GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text, negate boolean) TO dashboard_user;
GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text, negate boolean) TO anon;
GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text, negate boolean) TO authenticated;
GRANT ALL ON FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text, negate boolean) TO service_role;


--
-- Name: FUNCTION is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]) TO postgres;
GRANT ALL ON FUNCTION realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]) TO dashboard_user;
GRANT ALL ON FUNCTION realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]) TO anon;
GRANT ALL ON FUNCTION realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]) TO authenticated;
GRANT ALL ON FUNCTION realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]) TO service_role;


--
-- Name: FUNCTION list_changes(publication name, slot_name name, max_changes integer, max_record_bytes integer); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.list_changes(publication name, slot_name name, max_changes integer, max_record_bytes integer) TO postgres;
GRANT ALL ON FUNCTION realtime.list_changes(publication name, slot_name name, max_changes integer, max_record_bytes integer) TO dashboard_user;


--
-- Name: FUNCTION quote_wal2json(entity regclass); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.quote_wal2json(entity regclass) TO postgres;
GRANT ALL ON FUNCTION realtime.quote_wal2json(entity regclass) TO dashboard_user;
GRANT ALL ON FUNCTION realtime.quote_wal2json(entity regclass) TO anon;
GRANT ALL ON FUNCTION realtime.quote_wal2json(entity regclass) TO authenticated;
GRANT ALL ON FUNCTION realtime.quote_wal2json(entity regclass) TO service_role;


--
-- Name: FUNCTION send(payload jsonb, event text, topic text, private boolean); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.send(payload jsonb, event text, topic text, private boolean) TO postgres;
GRANT ALL ON FUNCTION realtime.send(payload jsonb, event text, topic text, private boolean) TO dashboard_user;


--
-- Name: FUNCTION send_binary(payload bytea, event text, topic text, private boolean); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.send_binary(payload bytea, event text, topic text, private boolean) TO postgres;
GRANT ALL ON FUNCTION realtime.send_binary(payload bytea, event text, topic text, private boolean) TO dashboard_user;


--
-- Name: FUNCTION subscription_check_filters(); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.subscription_check_filters() TO postgres;
GRANT ALL ON FUNCTION realtime.subscription_check_filters() TO dashboard_user;
GRANT ALL ON FUNCTION realtime.subscription_check_filters() TO anon;
GRANT ALL ON FUNCTION realtime.subscription_check_filters() TO authenticated;
GRANT ALL ON FUNCTION realtime.subscription_check_filters() TO service_role;


--
-- Name: FUNCTION to_regrole(role_name text); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.to_regrole(role_name text) TO postgres;
GRANT ALL ON FUNCTION realtime.to_regrole(role_name text) TO dashboard_user;
GRANT ALL ON FUNCTION realtime.to_regrole(role_name text) TO anon;
GRANT ALL ON FUNCTION realtime.to_regrole(role_name text) TO authenticated;
GRANT ALL ON FUNCTION realtime.to_regrole(role_name text) TO service_role;


--
-- Name: FUNCTION topic(); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.topic() TO postgres;
GRANT ALL ON FUNCTION realtime.topic() TO dashboard_user;


--
-- Name: FUNCTION wal2json_escape_identifier(name text); Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON FUNCTION realtime.wal2json_escape_identifier(name text) TO postgres;
GRANT ALL ON FUNCTION realtime.wal2json_escape_identifier(name text) TO dashboard_user;


--
-- Name: FUNCTION _crypto_aead_det_decrypt(message bytea, additional bytea, key_id bigint, context bytea, nonce bytea); Type: ACL; Schema: vault; Owner: supabase_admin
--

GRANT ALL ON FUNCTION vault._crypto_aead_det_decrypt(message bytea, additional bytea, key_id bigint, context bytea, nonce bytea) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION vault._crypto_aead_det_decrypt(message bytea, additional bytea, key_id bigint, context bytea, nonce bytea) TO service_role;


--
-- Name: FUNCTION create_secret(new_secret text, new_name text, new_description text, new_key_id uuid); Type: ACL; Schema: vault; Owner: supabase_admin
--

GRANT ALL ON FUNCTION vault.create_secret(new_secret text, new_name text, new_description text, new_key_id uuid) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION vault.create_secret(new_secret text, new_name text, new_description text, new_key_id uuid) TO service_role;


--
-- Name: FUNCTION update_secret(secret_id uuid, new_secret text, new_name text, new_description text, new_key_id uuid); Type: ACL; Schema: vault; Owner: supabase_admin
--

GRANT ALL ON FUNCTION vault.update_secret(secret_id uuid, new_secret text, new_name text, new_description text, new_key_id uuid) TO postgres WITH GRANT OPTION;
GRANT ALL ON FUNCTION vault.update_secret(secret_id uuid, new_secret text, new_name text, new_description text, new_key_id uuid) TO service_role;


--
-- Name: FUNCTION avg(public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.avg(public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.avg(public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.avg(public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.avg(public.halfvec) TO service_role;


--
-- Name: FUNCTION avg(public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.avg(public.vector) TO postgres;
GRANT ALL ON FUNCTION public.avg(public.vector) TO anon;
GRANT ALL ON FUNCTION public.avg(public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.avg(public.vector) TO service_role;


--
-- Name: FUNCTION sum(public.halfvec); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sum(public.halfvec) TO postgres;
GRANT ALL ON FUNCTION public.sum(public.halfvec) TO anon;
GRANT ALL ON FUNCTION public.sum(public.halfvec) TO authenticated;
GRANT ALL ON FUNCTION public.sum(public.halfvec) TO service_role;


--
-- Name: FUNCTION sum(public.vector); Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON FUNCTION public.sum(public.vector) TO postgres;
GRANT ALL ON FUNCTION public.sum(public.vector) TO anon;
GRANT ALL ON FUNCTION public.sum(public.vector) TO authenticated;
GRANT ALL ON FUNCTION public.sum(public.vector) TO service_role;


--
-- Name: TABLE audit_log_entries; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.audit_log_entries TO dashboard_user;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.audit_log_entries TO postgres;
GRANT SELECT ON TABLE auth.audit_log_entries TO postgres WITH GRANT OPTION;


--
-- Name: TABLE custom_oauth_providers; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.custom_oauth_providers TO postgres;
GRANT ALL ON TABLE auth.custom_oauth_providers TO dashboard_user;


--
-- Name: TABLE flow_state; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.flow_state TO postgres;
GRANT SELECT ON TABLE auth.flow_state TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.flow_state TO dashboard_user;


--
-- Name: TABLE identities; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.identities TO postgres;
GRANT SELECT ON TABLE auth.identities TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.identities TO dashboard_user;


--
-- Name: TABLE instances; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.instances TO dashboard_user;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.instances TO postgres;
GRANT SELECT ON TABLE auth.instances TO postgres WITH GRANT OPTION;


--
-- Name: TABLE mfa_amr_claims; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.mfa_amr_claims TO postgres;
GRANT SELECT ON TABLE auth.mfa_amr_claims TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.mfa_amr_claims TO dashboard_user;


--
-- Name: TABLE mfa_challenges; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.mfa_challenges TO postgres;
GRANT SELECT ON TABLE auth.mfa_challenges TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.mfa_challenges TO dashboard_user;


--
-- Name: TABLE mfa_factors; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.mfa_factors TO postgres;
GRANT SELECT ON TABLE auth.mfa_factors TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.mfa_factors TO dashboard_user;


--
-- Name: TABLE oauth_authorizations; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.oauth_authorizations TO postgres;
GRANT ALL ON TABLE auth.oauth_authorizations TO dashboard_user;


--
-- Name: TABLE oauth_client_states; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.oauth_client_states TO postgres;
GRANT ALL ON TABLE auth.oauth_client_states TO dashboard_user;


--
-- Name: TABLE oauth_clients; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.oauth_clients TO postgres;
GRANT ALL ON TABLE auth.oauth_clients TO dashboard_user;


--
-- Name: TABLE oauth_consents; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.oauth_consents TO postgres;
GRANT ALL ON TABLE auth.oauth_consents TO dashboard_user;


--
-- Name: TABLE one_time_tokens; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.one_time_tokens TO postgres;
GRANT SELECT ON TABLE auth.one_time_tokens TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.one_time_tokens TO dashboard_user;


--
-- Name: TABLE refresh_tokens; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.refresh_tokens TO dashboard_user;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.refresh_tokens TO postgres;
GRANT SELECT ON TABLE auth.refresh_tokens TO postgres WITH GRANT OPTION;


--
-- Name: SEQUENCE refresh_tokens_id_seq; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON SEQUENCE auth.refresh_tokens_id_seq TO dashboard_user;
GRANT ALL ON SEQUENCE auth.refresh_tokens_id_seq TO postgres;


--
-- Name: TABLE saml_providers; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.saml_providers TO postgres;
GRANT SELECT ON TABLE auth.saml_providers TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.saml_providers TO dashboard_user;


--
-- Name: TABLE saml_relay_states; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.saml_relay_states TO postgres;
GRANT SELECT ON TABLE auth.saml_relay_states TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.saml_relay_states TO dashboard_user;


--
-- Name: TABLE schema_migrations; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT SELECT ON TABLE auth.schema_migrations TO postgres WITH GRANT OPTION;


--
-- Name: TABLE sessions; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.sessions TO postgres;
GRANT SELECT ON TABLE auth.sessions TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.sessions TO dashboard_user;


--
-- Name: TABLE sso_domains; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.sso_domains TO postgres;
GRANT SELECT ON TABLE auth.sso_domains TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.sso_domains TO dashboard_user;


--
-- Name: TABLE sso_providers; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.sso_providers TO postgres;
GRANT SELECT ON TABLE auth.sso_providers TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE auth.sso_providers TO dashboard_user;


--
-- Name: TABLE users; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.users TO dashboard_user;
GRANT INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,MAINTAIN,UPDATE ON TABLE auth.users TO postgres;
GRANT SELECT ON TABLE auth.users TO postgres WITH GRANT OPTION;


--
-- Name: TABLE webauthn_challenges; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.webauthn_challenges TO postgres;
GRANT ALL ON TABLE auth.webauthn_challenges TO dashboard_user;


--
-- Name: TABLE webauthn_credentials; Type: ACL; Schema: auth; Owner: supabase_auth_admin
--

GRANT ALL ON TABLE auth.webauthn_credentials TO postgres;
GRANT ALL ON TABLE auth.webauthn_credentials TO dashboard_user;


--
-- Name: TABLE pg_stat_statements; Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON TABLE extensions.pg_stat_statements FROM postgres;
GRANT ALL ON TABLE extensions.pg_stat_statements TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE extensions.pg_stat_statements TO dashboard_user;


--
-- Name: TABLE pg_stat_statements_info; Type: ACL; Schema: extensions; Owner: postgres
--

REVOKE ALL ON TABLE extensions.pg_stat_statements_info FROM postgres;
GRANT ALL ON TABLE extensions.pg_stat_statements_info TO postgres WITH GRANT OPTION;
GRANT ALL ON TABLE extensions.pg_stat_statements_info TO dashboard_user;


--
-- Name: TABLE sec_8k_filings; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sec_8k_filings TO anon;
GRANT ALL ON TABLE public.sec_8k_filings TO authenticated;
GRANT ALL ON TABLE public.sec_8k_filings TO service_role;


--
-- Name: TABLE securities; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.securities TO anon;
GRANT ALL ON TABLE public.securities TO authenticated;
GRANT ALL ON TABLE public.securities TO service_role;


--
-- Name: TABLE candidate_8k_events; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.candidate_8k_events TO anon;
GRANT ALL ON TABLE public.candidate_8k_events TO authenticated;
GRANT ALL ON TABLE public.candidate_8k_events TO service_role;


--
-- Name: TABLE candidate_8k_events_legacy; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.candidate_8k_events_legacy TO anon;
GRANT ALL ON TABLE public.candidate_8k_events_legacy TO authenticated;
GRANT ALL ON TABLE public.candidate_8k_events_legacy TO service_role;


--
-- Name: TABLE financial_growth_classified; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.financial_growth_classified TO anon;
GRANT ALL ON TABLE public.financial_growth_classified TO authenticated;
GRANT ALL ON TABLE public.financial_growth_classified TO service_role;


--
-- Name: TABLE financial_metrics; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.financial_metrics TO anon;
GRANT ALL ON TABLE public.financial_metrics TO authenticated;
GRANT ALL ON TABLE public.financial_metrics TO service_role;


--
-- Name: TABLE financial_statements; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.financial_statements TO anon;
GRANT ALL ON TABLE public.financial_statements TO authenticated;
GRANT ALL ON TABLE public.financial_statements TO service_role;


--
-- Name: TABLE market_prices; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.market_prices TO anon;
GRANT ALL ON TABLE public.market_prices TO authenticated;
GRANT ALL ON TABLE public.market_prices TO service_role;


--
-- Name: TABLE sec_filings; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sec_filings TO anon;
GRANT ALL ON TABLE public.sec_filings TO authenticated;
GRANT ALL ON TABLE public.sec_filings TO service_role;


--
-- Name: TABLE financial_market_reactions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.financial_market_reactions TO anon;
GRANT ALL ON TABLE public.financial_market_reactions TO authenticated;
GRANT ALL ON TABLE public.financial_market_reactions TO service_role;


--
-- Name: TABLE candidate_financial_events; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.candidate_financial_events TO anon;
GRANT ALL ON TABLE public.candidate_financial_events TO authenticated;
GRANT ALL ON TABLE public.candidate_financial_events TO service_role;


--
-- Name: TABLE candidate_review_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.candidate_review_log TO anon;
GRANT ALL ON TABLE public.candidate_review_log TO authenticated;
GRANT ALL ON TABLE public.candidate_review_log TO service_role;


--
-- Name: TABLE classification_corrections; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.classification_corrections TO anon;
GRANT ALL ON TABLE public.classification_corrections TO authenticated;
GRANT ALL ON TABLE public.classification_corrections TO service_role;


--
-- Name: TABLE event_entity_relationships; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_entity_relationships TO anon;
GRANT ALL ON TABLE public.event_entity_relationships TO authenticated;
GRANT ALL ON TABLE public.event_entity_relationships TO service_role;


--
-- Name: TABLE event_market_reactions_corrected; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_market_reactions_corrected TO anon;
GRANT ALL ON TABLE public.event_market_reactions_corrected TO authenticated;
GRANT ALL ON TABLE public.event_market_reactions_corrected TO service_role;


--
-- Name: TABLE events; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.events TO anon;
GRANT ALL ON TABLE public.events TO authenticated;
GRANT ALL ON TABLE public.events TO service_role;


--
-- Name: TABLE event_market_reactions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_market_reactions TO anon;
GRANT ALL ON TABLE public.event_market_reactions TO authenticated;
GRANT ALL ON TABLE public.event_market_reactions TO service_role;


--
-- Name: TABLE filing_ai_classifications; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.filing_ai_classifications TO anon;
GRANT ALL ON TABLE public.filing_ai_classifications TO authenticated;
GRANT ALL ON TABLE public.filing_ai_classifications TO service_role;


--
-- Name: TABLE classifier_confidence_calibration; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.classifier_confidence_calibration TO anon;
GRANT ALL ON TABLE public.classifier_confidence_calibration TO authenticated;
GRANT ALL ON TABLE public.classifier_confidence_calibration TO service_role;


--
-- Name: TABLE company_sentiment_timeline; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.company_sentiment_timeline TO anon;
GRANT ALL ON TABLE public.company_sentiment_timeline TO authenticated;
GRANT ALL ON TABLE public.company_sentiment_timeline TO service_role;


--
-- Name: TABLE event_relationships; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_relationships TO anon;
GRANT ALL ON TABLE public.event_relationships TO authenticated;
GRANT ALL ON TABLE public.event_relationships TO service_role;


--
-- Name: TABLE cross_entity_web; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.cross_entity_web TO anon;
GRANT ALL ON TABLE public.cross_entity_web TO authenticated;
GRANT ALL ON TABLE public.cross_entity_web TO service_role;


--
-- Name: TABLE cross_entity_web_v2; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.cross_entity_web_v2 TO anon;
GRANT ALL ON TABLE public.cross_entity_web_v2 TO authenticated;
GRANT ALL ON TABLE public.cross_entity_web_v2 TO service_role;


--
-- Name: TABLE entities; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.entities TO anon;
GRANT ALL ON TABLE public.entities TO authenticated;
GRANT ALL ON TABLE public.entities TO service_role;


--
-- Name: TABLE event_article_relationships; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_article_relationships TO anon;
GRANT ALL ON TABLE public.event_article_relationships TO authenticated;
GRANT ALL ON TABLE public.event_article_relationships TO service_role;


--
-- Name: TABLE event_candidate_triage; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_candidate_triage TO anon;
GRANT ALL ON TABLE public.event_candidate_triage TO authenticated;
GRANT ALL ON TABLE public.event_candidate_triage TO service_role;


--
-- Name: TABLE event_component_dates; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_component_dates TO anon;
GRANT ALL ON TABLE public.event_component_dates TO authenticated;
GRANT ALL ON TABLE public.event_component_dates TO service_role;


--
-- Name: TABLE event_pre_context; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_pre_context TO anon;
GRANT ALL ON TABLE public.event_pre_context TO authenticated;
GRANT ALL ON TABLE public.event_pre_context TO service_role;


--
-- Name: TABLE event_tag_suggestions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_tag_suggestions TO anon;
GRANT ALL ON TABLE public.event_tag_suggestions TO authenticated;
GRANT ALL ON TABLE public.event_tag_suggestions TO service_role;


--
-- Name: TABLE event_tags; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_tags TO anon;
GRANT ALL ON TABLE public.event_tags TO authenticated;
GRANT ALL ON TABLE public.event_tags TO service_role;


--
-- Name: TABLE event_type_relationships; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_type_relationships TO anon;
GRANT ALL ON TABLE public.event_type_relationships TO authenticated;
GRANT ALL ON TABLE public.event_type_relationships TO service_role;


--
-- Name: TABLE event_types; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.event_types TO anon;
GRANT ALL ON TABLE public.event_types TO authenticated;
GRANT ALL ON TABLE public.event_types TO service_role;


--
-- Name: TABLE financial_analysis; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.financial_analysis TO anon;
GRANT ALL ON TABLE public.financial_analysis TO authenticated;
GRANT ALL ON TABLE public.financial_analysis TO service_role;


--
-- Name: TABLE financial_analysis_clean; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.financial_analysis_clean TO anon;
GRANT ALL ON TABLE public.financial_analysis_clean TO authenticated;
GRANT ALL ON TABLE public.financial_analysis_clean TO service_role;


--
-- Name: TABLE financial_health_snapshot; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.financial_health_snapshot TO anon;
GRANT ALL ON TABLE public.financial_health_snapshot TO authenticated;
GRANT ALL ON TABLE public.financial_health_snapshot TO service_role;


--
-- Name: TABLE fundamental_signals; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.fundamental_signals TO anon;
GRANT ALL ON TABLE public.fundamental_signals TO authenticated;
GRANT ALL ON TABLE public.fundamental_signals TO service_role;


--
-- Name: TABLE financial_condition_summary; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.financial_condition_summary TO anon;
GRANT ALL ON TABLE public.financial_condition_summary TO authenticated;
GRANT ALL ON TABLE public.financial_condition_summary TO service_role;


--
-- Name: TABLE financial_filing_events; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.financial_filing_events TO anon;
GRANT ALL ON TABLE public.financial_filing_events TO authenticated;
GRANT ALL ON TABLE public.financial_filing_events TO service_role;


--
-- Name: TABLE hypopg_list_indexes; Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON TABLE public.hypopg_list_indexes TO postgres;
GRANT ALL ON TABLE public.hypopg_list_indexes TO anon;
GRANT ALL ON TABLE public.hypopg_list_indexes TO authenticated;
GRANT ALL ON TABLE public.hypopg_list_indexes TO service_role;


--
-- Name: TABLE hypopg_hidden_indexes; Type: ACL; Schema: public; Owner: supabase_admin
--

GRANT ALL ON TABLE public.hypopg_hidden_indexes TO postgres;
GRANT ALL ON TABLE public.hypopg_hidden_indexes TO anon;
GRANT ALL ON TABLE public.hypopg_hidden_indexes TO authenticated;
GRANT ALL ON TABLE public.hypopg_hidden_indexes TO service_role;


--
-- Name: TABLE macro_data_releases; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.macro_data_releases TO anon;
GRANT ALL ON TABLE public.macro_data_releases TO authenticated;
GRANT ALL ON TABLE public.macro_data_releases TO service_role;


--
-- Name: TABLE market_regimes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.market_regimes TO anon;
GRANT ALL ON TABLE public.market_regimes TO authenticated;
GRANT ALL ON TABLE public.market_regimes TO service_role;


--
-- Name: TABLE news_ai_classifications; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.news_ai_classifications TO anon;
GRANT ALL ON TABLE public.news_ai_classifications TO authenticated;
GRANT ALL ON TABLE public.news_ai_classifications TO service_role;


--
-- Name: TABLE news_article_entities; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.news_article_entities TO anon;
GRANT ALL ON TABLE public.news_article_entities TO authenticated;
GRANT ALL ON TABLE public.news_article_entities TO service_role;


--
-- Name: TABLE news_articles; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.news_articles TO anon;
GRANT ALL ON TABLE public.news_articles TO authenticated;
GRANT ALL ON TABLE public.news_articles TO service_role;


--
-- Name: TABLE news_candidate_events; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.news_candidate_events TO anon;
GRANT ALL ON TABLE public.news_candidate_events TO authenticated;
GRANT ALL ON TABLE public.news_candidate_events TO service_role;


--
-- Name: TABLE pattern_significance_tests; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.pattern_significance_tests TO anon;
GRANT ALL ON TABLE public.pattern_significance_tests TO authenticated;
GRANT ALL ON TABLE public.pattern_significance_tests TO service_role;


--
-- Name: TABLE recoverable_rejected_noise; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.recoverable_rejected_noise TO anon;
GRANT ALL ON TABLE public.recoverable_rejected_noise TO authenticated;
GRANT ALL ON TABLE public.recoverable_rejected_noise TO service_role;


--
-- Name: TABLE tags; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.tags TO anon;
GRANT ALL ON TABLE public.tags TO authenticated;
GRANT ALL ON TABLE public.tags TO service_role;


--
-- Name: TABLE same_entity_sequence_chain_position; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.same_entity_sequence_chain_position TO anon;
GRANT ALL ON TABLE public.same_entity_sequence_chain_position TO authenticated;
GRANT ALL ON TABLE public.same_entity_sequence_chain_position TO service_role;


--
-- Name: TABLE messages; Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON TABLE realtime.messages TO postgres;
GRANT ALL ON TABLE realtime.messages TO dashboard_user;
GRANT SELECT,INSERT,UPDATE ON TABLE realtime.messages TO anon;
GRANT SELECT,INSERT,UPDATE ON TABLE realtime.messages TO authenticated;
GRANT SELECT,INSERT,UPDATE ON TABLE realtime.messages TO service_role;


--
-- Name: TABLE schema_migrations; Type: ACL; Schema: realtime; Owner: supabase_admin
--

GRANT ALL ON TABLE realtime.schema_migrations TO postgres;
GRANT ALL ON TABLE realtime.schema_migrations TO dashboard_user;


--
-- Name: TABLE subscription; Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON TABLE realtime.subscription TO postgres;
GRANT ALL ON TABLE realtime.subscription TO dashboard_user;
GRANT SELECT ON TABLE realtime.subscription TO anon;
GRANT SELECT ON TABLE realtime.subscription TO authenticated;
GRANT SELECT ON TABLE realtime.subscription TO service_role;


--
-- Name: SEQUENCE subscription_id_seq; Type: ACL; Schema: realtime; Owner: supabase_realtime_admin
--

GRANT ALL ON SEQUENCE realtime.subscription_id_seq TO postgres;
GRANT ALL ON SEQUENCE realtime.subscription_id_seq TO dashboard_user;
GRANT USAGE ON SEQUENCE realtime.subscription_id_seq TO anon;
GRANT USAGE ON SEQUENCE realtime.subscription_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE realtime.subscription_id_seq TO service_role;


--
-- Name: TABLE buckets; Type: ACL; Schema: storage; Owner: supabase_storage_admin
--

REVOKE ALL ON TABLE storage.buckets FROM supabase_storage_admin;
GRANT ALL ON TABLE storage.buckets TO supabase_storage_admin WITH GRANT OPTION;
GRANT ALL ON TABLE storage.buckets TO service_role;
GRANT ALL ON TABLE storage.buckets TO authenticated;
GRANT ALL ON TABLE storage.buckets TO anon;
GRANT ALL ON TABLE storage.buckets TO postgres WITH GRANT OPTION;


--
-- Name: TABLE buckets_analytics; Type: ACL; Schema: storage; Owner: supabase_storage_admin
--

GRANT ALL ON TABLE storage.buckets_analytics TO service_role;
GRANT ALL ON TABLE storage.buckets_analytics TO authenticated;
GRANT ALL ON TABLE storage.buckets_analytics TO anon;


--
-- Name: TABLE buckets_vectors; Type: ACL; Schema: storage; Owner: supabase_storage_admin
--

GRANT SELECT ON TABLE storage.buckets_vectors TO service_role;
GRANT SELECT ON TABLE storage.buckets_vectors TO authenticated;
GRANT SELECT ON TABLE storage.buckets_vectors TO anon;


--
-- Name: TABLE objects; Type: ACL; Schema: storage; Owner: supabase_storage_admin
--

REVOKE ALL ON TABLE storage.objects FROM supabase_storage_admin;
GRANT ALL ON TABLE storage.objects TO supabase_storage_admin WITH GRANT OPTION;
GRANT ALL ON TABLE storage.objects TO service_role;
GRANT ALL ON TABLE storage.objects TO authenticated;
GRANT ALL ON TABLE storage.objects TO anon;
GRANT ALL ON TABLE storage.objects TO postgres WITH GRANT OPTION;


--
-- Name: TABLE s3_multipart_uploads; Type: ACL; Schema: storage; Owner: supabase_storage_admin
--

GRANT ALL ON TABLE storage.s3_multipart_uploads TO service_role;
GRANT SELECT ON TABLE storage.s3_multipart_uploads TO authenticated;
GRANT SELECT ON TABLE storage.s3_multipart_uploads TO anon;


--
-- Name: TABLE s3_multipart_uploads_parts; Type: ACL; Schema: storage; Owner: supabase_storage_admin
--

GRANT ALL ON TABLE storage.s3_multipart_uploads_parts TO service_role;
GRANT SELECT ON TABLE storage.s3_multipart_uploads_parts TO authenticated;
GRANT SELECT ON TABLE storage.s3_multipart_uploads_parts TO anon;


--
-- Name: TABLE vector_indexes; Type: ACL; Schema: storage; Owner: supabase_storage_admin
--

GRANT SELECT ON TABLE storage.vector_indexes TO service_role;
GRANT SELECT ON TABLE storage.vector_indexes TO authenticated;
GRANT SELECT ON TABLE storage.vector_indexes TO anon;


--
-- Name: TABLE secrets; Type: ACL; Schema: vault; Owner: supabase_admin
--

GRANT SELECT,REFERENCES,DELETE,TRUNCATE ON TABLE vault.secrets TO postgres WITH GRANT OPTION;
GRANT SELECT,DELETE ON TABLE vault.secrets TO service_role;


--
-- Name: TABLE decrypted_secrets; Type: ACL; Schema: vault; Owner: supabase_admin
--

GRANT SELECT,REFERENCES,DELETE,TRUNCATE ON TABLE vault.decrypted_secrets TO postgres WITH GRANT OPTION;
GRANT SELECT,DELETE ON TABLE vault.decrypted_secrets TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: auth; Owner: supabase_auth_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_auth_admin IN SCHEMA auth GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_auth_admin IN SCHEMA auth GRANT ALL ON SEQUENCES TO dashboard_user;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: auth; Owner: supabase_auth_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_auth_admin IN SCHEMA auth GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_auth_admin IN SCHEMA auth GRANT ALL ON FUNCTIONS TO dashboard_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: auth; Owner: supabase_auth_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_auth_admin IN SCHEMA auth GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_auth_admin IN SCHEMA auth GRANT ALL ON TABLES TO dashboard_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: extensions; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA extensions GRANT ALL ON SEQUENCES TO postgres WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: extensions; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA extensions GRANT ALL ON FUNCTIONS TO postgres WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: extensions; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA extensions GRANT ALL ON TABLES TO postgres WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: graphql; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON SEQUENCES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON SEQUENCES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON SEQUENCES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: graphql; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON FUNCTIONS TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON FUNCTIONS TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON FUNCTIONS TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: graphql; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql GRANT ALL ON TABLES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: graphql_public; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON SEQUENCES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON SEQUENCES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON SEQUENCES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: graphql_public; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON FUNCTIONS TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON FUNCTIONS TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON FUNCTIONS TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: graphql_public; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA graphql_public GRANT ALL ON TABLES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON TABLES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: realtime; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA realtime GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA realtime GRANT ALL ON SEQUENCES TO dashboard_user;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: realtime; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA realtime GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA realtime GRANT ALL ON FUNCTIONS TO dashboard_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: realtime; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA realtime GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA realtime GRANT ALL ON TABLES TO dashboard_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: storage; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON SEQUENCES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON SEQUENCES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON SEQUENCES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: storage; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON FUNCTIONS TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON FUNCTIONS TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON FUNCTIONS TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: storage; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA storage GRANT ALL ON TABLES TO service_role;


--
-- Name: issue_graphql_placeholder; Type: EVENT TRIGGER; Schema: -; Owner: supabase_admin
--

CREATE EVENT TRIGGER issue_graphql_placeholder ON sql_drop
         WHEN TAG IN ('DROP EXTENSION')
   EXECUTE FUNCTION extensions.set_graphql_placeholder();


ALTER EVENT TRIGGER issue_graphql_placeholder OWNER TO supabase_admin;

--
-- Name: issue_pg_cron_access; Type: EVENT TRIGGER; Schema: -; Owner: supabase_admin
--

CREATE EVENT TRIGGER issue_pg_cron_access ON ddl_command_end
         WHEN TAG IN ('CREATE EXTENSION')
   EXECUTE FUNCTION extensions.grant_pg_cron_access();


ALTER EVENT TRIGGER issue_pg_cron_access OWNER TO supabase_admin;

--
-- Name: issue_pg_graphql_access; Type: EVENT TRIGGER; Schema: -; Owner: supabase_admin
--

CREATE EVENT TRIGGER issue_pg_graphql_access ON ddl_command_end
         WHEN TAG IN ('CREATE EXTENSION')
   EXECUTE FUNCTION extensions.grant_pg_graphql_access();


ALTER EVENT TRIGGER issue_pg_graphql_access OWNER TO supabase_admin;

--
-- Name: issue_pg_net_access; Type: EVENT TRIGGER; Schema: -; Owner: supabase_admin
--

CREATE EVENT TRIGGER issue_pg_net_access ON ddl_command_end
         WHEN TAG IN ('CREATE EXTENSION')
   EXECUTE FUNCTION extensions.grant_pg_net_access();


ALTER EVENT TRIGGER issue_pg_net_access OWNER TO supabase_admin;

--
-- Name: pgrst_ddl_watch; Type: EVENT TRIGGER; Schema: -; Owner: supabase_admin
--

CREATE EVENT TRIGGER pgrst_ddl_watch ON ddl_command_end
   EXECUTE FUNCTION extensions.pgrst_ddl_watch();


ALTER EVENT TRIGGER pgrst_ddl_watch OWNER TO supabase_admin;

--
-- Name: pgrst_drop_watch; Type: EVENT TRIGGER; Schema: -; Owner: supabase_admin
--

CREATE EVENT TRIGGER pgrst_drop_watch ON sql_drop
   EXECUTE FUNCTION extensions.pgrst_drop_watch();


ALTER EVENT TRIGGER pgrst_drop_watch OWNER TO supabase_admin;

--
-- PostgreSQL database dump complete
--

\unrestrict v8JkyzkwOmGjn5QFRjWZBkZHHRH87JGbkyyo7gYQxa2BrFEDlbwU3augD8hoKDq

