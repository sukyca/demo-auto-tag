--  EDP_CONSUMER.DW_NCRUA."T_ABPZ05001_TRANSACTIONS_DEPOSIT" definition

CREATE TABLE "T_ABPZ05001_TRANSACTIONS_DEPOSIT" (
	"AZACTTYP_Account_Type" VARCHAR(1024) NOT NULL,
	"AZACCT_Account_Nbr" DECIMAL(12,0) NOT NULL,
	ACCOUNT_ID VARCHAR(63),
	TRANSACTION_ID VARCHAR(31) NOT NULL,
	"AZALTYPE_Alert_Type" VARCHAR(1024) NOT NULL,
	"AZDRCR_DR_CR_Code" VARCHAR(1024) NOT NULL,
	"AZALAMT_Alert_Amount" DECIMAL(13,2) NOT NULL,
	"AZCHECK_Check_Nbr" DECIMAL(15,0) NOT NULL,
	"AZBAL_Account_Balance" DECIMAL(15,2) NOT NULL,
	"AZDESC_Trans_Description" VARCHAR(1024) NOT NULL,
	"AZHARDPOST_Hard_Post_Flag" VARCHAR(1024) NOT NULL,
	"AZPGMID_Program_ID" VARCHAR(1024) NOT NULL,
	"AZTMSTAMP_Alert_Timestamp" VARCHAR(1024) NOT NULL,
	"AZMCC_Merchant_Code" DECIMAL(4,0) NOT NULL,
	"AZMCNM_Merchant_Name" VARCHAR(1024) NOT NULL,
	EDP_DATA_DT DATE NOT NULL,
	EDP_LOAD_DTTM TIMESTAMP NOT NULL,
	EDP_RUN_ID DECIMAL(38,0) NOT NULL
);


