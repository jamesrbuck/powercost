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

delete from pse.usage_e where ID >= 0;
commit;
select * from pse.usage_e where UDate = '2025-01-29';

-- select
--    UDate as Date
--    ,ELT(dayofweek(UDate),'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') as DoW
--    ,round(sum(kWh)/count(kWh),3) as kWh_Hr_avg
--    ,count(kWh) as hours
--    ,sum(kWh) as kWh_day_total
--    ,round(((sum(kWh)/count(kWh))*24*0.105),2) as kWh_day_total_cost
-- from
--    pse.usage_e
-- group by
--    UDate
-- order by
--    UDate
-- ;

select
   UDate as Date
   ,ELT(dayofweek(UDate),'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') as DoW
   ,round(sum(kWh)/count(kWh),3) as kWh_Hr_avg
   ,count(kWh) as hours
   ,sum(kWh) as kWh_total
   ,round(((sum(kWh)/count(kWh))*(count(kWh))*0.115433),2) as kWh_cost
from
   pse.usage_e
group by
   UDate
order by
   UDate
;

delete from pse.usage_e where UDate = '2025-01-27';

-- PSE of September 2024
-- Your Electric Charge Details (31 days) Rate x Unit = Charge
-- 1,669 kWh used for service 11/6/2024 - 12/6/2024
-- 
-- Basic Charge                     $7.49 per month             $  7.49
-- Electricity
--    Tier 1 (First 484 kWh Used)   0.115433 484 kWh            $ 55.87
--      (11/6/2024 - 11/30/2024)
--    Tier 2 (Above 484 kWh Used)   0.134850 861.967 kWh        $116.24
--      (11/6/2024 - 11/30/2024)
--    Tier 1 (First 116 kWh Used)   0.115433 116 kWh            $ 13.39
--      (12/1/2024 - 12/6/2024)
--    Tier 2 (Above 116 kWh Used)   0.134850 207.033 kWh        $ 27.92
--      (12/1/2024 - 12/6/2024)
--    Electric Cons. Program Charge 0.006095 1,669 kWh          $ 10.17
--    Power Cost Adjustment         0.014227 1,669 kWh          $ 23.74
-- Energy Exchange Credit          −0.007534 1,669 kWh          $−12.57
-- Other Electric Charges & Credits 0.000007 1,669 kWh          $  0.01
-- Subtotal of Electric Charges                                 $242.26
-- Taxes
--    State Utility Tax ($9.38 included in above charges) 3.873%
-- Current Electric Charges                                     $242.26


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
