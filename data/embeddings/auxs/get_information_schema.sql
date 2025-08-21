SELECT
    c.table_catalog AS db_name,
    c.table_schema AS schema_name,
    c.table_name,
    c.column_name,
    UPPER(
        CASE
            WHEN c.character_maximum_length IS NOT NULL THEN CONCAT(c.udt_name, '(', c.character_maximum_length, ')')
            ELSE c.udt_name
        END
    ) AS column_type,
    EXISTS(
        SELECT
            true
        FROM
            information_schema.table_constraints AS p
            INNER JOIN information_schema.key_column_usage AS k USING (constraint_catalog, constraint_schema, constraint_name)
        WHERE
            p.table_schema = c.table_schema
            AND p.table_name = c.table_name
            AND k.column_name = c.column_name
            AND p.constraint_type = 'PRIMARY KEY'
    ) AS primary_key,
    EXISTS (
        SELECT
            true
        FROM
            information_schema.table_constraints AS f
            INNER JOIN information_schema.key_column_usage AS k USING (constraint_catalog, constraint_schema, constraint_name)
        WHERE
            f.table_schema = c.table_schema
            AND f.table_name = c.table_name
            AND k.column_name = c.column_name
            AND f.constraint_type = 'FOREIGN KEY'
    ) AS foreign_key,
    (
        SELECT
            refs.table_schema || '.' || refs.table_name || '.' || refs.column_name
        FROM
            information_schema.table_constraints AS t
            INNER JOIN information_schema.key_column_usage AS k USING (constraint_catalog, constraint_schema, constraint_name)
            INNER JOIN information_schema.referential_constraints AS r USING (constraint_catalog, constraint_schema, constraint_name)
            INNER JOIN information_schema.key_column_usage AS refs ON (
                r.constraint_catalog = refs.constraint_catalog
                AND r.constraint_schema = refs.constraint_schema
                AND r.unique_constraint_name = refs.constraint_name
                AND k.column_name = refs.column_name
            )
        WHERE
            t.table_schema = c.table_schema
            AND t.table_name = c.table_name
            AND k.column_name = c.column_name
            AND t.constraint_type = 'FOREIGN KEY'
    ) AS target

FROM 
    information_schema.columns AS c

WHERE
    c.table_catalog IN (%s)
    AND c.table_schema IN (%s)

ORDER BY
    c.table_catalog
    , c.table_schema
    , c.table_name
    , c.ordinal_position
;