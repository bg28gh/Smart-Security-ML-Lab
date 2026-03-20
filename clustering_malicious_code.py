import zipfile, csv
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.metrics import adjusted_rand_score
import pefile
import glob

def decoder(name, z):
    for encoder in ['utf-8', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-32']:
        try:
            return z.read(name).decode(encoder)
        except:
            continue
    return z.read(name)

# Function to read files from a zip archive
def readZip(zip_file_path):
    global Y
    global names
    files = []
    f = zipfile.ZipFile(zip_file_path)
    for name in f.namelist():
        if name.endswith("labels"):
            continue
        files.append(name)
        Y.append(name[-1])
        names.append(name)
    return files

# Function to extract features from code
def extract_features(file_paths):
    # You can customize this function based on the characteristics of your code
    # Here, we use a simple TF-IDF representation
    # Agregar codigo ofuscado, label 4, POPEN, .exe
    # Descargar, Ejecutar, /tmp /var/tmp, $url, $sfe label 3 NO TIENE LA PALABRA WEB
    # IO::Socket::INET , comandos IRC, LFI/RFI, label 2 KEYWORD: IRC_SOCKET , DOWNLOAD .exe, PRIVMSG
    # Muchos strings label 1, REMOTE, DATE, PRIVMSG
    
    entrypoints = extract_entrypoints(file_paths)
    features = []
    for file_features in entrypoints:
        try:
            # Convertir las características de cadena a números antes de combinarlas
            file_features = [int(feature, 16) for feature in file_features]
            features.append(file_features)
        except ValueError as ve:
            print(f"Error al convertir características a números: {ve}")
            features.append([0, 0])  # Manejar el error asignando un valor por defecto

    # Convertir la lista de listas a un array de NumPy
    features = np.array(features, dtype=np.int64)
    return features
    

def extract_entrypoints(file_paths):
    features = []
    for file in file_paths:
        try:
            fileFeatures = []
            archivo_pe = pefile.PE(file, fast_load=True)
            fileFeatures.append(hex(archivo_pe.OPTIONAL_HEADER.SizeOfHeapReserve))
            fileFeatures.append(hex(archivo_pe.OPTIONAL_HEADER.SizeOfInitializedData))
            fileFeatures.append(hex(archivo_pe.OPTIONAL_HEADER.MajorLinkerVersion))
            
            features.append(fileFeatures)

        except Exception as e:
            print(f"Error al analizar el archivo PE ({os.path.basename(file)}): {e}")
            features.append(['0', '0', '0'])
            
    return features

# Set the path to your zip file
zip_file_path = 'training/training.zip'
Y = []
names = []

# Read files from the zip archive and extract features
code_files = readZip(zip_file_path)
features = extract_features(code_files)

min_samples = 5
eps = 0.5
    
def perform_clustering(zip_file_path, eps, min_samples):
    global Y
    global names
    
    # Apply DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(features)

    result = []
    cluster_counts = {}
    
    for i, prediction in enumerate(labels):
        result.append(f"{names[i]};{prediction}")
        
        # Contar archivos por clúster
        if prediction in cluster_counts:
            cluster_counts[prediction] += 1
        else:
            cluster_counts[prediction] = 1
            
    csvFile = "output.csv"
    with open(csvFile, mode = 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for line in result:
            values = line.split(";")
            writer.writerow(values)
    print("CSV written.")
    
    silhouette_avg = silhouette_score(features, labels)
    print(f"Silhouette Score: {silhouette_avg}")
    
    # Print cluster assignment for each file
    unique_labels = set(labels)
    num_clusters = len(unique_labels) - (1 if -1 in labels else 0)  # Resta 1 si hay puntos etiquetados como ruido (-1)
        
    print(f"Número de Clústeres: {num_clusters}")
    print(f"Etiquetas de Clústeres: {unique_labels}")
    
    # Calculate ARI (Adjusted Rand Index)
    ari = adjusted_rand_score(Y, labels)
    print(f"Adjusted Rand Index (ARI): {ari}")
    
    print("Número de archivos por clúster:")
    for cluster, count in cluster_counts.items():
        print(f"Clúster {cluster}: {count} archivos")

# Example usage
perform_clustering(zip_file_path, eps, min_samples)
