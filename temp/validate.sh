flyway -locations="filesystem://c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\sql\EDP_CONSUMER\DW_NCR" -configFiles="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\config\development.dw_ncr.config" -schemas=DW_NCR -outputFile="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\output\validate.DW_NCR.FlywayOutput.txt" validate
flyway -locations="filesystem://c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\sql\EDP_CONSUMER\DW_NCRUA" -configFiles="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\config\development.dw_ncrua.config" -schemas=DW_NCRUA -outputFile="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\output\validate.DW_NCRUA.FlywayOutput.txt" validate
flyway -locations="filesystem://c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\sql\EDP_CONSUMER\DW_PERSONETICS" -configFiles="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\config\development.dw_personetics.config" -schemas=DW_PERSONETICS -outputFile="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\output\validate.DW_PERSONETICS.FlywayOutput.txt" validate