--
-- PostgreSQL database dump
--

\restrict TCES4My8EjOQT3CV7F5CAoe4HoNaZiR15O5Iwj7ctrQwkUrGaCkFtDhR8F7Y3hF

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

-- Started on 2026-05-04 19:45:31

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 227 (class 1259 OID 16484)
-- Name: archivos_diseno; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.archivos_diseno (
    id_archivo integer NOT NULL,
    id_usuario integer NOT NULL,
    nombre_original character varying(255),
    nombre_almacenado character varying(255) NOT NULL,
    ruta_archivo character varying(500) NOT NULL,
    ruta_thumbnail character varying(500),
    tipo_mime character varying(100),
    tamano_bytes integer,
    ancho_px integer,
    alto_px integer,
    hash_md5 character varying(32),
    es_generado_ia boolean DEFAULT false NOT NULL,
    prompt_usado text,
    fecha_subida timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.archivos_diseno OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16483)
-- Name: archivos_diseno_id_archivo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.archivos_diseno_id_archivo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.archivos_diseno_id_archivo_seq OWNER TO postgres;

--
-- TOC entry 4958 (class 0 OID 0)
-- Dependencies: 226
-- Name: archivos_diseno_id_archivo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.archivos_diseno_id_archivo_seq OWNED BY public.archivos_diseno.id_archivo;


--
-- TOC entry 235 (class 1259 OID 16577)
-- Name: cupones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cupones (
    id_cupon integer NOT NULL,
    codigo character varying(50) NOT NULL,
    descripcion character varying(200),
    descuento_porcentaje numeric(5,2) NOT NULL,
    usos_maximos integer,
    usos_actuales integer DEFAULT 0 NOT NULL,
    fecha_expiracion date,
    activo boolean DEFAULT true NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cupones OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 16576)
-- Name: cupones_id_cupon_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cupones_id_cupon_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cupones_id_cupon_seq OWNER TO postgres;

--
-- TOC entry 4959 (class 0 OID 0)
-- Dependencies: 234
-- Name: cupones_id_cupon_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cupones_id_cupon_seq OWNED BY public.cupones.id_cupon;


--
-- TOC entry 237 (class 1259 OID 16590)
-- Name: descuentos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.descuentos (
    id_descuento integer NOT NULL,
    tipo character varying(50) NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    porcentaje numeric(5,2) NOT NULL,
    fecha_inicio date,
    fecha_fin date,
    condicion_json jsonb,
    activo boolean DEFAULT true NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.descuentos OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 16589)
-- Name: descuentos_id_descuento_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.descuentos_id_descuento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.descuentos_id_descuento_seq OWNER TO postgres;

--
-- TOC entry 4960 (class 0 OID 0)
-- Dependencies: 236
-- Name: descuentos_id_descuento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.descuentos_id_descuento_seq OWNED BY public.descuentos.id_descuento;


--
-- TOC entry 233 (class 1259 OID 16562)
-- Name: pagos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pagos (
    id_pago integer NOT NULL,
    id_pedido integer NOT NULL,
    metodo_pago character varying(50),
    referencia_externa character varying(200),
    monto numeric(10,2) NOT NULL,
    estado character varying(50) DEFAULT 'pendiente'::character varying NOT NULL,
    fecha_pago timestamp with time zone DEFAULT now() NOT NULL,
    fecha_aprobacion timestamp with time zone
);


ALTER TABLE public.pagos OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16561)
-- Name: pagos_id_pago_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pagos_id_pago_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pagos_id_pago_seq OWNER TO postgres;

--
-- TOC entry 4961 (class 0 OID 0)
-- Dependencies: 232
-- Name: pagos_id_pago_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pagos_id_pago_seq OWNED BY public.pagos.id_pago;


--
-- TOC entry 229 (class 1259 OID 16501)
-- Name: pedidos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pedidos (
    id_pedido integer NOT NULL,
    numero_orden character varying(30) NOT NULL,
    id_usuario integer NOT NULL,
    fecha_pedido timestamp with time zone DEFAULT now() NOT NULL,
    estado character varying(50) DEFAULT 'pendiente'::character varying NOT NULL,
    estado_pago character varying(50) DEFAULT 'pendiente'::character varying NOT NULL,
    subtotal numeric(10,2) DEFAULT 0 NOT NULL,
    descuento numeric(10,2) DEFAULT 0 NOT NULL,
    gastos_envio numeric(10,2) DEFAULT 0 NOT NULL,
    total numeric(10,2) DEFAULT 0 NOT NULL,
    direccion_envio character varying(300),
    ciudad character varying(100),
    provincia character varying(100),
    codigo_postal character varying(20),
    telefono_contacto character varying(30),
    notas_cliente text,
    notas_admin text,
    referencia_externa character varying(200),
    fecha_pago timestamp with time zone
);


ALTER TABLE public.pedidos OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16602)
-- Name: pedidos_detalle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pedidos_detalle (
    id_detalle integer NOT NULL,
    id_pedido integer NOT NULL,
    id_producto integer NOT NULL,
    detalle character varying(255),
    imagen text,
    imagen_ruta character varying(500),
    fecha timestamp with time zone DEFAULT now() NOT NULL,
    estado character varying(50) DEFAULT 'pendiente'::character varying NOT NULL,
    pago character varying(50) DEFAULT 'pendiente'::character varying NOT NULL,
    total numeric(10,2)
);


ALTER TABLE public.pedidos_detalle OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 16601)
-- Name: pedidos_detalle_id_detalle_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pedidos_detalle_id_detalle_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pedidos_detalle_id_detalle_seq OWNER TO postgres;

