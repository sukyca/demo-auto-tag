flyway -locations="filesystem://C:/Users/AntonioSuljic/Desktop/snowflake-test-repo/temp/sql/EDP_CONSUMER/DW_NCR" 
-configFiles="C:/Users/AntonioSuljic/Desktop/snowflake-test-repo/temp/config/development.dw_ncr.config" 
-schemas=DW_NCR 
-outputFile="C:/Users/AntonioSuljic/Desktop/snowflake-test-repo/temp/output/migrate.DW_NCR.FlywayOutput.txt" migrate


flyway -locations="filesystem://C:/Users/AntonioSuljic/Desktop/snowflake-test-repo/temp/sql/EDP_CONSUMER/DW_NCRUA" 
-configFiles="C:/Users/AntonioSuljic/Desktop/snowflake-test-repo/temp/config/development.dw_ncrua.config" 
-schemas=DW_NCRUA 
-outputFile="C:/Users/AntonioSuljic/Desktop/snowflake-test-repo/temp/output/migrate.DW_NCRUA.FlywayOutput.txt" migrate


flyway -locations="filesystem://C:/Users/AntonioSuljic/Desktop/snowflake-test-repo/temp/sql/EDP_CONSUMER/DW_PERSONETICS" 
-configFiles="C:/Users/AntonioSuljic/Desktop/snowflake-test-repo/temp/config/development.dw_personetics.config" 
-schemas=DW_PERSONETICS 
-outputFile="C:/Users/AntonioSuljic/Desktop/snowflake-test-repo/temp/output/migrate.DW_PERSONETICS.FlywayOutput.txt" migrate