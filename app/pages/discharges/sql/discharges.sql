WITH loc AS (
    SELECT *,
        ROW_NUMBER() OVER(
            PARTITION BY csn,
            horizon_datetime
            ORDER BY log_datetime DESC
        ) As log_number
    FROM [dbo].[location_v1]
),
adm AS (
    SELECT *,
        ROW_NUMBER() OVER(
            PARTITION BY csn,
            horizon_datetime
            ORDER BY log_datetime DESC
        ) AS log_number
    FROM [dbo].[admission_v1]
),
dob AS (
    SELECT *,
        ROW_NUMBER() OVER(
            PARTITION BY csn,
            horizon_datetime
            ORDER BY log_datetime DESC
        ) As log_number
    FROM [dbo].[date_of_birth_v1]
),
mrn AS (
    SELECT *,
        ROW_NUMBER() OVER(
            PARTITION BY csn,
            horizon_datetime
            ORDER BY log_datetime DESC
        ) AS log_number
    FROM [dbo].[mrn_v1]
),
nom AS (
    SELECT *,
        ROW_NUMBER() OVER(
            PARTITION BY csn,
            horizon_datetime
            ORDER BY log_datetime DESC
        ) AS log_number
    FROM [dbo].[name_v1]
),
new AS (
    SELECT *,
        ROW_NUMBER() OVER(
            PARTITION BY csn,
            horizon_datetime
            ORDER BY log_datetime DESC
        ) AS log_number
    FROM [dbo].[news2_average_last_24_hours_v1]
),
sex AS(
    SELECT *,
        ROW_NUMBER() OVER(
            PARTITION BY csn,
            horizon_datetime
            ORDER BY log_datetime DESC
        ) AS log_number
    FROM [dbo].[sex_v1]
),
los AS (
    SELECT *,
        ROW_NUMBER() OVER(
            PARTITION BY csn,
            horizon_datetime
            ORDER BY log_datetime DESC
        ) AS log_number
    FROM [dbo].[length_of_stay_v1]
)
SELECT TOP 15 loc.csn,
    loc.horizon_datetime,
    loc.hl7_location,
    -- adm.department,
    adm.admission_datetime,
    dob.date_of_birth,
    mrn.mrn,
    nom.firstname,
    nom.lastname,
    sex.sex,
    new.value as avg_news,
    los.length_of_stay
FROM loc
    LEFT JOIN adm ON adm.csn = loc.csn
    AND adm.horizon_datetime = loc.horizon_datetime
    LEFT JOIN dob ON dob.csn = loc.csn
    AND dob.horizon_datetime = loc.horizon_datetime
    LEFT JOIN mrn ON mrn.csn = loc.csn
    AND mrn.horizon_datetime = loc.horizon_datetime
    LEFT JOIN nom ON nom.csn = loc.csn
    AND nom.horizon_datetime = loc.horizon_datetime
    LEFT JOIN new ON new.csn = loc.csn
    AND new.horizon_datetime = loc.horizon_datetime
    LEFT JOIN sex ON sex.csn = loc.csn
    AND sex.horizon_datetime = loc.horizon_datetime
    LEFT JOIN los ON los.csn = loc.csn
    AND los.horizon_datetime = loc.horizon_datetime
WHERE loc.horizon_datetime = '2023-04-01 00:00:00.000'
    AND loc.log_number = 1
    AND adm.log_number = 1
    AND dob.log_number = 1
    AND mrn.log_number = 1
    AND nom.log_number = 1
    AND new.log_number = 1
    AND sex.log_number = 1
    AND los.log_number = 1