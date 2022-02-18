--  EDP_CONSUMER.DW_PERSONETICS."T_CUSTOMERS" definition

CREATE TABLE "T_CUSTOMERS" (
	CUSTOMERID VARCHAR(1024) NOT NULL,
	ADDRESS VARCHAR(1024),
	BIRTH_DATE DATE,
	CITY VARCHAR(1024),
	COUNTRY VARCHAR(1024),
	CREATE_DATE DATE,
	CUSTOMER_SEGMENT VARCHAR(1024),
	EMAIL VARCHAR(1024),
	FIRST_NAME VARCHAR(1024),
	GENDER VARCHAR(1024),
	HAS_EMAIL DECIMAL(38,0),
	HAS_PHONE DECIMAL(38,0),
	IS_ABROAD DECIMAL(38,0),
	IS_ELIGIBLE_FOR_LOAN DECIMAL(38,0),
	IS_ELIGIBLE_FOR_MORTGAGE DECIMAL(38,0),
	IS_ENABLED_FACEID DECIMAL(38,0),
	IS_ENABLED_TOUCHID DECIMAL(38,0),
	IS_RECOMMENDED_FOR_LOAN DECIMAL(38,0),
	IS_RECOMMENDED_FOR_MORTGAGE DECIMAL(38,0),
	IS_RETURNMAIL DECIMAL(38,0),
	ZIPCODE VARCHAR(1024),
	TOTAL_ASSETS DECIMAL(38,0),
	CUSTOMER_AGE DECIMAL(38,0),
	INVESTMENT_KNOWLEDGE_LEVEL DECIMAL(38,0),
	INVESTMENT_ACTIVITY_LEVEL DECIMAL(38,0),
	INVESTMENT_HORIZON DECIMAL(38,0),
	INVESTMENT_PURPOSE VARCHAR(1024),
	EDP_LOAD_DTTM TIMESTAMP,
	EDP_DATA_DT DATE,
	EDP_RUN_ID DECIMAL(38,0),
	EDP_HASH_VALUE VARCHAR(255),
	primary key (CUSTOMERID)
);


