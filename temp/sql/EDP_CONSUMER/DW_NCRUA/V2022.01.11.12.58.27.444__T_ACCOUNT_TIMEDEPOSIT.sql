--  EDP_CONSUMER.DW_NCRUA.T_ACCOUNT_TIMEDEPOSIT definition

CREATE TABLE T_ACCOUNT_TIMEDEPOSIT (
	ACCOUNT_ID VARCHAR(63) NOT NULL,
	COMPANY_UNIQUE_ID VARCHAR(63),
	"DELETE" BOOLEAN,
	PRODUCT_UNIQUE_ID VARCHAR(63),
	NAME VARCHAR(127),
	ROUTING_TRANSIT_NUMBER VARCHAR(9),
	ACCOUNT_NUMBER VARCHAR(200),
	BALANCE DECIMAL(19,6),
	STATUS VARCHAR(1024),
	CURRENCY_CODE VARCHAR(3),
	AVAILABLE_BALANCE DECIMAL(19,6),
	RESTRICTED BOOLEAN,
	ESTATEMENT VARCHAR(1024),
	OPEN_DATE DATE,
	CLOSED_DATE DATE,
	ATTRIBUTES VARCHAR(256),
	EDP_LOAD_DTTM TIMESTAMP,
	EDP_DATA_DT DATE,
	EDP_RUN_ID DECIMAL(22,0),
	constraint PK_ACCOUNT_TD_ID primary key (ACCOUNT_ID)
);