--
-- TOC entry 4962 (class 0 OID 0)
-- Dependencies: 238
-- Name: pedidos_detalle_id_detalle_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pedidos_detalle_id_detalle_seq OWNED BY public.pedidos_detalle.id_detalle;


--
-- TOC entry 228 (class 1259 OID 16500)
-- Name: pedidos_id_pedido_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pedidos_id_pedido_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pedidos_id_pedido_seq OWNER TO postgres;

--
-- TOC entry 4963 (class 0 OID 0)
-- Dependencies: 228
-- Name: pedidos_id_pedido_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pedidos_id_pedido_seq OWNED BY public.pedidos.id_pedido;


--
-- TOC entry 231 (class 1259 OID 16526)
-- Name: pedidos_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pedidos_items (
    id_item integer NOT NULL,
    id_pedido integer NOT NULL,
    id_variante integer NOT NULL,
    cantidad integer DEFAULT 1 NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,
    subtotal numeric(10,2) GENERATED ALWAYS AS (((cantidad)::numeric * precio_unitario)) STORED,
    estado character varying(50) DEFAULT 'pendiente'::character varying NOT NULL,
    archivo_diseno integer,
    id_diseno integer,
    tiene_diseno boolean DEFAULT false NOT NULL,
    diseno_posicion_x numeric(10,4) DEFAULT 0,
    diseno_posicion_y numeric(10,4) DEFAULT 0,
    diseno_zoom numeric(10,4) DEFAULT 1
);


ALTER TABLE public.pedidos_items OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16525)
-- Name: pedidos_items_id_item_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pedidos_items_id_item_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pedidos_items_id_item_seq OWNER TO postgres;

--
-- TOC entry 4964 (class 0 OID 0)
-- Dependencies: 230
-- Name: pedidos_items_id_item_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pedidos_items_id_item_seq OWNED BY public.pedidos_items.id_item;


--
-- TOC entry 222 (class 1259 OID 16437)
-- Name: producto_atributo_valores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.producto_atributo_valores (
    id_valor integer NOT NULL,
    id_atributo integer NOT NULL,
    valor character varying(100) NOT NULL
);


ALTER TABLE public.producto_atributo_valores OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16436)
-- Name: producto_atributo_valores_id_valor_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.producto_atributo_valores_id_valor_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.producto_atributo_valores_id_valor_seq OWNER TO postgres;

--
-- TOC entry 4965 (class 0 OID 0)
-- Dependencies: 221
-- Name: producto_atributo_valores_id_valor_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.producto_atributo_valores_id_valor_seq OWNED BY public.producto_atributo_valores.id_valor;


--
-- TOC entry 220 (class 1259 OID 16428)
-- Name: producto_atributos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.producto_atributos (
    id_atributo integer NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.producto_atributos OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16427)
-- Name: producto_atributos_id_atributo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.producto_atributos_id_atributo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.producto_atributos_id_atributo_seq OWNER TO postgres;

--
-- TOC entry 4966 (class 0 OID 0)
-- Dependencies: 219
-- Name: producto_atributos_id_atributo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.producto_atributos_id_atributo_seq OWNED BY public.producto_atributos.id_atributo;


--
-- TOC entry 224 (class 1259 OID 16451)
-- Name: producto_variantes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.producto_variantes (
    id_variante integer NOT NULL,
    id_producto integer NOT NULL,
    sku character varying(100),
    precio numeric(10,2) NOT NULL,
    stock_actual integer DEFAULT 0 NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


ALTER TABLE public.producto_variantes OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16450)
-- Name: producto_variantes_id_variante_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.producto_variantes_id_variante_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.producto_variantes_id_variante_seq OWNER TO postgres;

--
-- TOC entry 4967 (class 0 OID 0)
-- Dependencies: 223
-- Name: producto_variantes_id_variante_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.producto_variantes_id_variante_seq OWNED BY public.producto_variantes.id_variante;


--
-- TOC entry 218 (class 1259 OID 16415)
-- Name: productos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.productos (
    id_producto integer NOT NULL,
    nombre character varying(255) NOT NULL,
    descripcion text,
    categoria character varying(100),
    imagen_mockup character varying(500),
    area_impresion_ancho integer,
    area_impresion_alto integer,
    activo boolean DEFAULT true NOT NULL,
    orden_visualizacion integer DEFAULT 0 NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.productos OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16414)
-- Name: productos_id_producto_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.productos_id_producto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.productos_id_producto_seq OWNER TO postgres;

--
-- TOC entry 4968 (class 0 OID 0)
-- Dependencies: 217
-- Name: productos_id_producto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.productos_id_producto_seq OWNED BY public.productos.id_producto;


--
-- TOC entry 216 (class 1259 OID 16399)
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id_usuario integer NOT NULL,
    nombre character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    telefono character varying(20),
    password_user character varying(255) NOT NULL,
    tipo character varying(50) DEFAULT 'cliente'::character varying NOT NULL,
    cuenta_bloqueada boolean DEFAULT false NOT NULL,
    fecha_registro timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 16398)
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_usuario_seq OWNER TO postgres;

--
-- TOC entry 4969 (class 0 OID 0)
-- Dependencies: 215
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_usuario_seq OWNED BY public.usuarios.id_usuario;


--
-- TOC entry 225 (class 1259 OID 16468)
-- Name: variante_atributos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.variante_atributos (
    id_variante integer NOT NULL,
    id_valor integer NOT NULL
);


