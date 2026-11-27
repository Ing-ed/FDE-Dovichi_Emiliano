from src.motor import ProcesarComprobante

casos_prueba = [
    {"nombre": "1. Ticket Almuerzo Claro", "ruta": "test_data/ticket_almuerzo.jpg", "mime": "image/jpeg"},
    {"nombre": "2. Factura Combustible", "ruta": "test_data/factura_nafta.png", "mime": "image/png"},
    {"nombre": "3. Recibo Hospedaje", "ruta": "test_data/hotel.jpg", "mime": "image/jpeg"},
    {"nombre": "4. Ticket Borroso / Ilegible", "ruta": "test_data/ticket_borroso.jpg", "mime": "image/jpeg"},
    {"nombre": "5. Imagen Fuera de Tema", "ruta": "test_data/foto_paisaje.jpg", "mime": "image/jpeg"}
]

if __name__ == "__main__":
    resultados = []
    print("=" * 60)
    print("INICIANDO EVALUACIÓN DE CASOS DE PRUEBA")
    print("=" * 60)

    for caso in casos_prueba:
        print(f"\nEjecutando: {caso['nombre']}...")
        res = ProcesarComprobante(caso["ruta"], caso["mime"])
        resultados.append(res)
        print(res["salida"])

    exitos = [r for r in resultados if r.get("status") == "OK"]
    if exitos:
        prom_lat = sum(r["latencia_ms"] for r in exitos) / len(exitos)
        prom_tokens = sum(r["total_tokens"] for r in exitos) / len(exitos)
        prom_tok_in = sum(r["in_tok"] for r in exitos) / len(exitos)
        prom_costo = sum(r["costo"] for r in exitos) / len(exitos)
        costo = sum(r["costo"] for r in exitos)
        print("\n" + "=" * 60)
        print("MÉTRICAS PROMEDIO (Para la tabla del PDF):")
        print(f"Latencia promedio: {prom_lat:.2f} ms")
        print(f"Tokens promedio: {prom_tokens:.2f}")
        print(f"Costo promedio: ${prom_costo:.6f} USD")
        print(f"Costo total: ${costo}")
        print(f"in_toks: {prom_tok_in}")
        print("=" * 60)
