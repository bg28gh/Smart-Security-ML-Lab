import zipfile, fitz, os, csv, gc
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

def getText(pdfFile):
    text = ""
    for page in pdfFile:
        text += page.get_text()
    return text

def extractFeatures(pdfFile):
    metadata = pdfFile.metadata
    authors = metadata['author']
    producer = metadata['producer']
    pdfText = getText(pdfFile).replace("\n", " ")
    
    if (((authors == "Anonymus" or authors == "Anonym") or (authors == "anonym" or authors == "anonymus")) or (authors == "" or authors == " ")):
        authors = 0
    else:
        authors = authors.count(",") + 1
    
    return (producer, pdfText, authors)

def parsePDF(pdfName, dict):
    try:
        dict['names'].append(pdfName)
        dict['labels'].append(pdfName[-1])
        doc = fitz.open(pdfName)
        features = extractFeatures(doc)
        dict['producers'].append(features[0])
        dict['texts'].append(features[1])
        dict['authors'].append(features[2])
    except:
        dict['producers'].append('Malware')
        dict['texts'].append('Malware')
        dict['authors'].append(-1)
            
def readZip(filename, dict):
    f = zipfile.ZipFile(filename)
    f.extractall()
    
    namelist = f.namelist()
    for name in namelist:
        if name.endswith("labels"):
            continue
        parsePDF(name, dict)

def main(train, test):
    global trainingFeatures
    
    print("Reading training data")
    readZip(train, trainingFeatures)
    print("Reading testing data")
    readZip(test, testingFeatures)
    print("Data extracted from zips.")
    
    tfidfVectorizerProducers = TfidfVectorizer()
    tfidfVectorizerText = TfidfVectorizer()
    
    tfidfProducers = tfidfVectorizerProducers.fit_transform(trainingFeatures['producers'])
    tfidfText = tfidfVectorizerText.fit_transform(trainingFeatures['texts'])
    
    print("Training data vectorized")
    
    xTrain = np.hstack((tfidfProducers.toarray(), tfidfText.toarray(), np.array(trainingFeatures['authors'])[:, np.newaxis]))
    
    print("Training data combined")
    
    classifier = LogisticRegression()
    classifier.fit(xTrain, trainingFeatures['labels'])
    
    del trainingFeatures
    del xTrain
    
    gc.collect()
    
    print("Classifier trained")
    
    tfidfProducers = tfidfVectorizerProducers.transform(testingFeatures['producers'])
    tfidfText = tfidfVectorizerText.transform(testingFeatures['texts'])
    
    print("Testing data vectorized")
    
    xTest = np.hstack((tfidfProducers.toarray(), tfidfText.toarray(), np.array(testingFeatures['authors'])[:, np.newaxis]))
    
    predictions = classifier.predict(xTest)
    print("Prediction obtained.")
    
    result = []
    
    for i, prediction in enumerate(predictions):
        result.append(f"{testingFeatures['names'][i]};{prediction}")
    csvFile = "output.csv"
    with open(csvFile, mode = 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for line in result:
            values = line.split(";")
            writer.writerow(values)
    print("CSV written.")

trainingFeatures = {
    "names" : [],
    "authors" : [],
    "texts" : [],
    "producers" : [],
    "labels" : []
}

testingFeatures = {
    "names" : [],
    "authors" : [],
    "texts" : [],
    "producers" : [],
    "labels" : []
}

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