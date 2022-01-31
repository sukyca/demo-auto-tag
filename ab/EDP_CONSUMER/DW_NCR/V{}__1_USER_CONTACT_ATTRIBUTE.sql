--  EDP_CONSUMER.DW_NCR."USER_CONTACT_ATTRIBUTE" definition

CREATE TABLE "USER_CONTACT_ATTRIBUTE" (
	USER_ID VARCHAR(63),
	CONTACT_UNIQUE_ID VARCHAR(63),
	NAME VARCHAR(40),
	TYPE VARCHAR(1024),
	VISIBLE BOOLEAN,
	DISPLAY_ORDER DECIMAL(38,0),
	VALUE VARCHAR(255),
	constraint UCA_USER_ID unique (USER_ID)
);