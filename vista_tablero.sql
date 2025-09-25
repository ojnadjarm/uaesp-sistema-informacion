CREATE VIEW disposicion_final_detallada AS
SELECT
    EXTRACT(YEAR FROM df.fecha_entrada) AS "AÑO",
    EXTRACT(MONTH FROM df.fecha_entrada) AS "MES",
    EXTRACT(DAY FROM df.fecha_entrada) AS "DÍA",
    ROUND(df.peso_residuos / 1000.0, 2) AS "PESO RESIDUOS TON",
    df.fecha_entrada AS "FECHA ENTRADA",
    df.fecha_salida AS "FECHA SALIDA",
    df.consecutivo_entrada AS "CONSECUTIVO ENTRADA",
    df.consecutivo_salida AS "CONSECUTIVO SALIDA",
    df.placa AS "PLACA",
    df.numero_vehiculo AS "NUMERO VEHICULO",
    UPPER(TRIM(df.concesion)) AS "CONCESION",
    df.macroruta AS "MACRORUTA",
    df.microruta AS "MICRORUTA",
    UPPER(TRIM(df.ase)) AS "ASE",
    UPPER(TRIM(df.servicio)) AS "SERVICIO",
    UPPER(TRIM(df.zona_descarga)) AS "ZONA DESCARGA",
    df.peso_entrada AS "PESO ENTRADA",
    df.peso_salida AS "PESO SALIDA",
    df.peso_residuos AS "PESO RESIDUOS",
    s.categoria AS "CATEGORIA DEL SERVICIO",
    c.categoria AS "ORIGEN DEL RESIDUO",
    CASE
        WHEN zd.categoria = 'PIDJ' THEN 'PIDJ'
        ELSE NULL
    END AS "DISPUESTOS PIDJ"
FROM
    ingesta_disposicionfinal df
LEFT JOIN
    ingesta_concesion c ON UPPER(TRIM(df.concesion)) = UPPER(TRIM(c.nombre))
LEFT JOIN
    ingesta_servicio s ON UPPER(TRIM(df.servicio)) = UPPER(TRIM(s.nombre))
LEFT JOIN
    ingesta_zonadescarga zd ON UPPER(TRIM(df.zona_descarga)) = UPPER(TRIM(zd.nombre))
LEFT JOIN
    ingesta_ase a ON UPPER(TRIM(df.ase)) = UPPER(TRIM(a.nombre))
WHERE
    df.fecha_entrada IS NOT NULL
ORDER BY
    df.fecha_entrada DESC;