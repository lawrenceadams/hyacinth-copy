-- SELECT [mrn].[mrn], [name].[fullname], [sex].[sex], [dc].[admission_datetime], news.[value] news
--   FROM [dbo].[admission_t03_v1] ad
--   LEFT JOIN [dbo].[mrn_v1] mrn ON ad.csn = mrn.csn
--   LEFT JOIN [dbo].[name_v1] name ON ad.csn = name.csn
--   LEFT JOIN [dbo].[discharge_t03_v1] dc ON ad.csn = dc.csn
--   LEFT JOIN [dbo].[sex_v1] sex ON sex.csn = ad.csn
--   LEFT JOIN [dbo].[news2_average_last_24_hours_v1] news ON ad.csn = news.csn
-- Only the mrn, name, and sex fields of the mock data seem to be filled in...
SELECT TOP 50 [mrn].[mrn],
    [name].[fullname],
    [sex].[sex]
FROM (
        SELECT TOP 50 fullname,
            csn
        FROM [dbo].[name_v1]
    ) name
    LEFT JOIN [dbo].[mrn_v1] mrn ON name.csn = mrn.csn
    LEFT JOIN [dbo].[sex_v1] sex ON sex.csn = name.csn