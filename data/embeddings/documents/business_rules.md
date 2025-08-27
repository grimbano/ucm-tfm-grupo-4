# Reglas de Negocio y Lógica SQL para el Modelo de Datos reducido `sales` de la Base de Datos AdventureWorks DW

Este documento describe reglas de negocio para el modelo reducido `sales` de la Base de Datos AdventureWorks DW, centrándose en la **derivación de métricas, el manejo inteligente de datos y la aplicación de lógica transformacional mediante SQL**, con la sintaxis específicamente adaptada para **PostgreSQL**. Estas reglas son cruciales para la construcción de informes, análisis de datos y la operacionalización de la inteligencia de negocio.

## 1. Representación de Entidades y Preferencias Lingüísticas

Cuando se solicita conceptualmente una entidad, como "productos", "clientes", "promociones" o "revendedores", se establece como principio operativo priorizar los campos que finalizan en `_name` para su adecuada representación en las salidas de las consultas SQL. Adicionalmente, se procurará mantener la coherencia con el idioma en que la consulta original fue formulada.

- **Principio Operativo:** Para la visualización de entidades en los resultados de consultas, se debe seleccionar el campo `_name` que mejor represente la entidad. En el caso de campos bilingües donde la versión en español (`spanish_..._name`, `spanish_..._description`) pueda ser nula y la consulta se realice en español, se utilizará la versión en inglés como alternativa (`fallback`) para asegurar la disponibilidad del dato y mantener la representación de la entidad.
- **Lógica SQL (Ejemplo para `dim_product`):**

    ```sql
    -- Selección del nombre del producto en español o, si es NULL, en inglés, para su representación
    SELECT
        product_key,
        COALESCE(spanish_product_name, english_product_name) AS producto_nombre,
        COALESCE(spanish_product_category_name, english_product_category_name) AS producto_category,
        COALESCE(spanish_product_subcategory_name, english_product_subcategory_name) AS producto_subcategoria
    FROM
        sales.dim_product;
    ```

    Este enfoque se aplicaría de manera similar a la representación de nombres de entidades en `dim_promotion`, `dim_customer`, `dim_reseller`, `dim_sales_person`, `dim_sales_reason`, `dim_sales_territory` y `dim_geography`, siempre privilegiando los campos `_name` relevantes y aplicando la lógica de `fallback` para el idioma.

Cuando se trata de campos como `product_line`, `class` y `style` de la tabla `dim_product`, los cuales pueden contener valores `NULL`, se establece como principio operativo completar los valores faltantes con una etiqueta que indique la ausencia de información, respetando el idioma de la consulta del usuario.

- **Principio Operativo:** Para la visualización de atributos de productos que puedan ser nulos, se debe reemplazar el valor faltante por un placeholder que indique "no registrado", manteniendo la coherencia con el idioma de la consulta. Por ejemplo, se usará `'|| No registrado ||'` para consultas en español y `'|| Not registered ||'` para consultas en inglés.
- **Lógica SQL (Ejemplo para `dim_product`):**

    ```sql
    -- Completar valores nulos en atributos de producto según el idioma de la consulta
    SELECT
        product_key,
        COALESCE(product_line, '|| No registrado ||') AS producto_linea,
        COALESCE(class, '|| No registrado ||') AS producto_clase,
        COALESCE(style, '|| No registrado ||') AS producto_estilo
    FROM
        sales.dim_product;
    ```

## 2. Cálculos Basados en Fechas

Las fechas en `fact_sales` permiten derivar métricas de tiempo cruciales para el análisis de la eficiencia de la cadena de suministro y la experiencia del cliente.

### 2.1 Métricas de Tiempo de Entrega y Envío

- **Regla de Negocio:** En caso de que se quiera hacer un análisis referido a los tiempos asociados a las ventas, se deben calcular los siguientes indicadores de tiempo:
  - **Tiempo de Envío (Shipping Time):** Días transcurridos desde que se creó el pedido (`order_date`) hasta que se envió (`ship_date`).
  - **Tiempo de Entrega (Delivery Time):** Días transcurridos desde que se envió el pedido (`ship_date`) hasta que se entregó al cliente (`due_date`).
  - **Tiempo Total de Procesamiento del Pedido (Order Processing Time):** Días transcurridos desde que se creó el pedido (`order_date`) hasta su entrega final (`due_date`).
