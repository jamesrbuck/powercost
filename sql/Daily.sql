use pse;

--   ,round(((sum(kWh)/count(kWh))*24*0.105),2) as kWh_day_cost_est

select
   UDate as Date
   ,ELT(dayofweek(UDate),'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') as DoW
   ,round(sum(kWh)/count(kWh),3) as kWh_Hr_avg
   ,count(kWh) as hours
   ,sum(kWh) as kWh_day_total
   ,round(0.0937212*sum(kWh),2) as KwH_24hr_Cost
from
   usage_e
group by
   UDate
order by
   UDate
;
