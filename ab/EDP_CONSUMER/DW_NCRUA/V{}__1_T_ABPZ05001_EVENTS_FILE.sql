--  EDP_CONSUMER.DW_NCRUA."T_ABPZ05001_EVENTS_FILE" definition

CREATE TABLE "T_ABPZ05001_EVENTS_FILE" (
	"AZACTTYP_Account_Type" VARCHAR(1024),
	"AZACCT_Account_Nbr" DECIMAL(12,0) NOT NULL,
	"AZALTYPE_Alert_Type" VARCHAR(1024),
	"AZDRCR_DR_CR_Code" VARCHAR(1024),
	"AZALAMT_Alert_Amount" DECIMAL(13,2),
	"AZCHECK_Check_Nbr" DECIMAL(15,0),
	"AZBAL_Account_Balance" DECIMAL(15,2),
	"AZDESC_Trans_Description" VARCHAR(1024),
	"AZHARDPOST_Hard_Post_Flag" VARCHAR(1024),
	"AZPGMID_Program_ID" VARCHAR(1024),
	"AZTMSTAMP_Alert_Timestamp" VARCHAR(1024),
	"AZCIF_Customer_Nbr" VARCHAR(1024),
	"AZCUSTNM_Customer_Name" VARCHAR(1024),
	"AZPRD_Product_Type" DECIMAL(3,0),
	"AZPRDDSC_Product_Desc" VARCHAR(1024),
	"AZPERS_Pers_Non_Pers_Flag" VARCHAR(1024),
	"AZEST_EStatement_Flag" VARCHAR(1024),
	"AZOTRNDT_Orig_Trans_Date" DECIMAL(8,0),
	"AZTC_Tran_Code" DECIMAL(3,0),
	"AZPMTDUEDT_Payment_Due_Dt" DECIMAL(8,0),
	"AZPDLS_Past_Due_Days" DECIMAL(5,0),
	"AZMCC_Merchant_Code" DECIMAL(4,0),
	"AZMCNM_Merchant_Name" VARCHAR(1024),
	PRODUCER_ROW_NUMBER DECIMAL(38,0) NOT NULL,
	EDP_DATA_DT DATE NOT NULL,
	EDP_LOAD_DTTM TIMESTAMP NOT NULL,
	EDP_RUN_ID DECIMAL(38,0) NOT NULL
);


