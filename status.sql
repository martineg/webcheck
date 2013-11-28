select site,
    avg(duration),
    duration as last_duration,
    size as last_size,
    strftime("%Y-%m-%d %H:%M", timestamp, "unixepoch", "localtime") as last_check,
    count(site) as checks
from webcheck 
group by site
order by avg(duration);
