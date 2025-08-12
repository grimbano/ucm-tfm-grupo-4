# Reglas de Negocio y Lógica SQL para el Modelo de Datos reducido `sales` de la Base de Datos AdventureWorks DW

Este documento describe reglas de negocio para el modelo reducido `sales` de la Base de Datos AdventureWorks DW, centrándose en la **derivación de métricas, el manejo inteligente de datos y la aplicación de lógica transformacional mediante SQL**, con la sintaxis específicamente adaptada para **PostgreSQL**. Estas reglas son cruciales para la construcción de informes, análisis de datos y la operacionalización de la inteligencia de negocio.

## 1. Representación de Entidades y Preferencias Lingüísticas

Cuando se solicita conceptualmente una entidad, como "productos", "clientes", "promociones" o "revendedores", se establece como principio operativo priorizar los campos que finalizan en `_name` para su adecuada representación en las salidas de las consultas SQL. Adicionalmente, se procurará mantener la coherencia con el idioma en que la consulta original fue formulada.

* **Principio Operativo:** Para la visualización de entidades en los resultados de consultas, se debe seleccionar el campo `_name` que mejor represente la entidad. En el caso de campos bilingües donde la versión en español (`spanish_..._name`, `spanish_..._description`) pueda ser nula y la consulta se realice en español, se utilizará la versión en inglés como alternativa (`fallback`) para asegurar la disponibilidad del dato y mantener la representación de la entidad.
* **Lógica SQL (Ejemplo para `dim_product`):**

    ```sql
    -- Selección del nombre del producto en español o, si es NULL, en inglés, para su representación
    SELECT
        product_key,
        COALESCE(spanish_product_name, english_product_name) AS product_name_localized,
        COALESCE(spanish_product_subcategory_name, english_product_subcategory_name) AS product_subcategory_name_localized,
        COALESCE(spanish_product_category_name, english_product_category_name) AS product_category_name_localized
    FROM
        sales.dim_product;
    ```

    Este enfoque se aplicaría de manera similar a la representación de nombres de entidades en `dim_promotion`, `dim_customer`, `dim_reseller`, `dim_sales_person`, `dim_sales_reason`, `dim_sales_territory` y `dim_geography`, siempre privilegiando los campos `_name` relevantes y aplicando la lógica de `fallback` para el idioma.

## 2. Cálculos Basados en Fechas

Las fechas en `fact_sales` permiten derivar métricas de tiempo cruciales para el análisis de la eficiencia de la cadena de suministro y la experiencia del cliente.

### 2.1 Métricas de Tiempo de Entrega y Envío

* **Regla de Negocio:** En caso de que se quiera hacer un análisis referido a los tiempos asociados a las ventas, se deben calcular los siguientes indicadores de tiempo:
  * **Tiempo de Envío (Shipping Time):** Días transcurridos desde que se creó el pedido (`order_date`) hasta que se envió (`ship_date`).
  * **Tiempo de Entrega (Delivery Time):** Días transcurridos desde que se envió el pedido (`ship_date`) hasta que se entregó al cliente (`due_date`).
  * **Tiempo Total de Procesamiento del Pedido (Order Processing Time):** Días transcurridos desde que se creó el pedido (`order_date`) hasta su entrega final (`due_date`).
* **Lógica SQL (Ejemplo para `fact_sales`):**

    ```sql
    SELECT
        sales_order_number,
        sales_order_line_number,
        order_date,
        ship_date,
        due_date,
        -- Tiempo de Envío / Shipping Time (en días)
        DATE_PART('day', ship_date - order_date) AS shipping_time_days,
        -- Tiempo de Entrega / Delivery Time (en días)
        DATE_PART('day', due_date - ship_date) AS delivery_time_days,
        -- Tiempo Total de Procesamiento del Pedido / Order Processing Time (en días)
        DATE_PART('day', due_date - order_date) AS total_order_processing_time_days
    FROM
        sales.fact_sales;
    ```

  ***Nota***: En Postgres, la resta de fechas `(fecha_final - fecha_inicial)` devuelve un tipo `INTERVAL`, y `DATE_PART('day', interval)` extrae el número de días de ese intervalo.

### 2.2 Desglose por Períodos Temporales Comunes

Para los informes de ventas, muchas veces es fundamental poder filtrar y agregar datos por **períodos estándar asociados a términos como "Este Año", "Año Pasado", "Acumulado del Año (YTD)" y la comparación "Año Actual vs. Año Pasado"**. A continuación, se define la lógica SQL para definir cada uno de estos:

