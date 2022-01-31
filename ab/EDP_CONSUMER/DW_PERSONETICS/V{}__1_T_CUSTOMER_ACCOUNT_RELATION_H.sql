--  EDP_CONSUMER.DW_PERSONETICS."T_CUSTOMER_ACCOUNT_RELATION_H" definition

CREATE TABLE "T_CUSTOMER_ACCOUNT_RELATION_H" (
	CUSTOMERID VARCHAR(1024) NOT NULL,
	ACCOUNTID VARCHAR(1024) NOT NULL,
	RELATION_TYPE VARCHAR(1024) NOT NULL,
	RELATION_TYPE_ORIGINAL VARCHAR(1024),
	IS_ENROLLED_PAPERLESS_STAT DECIMAL(38,0),
	EDP_LOAD_DTTM TIMESTAMP,
	EDP_DATA_DT DATE,
	EDP_RUN_ID DECIMAL(38,0),
	EDP_HASH_VALUE VARCHAR(255),
	EDP_CHANGE_CD VARCHAR(1),
	EDP_ACTIVE_IND VARCHAR(1),
	EDP_BEG_EFF_DT DATE,
	EDP_END_EFF_DT DATE
);


