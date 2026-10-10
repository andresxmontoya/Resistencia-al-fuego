# Análisis matemático del intumescente en la malla espacial

Modelo: `modelo_matematico.py` (salida completa en `salida_modelo.txt`). Calculadora: `calculadora_intumescente.html`.

## 1. Datos de partida

- Tubos de la ficha del proveedor: A500 Gr. C, Ø60, 73, 90 y 114 mm. **Espesores de pared asumidos:** 2,5 mm para Ø60 y Ø73; 3,0 mm para Ø90 y Ø114.
- Factor de forma de un tubo expuesto por fuera: A/V = 4d / (d² − (d − 2t)²). Resulta 417, 414, 345 y 342 m⁻¹.
- Longitud de tubo: 116.000 m (estimación del autor, módulo de 3,20 m). Mezcla supuesta de igual longitud por diámetro, superficie media 0,265 m² por metro: unos 30.700 m². No incluye nudos ni tornillos.
- Calibración con CYPE Colombia: R60, 1003 µm, 85 m⁻¹, 136.022 COP/m²; R90, 2223 µm, 297.314 COP/m² (factor de forma de R90 no visible).
- TRM oficial del 5 de octubre de 2026: 3.273,49 COP/USD.

## 2. Balance de calor y teorema de escala

Acero con temperatura uniforme y recubrimiento sin masa térmica (EN 1993-1-2, ec. 4.27 con φ = 0):

dTs/dt = r (Tg − Ts) / (ρ ca(Ts)),  r = (A/V) / R,  R = κ·DFT

con Tg = 20 + 345 log10(8t + 1) (ISO 834) y ca(T) de EN 1993-1-2.

La trayectoria Ts(t) depende solo de r. Si r*(t, θ) es la r con la que el acero llega a θ en t minutos, entonces

**DFT = (A/V) / (κ · r*(t, θ))**

Es decir, el espesor es exactamente proporcional al factor de forma. Con calibración en un punto:
DFT = DFT₀ · (A/V)/A₀ · r*(t₀, θ₀) / r*(t, θ).

Calibrado con CYPE R60 (supuesto: temperatura crítica de referencia 500 °C): R = 0,0764 m²K/W, equivalente a una conductividad de 0,013 W/(m·K) sobre el espesor seco.

## 3. Resultados del modelo

G = DFT/(A/V), con μ = 0,5 (θcr = 585 °C):

| Resistencia | G (µm por m⁻¹) |
|---|---|
| R30 | 3,27 |
| R60 | 8,54 |
| R90 | 14,54 |
| R120 | 21,02 |
| R180 | 34,96 |

- G crece como t^1,34: duplicar la resistencia multiplica el espesor por 2,5.
- Elasticidades en R60 a 345 m⁻¹: respecto al tiempo 1,33; respecto a A/V 1,00 (exacto). Subir la temperatura crítica 50 °C baja el espesor 18 %; subir la de referencia de calibración 50 °C lo sube 21 %.
- **Discrepancia con CYPE:** de R60 a R90 el espesor de CYPE crece con exponente 1,96 (ratio 2,22) y el modelo con 1,31 (ratio 1,68). Puede deberse a que CYPE usó otro A/V en R90 o a que el modelo se queda corto a tiempos largos. Se trata como incertidumbre (p entre 1,31 y 1,96).

## 4. Espesor y costo por tubo (μ = 0,5, R60)

| Tubo | A/V (m⁻¹) | DFT (µm) | COP/m² (CYPE) | COP por metro de tubo (CYPE) |
|---|---|---|---|---|
| Ø60×2,5 | 417 | 3.565 | 474.782 | 89.494 |
| Ø73×2,5 | 414 | 3.538 | 471.161 | 108.054 |
| Ø90×3,0 | 345 | 2.946 | 392.836 | 111.072 |
| Ø114×3,0 | 342 | 2.924 | 390.029 | 139.686 |

Para R90 los espesores van de 5.000 a 6.100 µm. La salida completa está en `salida_modelo.txt`.

## 5. Modelo de costo afín y referencia de EE. UU.

Costo c(DFT) = c₀ + c₁·DFT [COP/m²].

- **CYPE** (dos puntos): c₁ = 132,2 COP/(µm·m²), c₀ ≈ 3.400 COP/m². Casi proporcional al espesor.
- **EE. UU.** (tabla de un contratista, FlameOFF: USD 5–8/ft² a 60 min, 7–10 a 90, 8–12 a 120; puntos medios ajustados por mínimos cuadrados, TRM 3.273,49): c₁ = 96 COP/(µm·m²), c₀ ≈ 117.000 COP/m² (mano de obra fija, equipos, preparación).
- **Control físico del material:** 1 galón = 3.785 m²·µm al 100 % de sólidos. Con USD 70–110/galón, sólidos de 65 a 100 % y pérdidas de 20 a 30 %: c₁ = 97 a 171 COP/(µm·m²). El valor de CYPE (132) cae en el centro de ese rango.
- **Banda genérica de EE. UU.:** USD 10–30/ft² instalado (Bahl Fireproofing), sin distinguir rating: 353.000 a 1.057.000 COP/m².

Los precios de EE. UU. vienen de páginas de contratistas, no de bases de costos publicadas (RSMeans u otras); son una referencia débil. La propia página de FlameOFF tiene cifras de material inconsistentes con su cobertura.

Total para la población de tubos: C = L · Σᵢ fᵢ aᵢ [c₀ + c₁ G (A/V)ᵢ], con aᵢ = π dᵢ la superficie por metro y fᵢ la fracción de longitud.

## 6. Resultados para la bodega (116.000 m de tubo, μ = 0,5; miles de millones de COP)

| Resistencia | CYPE afín | EE. UU. afín | Banda genérica EE. UU. |
|---|---|---|---|
| R60 | 13,0 | 13,0 | 10,8 a 32,5 |
| R90 (modelo) | 22,1 | 19,6 | igual |
| R90 (exponente de CYPE) | 28,7 | 24,4 | igual |

## 7. Incertidumbre (Monte Carlo, N = 40.000)

Supuestos: θ de referencia ∼ U(450, 550) °C; μ ∼ triangular(0,3; 0,5; 0,8); exponente temporal p ∼ U(1,31; 1,96); c₁ ∼ U(97, 171); c₀ ∼ U(3.400; 117.000).

| Resistencia | DFT P10 / P50 / P90 (µm) | Costo P10 / P50 / P90 (MM COP) |
|---|---|---|
| R60 | 2.443 / 3.046 / 3.793 | 11.433 / 15.289 / 20.068 |
| R90 | 4.642 / 5.917 / 7.514 | 20.573 / 27.855 / 37.509 |

Correlación de rangos con el costo (R60): c₁ +0,66, μ +0,50, θ de referencia +0,43, c₀ +0,30. El precio por micra y el nivel de carga del elemento pesan más que el exponente temporal.

## 8. Advertencias

- No reemplaza la tabla certificada del fabricante (EN 13381-8, ASTM E119).
- Espesores de pared asumidos; mezcla de diámetros asumida; longitud total de tubo estimada.
- Con más de unos 5.000 µm, una película delgada acuosa difícilmente se aplica; probablemente se requiere epóxico grueso o diseño por desempeño (otro precio por micra).
- Los costos anteriores de 17.800 a 22.300 millones usaban 60.000 m² de acero (supuesto del modelo de mantenimiento, 1,2 veces el área en planta). La superficie de tubo con estos diámetros es de unos 30.700 m². Habría que reconciliar ambos supuestos.
- Quedan fuera nudos, tornillos y andamios.
