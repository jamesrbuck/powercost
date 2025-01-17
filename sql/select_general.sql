select
   UDate,
   -- concat(hour(UTime),':',minute(UTime)) as TimeHH,
   UTime,
   kWh
from
   pse.usage_e
-- where
--    UDate = '2024-10-03'
order by
   UDate, UTime
;


-- ==========================================================================
-- mysql> grant system_user on *.* to 'james'@'%';
-- mysql> select * from mysql.user where user in ('root','james');
-- mysql> show grants for 'james'@'localhost';
-- mysql> flush privileges;

select catalog, schema_name
from information_schema.schemata
order by schema_name;

select
   *
from
   information_schema.tables
where
   table_schema = 'pse'
;

-- select * from mysql.user where user in ('root','james');

-- describe usage_e;
-- show create table usage_e;
-- CREATE TABLE `usage_e` (
--   `ID` int NOT NULL AUTO_INCREMENT,
--   `UDate` date NOT NULL,
--   `UTime` time NOT NULL,
--   `kWh` decimal(7,3) DEFAULT \'0.000\',
--    PRIMARY KEY (`ID`),
--    UNIQUE KEY `I_USAGE_E_UNIQUE` (`ID`)) 
--    ENGINE=InnoDB 
--    AUTO_INCREMENT=75 
--    DEFAULT 
--    CHARSET=utf8mb4 
--    COLLATE=utf8mb4_0900_ai_ci 
--    COMMENT=\'Puget Sound Energy Electricity Usage for The Ponderosa\''


select 
   routine_name,
   routine_type,
   definer,
   created,
   last_altered,
   security_type,
   external_language,
   parameter_style,
   SQL_Data_Access
from
   information_schema.routines
where
  routine_type='PROCEDURE' and routine_schema='pse'
;

   -- SELECT VERSION();

-- select count(*) from (
--    select distinct UDate, UTime from pse.usage_e) as dt

-- create table usage_e_v3 as select * from usage_e;
-- delete from usage_e;
-- commit;
-- truncate table usage_e;
