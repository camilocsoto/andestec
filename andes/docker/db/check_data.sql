--
-- PostgreSQL database dump
--

-- Dumped from database version 12.22 (Ubuntu 12.22-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.22 (Ubuntu 12.22-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: andes_sensors; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.andes_sensors (sen_id, sen_name, sen_direction, max_output_force, sen_serialno, sen_imei, user_us_id_id, max_masa) FROM stdin;
1	sensor 1	Calle 74 # 86-40	7.40	YAVMMQYKDANVXPYU	867869060011038	2	10.00
\.


--
-- Data for Name: andes_users; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.andes_users (id, us_name, us_contact, us_mail, us_hash_pass, us_status) FROM stdin;
2	Andes Technologies	3143232442	jcamilo.csoto@gmail.com	hashed_password	\\x01
\.


--
-- Data for Name: andes_variables; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.andes_variables (id, var_temperature, var_radiofrecuency, var_presure, var_time, var_battery, localizacion, sensors_sen_id_id, var_current_capacity, var_output_capacity, var_litres) FROM stdin;
184	20.00	28	0.00	2024-10-03 17:44:14+00	96	4.294071 -74.028749	1	0	0	0.00
90	15.15	27	11.50	2024-08-29 07:34:41+00	97	4.294071 -74.028749	1	8	10	17.96
61	23.01	27	61.30	2024-08-28 03:30:41+00	97	4.294071 -74.028749	1	53	53	17.96
66	-30.01	27	50.53	2024-08-28 05:34:41+00	97	4.294071 -74.028749	1	25	0	17.96
65	35.01	27	34.53	2024-08-28 04:34:41+00	97	4.294071 -74.028749	1	13	0	17.96
39	17.20	27	110.86	2024-08-20 12:26:48+00	97	4.294071 -74.028749	1	15	46	17.96
47	18.70	24	0.00	2024-08-28 17:26:41+00	97	4.294071 -74.028749	1	0	0	17.96
38	17.60	27	15.46	2024-08-16 12:26:48+00	97	4.294071 -74.028749	1	15	49	17.96
37	17.30	25	15.76	2024-08-16 11:26:48+00	97	4.294071 -74.028749	1	15	49	17.96
36	17.10	24	15.45	2024-08-16 10:26:48+00	97	4.294071 -74.028749	1	15	49	17.96
35	17.10	27	43.29	2024-08-16 09:26:50+00	97	4.294071 -74.028749	1	15	49	17.96
34	16.70	26	96.86	2024-08-16 08:26:48+00	97	4.294071 -74.028749	1	15	49	17.96
33	18.00	26	99.17	2024-08-15 17:26:48+00	97	4.294071 -74.028749	1	15	49	17.96
32	17.90	30	98.91	2024-08-15 16:26:48+00	97	4.294071 -74.028749	1	15	49	17.96
27	17.30	23	97.39	2024-08-15 12:32:47+00	97	4.294071 -74.028749	1	16	49	17.96
28	17.30	23	97.40	2024-08-15 12:33:47+00	97	4.294071 -74.028749	1	16	49	17.96
29	17.30	28	97.42	2024-08-15 12:34:47+00	97	4.294071 -74.028749	1	16	49	17.96
30	17.30	22	97.43	2024-08-15 12:35:47+00	97	4.294071 -74.028749	1	16	49	17.96
31	17.30	23	97.44	2024-08-15 12:36:47+00	97	4.294071 -74.028749	1	16	49	17.96
21	17.30	22	97.32	2024-08-15 12:24:47+00	97	4.294071 -74.028749	1	17	49	17.96
22	17.30	26	97.33	2024-08-15 12:26:47+00	97	4.294071 -74.028749	1	17	49	17.96
23	17.30	23	97.34	2024-08-15 12:27:47+00	97	4.294071 -74.028749	1	17	49	17.96
24	17.30	22	97.35	2024-08-15 12:28:47+00	97	4.294071 -74.028749	1	17	49	17.96
25	17.30	23	97.36	2024-08-15 12:29:47+00	97	4.294071 -74.028749	1	17	49	17.96
26	17.30	23	97.38	2024-08-15 12:31:47+00	97	4.294071 -74.028749	1	17	49	17.96
20	17.20	29	97.31	2024-08-15 12:23:47+00	97	4.294071 -74.028749	1	18	49	17.96
16	17.20	27	97.26	2024-08-15 12:19:47+00	97	4.294071 -74.028749	1	18	49	17.96
17	17.20	28	97.27	2024-08-15 12:20:47+00	97	4.294071 -74.028749	1	18	49	17.96
18	17.20	21	97.28	2024-08-15 12:21:47+00	97	4.294071 -74.028749	1	18	49	17.96
19	17.20	22	97.29	2024-08-15 12:22:47+00	97	4.294071 -74.028749	1	18	49	17.96
12	17.20	23	97.22	2024-08-15 12:15:47+00	97	4.294071 -74.028749	1	19	50	17.96
13	17.20	28	97.23	2024-08-15 12:16:47+00	97	4.294071 -74.028749	1	19	49	17.96
14	17.20	23	97.24	2024-08-15 12:17:47+00	97	4.294071 -74.028749	1	19	49	17.96
15	17.20	23	97.25	2024-08-15 12:18:47+00	97	4.294071 -74.028749	1	19	49	17.96
5	17.60	27	99.05	2024-08-12 01:18:32+00	98	4.294071 -74.028749	1	20	50	17.96
6	17.60	26	99.08	2024-08-12 01:19:32+00	98	4.294071 -74.028749	1	20	50	17.96
7	17.60	26	99.14	2024-08-12 01:24:32+00	98	4.294071 -74.028749	1	20	50	17.96
8	17.70	27	99.12	2024-08-12 01:29:32+00	98	4.294071 -74.028749	1	20	50	17.96
9	16.80	23	96.82	2024-08-15 11:41:47+00	97	4.294071 -74.028749	1	20	50	17.96
10	17.20	26	97.18	2024-08-15 12:11:47+00	97	4.294071 -74.028749	1	20	50	17.96
11	17.20	29	97.19	2024-08-15 12:12:47+00	97	4.294071 -74.028749	1	20	50	17.96
1	17.50	24	15.01	2024-08-09 23:52:38+00	98	4.294071 -74.028749	1	21	50	17.96
2	17.80	27	14.99	2024-08-11 20:33:32+00	98	4.294071 -74.028749	1	21	50	17.96
3	17.70	27	14.98	2024-08-11 22:33:32+00	98	4.294071 -74.028749	1	21	50	17.96
4	17.60	27	99.01	2024-08-12 01:17:32+00	98	4.294071 -74.028749	1	21	50	17.96
123	19.70	27	0.00	2024-10-03 16:02:14+00	96	4.294071 -74.028749	1	0	0	0.00
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
37	Can add api	10	add_api
38	Can change api	10	change_api
39	Can delete api	10	delete_api
40	Can view api	10	view_api
41	Can add sensor	11	add_sensor
42	Can change sensor	11	change_sensor
43	Can delete sensor	11	delete_sensor
44	Can view sensor	11	view_sensor
45	Can add user	12	add_user
46	Can change user	12	change_user
47	Can delete user	12	delete_user
48	Can view user	12	view_user
49	Can add variable	13	add_variable
50	Can change variable	13	change_variable
51	Can delete variable	13	delete_variable
52	Can view variable	13	view_variable
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
10	api	api
11	interface	sensor
12	interface	user
13	interface	variable
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2024-08-09 22:51:38.652464+00
2	auth	0001_initial	2024-08-09 22:51:38.755327+00
3	admin	0001_initial	2024-08-09 22:51:38.780729+00
4	admin	0002_logentry_remove_auto_add	2024-08-09 22:51:38.790592+00
5	admin	0003_logentry_add_action_flag_choices	2024-08-09 22:51:38.799531+00
6	api	0001_initial	2024-08-09 22:51:38.809982+00
7	contenttypes	0002_remove_content_type_name	2024-08-09 22:51:38.82817+00
8	auth	0002_alter_permission_name_max_length	2024-08-09 22:51:38.839148+00
9	auth	0003_alter_user_email_max_length	2024-08-09 22:51:38.849303+00
10	auth	0004_alter_user_username_opts	2024-08-09 22:51:38.859585+00
11	auth	0005_alter_user_last_login_null	2024-08-09 22:51:38.871681+00
12	auth	0006_require_contenttypes_0002	2024-08-09 22:51:38.876211+00
13	auth	0007_alter_validators_add_error_messages	2024-08-09 22:51:38.889365+00
14	auth	0008_alter_user_username_max_length	2024-08-09 22:51:38.908519+00
15	auth	0009_alter_user_last_name_max_length	2024-08-09 22:51:38.920731+00
16	auth	0010_alter_group_name_max_length	2024-08-09 22:51:38.933511+00
17	auth	0011_update_proxy_permissions	2024-08-09 22:51:38.944567+00
18	auth	0012_alter_user_first_name_max_length	2024-08-09 22:51:38.956159+00
19	dashboard	0001_initial	2024-08-10 02:26:57.360124+00
20	sessions	0001_initial	2024-08-10 02:26:57.390391+00
21	dashboard	0002_remove_variable_var_capacity_sensor_sen_porc_cap_and_more	2024-08-20 13:25:33.621994+00
22	dashboard	0003_rename_max_capacity_sensor_max_output_force_and_more	2024-08-20 14:53:05.386972+00
23	dashboard	0004_remove_sensor_sen_porc_cap	2024-08-20 15:25:06.442596+00
24	api	0002_delete_api	2024-09-02 16:23:35.544813+00
25	dashboard	0005_variable_var_litres_alter_sensor_max_output_force	2024-09-02 16:23:35.588798+00
26	dashboard	0006_alter_variable_var_litres	2024-09-02 16:39:29.154033+00
27	dashboard	0007_alter_sensor_max_masa_alter_sensor_max_output_force	2024-09-12 14:50:52.463699+00
28	dashboard	0008_remove_variable_var_litres_variable_var_grams	2024-09-19 17:04:02.455725+00
29	dashboard	0009_rename_sen_type_sensor_sen_direction_and_more	2024-10-03 15:24:17.118325+00
30	interface	0001_initial	2025-06-09 19:46:20.677691+00
31	dashboard	0010_alter_sensor_options_alter_user_options_and_more	2025-06-09 19:58:16.293584+00
32	dashboard	0011_remove_variable_sensors_sen_id_delete_sensor_and_more	2025-06-09 19:58:16.302922+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: antec; Owner: andes_admin
--

COPY antec.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: andes_sensors; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.andes_sensors (sen_id, sen_name, sen_direction, max_output_force, max_masa, sen_serialno, sen_imei, user_us_id_id) FROM stdin;
\.


--
-- Data for Name: andes_users; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.andes_users (id, us_name, us_contact, us_mail, us_hash_pass, us_status) FROM stdin;
\.


--
-- Data for Name: andes_variables; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.andes_variables (id, var_temperature, var_radiofrecuency, var_presure, var_time, var_output_capacity, var_current_capacity, var_litres, var_battery, localizacion, sensors_sen_id_id) FROM stdin;
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add sensor	7	add_sensor
26	Can change sensor	7	change_sensor
27	Can delete sensor	7	delete_sensor
28	Can view sensor	7	view_sensor
29	Can add user	8	add_user
30	Can change user	8	change_user
31	Can delete user	8	delete_user
32	Can view user	8	view_user
33	Can add variable	9	add_variable
34	Can change variable	9	change_variable
35	Can delete variable	9	delete_variable
36	Can view variable	9	view_variable
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	interface	sensor
8	interface	user
9	interface	variable
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2025-06-11 03:40:51.898573+00
2	auth	0001_initial	2025-06-11 03:40:52.003318+00
3	admin	0001_initial	2025-06-11 03:40:52.031926+00
4	admin	0002_logentry_remove_auto_add	2025-06-11 03:40:52.042717+00
5	admin	0003_logentry_add_action_flag_choices	2025-06-11 03:40:52.053802+00
6	contenttypes	0002_remove_content_type_name	2025-06-11 03:40:52.072533+00
7	auth	0002_alter_permission_name_max_length	2025-06-11 03:40:52.082493+00
8	auth	0003_alter_user_email_max_length	2025-06-11 03:40:52.092379+00
9	auth	0004_alter_user_username_opts	2025-06-11 03:40:52.101918+00
10	auth	0005_alter_user_last_login_null	2025-06-11 03:40:52.11035+00
11	auth	0006_require_contenttypes_0002	2025-06-11 03:40:52.113631+00
12	auth	0007_alter_validators_add_error_messages	2025-06-11 03:40:52.124509+00
13	auth	0008_alter_user_username_max_length	2025-06-11 03:40:52.140697+00
14	auth	0009_alter_user_last_name_max_length	2025-06-11 03:40:52.151114+00
15	auth	0010_alter_group_name_max_length	2025-06-11 03:40:52.161019+00
16	auth	0011_update_proxy_permissions	2025-06-11 03:40:52.170755+00
17	auth	0012_alter_user_first_name_max_length	2025-06-11 03:40:52.17938+00
18	interface	0001_initial	2025-06-11 03:40:52.224897+00
19	sessions	0001_initial	2025-06-11 03:40:52.297297+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: andes_admin
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Name: andes_sensors_sen_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.andes_sensors_sen_id_seq', 1, true);


--
-- Name: andes_users_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.andes_users_id_seq', 2, true);


--
-- Name: andes_variables_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.andes_variables_id_seq', 184, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.auth_permission_id_seq', 52, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.auth_user_id_seq', 1, false);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.django_content_type_id_seq', 13, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: antec; Owner: andes_admin
--

SELECT pg_catalog.setval('antec.django_migrations_id_seq', 32, true);


--
-- Name: andes_sensors_sen_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.andes_sensors_sen_id_seq', 1, false);


--
-- Name: andes_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.andes_users_id_seq', 1, false);


--
-- Name: andes_variables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.andes_variables_id_seq', 1, false);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 36, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 1, false);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 9, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: andes_admin
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 19, true);


--
-- PostgreSQL database dump complete
--

