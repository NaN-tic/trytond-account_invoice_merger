================================
Contabilidad. Fusión de facturas
================================

Permite la fusión de facturas y abonos.

Añade nuevo menú para poder ver facturas y abonos a la vez.

Añade nuevo asistente en las facturas que permite fusionar las facturas
seleccionadas con el ratón.

Muestra un mensaje de error y abortará el proceso si todas las facturas
seleccionadas no tienen el mismo:
 * Estado (borrador)
 * Tercero
 * Dirección
 * Diario contable
 * Plazo de pago
 
Crea nueva factura normal con los datos anteriores, la descripción es la
concatenación de las descripciones de cada factura y las líneas las mueve de
las facturas originales a la nueva. A las líneas que provienen de una factura
de abono se les cambia el signo de la cantidad.

Las facturas originales, que quedan sin líneas, se eliminan.
