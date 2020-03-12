import os, codecs, math

class BayesText:

    def __init__(self, trainingdir, wordlist, ignoreBucket, mode):
        """This class implements a naive Bayes approach to text classification
        trainingdir is the training data. Each subdirectory of trainingdir is titled with the
        name of the classification category -- those subdirectories in turn contain the text files
        for that category.
        The stopwordlist is a list of words (one per line) will be removed before any counting takes
        place.
        if mode == 0: ignore wordlist
        if mode == 1: use it as stopwords
        if mode == 2: use only the words in wordlist to build classifier
        """
        self.vocabulary = {}
        self.prob = {}
        self.totals = {}
        self.stopwords = {}
        self.mode = mode
        self.ignoreBucket = ignoreBucket
        f = open(wordlist)
        for line in f:
            self.stopwords[line.strip()] = 1
        f.close()
        categories = os.listdir(trainingdir)
        #filter out files that are not directories
        self.categories = [filename for filename in categories if os.path.isdir(trainingdir + filename)]
        print("Counting ...")
        for category in self.categories:
            print('    ' + category)
            (self.prob[category], self.totals[category]) = self.train(trainingdir, category)
        # I am going to eliminate any word in the vocabulary that doesn't occur at least 3 times
        toDelete = []
        for word in self.vocabulary:
            if self.vocabulary[word] < 3:
                # mark word for deletion
                # can't delete now because you can't delete from a list you are currently
                # iterating over
                toDelete.append(word)
        # now delete
        for word in toDelete:
            del self.vocabulary[word]
        # now compute probabilities
        vocabLength = len(self.vocabulary)
        print("Computing probabilities:")
        for category in self.categories:
            print('    ' + category)
            denominator = self.totals[category] + vocabLength
            for word in self.vocabulary:
                if word in self.prob[category]:
                    count = self.prob[category][word]
                else:
                    count = 1
                self.prob[category][word] = (count + 1) / denominator
                    

    def train(self, trainingdir, category):
        """counts word occurrences for a particular category"""
        currentParentdir = trainingdir + category
        counts = {}
        total = 0
        for i in range(10):
            if i != self.ignoreBucket:
                #print("Processing Bucket %i" % i)
                currentdir = "%s/%i" % (currentParentdir, i)
                # ignore bucket
                files = os.listdir( currentdir)[:1000]
                for file in files:
                    #print(currentdir + '/' + file)
                    f = codecs.open(currentdir + '/' + file, 'r', 'iso8859-1')
                    for line in f:
                        tokens = line.split()
                        for token in tokens:
                            # get rid of punctuation and lowercase token
                            token = token.strip('\'".,?:-')
                            token = token.lower()
                            if self.mode == 1 and (token != '' and not token in self.stopwords):
                                self.vocabulary.setdefault(token, 0)
                                self.vocabulary[token] += 1
                                counts.setdefault(token, 0)
                                counts[token] += 1
                                total += 1
                            elif self.mode == 2 and (token != '' and token in self.stopwords):
                                self.vocabulary.setdefault(token, 0)
                                self.vocabulary[token] += 1
                                counts.setdefault(token, 0)
                                counts[token] += 1
                                total += 1
                            elif self.mode == 0 and token != '':
                                self.vocabulary.setdefault(token, 0)
                                self.vocabulary[token] += 1
                                counts.setdefault(token, 0)
                                counts[token] += 1
                                total += 1
                                

                f.close()
        return(counts, total)
                    
                    
    def classify(self, filename):
        results = {}
        for category in self.categories:
            results[category] = 0
        f = codecs.open(filename, 'r', 'iso8859-1')
        for line in f:
            tokens = line.split()
            for token in tokens:
                #print(token)
                token = token.strip('\'".,?:-').lower()
                if token in self.vocabulary:
                    for category in self.categories:
                        if self.prob[category][token] == 0:
                            print("%s %s" % (category, token))
                        results[category] += math.log(self.prob[category][token])
        f.close()
        results = list(results.items())
        results.sort(key=lambda tuple: tuple[1], reverse = True)
        # for debugging I can change this to give me the entire list
        return results[0][0]

    def testCategory(self, directory, category):
        files = os.listdir(directory)[:1000]
        total = 0
        correct = 0
        for file in files:
            total += 1
            result = self.classify(directory + file)
            if result == category:
                correct += 1
        return (correct, total)

    def test(self, testdir):
        """Test all files in the test directory--that directory is organized into subdirectories--
        each subdir is a classification category"""
        categories = os.listdir(testdir)
        #filter out files that are not directories
        categories = [filename for filename in categories if os.path.isdir(testdir + filename)]
        correct = 0
        total = 0
        for category in categories:
            (catCorrect, catTotal) = self.testCategory(testdir + category + '/', category)
            correct += catCorrect
            total += catTotal
        print("Accuracy is  %f%%  (%i test instances)" % ((correct / total) * 100, total))
        return (correct, total)


def testOneBucket(datadir, stoplist, bucket, mode):
    """creates a classifier trained on all data except that in bucket
    uses data in bucket to test.
    returns """
    results = {}
    cl = BayesText(datadir, stoplist, bucket, mode)
    #print (cl.stopwords)
    for category in cl.categories:
        results[category] = cl.testCategory("%s%s/%i/" % (datadir, category, bucket), category)
    return results
            

def test(datadir, wordlist, mode):
    resultsArray = {}
    for i in range(10):
        results = testOneBucket(datadir, wordlist, i, mode)
        print (results)
        for (key, value) in results.items():
            if key in resultsArray:
                resultsArray[key][0] += value[0]
                resultsArray[key][1] += (value[1] - value[0])
            else:
                resultsArray[key] = [value[0], value[1] - value[0]]
    #print (resultsArray)
    print("\n\n")
    #
    #  now print results matrix
    #  this code is specific to gender in Twitter project
    print ("   +----------+----------+----------+")
    print ("   |          |  female  |  male    |")
    print ("   +----------+----------+----------+")
    print ("   | female   |  %6i  | %6i   |" % (resultsArray['female'][0], resultsArray['female'][1]))
    print ("   +----------+----------+----------+")
    print ("   |   male   |  %6i  | %6i   |" % (resultsArray['male'][0], resultsArray['male'][1]))
    print ("   +----------+----------+----------+")

    correct = resultsArray['female'][0] + resultsArray['male'][1]
    total = correct + resultsArray['female'][1] + resultsArray['male'][0]
    print ("\n\n%% Accuracy: %4.2f\n\n" % (float(correct) / total * 100))

    
    
test('sample/', 'genderWords.txt', 2)
