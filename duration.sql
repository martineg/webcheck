select c.site, c.timestamp, abs(c.duration) from webcheck c, site s where c.site = s.hostname order by c.check_id;
