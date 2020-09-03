CREATE TABLE public.customers
(
    customer_id uuid NOT NULL,
    advertiser_name text COLLATE pg_catalog."default" NOT NULL,
    customer_name text COLLATE pg_catalog."default" NOT NULL,
    created_date timestamp without time zone,
    CONSTRAINT customers_pkey PRIMARY KEY (customer_id),
    CONSTRAINT unique_customer UNIQUE (customer_name)
)

TABLESPACE pg_default;

ALTER TABLE public.customers
    OWNER to postgres;