ALTER TABLE public.variante_atributos OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 16629)
-- Name: vw_cupones_disponibles; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_cupones_disponibles AS
 SELECT id_cupon,
    codigo,
    descripcion,
    descuento_porcentaje,
        CASE
            WHEN (usos_maximos IS NULL) THEN 'Ilimitado'::text
            ELSE (((usos_maximos - usos_actuales))::text || ' restantes'::text)
        END AS disponibilidad,
    fecha_expiracion,
        CASE
            WHEN (fecha_expiracion IS NULL) THEN 'Sin expiración'::text
            WHEN (fecha_expiracion < CURRENT_DATE) THEN 'Expirado'::text
            ELSE 'Vigente'::text
        END AS estado
   FROM public.cupones
  WHERE (activo = true);


ALTER VIEW public.vw_cupones_disponibles OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 16625)
-- Name: vw_descuentos_activos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_descuentos_activos AS
 SELECT id_descuento,
    tipo,
    nombre,
    descripcion,
    porcentaje,
    fecha_inicio,
    fecha_fin,
    (fecha_fin - CURRENT_DATE) AS dias_restantes
   FROM public.descuentos
  WHERE ((activo = true) AND ((CURRENT_DATE >= fecha_inicio) AND (CURRENT_DATE <= fecha_fin)));


ALTER VIEW public.vw_descuentos_activos OWNER TO postgres;

--
-- TOC entry 4684 (class 2604 OID 16487)
-- Name: archivos_diseno id_archivo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archivos_diseno ALTER COLUMN id_archivo SET DEFAULT nextval('public.archivos_diseno_id_archivo_seq'::regclass);


--
-- TOC entry 4706 (class 2604 OID 16580)
-- Name: cupones id_cupon; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cupones ALTER COLUMN id_cupon SET DEFAULT nextval('public.cupones_id_cupon_seq'::regclass);


--
-- TOC entry 4710 (class 2604 OID 16593)
-- Name: descuentos id_descuento; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.descuentos ALTER COLUMN id_descuento SET DEFAULT nextval('public.descuentos_id_descuento_seq'::regclass);


--
-- TOC entry 4703 (class 2604 OID 16565)
-- Name: pagos id_pago; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos ALTER COLUMN id_pago SET DEFAULT nextval('public.pagos_id_pago_seq'::regclass);


--
-- TOC entry 4687 (class 2604 OID 16504)
-- Name: pedidos id_pedido; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos ALTER COLUMN id_pedido SET DEFAULT nextval('public.pedidos_id_pedido_seq'::regclass);


--
-- TOC entry 4713 (class 2604 OID 16605)
-- Name: pedidos_detalle id_detalle; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_detalle ALTER COLUMN id_detalle SET DEFAULT nextval('public.pedidos_detalle_id_detalle_seq'::regclass);


--
-- TOC entry 4695 (class 2604 OID 16529)
-- Name: pedidos_items id_item; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_items ALTER COLUMN id_item SET DEFAULT nextval('public.pedidos_items_id_item_seq'::regclass);


--
-- TOC entry 4680 (class 2604 OID 16440)
-- Name: producto_atributo_valores id_valor; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_atributo_valores ALTER COLUMN id_valor SET DEFAULT nextval('public.producto_atributo_valores_id_valor_seq'::regclass);


--
-- TOC entry 4679 (class 2604 OID 16431)
-- Name: producto_atributos id_atributo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_atributos ALTER COLUMN id_atributo SET DEFAULT nextval('public.producto_atributos_id_atributo_seq'::regclass);


--
-- TOC entry 4681 (class 2604 OID 16454)
-- Name: producto_variantes id_variante; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_variantes ALTER COLUMN id_variante SET DEFAULT nextval('public.producto_variantes_id_variante_seq'::regclass);


--
-- TOC entry 4675 (class 2604 OID 16418)
-- Name: productos id_producto; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productos ALTER COLUMN id_producto SET DEFAULT nextval('public.productos_id_producto_seq'::regclass);


--
-- TOC entry 4671 (class 2604 OID 16402)
-- Name: usuarios id_usuario; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuarios_id_usuario_seq'::regclass);


--
-- TOC entry 4940 (class 0 OID 16484)
-- Dependencies: 227
-- Data for Name: archivos_diseno; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.archivos_diseno (id_archivo, id_usuario, nombre_original, nombre_almacenado, ruta_archivo, ruta_thumbnail, tipo_mime, tamano_bytes, ancho_px, alto_px, hash_md5, es_generado_ia, prompt_usado, fecha_subida) FROM stdin;
1	8	diseño_test_1.png	user8_20260504_125150_a77174e2.png	uploads/designs/user8_20260504_125150_a77174e2.png	uploads/thumbnails/thumb_user8_20260504_125150_a77174e2.png	image/png	2791	800	600	a77174e2003955f4c1826e3ea8d9a9e4	f	\N	2026-05-04 12:51:51.228714-03
2	8	diseño_test_2.png	user8_20260504_125152_e6f648c4.png	uploads/designs/user8_20260504_125152_e6f648c4.png	uploads/thumbnails/thumb_user8_20260504_125152_e6f648c4.png	image/png	2791	800	600	e6f648c42391a218bb14f8120124b8ed	f	\N	2026-05-04 12:51:52.965474-03
3	8	diseño_test_3.png	user8_20260504_125154_dde654c8.png	uploads/designs/user8_20260504_125154_dde654c8.png	uploads/thumbnails/thumb_user8_20260504_125154_dde654c8.png	image/png	2792	800	600	dde654c850317a54529058430015f5ba	f	\N	2026-05-04 12:51:54.441432-03
\.


