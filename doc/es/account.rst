#:before:account/account_invoice:section:cancelar#

.. inheritref:: account_invoice_line_standalone/account:section:fusionar_facturas

-----------------
Fusionar facturas
-----------------

En las facturas se dispone de un asistente para fusionar facturas. Esta acción permite
dos o más facturas seleccionadas, crear una nueva factura con todas las líneas que contienen
las facturas seleccionadas y se eliminan las facturas seleccionadas.

Las facturas seleccionas pasarán al estado cancelado y después serán eliminadas. La nueva factura
se nos abrirá en una nueva pestaña. Si refrescamos la lista de facturas, veremos que las facturas
que habiamos seleccionado ya no estan disponibles (se han eliminado) y nos aparecerá la nueva factura.

Para fusionar facturas, las facturas seleccionadas deben:

* Estado borrador. Sólo se fusionan facturas en el estado borrador
* Mismo tercero. Sólo se fusionan facturas seleccionando el mismo tercero.
* Misma dirección de facturación. Sólo se fusionan facturas que sean de la misma dirección de facturación.
* Mismo diario. Sólo se fusionaran facturas del mismo diario
* Mismo plazo de pago. Sólo se fusionaran facturas del mismo plazo de pago.

.. note:: Al eliminarse las facturas seleccionadas una vez generado la nueva, ya no podrá
          leerlas ya que no exiten (aparecerá un mensaje de alerta al respecto).
