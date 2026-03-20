import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest
from scapy.all import rdpcap, IP, TCP

def extraer_sesiones(pcap_file):
    paquetes = rdpcap(pcap_file)
    sesiones = {}
    
    for paquete in paquetes:
        if paquete.haslayer(TCP) and paquete[TCP].dport == 21:
            sesion = (paquete[IP].src, paquete[IP].dst, paquete[TCP].sport, paquete[TCP].dport)
            if sesion not in sesiones:
                sesiones[sesion] = []
            sesiones[sesion].append(paquete)
    
    return sesiones

def caracteristicas_sesion(sesion, sesiones_dict):
    # Extract features for each session
    num_paquetes = len(sesiones_dict[sesion])
    duracion = max(p.time for p in sesiones_dict[sesion]) - min(p.time for p in sesiones_dict[sesion])
    tamaño_total = sum(len(p) for p in sesiones_dict[sesion])
    return [f'{sesion[0]}:{sesion[2]}', sesion[1], num_paquetes, duracion, tamaño_total]

# Extract sessions
sesiones_dict = extraer_sesiones('nids-test.pcap')
caracteristicas = [caracteristicas_sesion(sesion, sesiones_dict) for sesion in sesiones_dict]

# Create dataframe with features
df_caracteristicas = pd.DataFrame(caracteristicas, columns=['ip_origen', 'ip_destino', 'num_paquetes', 'duracion', 'tamaño_total'])

# Split IP and features for training
direcciones_ip = df_caracteristicas[['ip_origen', 'ip_destino']]
datos_modelo = df_caracteristicas.drop(columns=['ip_origen', 'ip_destino'])

# Normalize features
scaler = MinMaxScaler()
datos_normalizados = scaler.fit_transform(datos_modelo)

# Create and train Isolation Forest Model
modelo_isolation_forest = IsolationForest(n_estimators=300, contamination='auto', random_state=29)
modelo_isolation_forest.fit(datos_normalizados)

# Do anomalies prediction
predicciones = modelo_isolation_forest.predict(datos_normalizados)

# Transform predictions into 0 and 1
predicciones = [1 if p == -1 else 0 for p in predicciones]

# Add predictions in dataframe
direcciones_ip['anomalia'] = predicciones

direcciones_ip['conexion'] = direcciones_ip['ip_origen'] + "->" + direcciones_ip['ip_destino'] + ":21"
resultado_csv = direcciones_ip[['conexion', 'anomalia']]

# Save CSV
resultado_csv.to_csv('output.csv', header=False, index=False, sep=';')