--
-- TOC entry 4948 (class 0 OID 16577)
-- Dependencies: 235
-- Data for Name: cupones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cupones (id_cupon, codigo, descripcion, descuento_porcentaje, usos_maximos, usos_actuales, fecha_expiracion, activo, fecha_creacion) FROM stdin;
2	AMIGOS15	Descuento por referido	15.00	100	0	2026-12-31	t	2026-05-01 10:03:42.83084-03
4	MICUPON2026	Cupon 2026	10.00	5	0	2026-05-09	t	2026-05-02 13:36:28.332445-03
1	PRIMERACOMPRA10	Descuento primera compra	10.00	\N	1	\N	t	2026-05-01 10:03:42.83084-03
3	VIP25	Cupón exclusivo VIP	25.00	20	2	\N	t	2026-05-01 10:03:42.83084-03
5	BIENVENIDA20	20% de descuento en tu primera compra	20.00	100	0	2026-06-03	t	2026-05-04 16:30:43.91911-03
\.


--
-- TOC entry 4950 (class 0 OID 16590)
-- Dependencies: 237
-- Data for Name: descuentos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.descuentos (id_descuento, tipo, nombre, descripcion, porcentaje, fecha_inicio, fecha_fin, condicion_json, activo, fecha_creacion) FROM stdin;
\.


--
-- TOC entry 4946 (class 0 OID 16562)
-- Dependencies: 233
-- Data for Name: pagos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pagos (id_pago, id_pedido, metodo_pago, referencia_externa, monto, estado, fecha_pago, fecha_aprobacion) FROM stdin;
1	1	manual	\N	27000.00	aprobado	2026-05-03 17:45:00.19818-03	2026-05-03 17:45:00.203717-03
2	2	manual	\N	9000.00	aprobado	2026-05-03 18:46:09.600969-03	2026-05-03 18:46:09.616929-03
\.


--
-- TOC entry 4942 (class 0 OID 16501)
-- Dependencies: 229
-- Data for Name: pedidos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pedidos (id_pedido, numero_orden, id_usuario, fecha_pedido, estado, estado_pago, subtotal, descuento, gastos_envio, total, direccion_envio, ciudad, provincia, codigo_postal, telefono_contacto, notas_cliente, notas_admin, referencia_externa, fecha_pago) FROM stdin;
1	ORD-2026-00001	2	2026-05-03 17:41:57.775568-03	en-proceso	aprobado	30000.00	3000.00	0.00	27000.00	\N	\N	\N	\N	\N		\N	\N	2026-05-03 17:45:00.19818-03
2	ORD-2026-00002	2	2026-05-03 18:40:24.674767-03	pendiente	aprobado	9000.00	0.00	0.00	9000.00	\N	\N	\N	\N	\N		\N	\N	2026-05-03 18:46:09.600969-03
3	ORD-2026-00003	8	2026-05-04 13:04:54.45587-03	pendiente	pendiente	7000.00	0.00	0.00	7000.00	Calle Test 123	Buenos Aires	\N	\N	1123456789		\N	\N	\N
4	ORD-2026-00004	2	2026-05-04 13:11:06.138954-03	pendiente	pendiente	35000.00	0.00	0.00	35000.00	\N	\N	\N	\N	\N	estampado solo el personaje	\N	\N	\N
5	ORD-2026-00005	8	2026-05-04 13:15:30.886778-03	pendiente	pendiente	7000.00	0.00	0.00	7000.00	Calle Test 123	Buenos Aires	\N	\N	1123456789		\N	\N	\N
6	ORD-2026-00006	8	2026-05-04 13:17:04.423592-03	pendiente	pendiente	7000.00	0.00	0.00	7000.00	Calle Test 123	Buenos Aires	\N	\N	1123456789	Imagen de prueba generada	\N	\N	\N
7	ORD-2026-00007	8	2026-05-04 13:25:27.001976-03	pendiente	pendiente	7000.00	0.00	0.00	7000.00	\N	\N	\N	\N	\N		\N	\N	\N
8	ORD-2026-00008	2	2026-05-04 13:29:10.570066-03	pendiente	pendiente	14000.00	0.00	0.00	14000.00	\N	\N	\N	\N	\N		\N	\N	\N
9	ORD-2026-00009	2	2026-05-04 13:30:06.694319-03	pendiente	pendiente	14000.00	0.00	0.00	14000.00	\N	\N	\N	\N	\N		\N	\N	\N
10	ORD-2026-00010	2	2026-05-04 13:35:21.594512-03	pendiente	pendiente	18000.00	4500.00	0.00	13500.00	\N	\N	\N	\N	\N		\N	\N	\N
11	ORD-2026-00011	2	2026-05-04 13:42:18.580517-03	pendiente	pendiente	18000.00	4500.00	0.00	13500.00	\N	\N	\N	\N	\N		\N	\N	\N
\.


--
-- TOC entry 4952 (class 0 OID 16602)
-- Dependencies: 239
-- Data for Name: pedidos_detalle; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pedidos_detalle (id_detalle, id_pedido, id_producto, detalle, imagen, imagen_ruta, fecha, estado, pago, total) FROM stdin;
\.


