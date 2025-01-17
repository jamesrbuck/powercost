use pse;

select
   UDate,DAYOFWEEK(UDate) as DOW,
   substring(UTime,1,2) as the_hour,
   kWh
from
   usage_e
-- where
--   substring(UTime,1,2) = '23'
order by
   ID asc;
