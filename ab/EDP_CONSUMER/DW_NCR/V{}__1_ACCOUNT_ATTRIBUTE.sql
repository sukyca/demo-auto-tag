--  EDP_CONSUMER.DW_NCR."ACCOUNT_ATTRIBUTE" definition

CREATE TABLE "ACCOUNT_ATTRIBUTE" (
	ACCOUNT_ID VARCHAR(63),
	NAME VARCHAR(40),
	TYPE VARCHAR(1024),
	VISIBLE BOOLEAN,
	DISPLAY_ORDER DECIMAL(38,0),
	VALUE VARCHAR(255)
);


