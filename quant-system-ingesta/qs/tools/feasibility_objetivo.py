"""¿QUÉ HACE FALTA PARA EL OBJETIVO DEL PROYECTO? — la cuenta que nunca se hizo.

**Por qué existe.** El proyecto nació para construir un bot que aportara **100-200 €/mes** al sueldo
del propietario. Seis meses midiendo markouts en puntos básicos, y ni una sola vez se tradujeron a
euros, a rotación ni a cuota de volumen. Esto debería haber sido la PRIMERA línea del programa, no
la última: si el objetivo exigiera un edge diez veces mayor que nada de lo medible, se sabría en una
tarde y no en seis meses.

**Qué contesta, y qué no.** Contesta cuánto nocional, cuántos fills y qué cuota del volumen del
símbolo harían falta para un objetivo dado, a cada nivel de edge NETO. NO dice que ese edge exista
—el único candidato positivo del programa quedó DESTRUIDO el 2026-08-24— ni que sea capturable: eso
depende de dos agujeros que nadie ha medido y que el bloque final nombra.

**Regla cero:** aquí solo hay conteos, nocional y aritmética. Ningún markout, media, signo ni t.

    python tools/feasibility_objetivo.py
"""
import sys

# --- INSUMOS. Los MEDIDOS llevan su procedencia; los SUPUESTOS van declarados como tales. ---
LIT_NOCIONAL_DIA = 26_698_658   # MEDIDO 2026-08-25 sobre el archivo propio del colector (4 h)
PRINT_MEDIO_USD = 253.0         # MEDIDO en la misma pasada
FX_USD_POR_EUR = 1.08           # SUPUESTO, aproximado y declarado
DIAS_ANO = 365                  # cripto opera 365 d/año
FEE_TAKER_BINANCE_BPS = 4.0     # SUPUESTO (~0,04 % futuros; menor con VIP/BNB)
NIVEL_MEDIDO_BPS = 12.0         # MEDIDO: componente antisimétrico Lighter-vs-Binance, BRUTO


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    print("=" * 90)
    print("QUÉ HACE FALTA PARA EL OBJETIVO — insumos medidos, aritmética explícita")
    print("=" * 90)
    print(f"  LIT mueve ${LIT_NOCIONAL_DIA:,.0f}/día · print medio ${PRINT_MEDIO_USD:,.0f}  [MEDIDO]")
    print(f"  {DIAS_ANO} días/año · {FX_USD_POR_EUR} USD/EUR  [supuesto declarado]\n")
    for eur in (100, 150, 200):
        print(f"  {eur:>3} EUR/mes = {eur * 12:,} EUR/año = ${eur * 12 / DIAS_ANO * FX_USD_POR_EUR:,.2f}/día")

    obj_usd_dia = 150 * 12 / DIAS_ANO * FX_USD_POR_EUR
    print(f"\n  Para el objetivo CENTRAL de 150 EUR/mes (${obj_usd_dia:.2f}/día):\n")
    print(f"  {'edge NETO':>10} | {'nocional/día':>13} | {'cuota de LIT':>13} | {'fills/día':>9} | {'fills/h':>8}")
    print("  " + "-" * 66)
    for e in (12, 8, 6, 4, 2, 1, 0.5, 0.25):
        v = obj_usd_dia / (e / 10_000)
        print(f"  {e:>10} | {v:>13,.0f} | {v / LIT_NOCIONAL_DIA:>12.3%} | "
              f"{v / PRINT_MEDIO_USD:>9,.0f} | {v / PRINT_MEDIO_USD / 24:>8,.1f}")

    print("\n" + "=" * 90)
    print("LA AMBICIÓN: profundidad vs anchura — solo una de las dos escala")
    print("=" * 90)
    print("\n  VÍA A — apretar MÁS un solo símbolo (a 2 bps netos). La cuota es el precio:")
    for eur in (150, 500, 1000, 2000):
        v = eur * 12 / DIAS_ANO * FX_USD_POR_EUR / 0.0002
        print(f"    {eur:>5} EUR/mes -> ${v:>10,.0f}/día = {v / LIT_NOCIONAL_DIA:>6.2%} del símbolo "
              f"· {v / PRINT_MEDIO_USD / 24:>5,.0f} fills/h")
    print("    Al 1,3 % del volumen ya se compite de frente con los MM colocados: hay techo de cola.")

    print("\n  VÍA B — la MISMA dificultad por símbolo (0,1 % de cuota), en N símbolos:")
    print(f"    {'símbolos':>9} | {'a 2 bps':>10} | {'a 4 bps':>10} | {'a 8 bps':>10}")
    base = LIT_NOCIONAL_DIA * 0.001
    for n in (1, 3, 5, 10, 20):
        fila = [base * n * (e / 10_000) * DIAS_ANO / 12 / FX_USD_POR_EUR for e in (2, 4, 8)]
        print(f"    {n:>9} | {fila[0]:>9,.0f}€ | {fila[1]:>9,.0f}€ | {fila[2]:>9,.0f}€")
    print("    (asume símbolos de volumen comparable a LIT; los hay mayores y menores)")
    print("\n  La ambición no pide un edge MAYOR: pide ANCHURA. Y la anchura es lo que hace un")
    print("  laboratorio de cribado — la máquina que ya está construida.")

    print("\n" + "=" * 90)
    print("LO QUE SE COME EL EDGE — y los dos agujeros que deciden si hay negocio")
    print("=" * 90)
    neto = NIVEL_MEDIDO_BPS
    print(f"  nivel MEDIDO (bruto, antisimétrico Lighter-vs-Binance)      {neto:+7.2f} bps")
    neto -= FEE_TAKER_BINANCE_BPS
    print(f"  fee taker Binance (segunda pata, supuesto)                  {-FEE_TAKER_BINANCE_BPS:+7.2f} bps"
          f"   -> {neto:+6.2f}")
    print(f"  fee Lighter (0/0 declarado)                                    +0.00 bps   -> {neto:+6.2f}")
    print("  slippage cruzando la segunda pata                              ?      <- SIN MEDIR")
    print("  selección adversa (el flujo es INFORMADO)                       ?      <- SIN MEDIR")
    print(f"\n  Suelo conocido antes de los dos agujeros: {neto:+.2f} bps"
          f"  ⇒ harían falta ${obj_usd_dia / (neto / 10_000):,.0f}/día.")
    print("  Con 1 bp neto: "
          f"${obj_usd_dia / 0.0001:,.0f}/día. Con 0, no hay negocio.")
    print("\n  LOS DOS AGUJEROS SON LA PREGUNTA ENTERA. Ninguno se ha medido nunca, y ambos")
    print("  dependen de la re-derivación desde crudos (docs/ENCARGO_REDERIVACION_I5.md).")
    print("\n  ADVERTENCIA que va delante de cualquier cifra de arriba: un basis cross-venue son DOS")
    print("  PATAS. Monetizarlo exige ejecutar en Binance, y eso no está medido en ningún sitio —")
    print("  ni latencia, ni capacidad, ni si el hueco sobrevive a los costes de las dos patas.")
    print("  Esto es una HIPÓTESIS NUEVA que necesita su propio pre-registro con muerte esperada,")
    print("  no el hallazgo destruido reciclado con otro nombre.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
