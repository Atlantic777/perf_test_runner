-- drop old views
pragma writable_schema = 1;
delete from sqlite_master where type == "view";
vacuum;
pragma writable_schema = 1;

-- create single compiler + level combination views
-- #########################################
-- clang views
create view clang_o0 as
select test_name, cpu_time as c0c, elapsed_time as c0e, hash as c0h
from test_case where compiler = "clang" and level = "O0";

create view clang_o1 as
select test_name, cpu_time as c1c, elapsed_time as c1e, hash as c1h
from test_case where compiler = "clang" and level = "O1";

create view clang_o2 as
select test_name, cpu_time as c2c, elapsed_time as c2e, hash as c2h
from test_case where compiler = "clang" and level = "O2";

create view clang_o3 as
select test_name, cpu_time as c3c, elapsed_time as c3e, hash as c3h
from test_case where compiler = "clang" and level = "O3";

create view clang_os as
select test_name, cpu_time as csc, elapsed_time as cse, hash as csh
from test_case where compiler = "clang" and level = "Os";

-- gcc views
create view gcc_o0 as
select test_name, cpu_time as g0c, elapsed_time as g0e, hash as g0h
from test_case where compiler = "gcc" and level = "O0";

create view gcc_o1 as
select test_name, cpu_time as g1c, elapsed_time as g1e, hash as g1h
from test_case where compiler = "gcc" and level = "O1";

create view gcc_o2 as
select test_name, cpu_time as g2c, elapsed_time as g2e, hash as g2h
from test_case where compiler = "gcc" and level = "O2";

create view gcc_o3 as
select test_name, cpu_time as g3c, elapsed_time as g3e, hash as g3h
from test_case where compiler = "gcc" and level = "O3";

create view gcc_os as
select test_name, cpu_time as gsc, elapsed_time as gse, hash as gsh
from test_case where compiler = "gcc" and level = "Os";
-- #######################################

-- create composite views
-- ##################################################
create view clang_full as
select * from clang_o0 join clang_o1 using (test_name) join clang_o2 using (test_name) join clang_o3 using (test_name);

create view gcc_full as
select * from gcc_o0 join gcc_o1 using (test_name) join gcc_o2 using (test_name) join gcc_o3 using (test_name);

create view full_report as
select * from clang_full join gcc_full using (test_name);

create view short_report as
select test_name, c0c, c1c, c2c, c3c, g0c, g1c, g2c, g3c from full_report;

create view hash_report as
select test_name, c0c, c1c, c2c, c3c, g0c, g1c, g2c, g3c,
c0h, c1h, c2h, c3h, g0h, g1h, g2h, g3h
from full_report;

-- ##################################################

create view test_names as select distinct(test_name) from test_case;
