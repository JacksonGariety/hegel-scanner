import nltk
import random
import pickle
import os.path
# from somajo import Tokenizer, SentenceSplitter
from syntok.tokenizer import Tokenizer
from ClassifierBasedGermanTagger import ClassifierBasedGermanTagger
from germalemma import GermaLemma
from collections import Counter


def train():
    corp = nltk.corpus.ConllCorpusReader('./resources/tigercorpus-2.2.conll09',
                                           'tiger_release_aug07.corrected.16012013.conll09',
                                           ['ignore', 'words', 'ignore', 'ignore', 'pos'],
                                           encoding='utf-8')

    tagged_sents = list(corp.tagged_sents())
    random.shuffle(tagged_sents)

    # set a split size: use 90% for training, 10% for testing
    split_perc = 0.1
    split_size = int(len(tagged_sents) * split_perc)
    train_sents, test_sents = tagged_sents[split_size:], tagged_sents[:split_size]

    tagger = ClassifierBasedGermanTagger(train=train_sents)
    accuracy = tagger.evaluate(test_sents)

    return tagger


def main():
    # train
    if os.path.exists('./resources/nltk_german_classifier_data.pickle'):
        with open('./resources/nltk_german_classifier_data.pickle', 'rb') as f:
            print('./resources/nltk_german_classifier_data.pickle found')
            tagger = pickle.load(f)
    else:
        print('could not find ./resources/nltk_german_classifier_data.pickle: training: IN PROGRESS')
        tagger = train()
        with open('./resources/nltk_german_classifier_data.pickle', 'wb') as f:
            pickle.dump(tagger, f, protocol=2)
        print('training FINISHED')

    # tokenize
    if os.path.exists('./data/1.pickle'):
        with open('./data/1.pickle', 'rb') as f:
            print('1.pickle found')
            words = pickle.load(f)
    else:
        print('could not find 1.pickle: tokenizing: IN PROGRESS')
        document = open('./resources/logik-band-eins.txt').read()
        tok = Tokenizer()
        tokens = tok.tokenize(document)

        words = []
        i = 0
        for token in tokens:
            if i < 10000:
                v = token.value
                if len(v) > 1 and (not str.isdigit(v)) or True:
                    words.append(v)
                # i = i + 1
            else:
                break
        with open('./data/1.pickle', 'wb') as f:
            pickle.dump(words, f, protocol=2)
        print('tokenizing FINISHED')

    # tag
    if os.path.exists('./data/2.pickle'):
        with open('./data/2.pickle', 'rb') as f:
            print('2.pickle found')
            tagged_words = pickle.load(f)
    else:
        print('could not find 2.pickle: tagging: IN PROGRESS')
        tagged_words = tagger.tag(words)
        with open('./data/2.pickle', 'wb') as f:
            pickle.dump(tagged_words, f, protocol=2)

    # filter-in As, Ns, and Vs
    if os.path.exists('./data/3.pickle'):
        with open('./data/3.pickle', 'rb') as f:
            print('3.pickle found')
            filtered_words = pickle.load(f)
    else:
        print('could not find 3.pickle: filtering: IN PROGRESS')
        parts_of_speech = ['ADJA', 'ADJD', 'NN', 'NN',]
        filtered_words = list(filter(lambda word: word[1][0] == 'V' or any(pos == word[1] for pos in parts_of_speech), tagged_words))
        with open('./data/3.pickle', 'wb') as f:
            pickle.dump(filtered_words, f, protocol=2)

    # lemmatize
    if os.path.exists('./data/4.pickle'):
        with open('./data/4.pickle', 'rb') as f:
            print('4.pickle found')
            lemmatized_words = pickle.load(f)
    else:
        print('could not find 4.pickle: lematization: IN PROGRESS')
        lemmatizer = GermaLemma()
        lemmatized_words = []
        for word in filtered_words:
            try:
                lemmatized_words.append(lemmatizer.find_lemma(word[0], word[1]))
            except:
                w = word[0]
                l = word[1]
                print(f"EXCEPT: {w} {l}")
                continue
        with open('./data/4.pickle', 'wb') as f:
            pickle.dump(lemmatized_words, f, protocol=2)

    # filter-out modals
    f = open('./resources/modal-words.txt', 'r')
    modal_words = f.read().splitlines()[:1000]
    non_modals = [item for item in lemmatized_words if item not in modal_words]
    # non_modals = list(filter(lambda word: not any(modal == word for modal in modals), lemmatized_words))
    # modals = []
    # line = f.readline()
    # modals.append(line)
    # while line:
    #     line = f.readline()
    #     modals.append(line)
     
    for pair in Counter(non_modals).most_common(30):
        print(pair[0] + " " + str(pair[1]))
            
    # tokenizer = Tokenizer(split_camel_case=True, token_classes=False, extra_info=False)
    # tokenized_paragraphs = tokenizer.tokenize_file('./data/logik-band-eins.txt',
    #                                                 parsep_empty_lines=False)
    # sentence_splitter = SentenceSplitter(is_tuple=False)

    # words = []
    # for paragraph in tokenized_paragraphs:
    #     sentences = sentence_splitter.split(paragraph)
    #     for sentence in sentences:
    #         words.append(sentence)
    #         print("\n".join(sentence), "\n")




    # lines = []
    # file = open("./data/logik-band-eins.txt")
    # for line in file:
    #     words = nltk.word_tokenize(line)
    #     lines.append()



main()
