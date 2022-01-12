--  EDP_CONSUMER.DW_NCRUA.T_USER_H definition

CREATE TABLE T_USER_H (
	USER_ID VARCHAR(63),
	COMPANY_UNIQUE_ID VARCHAR(63),
	PARENT_UNIQUE_ID VARCHAR(63),
	CIF VARCHAR(63),
	"DELETE" BOOLEAN,
	LOGIN VARCHAR(128),
	USER_TYPE VARCHAR(1024),
	ENROLL BOOLEAN,
	LOCKED BOOLEAN,
	ENABLED BOOLEAN,
	ON_DEMAND BOOLEAN,
	PROFILE_TYPE VARCHAR(1024),
	FIRST_NAME VARCHAR(40),
	MIDDLE_NAME VARCHAR(40),
	LAST_NAME VARCHAR(100),
	BUSINESS_NAME VARCHAR(100),
	EMPLOYEE BOOLEAN,
	TAX_ID VARCHAR(31),
	TAX_ID_TYPE VARCHAR(1024),
	MOBILE BOOLEAN,
	EMAIL_OPT_OUT BOOLEAN,
	DATE_OF_BIRTH DATE,
	GENDER VARCHAR(1),
	CREDIT_SCORE DECIMAL(38,0),
	CLASS VARCHAR(63),
	PHYSICAL_ADDRESS_ADDRESS_1 VARCHAR(1024),
	PHYSICAL_ADDRESS_ADDRESS_2 VARCHAR(1024),
	PHYSICAL_ADDRESS_ADDRESS_3 VARCHAR(1024),
	PHYSICAL_ADDRESS_ADDRESS_4 VARCHAR(1024),
	PHYSICAL_ADDRESS_CITY VARCHAR(50),
	PHYSICAL_ADDRESS_STATE VARCHAR(3),
	PHYSICAL_ADDRESS_COUNTRY_CODE VARCHAR(2),
	PHYSICAL_ADDRESS_POSTAL_CODE VARCHAR(20),
	PHYSICAL_ADDRESS_LATITUDE DECIMAL(11,8),
	PHYSICAL_ADDRESS_LONGITUDE DECIMAL(11,8),
	MAILING_ADDRESS_ADDRESS_1 VARCHAR(1024),
	MAILING_ADDRESS_ADDRESS_2 VARCHAR(1024),
	MAILING_ADDRESS_ADDRESS_3 VARCHAR(1024),
	MAILING_ADDRESS_ADDRESS_4 VARCHAR(1024),
	MAILING_ADDRESS_CITY VARCHAR(50),
	MAILING_ADDRESS_STATE VARCHAR(3),
	MAILING_ADDRESS_COUNTRY_CODE VARCHAR(2),
	MAILING_ADDRESS_POSTAL_CODE VARCHAR(20),
	ACCOUNT_ASSOCIATION_MODE VARCHAR(32),
	ATTRIBUTES VARCHAR(256),
	EDP_LOAD_DTTM TIMESTAMP,
	EDP_DATA_DT DATE,
	EDP_RUN_ID DECIMAL(22,0)
);