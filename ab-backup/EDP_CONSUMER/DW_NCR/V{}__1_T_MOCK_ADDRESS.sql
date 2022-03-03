--  EDP_CONSUMER.DW_NCR."T_MOCK_ADDRESS" definition

CREATE TABLE "T_MOCK_ADDRESS" (
	ADDRESS_ID VARCHAR(63) NOT NULL,
	USER_ID VARCHAR(63) NOT NULL,
	ADDRESS_1 VARCHAR(100) NOT NULL,
	ADDRESS_2 VARCHAR(100),
	ADDRESS_3 VARCHAR(100),
	ADDRESS_4 VARCHAR(100),
	CITY VARCHAR(100) NOT NULL,
	STATE VARCHAR(100) NOT NULL,
	COUNTRY VARCHAR(10) NOT NULL,
	ZIPCODE VARCHAR(10) NOT NULL,
	ADDRESS_CODE VARCHAR(1) NOT NULL,
	primary key (ADDRESS_ID)
);