--
-- TOC entry 4944 (class 0 OID 16526)
-- Dependencies: 231
-- Data for Name: pedidos_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pedidos_items (id_item, id_pedido, id_variante, cantidad, precio_unitario, estado, archivo_diseno, id_diseno, tiene_diseno, diseno_posicion_x, diseno_posicion_y, diseno_zoom) FROM stdin;
1	1	5	6	5000.00	pendiente	\N	\N	f	0.0000	0.0000	1.0000
2	2	2	1	9000.00	pendiente	\N	\N	f	0.0000	0.0000	1.0000
3	3	7	1	7000.00	pendiente	3	\N	t	0.0000	0.0000	1.0000
4	4	6	5	7000.00	pendiente	\N	\N	f	0.0000	0.0000	1.0000
5	5	7	1	7000.00	pendiente	3	\N	t	0.0000	0.0000	1.0000
6	6	7	1	7000.00	pendiente	\N	\N	f	0.0000	0.0000	1.0000
7	7	7	1	7000.00	pendiente	\N	\N	f	0.0000	0.0000	1.0000
8	8	7	2	7000.00	pendiente	\N	\N	f	0.0000	0.0000	1.0000
9	9	6	2	7000.00	pendiente	\N	\N	f	0.0000	0.0000	1.0000
10	10	1	2	9000.00	pendiente	\N	\N	f	0.0000	0.0000	1.0000
11	11	1	2	9000.00	pendiente	\N	\N	f	0.0000	0.0000	1.0000
\.


--
-- TOC entry 4935 (class 0 OID 16437)
-- Dependencies: 222
-- Data for Name: producto_atributo_valores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producto_atributo_valores (id_valor, id_atributo, valor) FROM stdin;
1	1	Blanco
2	1	Negro
3	1	Rojo
4	1	Azul
5	2	S
6	2	M
7	2	L
8	2	XL
16	3	acero
17	3	madera
\.


--
-- TOC entry 4933 (class 0 OID 16428)
-- Dependencies: 220
-- Data for Name: producto_atributos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producto_atributos (id_atributo, nombre) FROM stdin;
1	Color
2	Talle
3	Material
\.


--
-- TOC entry 4937 (class 0 OID 16451)
-- Dependencies: 224
-- Data for Name: producto_variantes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producto_variantes (id_variante, id_producto, sku, precio, stock_actual, activo) FROM stdin;
3	3	HOO-NEG-M	15000.00	30	t
4	3	HOO-AZU-L	15000.00	25	t
5	4	TAZA-BLA	5000.00	100	t
8	7	MOUSEPAD-STD	4000.00	80	t
9	8	CANVAS-40X60	12000.00	20	t
10	9	STICKER-PACK	3000.00	150	t
11	10	DEL-BLA	7000.00	35	t
12	11	FUNDA-15	9000.00	45	t
7	6	TOTE-BLA	7000.00	70	t
1	2	REM-OV-BLA-M	9000.00	50	t
2	2	REM-OV-NEG-L	9000.00	40	t
6	5	GOR-NEG	7000.00	60	t
13	13	TEST-SKU-ROJO-S-13	2000.00	10	t
14	13	TEST-SKU-AZUL-L-13	2000.00	5	t
17	16	09876554	4526.00	10	t
16	15	123414313123	4526.00	10	f
\.


--
-- TOC entry 4931 (class 0 OID 16415)
-- Dependencies: 218
-- Data for Name: productos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.productos (id_producto, nombre, descripcion, categoria, imagen_mockup, area_impresion_ancho, area_impresion_alto, activo, orden_visualizacion, fecha_creacion) FROM stdin;
2	Remera Oversize	Remera amplia ideal para estampados grandes	Indumentaria	/img/remera_oversize.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
3	Buzo Hoodie	Buzo con capucha personalizable	Indumentaria	/img/hoodie.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
4	Taza Cerámica	Taza blanca sublimable	Accesorios	/img/taza.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
5	Gorra Trucker	Gorra con frente estampable	Accesorios	/img/gorra.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
6	Bolsa Tote	Bolsa ecológica estampable	Accesorios	/img/tote.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
7	Mousepad	Mousepad rectangular personalizado	Oficina	/img/mousepad.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
8	Cuadro Canvas	Lienzo decorativo personalizado	Decoración	/img/canvas.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
9	Sticker Pack	Pack de stickers personalizados	Accesorios	/img/stickers.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
10	Delantal	Delantal de cocina estampable	Hogar	/img/delantal.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
11	Funda Notebook	Funda personalizada para laptop	Tecnología	/img/funda.png	\N	\N	t	0	2026-05-02 17:33:40.409366-03
12	Remera	Remera de Boca	\N	\N	\N	\N	f	0	2026-05-03 14:54:58.330715-03
1	Remera	Remera Blanca	\N	/imagenes/mockup_b35d745aefe64b79b43ac861f947777e.png	\N	\N	f	0	2026-05-02 13:42:19.826063-03
13	Producto Test 1777921444	Descripción generada por test automático	\N	\N	\N	\N	t	0	2026-05-04 16:04:05.602081-03
16	Mate	Mate de madera	\N	\N	\N	\N	t	0	2026-05-04 16:17:51.198806-03
14	Mate	Mate de acero	\N	\N	\N	\N	f	0	2026-05-04 16:14:35.448957-03
15	Mate	Mate de acero	\N	\N	\N	\N	f	0	2026-05-04 16:16:54.231347-03
\.


