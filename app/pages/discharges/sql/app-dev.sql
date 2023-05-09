SELECT TOP 10 [mrn].[mrn],
    [name].[firstname],
    [sex].[sex],
    [loc].[hl7_location]
FROM (
        SELECT TOP 50 firstname,
            csn
        FROM [dbo].[name_v1]
    ) name
    LEFT JOIN [dbo].[mrn_v1] mrn ON name.csn = mrn.csn
    LEFT JOIN [dbo].[sex_v1] sex ON sex.csn = name.csn
    LEFT JOIN [dbo].[location_v1] loc ON mrn.csn = loc.csn -- temporary so some data can come in 
    -- SELECT [loc].hl7_location,
    --     [mrn].[mrn],
    --     [name].[fullname],
    --     [sex].[sex],
    --     [dob].[date_of_birth],
    --     [dc].[admission_datetime],
    --     [news].[value] news,
    --     [los].[length_of_stay]
    -- FROM [dbo].[admission_t03_v1] ad
    --     LEFT JOIN [dbo].[mrn_v1] mrn ON ad.csn = mrn.csn
    --     LEFT JOIN [dbo].[name_v1] name ON ad.csn = name.csn
    --     LEFT JOIN [dbo].[discharge_t03_v1] dc ON ad.csn = dc.csn
    --     LEFT JOIN [dbo].[date_of_birth_v1] dob on ad.csn = dob.csn
    --     LEFT JOIN [dbo].[sex_v1] sex ON sex.csn = ad.csn
    --     LEFT JOIN [dbo].[news2_average_last_24_hours_v1] news ON ad.csn = news.csn
    --     LEFT JOIN [dbo].[location_v1] loc on ad.csn = loc.csn
    --     LEFT JOIN [dbo].[length_of_stay_t03_v1] los ON ad.csn = los.csn