- **Lógica SQL (Ejemplo para `fact_sales`):**

    ```sql
    SELECT
        sales_order_number AS pedido_numero,
        sales_order_line_number AS pedido_numero_linea,
        order_date AS fecha_pedido,
        ship_date AS fecha_envio,
        due_date AS fecha_entrega,
        -- Tiempo de Envío / Shipping Time (en días)
        DATE_PART('day', ship_date::TIMESTAMP - order_date::TIMESTAMP) AS tiempo_envio,
        -- Tiempo de Entrega / Delivery Time (en días)
        DATE_PART('day', due_date::TIMESTAMP - ship_date::TIMESTAMP) AS tiempo_entrega,
        -- Tiempo Total de Procesamiento del Pedido / Order Processing Time (en días)
        DATE_PART('day', due_date::TIMESTAMP - order_date::TIMESTAMP) AS tiempo_total_procesamiento
    FROM
        sales.fact_sales;
    ```

    ***Nota:*** En Postgres, para que la resta de fechas `(fecha_final - fecha_inicial)` devuelve un tipo `INTERVAL`, se debe forzar a que cada fecha sea considerada como tipo `TIMESTAMP`, y `DATE_PART('day', interval)` extrae el número de días de ese intervalo.

### 2.2 Desglose por Períodos Temporales Comunes

Para los informes de ventas, muchas veces es fundamental poder filtrar y agregar datos por **períodos estándar asociados a términos como "Este Año", "Año Pasado", "Acumulado del Año (YTD)" y la comparación "Año Actual vs. Año Pasado"**.

- **Definiciones de Períodos Agregados:**
  - **Trimestre:** Período de tres meses. Un año natural se compone de cuatro trimestres (Q1: Ene-Mar, Q2: Abr-Jun, Q3: Jul-Sep, Q4: Oct-Dic).
  - **Semestre:** Período de seis meses. Un año natural se compone de dos semestres (H1: Ene-Jun, H2: Jul-Dic).

