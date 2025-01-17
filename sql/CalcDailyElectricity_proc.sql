delimiter $$
use pse $$

-- Note: PSE has a complicated charge scheme for electricity that we cannot
-- account for in a daily computation.  There are fixed monthly charges
-- independent of the amount of electricity used.
-- Monthly Charges (as of 9/26/2024):
--    (1) Basic Charge of $7.49
--    (2) Energy Exchange Credit: -0.007534 * total kWh (~ -$6.37)
--    (3) Other Electric Charges and Credits: 0.000007 * total kWh (~ $0.01)
--    (4) Electric Cons. Program Charge: 0.006095 * total kWh (~ $5.15)
--    (5) Power Cost Adjustment: 0.011344 * total kWh (~ $9.59)


drop procedure if exists CalcDailyElectricity $$
create procedure CalcDailyElectricity(
   in fromDate date,
   in toDate date)
begin
   declare kWh_temp int;
   declare costBelow600 float default 0.0937212;
   declare kWh_total_cost decimal (5,2);
   declare kWh_Total decimal (7,3);
   
   declare l_UDate           date;
   declare l_dow             varchar(15);
   declare l_kWh             decimal(7,3);
   declare l_hours           int;
   declare l_kWh_day_total   decimal(7,3);
   declare l_KwH_24hr_Cost   decimal(7,3);
   declare finished          int default false;

   declare cur1 cursor for
      select
         UDate as date
         ,ELT(dayofweek(UDate),'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') as DoW
         ,round(sum(kWh)/count(kWh),3) as kWh_Hr_avg
         ,count(kWh) as hours
         ,sum(kWh) as kWh_day_total
         ,round(costBelow600*sum(kWh),2) as KwH_24hr_Cost
      from
         usage_e
      where
         UDate >= fromDate and UDate <= toDate
      group by
         UDate
      order by
         UDate
   ;
   declare continue handler for not found set finished = true;
      
   set finished = false;
   open cur1;
   
   read_loop: loop
      fetch cur1 into l_UDate, l_dow, l_kWh, l_hours, l_kWh_day_total, l_KwH_24hr_Cost;
      select l_UDate, l_dow, l_kWh, l_hours, l_kWh_day_total, l_KwH_24hr_Cost;
      if finished then 
         leave read_loop;
      end if;
   end loop;
   close cur1;

END
$$
