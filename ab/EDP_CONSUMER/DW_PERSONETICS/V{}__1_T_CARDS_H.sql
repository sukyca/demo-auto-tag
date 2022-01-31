--  EDP_CONSUMER.DW_PERSONETICS."T_CARDS_H" definition

CREATE TABLE "T_CARDS_H" (
	CARDID VARCHAR(1024) NOT NULL,
	ACCOUNTID VARCHAR(1024) NOT NULL,
	NAME_FOR_DISPLAY VARCHAR(1024) NOT NULL,
	NUMBER_FOR_DISPLAY VARCHAR(1024) NOT NULL,
	CARD_STATUS VARCHAR(1024) NOT NULL,
	CARD_TYPE VARCHAR(1024) NOT NULL,
	CARD_OUTSTANDING_BALANCE DECIMAL(38,0),
	CARD_AVAILABLE_CREDIT DECIMAL(38,0),
	CARD_CREDIT_LIMIT DECIMAL(38,0),
	ACTIVATION_DATE DATE,
	EXPIRATION_DATE DATE,
	SHIPMENT_DATE DATE,
	ISSUE_DATE DATE,
	STATUS_ORIGINAL VARCHAR(1024),
	TYPE_ORIGINAL VARCHAR(1024),
	CUSTOMERID VARCHAR(1024),
	IS_PRIMARY_CARD DECIMAL(38,0),
	EDP_LOAD_DTTM TIMESTAMP,
	EDP_DATA_DT DATE,
	EDP_RUN_ID DECIMAL(38,0),
	EDP_HASH_VALUE VARCHAR(255),
	EDP_CHANGE_CD VARCHAR(1),
	EDP_ACTIVE_IND VARCHAR(1),
	EDP_BEG_EFF_DT DATE,
	EDP_END_EFF_DT DATE,
	primary key (CARDID)
);


