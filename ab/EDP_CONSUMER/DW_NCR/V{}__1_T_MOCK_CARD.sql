--  EDP_CONSUMER.DW_NCR."T_MOCK_CARD" definition

CREATE TABLE "T_MOCK_CARD" (
	CARD_ID VARCHAR(63) NOT NULL,
	ACCOUNT_ID VARCHAR(63) NOT NULL,
	CARD_TYPE VARCHAR(2) NOT NULL,
	CARD_NUMBER VARCHAR(20) NOT NULL,
	primary key (CARD_ID)
);