--
-- TOC entry 4929 (class 0 OID 16399)
-- Dependencies: 216
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id_usuario, nombre, email, telefono, password_user, tipo, cuenta_bloqueada, fecha_registro) FROM stdin;
2	Cliente Demo	cliente_101221@prendeterock.com	1160000002	0a2ddd80d1afed3573521888120ec51e$fdfbe44b888eacfdf54009dca3ebfe59db4d359995b921395bf371b4710d40e4	cliente	f	2026-05-01 10:12:21.644434-03
4	Usuario Test 104949	test_104949@prueba.com	011-9999-0000	17ef8d4148bcf192e85e4591e4f2de96$2f3e93fa9641bc42775cd19e0ae1979c0e1715a5b6a9592ef830a856c684d1a8	cliente	f	2026-05-01 10:49:50.507448-03
5	Usuario Test 105339	test_105339@prueba.com	011-9999-0000	781df645e31fac75d7d6a12a24485f11$63ddf23765ad5d0a17a76c8062a83c9c1d6908316a8726fe77452a75d011e6d3	cliente	f	2026-05-01 10:53:41.524556-03
6	Test Debug	debug_test999@x.com	123	3af5a01cf298a4731b6b9980690d8650$c7297d5583b8e313b0c31945869547539273560e9901b846e7a32ff8159389c2	cliente	f	2026-05-01 10:54:22.351278-03
7	Gabriel Sotelo	gabrielsotelo52@gmail.com	11 5566-9999	8c2463de57499bd9c846275541ec3b67$0c507f3b97a012a4a691e0689d7eb2273d77a2e9580657ce31c36c2274904cd8	cliente	f	2026-05-02 09:28:05.297746-03
3	Usuario Test 104336	test_104336@prueba.com	011-9999-8888	5344dea34cc346cb00e6b7bd74c3ea50$f5a70c553e19748e7edd5eadc818c7495215590e634d8d944180b7a8f2cbc1c7	cliente	f	2026-05-01 10:43:37.327481-03
8	María González	maria.gonzalez@email.com	11 2345-6789	f891a0278e62226e1b2143bb1c333c76$df00b677390009f2f879fb085f4ff63f6b6ffd48ec51ac09bd891a638f42456e	cliente	f	2026-05-04 12:49:42.165723-03
9	Lucas Rodríguez	lucas.rodriguez@email.com	11 9876-5432	1637e3c6c61739870ff9293a2d457d9e$b985fba059455a45e026a459032f87bbe32aa19b1398be1e6e9d75ff43cacb22	cliente	f	2026-05-04 12:49:42.954152-03
10	Ana Vázquez	ana.vazquez@email.com	11 4567-8901	6a42f2ee9a7c903e2aec82e7d2b7c737$44bf2f3188130d5439ef21c7da915069e6f4ce343570f8b8daab02fcd6b177fe	cliente	f	2026-05-04 12:49:43.36644-03
11	Carlos Pérez	carlos.perez@email.com	11 1122-3344	c3eaaf4e43fb43122b5735965fa55d6b$755f9da7ffc40a7fa79f40c816769df8750f9baef5eb6faa75cea571aea6f9dc	cliente	f	2026-05-04 12:49:43.791782-03
12	Sofía Martínez	sofia.martinez@email.com	11 5566-7788	247e6cf6ed209f507be2c67574e0156a$4698ade757a394d4bbdc52b4726330c968bfa546941725496a67777a02298775	cliente	f	2026-05-04 12:49:44.286023-03
1	Admin Principal	admin@prendeterock.com	1160000001	4d75ed5d6f5627b7e65e3c92cf1ceef3$8077c90513a2b7cf327df2d8e5a14c614be28095bc99f38017c45093375a9a9b	admin	f	2026-05-01 10:12:21.644434-03
13	Administrador	admin_101221@prendeterock.com	\N	c22a4bfbaba679a7e415527c96c5d700$0cab1edc227b639643d6a1db22b9ad44e9e1deb9218b0dec79e712dda5fddf20	admin	f	2026-05-04 17:27:25.138356-03
14	Gabriel Sotelo	gs@prendeterock.com	01165024399	de5d961b1460fdb2785f85bbca3f15e1$9e78d2cfe03a0cd19b1dade9fc116f894a84ed6959269850befd81d6ed399668	cliente	f	2026-05-04 17:29:36.914799-03
\.


--
-- TOC entry 4938 (class 0 OID 16468)
-- Dependencies: 225
-- Data for Name: variante_atributos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.variante_atributos (id_variante, id_valor) FROM stdin;
1	1
1	6
2	2
2	7
3	2
3	6
4	4
4	7
5	1
6	2
7	1
8	1
9	1
10	1
11	1
12	1
13	3
13	5
14	4
14	7
16	16
17	17
\.


--
-- TOC entry 4970 (class 0 OID 0)
-- Dependencies: 226
-- Name: archivos_diseno_id_archivo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.archivos_diseno_id_archivo_seq', 3, true);


--
-- TOC entry 4971 (class 0 OID 0)
-- Dependencies: 234
-- Name: cupones_id_cupon_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cupones_id_cupon_seq', 5, true);


--
-- TOC entry 4972 (class 0 OID 0)
-- Dependencies: 236
-- Name: descuentos_id_descuento_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.descuentos_id_descuento_seq', 1, false);


--
-- TOC entry 4973 (class 0 OID 0)
-- Dependencies: 232
-- Name: pagos_id_pago_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pagos_id_pago_seq', 2, true);


--
-- TOC entry 4974 (class 0 OID 0)
-- Dependencies: 238
-- Name: pedidos_detalle_id_detalle_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pedidos_detalle_id_detalle_seq', 1, false);


--
-- TOC entry 4975 (class 0 OID 0)
-- Dependencies: 228
-- Name: pedidos_id_pedido_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pedidos_id_pedido_seq', 11, true);


--
-- TOC entry 4976 (class 0 OID 0)
-- Dependencies: 230
-- Name: pedidos_items_id_item_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pedidos_items_id_item_seq', 11, true);


