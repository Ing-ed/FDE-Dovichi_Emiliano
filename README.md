# Motor LLM Base y Validación Estructurada - Control de Gastos

Motor de procesamiento y extracción estructurada de comprobantes de gastos a partir de imágenes, implementando validación de esquemas con Pydantic y un flujo interactivo de confirmación humana (*Human-in-the-loop*).

---

## 📋 Descripción del Caso

El sistema actúa como un agente inteligente de OCR y análisis. Recibe como entrada una imagen de un ticket o comprobante de gasto (o una entrada manual de texto) y devuelve la información extraída y normalizada (comercio, monto total, moneda, categoría y nivel de confianza), junto con un mensaje claro para que el usuario confirme o corrija los datos antes de persistirlos.

---

## 🛠️ Requisitos Previos

- **Python:** 3.10 o superior
- **API Key:** Cuenta activa en OpenAI (o Anthropic) con acceso a modelos multimodales (ej. `gpt-4o` o `gpt-4o-mini`).

---

## ⚙️ Instalación y Configuración

1. **Clonar el repositorio y situarse en la etiqueta de la entrega:**
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd <NOMBRE_DEL_REPO>
   git checkout pe2