- **Lógica SQL:**

    ```sql
    -- Ventas de 'Este Año' (basado en order_date)
    SELECT *
    FROM sales.fact_sales
    WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE);

    -- Ventas de 'El Año Pasado'
    SELECT *
    FROM sales.fact_sales
    WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1;

    -- Ventas 'YTD' (Year To Date) del año actual
    SELECT *
    FROM sales.fact_sales
    WHERE order_date BETWEEN DATE_TRUNC('year', CURRENT_DATE) AND CURRENT_DATE;

    -- Ventas Mes en Curso
    SELECT *
    FROM sales.fact_sales
    WHERE order_date BETWEEN DATE_TRUNC('year', CURRENT_DATE) AND CURRENT_DATE;

    -- Comparativa 'Año Actual vs. Año Pasado' (Same Period Last Year) con ejemplos de dimensiones
    SELECT
        customer_key,
        reseller_key,
        product_key,
        SUM(
            CASE
            WHEN EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE) THEN sales_amount
            ELSE 0
            END
        ) AS current_year,
        SUM(
            CASE
            WHEN EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1 THEN sales_amount
            ELSE 0
            END
        ) AS last_year
    FROM sales.fact_sales
    WHERE
        EXTRACT(YEAR FROM order_date) BETWEEN EXTRACT(YEAR FROM CURRENT_DATE) -1 AND EXTRACT(YEAR FROM CURRENT_DATE)
        -- Filtro adicional para periodo (ejemplo, 2do trimestre del año)
        AND EXTRACT(QUARTER FROM order_date) = 1
    GROUP BY
        customer_key, reseller_key, product_key;

    -- Ventas del 'Segundo trimestre del año pasado'
    SELECT *
    FROM sales.fact_sales
    WHERE
        order_date >= DATE_TRUNC('year', CURRENT_DATE - interval '1 year') + interval '3 months'
        AND order_date < DATE_TRUNC('year', CURRENT_DATE - interval '1 year') + interval '6 months';

    -- Ventas del 'Trimestre en Curso'
    SELECT *
    FROM sales.fact_sales
    WHERE order_date BETWEEN DATE_TRUNC('quarter', CURRENT_DATE) AND CURRENT_DATE;

    -- Ventas del 'Trimestre Pasado'
    SELECT *
    FROM sales.fact_sales
    WHERE order_date BETWEEN DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '3 months') AND DATE_TRUNC('quarter', CURRENT_DATE) - INTERVAL '1 day';

    -- Ventas del 'Primer semestre del año pasado'
    SELECT *
    FROM sales.fact_sales
    WHERE
        order_date >= DATE_TRUNC('year', CURRENT_DATE - interval '1 year')
        AND order_date < DATE_TRUNC('year', CURRENT_DATE - interval '1 year') + interval '6 months';;

    -- Ventas del 'Semestre en Curso'
    SELECT *
    FROM sales.fact_sales
    WHERE
        order_date >= (
            CASE
                WHEN EXTRACT(MONTH FROM CURRENT_DATE) <= 6 THEN DATE_TRUNC('year', CURRENT_DATE)
                ELSE DATE_TRUNC('year', CURRENT_DATE) + interval '6 months'
            END
        )
        AND order_date < (
            CASE
                WHEN EXTRACT(MONTH FROM CURRENT_DATE) > 6 THEN CURRENT_DATE
                ELSE DATE_TRUNC('year', CURRENT_DATE) + interval '6 months'
            END
        );

    -- Ventas del 'Semestre Pasado'
    SELECT *
    FROM sales.fact_sales
    WHERE
        order_date >= (
            CASE
                WHEN EXTRACT(MONTH FROM CURRENT_DATE) > 6 THEN DATE_TRUNC('year', CURRENT_DATE)
                ELSE DATE_TRUNC('year', CURRENT_DATE - interval '1 year') + interval '6 months'
            END
        )
        AND order_date < (
            CASE
                WHEN EXTRACT(MONTH FROM CURRENT_DATE) <= 6 THEN DATE_TRUNC('year', CURRENT_DATE)
                ELSE DATE_TRUNC('year', CURRENT_DATE) + interval '6 months'
            END
        );
    ```

    ***Nota:*** Para extraer partes de fechas, PostgreSQL soporta `EXTRACT(part FROM date_expression)` además de `DATE_PART`. `DATE_TRUNC('quarter', date)` es una función útil en PostgreSQL para truncar fechas al inicio del trimestre. `INTERVAL` se utiliza para operaciones de resta de tiempo.

## 3. Métricas Clásicas del Retail y su Interpretación

Es crucial entender cómo se miden las diferentes métricas en el contexto de negocio.

- Cuando se habla de **productos "más vendidos"**, sin especificar más, generalmente nos referimos a la **cantidad de unidades (`order_quantity`) vendidas**. También puede ser relevante medir esto por el **importe facturado (`sales_amount`)** para identificar productos que, aunque se vendan en menor volumen, generan más ingresos. Pero, en este último caso se especificarán **términos como "de mayor facturación"**.
- Cuando se refiere a **clientes, tiendas/distribuidores o vendedores que "más compran/venden"**, esto se mide por el **importe facturado (`sales_amount`) o `net sales`**. Adicionalmente, se puede considerar la **frecuencia de compra** (para clientes y distribuidores) o el **número de pedidos gestionados** (para vendedores) como métricas complementarias.
- Para el **análisis de rentabilidad**, la métrica clave es el **margen bruto (`gross margin`) o el porcentaje de margen bruto (`gross margin percentage`)**, lo cual permite comprender la contribución real de cada venta o producto a las ganancias, más allá del volumen o ingreso total. Este enfoque es vital para evaluar la eficiencia operativa.
- En el contexto de la **gestión de promociones**, el éxito no solo se mide por el discount_amount o average_discount_rate, sino también por el **incremento en `order_quantity` o `sales_amount`** directamente atribuible a la promoción. Es fundamental analizar la **rentabilidad general del período promocional** para determinar su efectividad.
- **Ventas B2C (Business-to-Consumer):** Estas ventas se refieren a transacciones directas con el consumidor final. En el modelo, corresponden a los pedidos donde `sale_source` es igual a `'internet_sales'`. Puede identificarse también como la unidad de negocio encargada del comercio minorista.
- **Ventas B2B (Business-to-Business):** Estas ventas se refieren a transacciones entre empresas, como las realizadas con distribuidores o tiendas minoristas. En el modelo, corresponden a los pedidos donde `sale_source` es igual a `'reseller_sales'`. Puede identificarse también como la unidad de negocio encargada del comercio mayorista.