--
-- TOC entry 4977 (class 0 OID 0)
-- Dependencies: 221
-- Name: producto_atributo_valores_id_valor_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.producto_atributo_valores_id_valor_seq', 17, true);


--
-- TOC entry 4978 (class 0 OID 0)
-- Dependencies: 219
-- Name: producto_atributos_id_atributo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.producto_atributos_id_atributo_seq', 3, true);


--
-- TOC entry 4979 (class 0 OID 0)
-- Dependencies: 223
-- Name: producto_variantes_id_variante_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.producto_variantes_id_variante_seq', 17, true);


--
-- TOC entry 4980 (class 0 OID 0)
-- Dependencies: 217
-- Name: productos_id_producto_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.productos_id_producto_seq', 16, true);


--
-- TOC entry 4981 (class 0 OID 0)
-- Dependencies: 215
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_usuario_seq', 14, true);


--
-- TOC entry 4743 (class 2606 OID 16493)
-- Name: archivos_diseno archivos_diseno_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archivos_diseno
    ADD CONSTRAINT archivos_diseno_pkey PRIMARY KEY (id_archivo);


--
-- TOC entry 4759 (class 2606 OID 16587)
-- Name: cupones cupones_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cupones
    ADD CONSTRAINT cupones_codigo_key UNIQUE (codigo);


--
-- TOC entry 4761 (class 2606 OID 16585)
-- Name: cupones cupones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cupones
    ADD CONSTRAINT cupones_pkey PRIMARY KEY (id_cupon);


--
-- TOC entry 4764 (class 2606 OID 16599)
-- Name: descuentos descuentos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.descuentos
    ADD CONSTRAINT descuentos_pkey PRIMARY KEY (id_descuento);


--
-- TOC entry 4757 (class 2606 OID 16569)
-- Name: pagos pagos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_pkey PRIMARY KEY (id_pago);


--
-- TOC entry 4769 (class 2606 OID 16612)
-- Name: pedidos_detalle pedidos_detalle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_detalle
    ADD CONSTRAINT pedidos_detalle_pkey PRIMARY KEY (id_detalle);


--
-- TOC entry 4754 (class 2606 OID 16538)
-- Name: pedidos_items pedidos_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_items
    ADD CONSTRAINT pedidos_items_pkey PRIMARY KEY (id_item);


--
-- TOC entry 4748 (class 2606 OID 16517)
-- Name: pedidos pedidos_numero_orden_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_numero_orden_key UNIQUE (numero_orden);


--
-- TOC entry 4750 (class 2606 OID 16515)
-- Name: pedidos pedidos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_pkey PRIMARY KEY (id_pedido);


--
-- TOC entry 4731 (class 2606 OID 16444)
-- Name: producto_atributo_valores producto_atributo_valores_id_atributo_valor_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_atributo_valores
    ADD CONSTRAINT producto_atributo_valores_id_atributo_valor_key UNIQUE (id_atributo, valor);


--
-- TOC entry 4733 (class 2606 OID 16442)
-- Name: producto_atributo_valores producto_atributo_valores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_atributo_valores
    ADD CONSTRAINT producto_atributo_valores_pkey PRIMARY KEY (id_valor);


--
-- TOC entry 4727 (class 2606 OID 16435)
-- Name: producto_atributos producto_atributos_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_atributos
    ADD CONSTRAINT producto_atributos_nombre_key UNIQUE (nombre);


--
-- TOC entry 4729 (class 2606 OID 16433)
-- Name: producto_atributos producto_atributos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_atributos
    ADD CONSTRAINT producto_atributos_pkey PRIMARY KEY (id_atributo);


--
-- TOC entry 4737 (class 2606 OID 16458)
-- Name: producto_variantes producto_variantes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_variantes
    ADD CONSTRAINT producto_variantes_pkey PRIMARY KEY (id_variante);


--
-- TOC entry 4739 (class 2606 OID 16460)
-- Name: producto_variantes producto_variantes_sku_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_variantes
    ADD CONSTRAINT producto_variantes_sku_key UNIQUE (sku);


--
-- TOC entry 4725 (class 2606 OID 16425)
-- Name: productos productos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (id_producto);


--
-- TOC entry 4720 (class 2606 OID 16411)
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- TOC entry 4722 (class 2606 OID 16409)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- TOC entry 4741 (class 2606 OID 16472)
-- Name: variante_atributos variante_atributos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variante_atributos
    ADD CONSTRAINT variante_atributos_pkey PRIMARY KEY (id_variante, id_valor);


--
-- TOC entry 4744 (class 1259 OID 16499)
-- Name: idx_disenos_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_disenos_usuario ON public.archivos_diseno USING btree (id_usuario);


--
-- TOC entry 4751 (class 1259 OID 16559)
-- Name: idx_items_pedido; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_items_pedido ON public.pedidos_items USING btree (id_pedido);


--
-- TOC entry 4752 (class 1259 OID 16560)
-- Name: idx_items_variante; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_items_variante ON public.pedidos_items USING btree (id_variante);


--
-- TOC entry 4755 (class 1259 OID 16575)
-- Name: idx_pagos_pedido; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pagos_pedido ON public.pagos USING btree (id_pedido);


--
-- TOC entry 4766 (class 1259 OID 16623)
-- Name: idx_pedidos_detalle_pedido; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pedidos_detalle_pedido ON public.pedidos_detalle USING btree (id_pedido);


--
-- TOC entry 4767 (class 1259 OID 16624)
-- Name: idx_pedidos_detalle_producto; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pedidos_detalle_producto ON public.pedidos_detalle USING btree (id_producto);


