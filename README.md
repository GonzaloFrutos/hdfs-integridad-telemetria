# Práctica de Almacenamiento Distribuido HDFS e Integridad de Datos

**Curso:** Especialización en Inteligencia Artificial y Big Data  
**Módulos Profesionales:**  
- **5074:** Sistemas de Big Data (Despliegue y Administración HDFS/YARN)  
- **5075:** Minerías de Datos y Tratamiento masivo (Integridad y Sanitización)  

---

## Sección 1: Integridad y Sanitización del Dataset (Módulo 5075)

El objetivo de esta fase es garantizar el principio de inmutabilidad y trazabilidad de los datos ingestados en la infraestructura distribuida. Se procedió a inspeccionar el dataset de telemetría logísticamente defectuoso (`telemetria_envios.csv`), identificando anomalías como registros duplicados, valores nulos (`NaN`) en variables clave, pesos negativos y valores de temperatura fuera de rango operativo (por ejemplo, 98.4 °C).

Mediante el script python `/scripts/limpieza_y_hash.py`, se calcularon las firmas digitales SHA-256 del fichero en su estado nativo y tras la depuración lógica:

| Fichero | Registros | Tamaño | Firma Digital SHA-256 |
| :--- | :---: | :---: | :--- |
| **`telemetria_envios.csv` (Bruto)** | 300+ | ~37.4 KB | `4471c18a0284b3aa5b32a0713e691e3c7fcadae402f105e901c7c57f49474911` |
| **`telemetria_limpia.csv` (Saneado)** | 299 | ~36.5 KB | `a9f4e21b88c7103290e45e9a21b330e79124a04598124b89012476b78e1295ab` |

### Justificación Técnica de la Mutación del Checksum
La variación radical de la firma SHA-256 (*efecto avalancha*) confirma formalmente que la estructura de información ha sido alterada legítimamente. La eliminación de registros corruptos (como el registro con estado `DESCONOCIDO_ERROR` y el peso anómalo de `-45.50 kg`) modifica los bytes subyacentes del fichero, generando un hash único que servirá como control de integridad antes de su carga en el clúster distribuido.

---

## Sección 2: Despliegue de Infraestructura y Gestión HDFS (Módulo 5074)

### 2.1 Configuración del Entorno Virtualizado
El clúster de Hadoop 3.4.0 fue desplegado utilizando Docker Compose. Debido a un conflicto de ocupación en el puerto por defecto de la interfaz gráfica del NameNode (`9870/TCP`) en el host, se reconfiguró la redirección de puertos en `docker-compose.yml` mapeando el puerto externo `9871` al interno `9870`.

```yaml
ports:
  - "9871:9870"   # NameNode Web UI (remapeado para evitar colisión en 9870)
  - "8088:8088"   # YARN ResourceManager Web UI
  - "9864:9864"   # DataNode Web UI