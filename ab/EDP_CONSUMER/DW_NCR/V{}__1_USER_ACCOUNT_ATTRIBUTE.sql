--  EDP_CONSUMER.DW_NCR."USER_ACCOUNT_ATTRIBUTE" definition

CREATE TABLE "USER_ACCOUNT_ATTRIBUTE" (
	USER_ID VARCHAR(63),
	ACCOUNT_ID VARCHAR(63),
	NAME VARCHAR(40),
	TYPE VARCHAR(1024),
	VISIBLE BOOLEAN,
	DISPLAY_ORDER DECIMAL(38,0),
	VALUE VARCHAR(255),
	constraint PK_USER_ACCOUNT unique (USER_ID, ACCOUNT_ID)
);


