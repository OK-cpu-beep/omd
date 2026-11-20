from math import log


class CountVectorizer:
    def __init__(self, lowercase=True, ngram_size=1):
        if (not isinstance(ngram_size, int) or isinstance(ngram_size, bool)
                or ngram_size not in (1, 2)):
            raise ValueError("ngram_size должен быть равен 1 или 2")
        self.lowercase = lowercase
        self.ngram_size = ngram_size
        self._vocabulary = dict()

    @property
    def vocabulary(self):
        return self._vocabulary

    @vocabulary.setter
    def vocabulary(self, words: dict):
        if not isinstance(words, dict):
            raise ValueError("Словарь должен быть dict")
        if any(not isinstance(word, str) for word in words):
            raise ValueError("Ключами словаря должны быть строки")
        if any(not isinstance(index, int) or isinstance(index, bool)
               for index in words.values()):
            raise ValueError("Индексы слов должны быть целыми числами")
        if sorted(words.values()) != list(range(len(words))):
            raise ValueError("Индексы должны идти с 0 без пропусков "
                             "и повторов")
        self._vocabulary = words.copy()

    @vocabulary.deleter
    def vocabulary(self):
        self._vocabulary = dict()

    def add_word(self, word: str):
        if word not in self._vocabulary:
            self._vocabulary[word] = len(self._vocabulary)
        return self._vocabulary[word]

    def tokenize(self, text: str):
        if self.lowercase:
            text = text.lower()
        words = text.split()
        if self.ngram_size == 1:
            return words
        return [" ".join(words[index:index + self.ngram_size])
                for index in range(len(words) - self.ngram_size + 1)]

    def fit(self, corpus: list[str]):
        vectorizer = CountVectorizer(self.lowercase, self.ngram_size)
        for text in corpus:
            for word in self.tokenize(text):
                vectorizer.add_word(word)
        if not vectorizer.vocabulary:
            raise ValueError("В корпусе нет слов для обучения")
        self.vocabulary = vectorizer.vocabulary
        return self

    def transform(self, corpus: list[str]):
        if not self._vocabulary:
            raise RuntimeError("Сначала обучите векторизатор "
                               "или задайте словарь")
        matrix = list()
        for text in corpus:
            row = [0] * len(self._vocabulary)
            for word in self.tokenize(text):
                if word in self._vocabulary:
                    row[self._vocabulary[word]] += 1
            matrix.append(row)
        return matrix

    def get_feature_names(self):
        return sorted(self._vocabulary, key=self._vocabulary.get)

    def fit_transform(self, corpus: list[str]):
        self.fit(corpus)
        return self.transform(corpus)

    def to_dict(self):
        return {
            "lowercase": self.lowercase,
            "ngram_size": self.ngram_size,
            "vocabulary": self._vocabulary.copy(),
        }

    @classmethod
    def from_dict(cls, state: dict):
        vectorizer = cls(lowercase=state["lowercase"],
                         ngram_size=state["ngram_size"])
        vectorizer.vocabulary = state["vocabulary"]
        return vectorizer


class BinaryVectorizer(CountVectorizer):
    def transform(self, corpus: list[str]):
        matrix = super().transform(corpus)
        return [[1 if count > 0 else 0 for count in row] for row in matrix]


class TfidfVectorizer(CountVectorizer):
    def __init__(self, lowercase=True, use_idf=True, ngram_size=1):
        super().__init__(lowercase=lowercase, ngram_size=ngram_size)
        self.use_idf = use_idf
        self._idf = list()

    @property
    def idf(self):
        return self._idf.copy()

    @classmethod
    def from_config(cls, config: dict):
        return cls(lowercase=config.get("lowercase", True),
                   use_idf=config.get("use_idf", True))

    def fit(self, corpus: list[str]):
        super().fit(corpus)
        idf = list()
        if self.use_idf:
            matrix = super().transform(corpus)
            amount_texts = len(corpus)
            for index in range(len(self.vocabulary)):
                document_count = sum(row[index] > 0 for row in matrix)
                idf.append(log((amount_texts + 1) / (document_count + 1)) + 1)
        self._idf = idf
        return self

    def transform(self, corpus: list[str]):
        matrix = super().transform(corpus)
        if self.use_idf and len(self._idf) != len(self.vocabulary):
            raise RuntimeError("Сначала обучите векторизатор для расчёта IDF")
        result = list()
        for row in matrix:
            amount_words = sum(row)
            weights = [0.0] * len(row)
            if amount_words > 0:
                for index, count in enumerate(row):
                    weights[index] = count / amount_words
                    if self.use_idf:
                        weights[index] *= self._idf[index]
            result.append(weights)
        return result


class KeywordExtractor:
    def __init__(self, vectorizer: CountVectorizer, top_n=3):
        self.vectorizer = vectorizer
        self.top_n = top_n

    @property
    def top_n(self):
        return self._top_n

    @top_n.setter
    def top_n(self, value: int):
        if (not isinstance(value, int) or isinstance(value, bool)
                or value <= 0):
            raise ValueError("top_n должен быть целым числом больше 0")
        self._top_n = value

    def fit(self, corpus: list[str]):
        self.vectorizer.fit(corpus)
        return self

    def extract(self, corpus: list[str]):
        matrix = self.vectorizer.transform(corpus)
        words = self.vectorizer.get_feature_names()
        result = list()
        for row in matrix:
            keywords = [(word, weight) for word, weight in zip(words, row)
                        if weight > 0]
            keywords.sort(key=lambda item: (-item[1], item[0]))
            result.append(keywords[:self.top_n])
        return result


TRAIN_CORPUS = [
    "Марс сигнал сигнал",
    "Марс пыль",
    "Марс сигнал антенна",
]

CHECK_CORPUS = [
    "СИГНАЛ шум сигнал",
    "антенна пыль",
    "марс марс марс",
    "комета",
    "",
]


def demo():
    print("Сценарий 1. Веса TF-IDF")
    tfidf = TfidfVectorizer.from_config({})
    train_matrix = tfidf.fit_transform(TRAIN_CORPUS)
    print("Слова:", tfidf.get_feature_names())
    print("IDF:", tfidf.idf)
    print("Матрица обучения:", train_matrix)
    print("Матрица проверки:", tfidf.transform(CHECK_CORPUS))
    saved_idf = tfidf.idf
    saved_idf.clear()
    print("IDF после очистки полученного списка:", tfidf.idf)

    print("\nСценарий 2. Настройки и новый fit()")
    tf = TfidfVectorizer.from_config({
        "lowercase": False,
        "use_idf": False,
    })
    tf_matrix = tf.fit_transform(["Марс марс", "МАРС сигнал"])
    print("Слова TF:", tf.get_feature_names())
    print("IDF без расчёта редкости:", tf.idf)
    print("Матрица TF:", tf_matrix)

    tfidf.fit(["Венера облака"])
    print("Слова после нового fit():", tfidf.get_feature_names())
    print("Новые IDF:", tfidf.idf)
    print("Новая матрица:", tfidf.transform(["Марс Венера облака"]))

    print("\nСценарий 3. Ключевые слова")
    extractor = KeywordExtractor(tfidf, top_n=2)
    extractor.fit(TRAIN_CORPUS)
    print("До двух слов:", extractor.extract(CHECK_CORPUS))
    extractor.top_n = 1
    print("По одному слову:", extractor.extract(CHECK_CORPUS))
    try:
        extractor.top_n = 0
    except ValueError as error:
        print("Ошибка изменения top_n:", error)


if __name__ == "__main__":
    demo()