### 3.1 Ventas Netas (`Net Sales`)

- **Definición:** El **total de dinero obtenido** de las ventas después de haber restado todos los descuentos.
- **Principio Operativo:** Este indicador se correlaciona directamente con el campo `sales_amount` de la tabla `fact_sales`.
- **Implementación Lógica SQL:**

    ```sql
    SUM(sales_amount) AS importe_ventas
    ```

### 3.2 Volumen de Unidades Comercializadas (`Quantity Sold`)

- **Definición:** La **cantidad total de productos** que han sido vendidos.
- **Principio Operativo:** Este indicador se corresponde con el campo `order_quantity` de la tabla `fact_sales`.
- **Implementación Lógica SQL:**

    ```sql
    SUM(order_quantity) AS cantidad_vendida
    ```

### 3.3 Precio Medio del Producto (`Average Product Price`)

- **Definición:** El **valor promedio** al que se vendió cada unidad de producto, calculado dividiendo las ventas netas por el número de unidades vendidas.
- **Principio Operativo:** Este indicador se calcula dividiendo el `sales_amount` por el `order_quantity` en la tabla `fact_sales`.
- **Implementación Lógica SQL:**

    ```sql
    SUM(fs.sales_amount) / NULLIF(SUM(fs.order_quantity), 0) AS precio_medio
    ```

### 3.4 Coste de la Mercancía Vendida (`COGS - Cost of Goods Sold`)

- **Definición:** El **coste total** de los productos que la empresa ha vendido, ya sea por comprarlos o por fabricarlos.
- **Principio Operativo:** Este indicador se corresponde con el campo `total_product_cost` de la tabla `fact_sales`.
- **Implementación Lógica SQL:**

    ```sql
    SUM(total_product_cost) AS coste_mercancia
    ```

### 3.5 Margen Bruto (`Gross Margin / Gross Profit`)

- **Definición:** La **ganancia directa** que se obtiene de las ventas, calculada al restar el costo de los productos vendidos del total de las ventas netas.
- **Principio Operativo:** El `Gross Margin` se calcula como `sales_amount - total_product_cost`.
- **Implementación Lógica SQL:**

    ```sql
    SUM(sales_amount - total_product_cost) AS margen_bruto
    ```

### 3.6 Porcentaje de Margen Bruto (`Gross Margin Percentage`)

- **Definición:** El **porcentaje de las ventas netas** que representa el margen bruto, indicando qué parte de cada venta es ganancia directa.
- **Principio Operativo:** El `Gross Margin Percentage` se computa como `(Gross Margin / sales_amount) * 100`.
- **Implementación Lógica SQL:**

    ```sql
    (SUM(sales_amount - total_product_cost) / NULLIF(SUM(sales_amount), 0)) * 100 AS gross_margin_percentagemargen_bruto_pct
    ```

### 3.7 Valor Promedio por Orden (`AOV - Average Order Value`) / `Valor Ticket Medio`

- **Definición:** El **importe promedio** de cada pedido o "ticket" de compra. Mide cuánto gasta, en promedio, un cliente en cada transacción.
- **Principio Operativo:** El cálculo de este valor se efectúa mediante la división del sumatorio total de `sales_amount` (cifra de negocio neta) entre el recuento distintivo de `sales_order_number` (órdenes de compra).
- **Implementación Lógica SQL:**

    ```sql
    SUM(sales_amount) / COUNT(DISTINCT sales_order_number) AS valor_ticket_medio
    ```

### 3.8 Tasa de Descuento Promedio (`Average Discount Rate`)

- **Definición:** El **porcentaje medio de rebaja** aplicado a los precios en todas las transacciones de venta.
- **Principio Operativo:** El cálculo se realiza mediante la división del sumatorio total de `discount_amount` entre el sumatorio total de `extended_amount` (el precio original previo a la aplicación del descuento).
- **Implementación Lógica SQL:**

    ```sql
    (SUM(discount_amount) / NULLIF(SUM(extended_amount), 0)) * 100 AS tasa_descuento_promedio_pct
    ```

