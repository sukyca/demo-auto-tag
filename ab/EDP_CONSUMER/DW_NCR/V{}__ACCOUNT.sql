--  EDP_CONSUMER.DW_NCR.""ACCOUNT"" definition

CREATE TABLE "ACCOUNT" (
	"ACCOUNT"_ID VARCHAR(63) NOT NULL,
	COMPANY_UNIQUE_ID VARCHAR(63),
	"DELETE" BOOLEAN,
	PRODUCT_UNIQUE_ID VARCHAR(63),
	NAME VARCHAR(127),
	ROUTING_TRANSIT_NUMBER VARCHAR(9),
	"ACCOUNT"_NUMBER VARCHAR(200),
	BALANCE DECIMAL(19,6),
	STATUS VARCHAR(1024),
	CURRENCY_CODE VARCHAR(3),
	AVAILABLE_BALANCE DECIMAL(19,6),
	RESTRICTED BOOLEAN,
	ESTATEMENT VARCHAR(1024),
	OPEN_DATE DATE,
	CLOSED_DATE DATE,
	SIGNATURE_ACCTID VARCHAR(1024),
	SIGNATURE_ACCTTYPE1 VARCHAR(1024),
	SIGNATURE_ACCTTYPE2 VARCHAR(1024),
	LAST4_CARDNO DECIMAL(4,0),
	constraint PK_"ACCOUNT"_ID primary key ("ACCOUNT"_ID)
);


