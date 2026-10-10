#!/usr/bin/env python3
"""
Modelo matematico del espesor (DFT) y costo de intumescente en tubos de acero.

1. BALANCE DE CALOR (EN 1993-1-2, ec. 4.27 con masa termica del recubrimiento nula)
       dTs/dt = r (Tg - Ts) / (rho ca(Ts)),     r = (A/V) / R,     R = kappa * DFT
   Tg = 20 + 345 log10(8 t + 1)  (ISO 834, t en min); ca(T) segun EN 1993-1-2 (3.4.1.2).

2. INVARIANZA DE ESCALA (se demuestra al sustituir): la trayectoria Ts(t) depende solo de r.
   Sea r*(t, theta) la unica r con Ts(t) = theta. Entonces
       DFT = (A/V) / (kappa r*(t, theta))     => DFT es EXACTAMENTE proporcional a A/V.
   Con calibracion en un punto (A0, DFT0, t0, theta0):
       DFT(A/V, t, theta) = DFT0 (A/V)/A0 * r*(t0, theta0) / r*(t, theta)

3. COSTO AFIN:  c(DFT) = c0 + c1 DFT   [COP/m2], c1 de material y c0 de mano de obra fija.
   Total para una poblacion de miembros:  C = sum_i A_i [c0 + c1 G (A/V)_i],  G = DFT/(A/V).

4. INCERTIDUMBRE: Monte Carlo sobre theta_ref, mu, exponente temporal p, c0 y c1.

Todo es un MODELO. El espesor certificado sale de ensayos del fabricante (EN 13381-8, ASTM E119).
"""
import math
import numpy as np

RHO = 7850.0
TRM = 3273.49                     # COP/USD, TRM oficial del 5-oct-2026 (portafolio.co)
FT2_A_M2 = 10.7639
CYPE = {"R60": (1003.0, 136022.04), "R90": (2223.0, 297314.00)}   # (DFT um, COP/m2) a 85 m-1 (R90: A/V no visible)
A_CAL, T_CAL, THETA_CAL = 85.0, 60.0, 500.0      # calibracion; THETA_CAL es SUPUESTO
TUBOS = [(60, 2.5), (73, 2.5), (90, 3.0), (114, 3.0)]   # (diametro mm, espesor mm) ASUMIDOS
L_TUBO = 116000.0                 # m de tubo, estimacion del autor (modulo 3,20 m, ~50.000 m2)
# mezcla ASUMIDA: igual longitud de cada diametro
_a = [math.pi * d / 1000 for d, t in TUBOS]
A_M = sum(_a) / len(_a)                                           # m2 de superficie por m de tubo
Q_M = sum(a * av_ for a, av_ in zip(_a, [1000*4*d/(d**2-(d-2*t)**2) for d, t in TUBOS])) / len(_a) / 345.0
AREA_ACERO = L_TUBO * A_M         # m2 de superficie de tubo (sin nudos ni tornillos)


def total_MM(c0, c1, dft345):
    """Costo total (MM COP) de la poblacion de tubos: L [c0 A_m + c1 DFT345 Q],  Q = media(a_i (A/V)_i/345)."""
    return L_TUBO * (c0 * A_M + c1 * dft345 * Q_M) / 1e6


# ---------------------------------------------------------------- fisica
def ca(T):
    T = np.asarray(T, dtype=float)
    return np.where(T < 600, 425 + 0.773 * T - 1.69e-3 * T**2 + 2.22e-6 * T**3,
           np.where(T < 735, 666 + 13002 / (738 - np.minimum(T, 737.9)),
           np.where(T < 900, 545 + 17820 / (np.maximum(T, 731.1) - 731), 650.0)))


def tgas(t_min):
    return 20 + 345 * np.log10(8 * t_min + 1)


