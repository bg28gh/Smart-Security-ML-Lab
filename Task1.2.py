import zipfile, csv, os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
import re

# Function to read the emails and check / handle the codification
def emailDecoder(name, z):
    for encoder in ['utf-8', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-32']:
        try:
            return z.read(name).decode(encoder)
        except:
            continue
    return z.read(name)

# Function to extract additional features from emails
def extract_features(content):
    num_letters = len(content)
    words = content.split()
    unique_words = len(set(words))
    num_uppercase = sum(1 for char in content if char.isupper())
    num_links = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content))
    return num_letters, (unique_words / len(words)) * 100, num_uppercase, num_links

# Read zip content and export to dictionary
def readZip(fileName):
    z = zipfile.ZipFile(fileName)
    emails = []
    labels = []
    names = []
    num_letters_list = []
    unique_words_percent_list = []
    num_uppercase_list = []
    num_links_list = []
    
    for name in z.namelist():
        if name.endswith("labels"):
            continue
        content = emailDecoder(name, z)
        content = content.replace('\r', '')  # Remove carriage return
        
        num_letters, unique_words_percent, num_uppercase, num_links = extract_features(content)
        
        emails.append(content)
        try:
            label = int(name[-1])
            labels.append(label)
        except:
            labels.append(name[-1])
        names.append(name)
        num_letters_list.append(num_letters)
        unique_words_percent_list.append(unique_words_percent)
        num_uppercase_list.append(num_uppercase)
        num_links_list.append(num_links)
    
    dictionary = {
        "emails": emails,
        "labels": labels,
        "names": names,
        "num_letters": num_letters_list,
        "unique_words_percent": unique_words_percent_list,
        "num_uppercase": num_uppercase_list,
        "num_links": num_links_list
    }
    return dictionary

# Resto del código sigue igual

def main(train, test):
    # Resto del código sigue igual
    trainData = readZip(train)
    testData = readZip(test)
    print("Data extracted from zips.")
    
    # TF-IDF Matrix from reading emails
    vectorizer = TfidfVectorizer()
    trainingContent = vectorizer.fit_transform(trainData['emails'])
    testingContent = vectorizer.transform(testData['emails'])
    print("Data vectorized.")

    # Definir los valores posibles de alpha para MultinomialNB
    paramGrid = {'alpha': [0.1, 0.5, 1.0, 2.0]}

    # Crear el objeto GridSearchCV
    gridSearch = GridSearchCV(MultinomialNB(), paramGrid, cv=5)

    # Realizar la búsqueda en cuadrícula en los datos de entrenamiento
    gridSearch.fit(trainingContent, trainData['labels'])

    # Obtener los mejores hiperparámetros
    bestAlpha = gridSearch.best_params_['alpha']
    
    # Train a text classifier
    clf = MultinomialNB(alpha=bestAlpha)
    clf.fit(trainingContent, trainData['labels'])
    
    # Label prediction
    predictions = clf.predict(testingContent)
    print("Prediction obtained.")
    result = []
    
    for i, prediction in enumerate(predictions):
        result.append(f"{testData['names'][i]};{prediction}")
    csvFile = "output.csv"
    with open(csvFile, mode = 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for line in result:
            values = line.split(";")
            writer.writerow(values)
    print("CSV written.")
while True:
    training = input("Please provide the path to the training .zip: ")
    if os.path.isfile(training) & (training.endswith(".zip")):
        break
    else:
        print("The path is not valid")
        
while True:
    test = input("Please provide the path to the testing .zip: ")
    if os.path.isfile(test) & (test.endswith(".zip")):
        break
    else:
        print("The path is not valid")
        
main(training, test)