# Resistencia al fuego: intumescente para malla espacial

Herramientas para estimar el espesor (DFT) y el costo de intumescente sobre los tubos de una malla espacial (bodega de ~50.000 m², Caldas, Antioquia).

- `ANALISIS.md`: análisis matemático, referencias de costo (Colombia y EE. UU.) e incertidumbre.
- `modelo_matematico.py`: modelo completo (balance de calor, escala, costo afín, Monte Carlo). Salida en `salida_modelo.txt`.
- `calculadora_intumescente.html`: calculadora de un solo archivo; resistencia en minutos y factor de forma sin límites; base de costos CYPE o EE. UU.
- `intumescente.py`: primera versión simple del modelo (referencia).

No reemplaza la tabla certificada del fabricante. Los precios no son cotizaciones.
