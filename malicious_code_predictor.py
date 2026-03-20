import zipfile, os, csv, gc
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from striprtf.striprtf import rtf_to_text
import chardet
                
def readZip(filename, dict):
    f = zipfile.ZipFile(filename)
    
    namelist = f.namelist()
    for name in namelist:
        if name.endswith("labels"):
            continue
        try:
            content = f.read(name)
            encoding = chardet.detect(content)['encoding']
            decoded_content = content.decode(encoding)
            text = rtf_to_text(decoded_content)
            dict['texts'].append(text)
        except:
            dict['texts'].append("Malware")

def main(train, test):
    global trainingFeatures
    
    print("Reading training data")
    readZip(train, trainingFeatures)
    print("Reading testing data")
    readZip(test, testingFeatures)
    print("Data extracted from zips.")
    
    tfidfVectorizerText = TfidfVectorizer()
    
    xTrain = tfidfVectorizerText.fit_transform(trainingFeatures['texts'])
    
    classifier = LogisticRegression()
    classifier.fit(xTrain, trainingFeatures['labels'])
    
    del trainingFeatures
    del xTrain
    
    gc.collect()
    
    print("Classifier trained")
    
    xTest = tfidfVectorizerText.transform(testingFeatures['texts'])
    
    print("Testing data vectorized")
    
    
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
    "texts" : [],
    "labels" : []
}

testingFeatures = {
    "names" : [],
    "texts" : [],
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