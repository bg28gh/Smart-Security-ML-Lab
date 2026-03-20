import zipfile
import os
import pyshark
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import csv

def readZip(fileName):
    global labels
    global features
    global names
    z = zipfile.ZipFile(fileName)
    z.extractall()
    longitudNamelist = len(z.namelist())
    print(f"Total de archivos {longitudNamelist}")
    for i, name in enumerate(z.namelist()):
        if name.endswith(".pcap"):
            names.append(os.path.basename(name))
            print(f"Archivos analizados {i}/{longitudNamelist}")
            labels.append(os.path.basename(name).split("_")[0])
            features.append(extraer_caracteristicas(name))

def extraer_caracteristicas(archivo_pcap):
    cap = pyshark.FileCapture(archivo_pcap, only_summaries=False, use_json=True)

    tiempos = []
    total_bytes = 0
    csent = 0
    crec = 0
    cpackets = 0
    acks_duplicados = Counter()
    tamanos_paquetes = []
    length_ips = []
    
    for paquete in cap:
        total_bytes += int(paquete.length)
        tiempos.append(float(paquete.sniff_timestamp))
        cpackets = cpackets + 1
        notTor = paquete.length != 609
        tamano = len(paquete)
        tamanos_paquetes.append(tamano)
        ncapas = len(paquete.layers)
        try:
            length_ip = len(paquete.ip.len)
            length_ips.append(length_ip)
        
            isSender = paquete.ip.src == '134.169.109.25'
            if isSender and notTor and 'tls' in paquete:
                csent = csent + 1
            else: 
                if isSender != True and notTor != 609 and 'tls' in paquete:
                    crec = crec + 1
            # Contar el número de ACK duplicados
            if 'ack' in paquete and paquete['ack'] in acks_duplicados:
                acks_duplicados[paquete['ack']] += 1
            else:
                acks_duplicados[paquete['ack']] = 1
        except: continue
        
    desviacion_estandar_tamano = np.std(tamanos_paquetes) if tamanos_paquetes else 0
    num_acks_duplicados = sum(1 for count in acks_duplicados.values() if count > 1)
    tamano_maximo = max(tamanos_paquetes, default=0)
    tamano_minimo = min(tamanos_paquetes, default=0)
    IP_maximo = max(length_ips, default=0)
    IP_minimo = min(length_ips, default=0)
    cap.close()
    
    return {
        "total_paquetes": cpackets,
        "sentPackets": csent, 
        "receivedPackets": crec,
        "num_acks_duplicados": num_acks_duplicados,
        "desviacion_estandar_tamano": desviacion_estandar_tamano,
        "tamano_maximo": tamano_maximo,
        "tamano_minimo": tamano_minimo,
        "total_bytes": total_bytes,
        "IP_maximo": IP_maximo,
        "IP_minimo": IP_minimo,
        "ncapas": ncapas
    }

labels = []
features = []
names = []
train_files_censored = ['training1.zip']
train_files_uncensored = ['training2.zip']

for train_file in train_files_censored:
    readZip(train_file)

for train_file in train_files_uncensored:
    readZip(train_file)

# Convertir las características y las etiquetas en DataFrames de Pandas
df_features = pd.DataFrame(features)
serie_labels = pd.Series(labels)

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(df_features, serie_labels, test_size=0.3, random_state=42)

# Crear y entrenar el modelo RandomForest
modelo_rf = RandomForestClassifier(max_features=57, n_estimators=30)
modelo_rf.fit(X_train, y_train)

# Hacer predicciones y evaluar
predicciones = modelo_rf.predict(X_test)

matriz_confusion = confusion_matrix(y_test, predicciones)
print(matriz_confusion)

csvFile = "output.csv"
with open(csvFile, mode='w', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(["Nombre de Archivo", "Prediccion"])
    for i, prediccion in enumerate(predicciones):
        name = names[i]
        values = [name, prediccion]
        writer.writerow(values)
print("CSV written.")
print(f"Precisión del modelo: {accuracy_score(y_test, predicciones)}")