* **Lógica SQL:**

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

    -- Comparativa 'Año Actual vs. Año Pasado' (requiere CTEs para agregaciones)
    WITH CurrentYearSales AS (
        SELECT
            EXTRACT(MONTH FROM order_date) AS sales_month,
            SUM(sales_amount) AS current_year_sales
        FROM sales.fact_sales
        WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE)
        GROUP BY 1
    ),
    LastYearSales AS (
        SELECT
            EXTRACT(MONTH FROM order_date) AS sales_month,
            SUM(sales_amount) AS last_year_sales
        FROM sales.fact_sales
        WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1
        GROUP BY 1
    )
    SELECT
        COALESCE(CY.sales_month, LY.sales_month) AS sales_month,
        COALESCE(CY.current_year_sales, 0) AS current_year_sales,
        COALESCE(LY.last_year_sales, 0) AS last_year_sales,
        (COALESCE(CY.current_year_sales, 0) - COALESCE(LY.last_year_sales, 0)) AS sales_difference,
        (COALESCE(CY.current_year_sales, 0) - COALESCE(LY.last_year_sales, 0)) / NULLIF(COALESCE(LY.last_year_sales, 0), 0) AS percentage_change
    FROM CurrentYearSales CY
    FULL OUTER JOIN LastYearSales LY ON CY.sales_month = LY.sales_month
    ORDER BY sales_month;
    ```

    ***Nota***: Para extraer partes de fechas, PostgreSQL soporta EXTRACT(part FROM date_expression) además de DATE_PART.

## 3. Métricas Clásicas del Retail y su Interpretación

Es crucial entender cómo se miden las diferentes métricas en el contexto de negocio.

* Cuando se habla de **productos "más vendidos"**, sin especificar más, generalmente nos referimos a la **cantidad de unidades (`order_quantity`) vendidas**. También puede ser relevante medir esto por el **importe facturado (`sales_amount`)** para identificar productos que, aunque se vendan en menor volumen, generan más ingresos. Pero, en este último caso se especificarán **términos como "de mayor facturación"**.
* Cuando se refiere a **clientes, tiendas/distribuidores o vendedores que "más compran/venden"**, esto se mide por el **importe facturado (`sales_amount`) o `net sales`**. Adicionalmente, se puede considerar la **frecuencia de compra** (para clientes y distribuidores) o el **número de pedidos gestionados** (para vendedores) como métricas complementarias.
* Para el **análisis de rentabilidad**, la métrica clave es el **margen bruto (`gross margin`) o el porcentaje de margen bruto (`gross margin percentage`)**, lo cual permite comprender la contribución real de cada venta o producto a las ganancias, más allá del volumen o ingreso total. Este enfoque es vital para evaluar la eficiencia operativa.
* En el contexto de la **gestión de promociones**, el éxito no solo se mide por el discount_amount o average_discount_rate, sino también por el **incremento en `order_quantity` o `sales_amount`** directamente atribuible a la promoción. Es fundamental analizar la **rentabilidad general del período promocional** para determinar su efectividad.
* **Ventas B2C (Business-to-Consumer):** Estas ventas se refieren a transacciones directas con el consumidor final. En el modelo, corresponden a los pedidos donde `sale_source` es igual a `'internet_sales'`.
* **Ventas B2B (Business-to-Business):** Estas ventas se refieren a transacciones entre empresas, como las realizadas con distribuidores o tiendas minoristas. En el modelo, corresponden a los pedidos donde `sale_source` es igual a `'reseller_sales'`.

### 3.1 Ventas Netas (`Net Sales`)

* **Definición:** El **total de dinero obtenido** de las ventas después de haber restado todos los descuentos.
* **Principio Operativo:** Este indicador se correlaciona directamente con el campo `sales_amount` de la tabla `fact_sales`.
* **Implementación Lógica SQL:**

    ```sql
    SUM(sales_amount)
    ```

### 3.2 Volumen de Unidades Comercializadas (`Quantity Sold`)

* **Definición:** La **cantidad total de productos** que han sido vendidos.
* **Principio Operativo:** Este indicador se corresponde con el campo `order_quantity` de la tabla `fact_sales`.
* **Implementación Lógica SQL:**

    ```sql
    SUM(order_quantity)
    ```

### 3.3 Coste de la Mercancía Vendida (`COGS - Cost of Goods Sold`)

* **Definición:** El **coste total** de los productos que la empresa ha vendido, ya sea por comprarlos o por fabricarlos.
* **Principio Operativo:** Este indicador se corresponde con el campo `total_product_cost` de la tabla `fact_sales`.
* **Implementación Lógica SQL:**

    ```sql
    SUM(total_product_cost)
    ```

### 3.4 Margen Bruto (`Gross Margin / Gross Profit`)

* **Definición:** La **ganancia directa** que se obtiene de las ventas, calculada al restar el costo de los productos vendidos del total de las ventas netas.
* **Principio Operativo:** El `Gross Margin` se calcula como `sales_amount - total_product_cost`.
* **Implementación Lógica SQL:**

    ```sql
    SUM(sales_amount - total_product_cost) AS gross_margin
    ```

### 3.5 Porcentaje de Margen Bruto (`Gross Margin Percentage`)

* **Definición:** El **porcentaje de las ventas netas** que representa el margen bruto, indicando qué parte de cada venta es ganancia directa.
* **Principio Operativo:** El `Gross Margin Percentage` se computa como `(Gross Margin / sales_amount) * 100`.
* **Implementación Lógica SQL:**

    ```sql
    (SUM(sales_amount - total_product_cost) / NULLIF(SUM(sales_amount), 0)) * 100 AS gross_margin_percentage
    ```

### 3.6 Valor Promedio por Orden (`AOV - Average Order Value`) / `Valor Ticket Medio`

* **Definición:** El **importe promedio** de cada pedido o "ticket" de compra. Mide cuánto gasta, en promedio, un cliente en cada transacción.
* **Principio Operativo:** El cálculo de este valor se efectúa mediante la división del sumatorio total de `sales_amount` (cifra de negocio neta) entre el recuento distintivo de `sales_order_number` (órdenes de compra).
* **Implementación Lógica SQL:**

    ```sql
    SUM(sales_amount) / COUNT(DISTINCT sales_order_number) AS average_order_value
    ```

### 3.7 Tasa de Descuento Promedio (`Average Discount Rate`)

* **Definición:** El **porcentaje medio de rebaja** aplicado a los precios en todas las transacciones de venta.
* **Principio Operativo:** El cálculo se realiza mediante la división del sumatorio total de `discount_amount` entre el sumatorio total de `extended_amount` (el precio original previo a la aplicación del descuento).
* **Implementación Lógica SQL:**

    ```sql
    (SUM(discount_amount) / NULLIF(SUM(extended_amount), 0)) * 100 AS average_discount_rate_pct
    ```

### 3.8 Volumen de Ventas por Cliente / Distribuidor (`Sales per Customer / Reseller`)

* **Definición:** El **total de ventas (en dinero)** que ha generado cada cliente (para ventas en línea - B2C) o cada distribuidor (para ventas a tiendas/distribuidores - B2B).
* **Principio Operativo:** Se procederá a la agregación del `sales_amount` por `customer_key` (B2C) o por `reseller_key` (B2B).
* **Implementación Lógica SQL (Ejemplo para clientes en línea - B2C):**

    ```sql
    SELECT
        fs.customer_key,
        dc.customer_full_name,
        SUM(fs.sales_amount) AS total_sales_by_customer
    FROM sales.fact_sales fs
    JOIN sales.dim_customer dc ON fs.customer_key = dc.customer_key
    WHERE fs.sale_source = 'internet_sales'
    GROUP BY fs.customer_key, dc.customer_full_name
    ORDER BY total_sales_by_customer DESC;
    ```

### 3.9 Volumen de Ventas por Agente Comercial (`Sales per Sales Person`)

* **Definición:** El **total de ventas (en dinero)** que ha generado cada vendedor.
* **Principio Operativo:** Se agregará el `sales_amount` por `employee_key` de la tabla `dim_sales_person` específicamente para las `reseller_sales` (B2B).
* **Implementación Lógica SQL:**

    ```sql
    SELECT
        fs.employee_key,
        dsp.employee_full_name,
        SUM(fs.sales_amount) AS total_sales_by_salesperson
    FROM sales.fact_sales fs
    JOIN sales.dim_sales_person dsp ON fs.employee_key = dsp.employee_key
    WHERE fs.sale_source = 'reseller_sales' -- La atribución a agentes comerciales se circunscribe a las ventas a distribuidores (B2B) 
    GROUP BY fs.employee_key, dsp.employee_full_name
    ORDER BY total_sales_by_salesperson DESC;
    ```

## 4. Derivación de Indicadores y Segmentación

La creación de nuevas dimensiones o indicadores es factible a partir de las propiedades preexistentes de las entidades.

### 4.1 Segmentación de Clientes Conforme a Ingresos y Patrones Comportamentales

* **Principio Operativo:** La clasificación de los clientes en categorías segmentadas, fundamentadas en su ingreso anual y en atributos como la condición de `house_owner` y el `number_children_at_home`, se impone para la ejecución de análisis en el ámbito de marketing y ventas.
* **Implementación Lógica SQL (Ejemplo para `dim_customer`):**

    ```sql
    SELECT
        customer_key,
        customer_full_name,
        yearly_income,
        house_owner,
        number_children_at_home,
        CASE
            WHEN yearly_income >= 100000 THEN 'Alto Valor'
            WHEN yearly_income >= 50000 AND yearly_income < 100000 THEN 'Valor Medio'
            ELSE 'Valor Básico'
        END AS customer_income_segment,
        CASE
            WHEN house_owner = TRUE AND number_children_at_home > 0 THEN 'Familia Propietaria'
            WHEN house_owner = TRUE AND number_children_at_home = 0 THEN 'Propietario Sin Hijos'
            WHEN house_owner = FALSE AND number_children_at_home > 0 THEN 'Familia Alquilada'
            ELSE 'Alquilado Sin Hijos'
        END AS customer_lifestyle_segment
    FROM
        sales.dim_customer;
    ```

### 4.2 Clasificación de Productos por Rango de Precios

* **Principio Operativo:** La categorización de los productos en distintas gamas de precio (e.g., "Premium", "Estándar", "Económico") se llevará a cabo basándose en el atributo `list_price`.
* **Implementación Lógica SQL (Ejemplo para `dim_product`):**

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
