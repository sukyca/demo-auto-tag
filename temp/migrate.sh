flyway -locations="filesystem://c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\sql\EDP_CONSUMER\DW_NCR" -configFiles="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\config\development.dw_ncr.config" -schemas=DW_NCR -outputFile="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\output\migrate.DW_NCR.FlywayOutput.txt" migrate
flyway -locations="filesystem://c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\sql\EDP_CONSUMER\DW_NCRUA" -configFiles="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\config\development.dw_ncrua.config" -schemas=DW_NCRUA -outputFile="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\output\migrate.DW_NCRUA.FlywayOutput.txt" migrate
flyway -locations="filesystem://c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\sql\EDP_CONSUMER\DW_PERSONETICS" -configFiles="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\config\development.dw_personetics.config" -schemas=DW_PERSONETICS -outputFile="c:/Users/AndreaHrelja/Projects/Associated Bank/snowflake-test-repo\temp\output\migrate.DW_PERSONETICS.FlywayOutput.txt" migrate