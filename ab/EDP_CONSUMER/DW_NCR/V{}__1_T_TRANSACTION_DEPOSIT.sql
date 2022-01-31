--  EDP_CONSUMER.DW_NCR."T_TRANSACTION_DEPOSIT" definition

CREATE TABLE "T_TRANSACTION_DEPOSIT" (
	ACCOUNT_ID VARCHAR(63),
	SIGNATURE_ACCOUNTID VARCHAR(63),
	TRANSACTION_ID VARCHAR(31),
	"DELETE" BOOLEAN,
	TYPE VARCHAR(1024),
	AMOUNT DECIMAL(19,6),
	PRINCIPAL_AMOUNT DECIMAL(19,6),
	INTEREST_AMOUNT DECIMAL(19,6),
	OTHER_AMOUNT DECIMAL(19,6),
	POST_DATE DATE,
	PENDING BOOLEAN,
	CONFIRMATION_NUMBER VARCHAR(31),
	MERCHANT_CATEGORY_CODE VARCHAR(4),
	RUNNING_BALANCE DECIMAL(19,6),
	ORIGINATION_DATE DATE,
	CODE VARCHAR(31),
	CHECK_NUMBER VARCHAR(50),
	DEPOSIT_NUMBER VARCHAR(50),
	IMAGE VARCHAR(512),
	POSTING_SEQUENCE DECIMAL(38,0),
	NAME VARCHAR(127),
	RENAME VARCHAR(127),
	MEMO VARCHAR(1024),
	ORIGINAL_LOCATION_ADDRESS_1 VARCHAR(255),
	ORIGINAL_LOCATION_ADDRESS_2 VARCHAR(255),
	ORIGINAL_LOCATION_ADDRESS_3 VARCHAR(255),
	ORIGINAL_LOCATION_ADDRESS_4 VARCHAR(255),
	ORIGINAL_LOCATION_CITY VARCHAR(50),
	ORIGINAL_LOCATION_STATE VARCHAR(2),
	ORIGINAL_LOCATION_COUNTRY VARCHAR(2),
	ORIGINAL_LOCATION_POSTAL_CODE VARCHAR(20),
	ORIGINAL_LOCATION_LATITUDE DECIMAL(11,8),
	ORIGINAL_LOCATION_LONGITUDE DECIMAL(11,8),
	SUPPRESS_ALERT BOOLEAN,
	FIT_ID VARCHAR(1024),
	EDP_LOAD_DTTM TIMESTAMP,
	EDP_DATA_DT DATE,
	EDP_RUN_ID DECIMAL(22,0)
);


