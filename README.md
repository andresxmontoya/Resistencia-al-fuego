# Resistencia al fuego: intumescente para malla espacial

Herramientas para estimar el espesor (DFT) y el costo de pintura intumescente sobre tubos de acero de una malla espacial (bodega de ~50.000 m², Caldas, Antioquia).

- `calculadora_intumescente.html`: calculadora de un solo archivo (abrir en el navegador). Resistencia al fuego en minutos y factor de forma A/V sin límites.
- `intumescente.py`: el mismo modelo en Python, con tabla de resultados para A/V = 345 m⁻¹ (tubo Ø90×3).

## Modelo

Calentamiento del acero con temperatura uniforme bajo la curva ISO 834 (calor específico de EN 1993-1-2). El aislamiento del intumescente se supone proporcional a su espesor y se calibra con un punto de CYPE Colombia (ficha IOR040, R60, 1003 µm, 85 m⁻¹). La temperatura crítica sale de EN 1993-1-2 (4.2.4).

## Advertencias

- No reemplaza la tabla certificada del fabricante (ensayos EN 13381-8, ASTM E119). Es para órdenes de magnitud y para pedir cotizaciones.
- La temperatura crítica de referencia (500 °C) y el precio por micra (~135 COP/µm·m²) son supuestos.
- El modelo subestima en ~32 % el R90 de CYPE; a resistencias altas el espesor real puede ser mayor.
- Los precios no son cotizaciones.