def tabla_trayectorias(nk=400, tmax=240):
    """Ts(t) para nk valores de r (W/m3K), log-espaciados. Esquema semi-implicito, dt = 1 s."""
    r = np.logspace(0, 5.5, nk)
    Ts = np.full(nk, 20.0)
    snaps = np.empty((tmax + 1, nk))
    snaps[0] = Ts
    for s in range(tmax * 60):
        a = r / (RHO * ca(Ts))
        Ts = Ts + (tgas(s / 60.0) - Ts) * a / (1 + a)
        if (s + 1) % 60 == 0:
            snaps[(s + 1) // 60] = Ts
    return r, snaps


TAB = tabla_trayectorias()


def rstar(t_min, theta):
    """r* tal que el acero llega a theta (C) a los t_min min. t_min escalar, theta escalar o arreglo."""
    r, snaps = TAB
    i = int(math.floor(t_min)); f = t_min - i
    Ts_t = snaps[i] * (1 - f) + snaps[min(i + 1, snaps.shape[0] - 1)] * f
    return np.exp(np.interp(theta, Ts_t, np.log(r)))


def theta_cr(mu):
    mu = np.asarray(mu, dtype=float)
    return 39.19 * np.log(1 / (0.9674 * mu**3.833) - 1) + 482


def dft(av, t_min, theta, theta_ref=THETA_CAL):
    """DFT (um) por la formula de escala con calibracion CYPE R60 (1003 um, 85 m-1)."""
    d0 = CYPE["R60"][0]
    return d0 * (av / A_CAL) * rstar(T_CAL, theta_ref) / rstar(t_min, theta)


def av_tubo(d, t):
    di = d - 2 * t
    return 1000 * 4 * d / (d**2 - di**2)


# ---------------------------------------------------------------- costo
def cype_afin():
    (d1, p1), (d2, p2) = CYPE["R60"], CYPE["R90"]
    c1 = (p2 - p1) / (d2 - d1)
    return p1 - c1 * d1, c1


def us_material_c1(precio_gal=90.0, vs=0.65, perdida=0.30):
    """COP por (um m2) de solo material: 1 galon = 3785 m2 um al 100 % de solidos en volumen."""
    return precio_gal / (3785.0 * vs * (1 - perdida)) * TRM


def us_afin():
    """Ajuste por minimos cuadrados de la tabla de FlameOFF (USD/ft2 instalado vs DFT medio)."""
    d = np.array([1250.0, 1750.0, 2500.0])          # um (60, 90, 120 min), puntos medios
    c = np.array([6.5, 8.5, 10.0])                   # USD/ft2, puntos medios
    c1, c0 = np.polyfit(d, c, 1)
    return c0 * FT2_A_M2 * TRM, c1 * FT2_A_M2 * TRM  # (COP/m2, COP/um m2)


def main():
    print(f"r*(60 min, 500 C) = {rstar(60, 500):.1f} W/m3K")
    R_cal = A_CAL / rstar(T_CAL, THETA_CAL)
    print(f"R de calibracion = {R_cal:.4f} m2K/W  ->  conductividad equivalente sobre espesor seco "
          f"= {CYPE['R60'][0]*1e-6/R_cal:.4f} W/mK")

    print("\nG = DFT/(A/V)  [um por m-1],  mu = 0,5 (theta_cr = %.0f C)" % theta_cr(0.5))
    th = float(theta_cr(0.5))
    ts = [30, 60, 90, 120, 180]
    G = [dft(1.0, t, th) for t in ts]
    for t, g in zip(ts, G):
        print(f"  R{t:<4d} G = {g:6.2f}")
    n = np.polyfit(np.log(ts[:4]), np.log(G[:4]), 1)[0]
    print(f"  exponente local G ~ t^n, n = {n:.2f} (ajuste R30-R120)")
    p_cype = math.log(CYPE['R90'][0] / CYPE['R60'][0]) / math.log(1.5)
    print(f"  exponente implicito en CYPE (R60->R90, mismo A/V) = {p_cype:.2f}")

    print("\nElasticidades en R60, 345 m-1, mu 0,5:")
    base = dft(345, 60, th)
    print(f"  dlnDFT/dlnt     = {(math.log(dft(345,66,th))-math.log(dft(345,54,th)))/(math.log(66)-math.log(54)):.2f}")
    print(f"  dlnDFT/dlnA/V   = 1,00 (exacto)")
    print(f"  DFT por +50 C de theta_cr: {dft(345,60,th+50)-base:+.0f} um ({(dft(345,60,th+50)/base-1)*100:+.0f} %)")
    print(f"  DFT por +50 C de theta_ref: {dft(345,60,th,THETA_CAL+50)-base:+.0f} um "
          f"({(dft(345,60,th,THETA_CAL+50)/base-1)*100:+.0f} %)")

    c0y, c1y = cype_afin()
    c0u, c1u = us_afin()
    print(f"\nCosto afin CYPE:   c0 = {c0y:10,.0f} COP/m2   c1 = {c1y:6.1f} COP/(um m2)")
    print(f"Costo afin EE.UU.: c0 = {c0u:10,.0f} COP/m2   c1 = {c1u:6.1f} COP/(um m2)  (FlameOFF, TRM {TRM})")
    print(f"Material EE.UU. por fisica: c1 = {us_material_c1(90,1.0,0.2):.0f} a {us_material_c1(90,0.65,0.30):.0f} "
          f"COP/(um m2) (USD 90/gal, solidos 65-100 %, perdida 20-30 %)")

    print(f"\nPunto central: {L_TUBO:,.0f} m de tubo (mezcla de igual longitud) = {AREA_ACERO:,.0f} m2; mu = 0,5; DFT dado a 345 m-1 (MM COP)")
    p60 = float(dft(345, 60, th))
    p90 = p60 * 1.5**p_cype
    p90m = float(dft(345, 90, th))
    for nom, d in (("R60", p60), ("R90 (modelo)", p90m), ("R90 (empirico CYPE)", p90)):
        print(f"  {nom:20s} DFT {d:6.0f} um | CYPE afin {total_MM(c0y,c1y,d):8,.0f} | "
              f"EE.UU. afin {total_MM(c0u,c1u,d):8,.0f}")
    lo, hi = 10 * FT2_A_M2 * TRM, 30 * FT2_A_M2 * TRM
    print(f"  Banda EE.UU. generica USD 10-30/ft2 (Bahl): {lo*AREA_ACERO/1e6:,.0f} a {hi*AREA_ACERO/1e6:,.0f} MM, sin distinguir rating")

    # --------------------------------------------------- Monte Carlo
    rng = np.random.default_rng(1)
    N = 40000
    th_ref = rng.uniform(450, 550, N)
    mu = rng.triangular(0.3, 0.5, 0.8, N)
    thc = theta_cr(mu)
    p_mod = math.log(float(dft(1, 90, th)) / float(dft(1, 60, th))) / math.log(1.5)
    p = rng.uniform(p_mod, p_cype, N)
    c1 = rng.uniform(us_material_c1(90, 1.0, 0.2), us_material_c1(90, 0.65, 0.30), N)
    c0 = rng.uniform(c0y, c0u, N)
    d60 = CYPE["R60"][0] * (345 / A_CAL) * rstar(60, th_ref) / rstar(60, thc)
    d90 = d60 * 1.5**p
    print("\nMonte Carlo (N=%d): theta_ref~U(450,550), mu~Tri(0.3,0.5,0.8), p~U(%.2f,%.2f), "
          "c1~U(material EE.UU.), c0~U(CYPE, EE.UU.)" % (N, p_mod, p_cype))
    for nom, d in (("R60", d60), ("R90", d90)):
        tot = total_MM(c0, c1, d)
        q = np.percentile(tot, [10, 50, 90])
        qd = np.percentile(d, [10, 50, 90])
        print(f"  {nom}: DFT P10/P50/P90 = {qd[0]:.0f}/{qd[1]:.0f}/{qd[2]:.0f} um ; "
              f"costo total = {q[0]:,.0f} / {q[1]:,.0f} / {q[2]:,.0f} MM COP")
        # contribucion a la varianza: correlacion de rangos
        from math import sqrt
        def rank(x): return np.argsort(np.argsort(x))
        names = [("theta_ref", th_ref), ("mu", mu), ("p", p), ("c1", c1), ("c0", c0)]
        out = []
        for nme, v in names:
            rho = np.corrcoef(rank(v), rank(tot))[0, 1]
            out.append(f"{nme} {rho:+.2f}")
        print("     correlacion de rangos con el costo: " + ", ".join(out))

    print("\nTubos de la ficha del proveedor (A500 Gr. C). Espesores ASUMIDOS: Ø60 y Ø73 -> 2,5 mm; Ø90 y Ø114 -> 3,0 mm")
    print("(mu 0,5; costo afin CYPE y EE.UU. por metro de tubo, y por m2 de superficie)")
    for r_ in (60, 90):
        print(f"  R{r_}")
        for d, t in TUBOS:
            av = av_tubo(d, t)
            dd = float(dft(av, r_, th))
            area_m = math.pi * d / 1000
            cy = c0y + c1y * dd
            us = c0u + c1u * dd
            print(f"   Ø{d}x{t}: A/V {av:4.0f}  DFT {dd:6.0f} um | CYPE {cy:8,.0f} COP/m2 {cy*area_m:8,.0f} COP/m | "
                  f"EE.UU. {us:8,.0f} COP/m2 {us*area_m:8,.0f} COP/m")


if __name__ == "__main__":
    main()
