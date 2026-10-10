#!/usr/bin/env python3
"""
Espesor indicativo de pintura intumescente y costo para tubos de la malla espacial.

MODELO (simplificado, ver advertencias al final):
  - Temperatura del gas: curva ISO 834, Tg = 20 + 345 log10(8 t + 1), t en min.
  - Acero con temperatura uniforme (parametro concentrado):
        dTs/dt = (A/V) / (rho * ca(Ts)) * (Tg - Ts) / R
    con calor especifico ca(T) de EN 1993-1-2 (3.4.1.2) y rho = 7850 kg/m3.
  - Resistencia termica del intumescente: R = kappa * DFT (el espesor de la capa
    carbonizada es proporcional al espesor seco). No se modela la masa termica del
    intumescente ni la fase previa a la expansion.
  - kappa se CALIBRA con un punto de CYPE: R60, 1003 um, A/V = 85 m-1, alcanzando
    la temperatura critica de referencia THETA_REF a los 60 min.
  - Temperatura critica del elemento (EN 1993-1-2, 4.2.4):
        theta_cr = 39.19 ln(1/(0.9674 mu^3.833) - 1) + 482,   mu = grado de utilizacion.
  - Precio = COP_POR_UM * DFT (supuesto, de las capturas de CYPE: ~135 COP/(um m2)).

ESTO NO REEMPLAZA LA TABLA DEL FABRICANTE. El espesor certificado sale de ensayos
(EN 13381-8, UL 263/ASTM E119) por producto y factor de forma. Usar solo para
orden de magnitud y para pedir cotizacion.
"""
import math

RHO = 7850.0
# Calibracion CYPE (capturas del usuario)
CYPE = {"R60": dict(av=85, dft=1003, precio=136022.04),
        "R90": dict(av=85, dft=2223, precio=297314.00)}  # R90: factor de forma no visible en la captura
THETA_REF = 500.0          # SUPUESTO: temperatura critica base del precio de CYPE
COP_POR_UM = 135.0         # COP por micra y m2 (de R60 y R90 de CYPE)


def ca(T):
    """Calor especifico del acero al carbono, J/(kg K), EN 1993-1-2."""
    if T < 600:
        return 425 + 0.773 * T - 1.69e-3 * T**2 + 2.22e-6 * T**3
    if T < 735:
        return 666 + 13002 / (738 - T)
    if T < 900:
        return 545 + 17820 / (T - 731)
    return 650.0


def tgas(t_min):
    return 20 + 345 * math.log10(8 * t_min + 1)


def temp_acero(av, dft_um, kappa, t_min, dt=1.0):
    """Temperatura del acero (C) a t_min min. dt en segundos."""
    R = kappa * dft_um
    Ts, t = 20.0, 0.0
    while t < t_min * 60:
        Tg = tgas(t / 60)
        Ts += av / (RHO * ca(Ts)) * (Tg - Ts) / R * dt
        t += dt
    return Ts


def calibrar(theta_ref=THETA_REF):
    """kappa tal que R60, 1003 um, A/V=85 llegue a theta_ref a los 60 min."""
    c = CYPE["R60"]
    lo, hi = 1e-6, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if temp_acero(c["av"], c["dft"], mid, 60) > theta_ref:
            lo = mid        # mas resistencia termica -> menos temperatura
        else:
            hi = mid
    return (lo + hi) / 2


def theta_cr(mu):
    return 39.19 * math.log(1 / (0.9674 * mu**3.833) - 1) + 482


def dft_requerido(av, t_min, theta, kappa):
    """DFT (um) para que el acero no pase de theta a t_min."""
    lo, hi = 10.0, 60000.0
    if temp_acero(av, hi, kappa, t_min) > theta:
        return float("inf")
    for _ in range(50):
        mid = (lo + hi) / 2
        if temp_acero(av, mid, kappa, t_min) > theta:
            lo = mid
        else:
            hi = mid
    return hi


def av_tubo(d_mm, t_mm):
    """Factor de forma de tubo circular expuesto por fuera, m-1."""
    di = d_mm - 2 * t_mm
    return 1000 * 4 * d_mm / (d_mm**2 - di**2)


def main():
    k = calibrar()
    print(f"kappa calibrado (R60, 1003 um, 85 m-1, {THETA_REF:.0f} C): {k:.4e}")
    # Verificacion cruzada con R90 de CYPE (si fuese a 85 m-1)
    c = CYPE["R90"]
    T90 = temp_acero(c["av"], c["dft"], k, 90)
    print(f"Chequeo: con 2223 um y 85 m-1 el acero llega a {T90:.0f} C a los 90 min "
          f"(si fuese ~{THETA_REF:.0f} C, el R90 de CYPE usa 85 m-1)\n")

    print("A/V del tubo (solo ejemplos geometricos; espesores de pared NO son del proveedor)")
    for d, t in [(60, 3), (76, 3), (90, 3), (114, 4), (114, 6)]:
        print(f"  Ø{d}x{t}: {av_tubo(d, t):6.0f} m-1")
    print()

    area = 60000.0   # m2 de acero, supuesto del autor
    print(f"DFT indicativo y costo, A/V = 345 m-1, {area:,.0f} m2 de acero")
    print(f"{'mu':>5} {'theta_cr':>9} {'R':>5} {'DFT um':>9} {'COP/m2':>10} {'MM COP total':>13}")
    for mu in (0.7, 0.5, 0.3):
        th = theta_cr(mu)
        for R in (30, 60, 90, 120):
            d = dft_requerido(345, R, th, k)
            if math.isinf(d):
                print(f"{mu:5.1f} {th:9.0f} {R:5d}  no alcanzable")
                continue
            p = d * COP_POR_UM
            print(f"{mu:5.1f} {th:9.0f} {R:5d} {d:9.0f} {p:10,.0f} {p*area/1e6:13,.0f}")
        print()

    print("Referencia a 85 m-1 (control del modelo), theta_cr =", THETA_REF)
    for R in (30, 60, 90):
        d = dft_requerido(85, R, THETA_REF, k)
        print(f"  R{R}: {d:6.0f} um  ->  {d*COP_POR_UM:9,.0f} COP/m2")


if __name__ == "__main__":
    main()