--
-- TOC entry 4723 (class 1259 OID 16426)
-- Name: idx_productos_activo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_productos_activo ON public.productos USING btree (activo);


--
-- TOC entry 4717 (class 1259 OID 16412)
-- Name: idx_usuarios_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuarios_email ON public.usuarios USING btree (email);


--
-- TOC entry 4718 (class 1259 OID 16413)
-- Name: idx_usuarios_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuarios_tipo ON public.usuarios USING btree (tipo);


--
-- TOC entry 4734 (class 1259 OID 16467)
-- Name: idx_variantes_activo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_variantes_activo ON public.producto_variantes USING btree (activo);


--
-- TOC entry 4735 (class 1259 OID 16466)
-- Name: idx_variantes_producto; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_variantes_producto ON public.producto_variantes USING btree (id_producto);


--
-- TOC entry 4762 (class 1259 OID 16588)
-- Name: ix_cupones_codigo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cupones_codigo ON public.cupones USING btree (codigo);


--
-- TOC entry 4765 (class 1259 OID 16600)
-- Name: ix_descuentos_fechas; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_descuentos_fechas ON public.descuentos USING btree (fecha_inicio, fecha_fin, activo);


--
-- TOC entry 4745 (class 1259 OID 16524)
-- Name: ix_pedidos_estado_pago_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pedidos_estado_pago_fecha ON public.pedidos USING btree (estado, estado_pago, fecha_pedido DESC);


--
-- TOC entry 4746 (class 1259 OID 16523)
-- Name: ix_pedidos_usuario_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pedidos_usuario_fecha ON public.pedidos USING btree (id_usuario, fecha_pedido DESC);


--
-- TOC entry 4774 (class 2606 OID 16494)
-- Name: archivos_diseno archivos_diseno_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archivos_diseno
    ADD CONSTRAINT archivos_diseno_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- TOC entry 4780 (class 2606 OID 16570)
-- Name: pagos pagos_id_pedido_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_id_pedido_fkey FOREIGN KEY (id_pedido) REFERENCES public.pedidos(id_pedido) ON DELETE CASCADE;


--
-- TOC entry 4781 (class 2606 OID 16613)
-- Name: pedidos_detalle pedidos_detalle_id_pedido_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_detalle
    ADD CONSTRAINT pedidos_detalle_id_pedido_fkey FOREIGN KEY (id_pedido) REFERENCES public.pedidos(id_pedido);


--
-- TOC entry 4782 (class 2606 OID 16618)
-- Name: pedidos_detalle pedidos_detalle_id_producto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_detalle
    ADD CONSTRAINT pedidos_detalle_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.productos(id_producto);


--
-- TOC entry 4775 (class 2606 OID 16518)
-- Name: pedidos pedidos_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos
    ADD CONSTRAINT pedidos_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario);


--
-- TOC entry 4776 (class 2606 OID 16549)
-- Name: pedidos_items pedidos_items_archivo_diseno_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_items
    ADD CONSTRAINT pedidos_items_archivo_diseno_fkey FOREIGN KEY (archivo_diseno) REFERENCES public.archivos_diseno(id_archivo);


--
-- TOC entry 4777 (class 2606 OID 16554)
-- Name: pedidos_items pedidos_items_id_diseno_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_items
    ADD CONSTRAINT pedidos_items_id_diseno_fkey FOREIGN KEY (id_diseno) REFERENCES public.archivos_diseno(id_archivo);


--
-- TOC entry 4778 (class 2606 OID 16539)
-- Name: pedidos_items pedidos_items_id_pedido_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_items
    ADD CONSTRAINT pedidos_items_id_pedido_fkey FOREIGN KEY (id_pedido) REFERENCES public.pedidos(id_pedido) ON DELETE CASCADE;


--
-- TOC entry 4779 (class 2606 OID 16544)
-- Name: pedidos_items pedidos_items_id_variante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedidos_items
    ADD CONSTRAINT pedidos_items_id_variante_fkey FOREIGN KEY (id_variante) REFERENCES public.producto_variantes(id_variante);


--
-- TOC entry 4770 (class 2606 OID 16445)
-- Name: producto_atributo_valores producto_atributo_valores_id_atributo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_atributo_valores
    ADD CONSTRAINT producto_atributo_valores_id_atributo_fkey FOREIGN KEY (id_atributo) REFERENCES public.producto_atributos(id_atributo) ON DELETE CASCADE;


--
-- TOC entry 4771 (class 2606 OID 16461)
-- Name: producto_variantes producto_variantes_id_producto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto_variantes
    ADD CONSTRAINT producto_variantes_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.productos(id_producto) ON DELETE CASCADE;


--
-- TOC entry 4772 (class 2606 OID 16478)
-- Name: variante_atributos variante_atributos_id_valor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variante_atributos
    ADD CONSTRAINT variante_atributos_id_valor_fkey FOREIGN KEY (id_valor) REFERENCES public.producto_atributo_valores(id_valor) ON DELETE CASCADE;


--
-- TOC entry 4773 (class 2606 OID 16473)
-- Name: variante_atributos variante_atributos_id_variante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variante_atributos
    ADD CONSTRAINT variante_atributos_id_variante_fkey FOREIGN KEY (id_variante) REFERENCES public.producto_variantes(id_variante) ON DELETE CASCADE;


-- Completed on 2026-05-04 19:45:33

--
-- PostgreSQL database dump complete
--

\unrestrict TCES4My8EjOQT3CV7F5CAoe4HoNaZiR15O5Iwj7ctrQwkUrGaCkFtDhR8F7Y3hF

