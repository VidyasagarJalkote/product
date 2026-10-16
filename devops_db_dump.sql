--
-- PostgreSQL database dump
--

\restrict AXdNp1X43od4aT513t7BcSLzv8wXB7ORgrssoWY805FBHkeWmQzkz7u6gvSDiWk

-- Dumped from database version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)
-- Dumped by pg_dump version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)

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

DROP INDEX IF EXISTS public.idx_employees_status;
DROP INDEX IF EXISTS public.idx_employees_department;
ALTER TABLE IF EXISTS ONLY public.employees DROP CONSTRAINT IF EXISTS employees_pkey;
ALTER TABLE IF EXISTS ONLY public.employees DROP CONSTRAINT IF EXISTS employees_email_key;
ALTER TABLE IF EXISTS public.employees ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.employees_id_seq;
DROP TABLE IF EXISTS public.employees;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: employees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    role character varying(100) NOT NULL,
    department character varying(100) NOT NULL,
    salary numeric(10,2) NOT NULL,
    status character varying(50) DEFAULT 'Active'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT employees_salary_check CHECK ((salary > (0)::numeric))
);


ALTER TABLE public.employees OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employees_id_seq OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employees (id, name, email, role, department, salary, status, created_at) FROM stdin;
1	Alex Johnson	alex.j@company.com	Senior DevOps Engineer	DevOps & Cloud	95000.00	Active	2026-10-16 14:44:11.619288+05:30
2	Priya Sharma	priya.s@company.com	Cloud Infrastructure Architect	DevOps & Cloud	115000.00	Active	2026-10-16 14:44:11.619288+05:30
3	Marcus Chen	marcus.c@company.com	Full Stack Developer	Engineering	88000.00	Active	2026-10-16 14:44:11.619288+05:30
4	Elena Rostova	elena.r@company.com	Site Reliability Engineer	DevOps & Cloud	102000.00	Active	2026-10-16 14:44:11.619288+05:30
\.


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employees_id_seq', 8, true);


--
-- Name: employees employees_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_email_key UNIQUE (email);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: idx_employees_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_department ON public.employees USING btree (department);


--
-- Name: idx_employees_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_employees_status ON public.employees USING btree (status);


--
-- PostgreSQL database dump complete
--

\unrestrict AXdNp1X43od4aT513t7BcSLzv8wXB7ORgrssoWY805FBHkeWmQzkz7u6gvSDiWk