### 3.9 Volumen de Ventas por Cliente / Distribuidor (`Sales per Customer / Reseller`)

- **Definición:** El **total de ventas (en dinero)** que ha generado cada cliente (para ventas en línea - B2C) o cada distribuidor (para ventas a tiendas/distribuidores - B2B).
- **Principio Operativo:** Se procederá a la agregación del `sales_amount` por `customer_key` (B2C) o por `reseller_key` (B2B).
- **Implementación Lógica SQL (Ejemplo para clientes en línea / mercado minorista - B2C):**

    ```sql
    SELECT
        fs.customer_key,
        dc.customer_full_name AS cliente,
        SUM(fs.sales_amount) AS importe_ventas_por_cliente
    FROM sales.fact_sales fs
    JOIN sales.dim_customer dc ON fs.customer_key = dc.customer_key
    WHERE fs.sale_source = 'internet_sales'
    GROUP BY fs.customer_key, dc.customer_full_name
    ORDER BY importe_ventas_por_cliente DESC;
    ```

### 3.10 Volumen de Ventas por Agente Comercial (`Sales per Sales Person`)

- **Definición:** El **total de ventas (en dinero)** que ha generado cada vendedor.
- **Principio Operativo:** Se agregará el `sales_amount` por `employee_key` de la tabla `dim_sales_person` específicamente para las `reseller_sales` (B2B).
- **Implementación Lógica SQL:**

    ```sql
    SELECT
        fs.employee_key,
        dsp.employee_full_name AS empleado,
        SUM(fs.sales_amount) AS importe_ventas_por_empleado
    FROM sales.fact_sales fs
    JOIN sales.dim_sales_person dsp ON fs.employee_key = dsp.employee_key
    WHERE fs.sale_source = 'reseller_sales' -- La atribución a agentes comerciales se circunscribe a las ventas a distribuidores / mayoristas (B2B) 
    GROUP BY fs.employee_key, dsp.employee_full_name
    ORDER BY importe_ventas_por_empleado DESC;
    ```

## 4. Derivación de Indicadores y Segmentación

La creación de nuevas dimensiones o indicadores es factible a partir de las propiedades preexistentes de las entidades.

### 4.1 Segmentación de Clientes Conforme a Ingresos y Patrones Comportamentales

- **Principio Operativo:** La clasificación de los clientes en categorías segmentadas, fundamentadas en su ingreso anual y en atributos como la condición de `house_owner` y el `number_children_at_home`, se impone para la ejecución de análisis en el ámbito de marketing y ventas.
- **Implementación Lógica SQL (Ejemplo para `dim_customer`):**

    ```sql
    SELECT
        customer_key,
        customer_full_name AS cliente,
        yearly_income AS ingreso_anual,
        house_owner AS propietarios,
        number_children_at_home AS hijos_en_casa,
        CASE
            WHEN yearly_income >= 100000 THEN 'Alto Valor'
            WHEN yearly_income >= 50000 AND yearly_income < 100000 THEN 'Valor Medio'
            ELSE 'Valor Básico'
        END AS segmento_ingresos,
        CASE
            WHEN house_owner = TRUE AND number_children_at_home > 0 THEN 'Familia Propietaria'
            WHEN house_owner = TRUE AND number_children_at_home = 0 THEN 'Propietario Sin Hijos'
            WHEN house_owner = FALSE AND number_children_at_home > 0 THEN 'Familia Inquilina'
            ELSE 'Inquilino Sin Hijos'
        END AS segmento_estilo_vida
    FROM
        sales.dim_customer;
    ```

### 4.2 Clasificación de Productos por Rango de Precios

- **Principio Operativo:** La categorización de los productos en distintas gamas de precio (e.g., "Premium", "Estándar", "Económico") se llevará a cabo basándose en el atributo `list_price`.
- **Implementación Lógica SQL (Ejemplo para `dim_product`):**

    ```sql
    SELECT
        product_key,
        COALESCE(spanish_product_name, english_product_name) AS product_name,
        list_price,
        CASE
            WHEN list_price >= 1000 THEN 'Premium'
            WHEN list_price >= 200 AND list_price < 1000 THEN 'Estándar'
            ELSE 'Económico'
        END AS product_price_tier
    FROM
        sales.dim_product;
    ```
