def mecab_list(text):
    import MeCab
    tagger = MeCab.Tagger("-Ochasen")
    tagger.parse('')
    node = tagger.parseToNode(text)
    word_class = []
    while node:
        word = node.surface
        wclass = node.feature.split(',')
        # wclass:品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音

        if wclass[0] != u'BOS/EOS':
            if wclass[6] == None:
                word_class.append((word,wclass[0],word))
            else:
                word_class.append((word,wclass[0],wclass[6]))
        node = node.next

    # word_class: 表層形, 品詞, 原形
    return word_class


# 入力された単語の原型を返す(改善版)
def genkei(word):
    import MeCab
    tagger = MeCab.Tagger("-Ochasen")
    tagger.parse('')
    node = tagger.parseToNode(word)

    while node:
        w = node.surface
        wclass = node.feature.split(',')
        # wclass:品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音

        if wclass[0] != u'BOS/EOS':
            if wclass[6] == None:
                return w
            else:
                return wclass[6]
        node = node.next


# 入力された単語の品詞を返す(改善版)
def hinshi(word):
    import MeCab
    tagger = MeCab.Tagger("-Ochasen")
    tagger.parse('')
    node = tagger.parseToNode(genkei(word))

    while node:
        word = node.surface
        wclass = node.feature.split(',')
        # wclass:品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音

        if wclass[0] != u'BOS/EOS':
            return wclass[0]
        node = node.next


# 登場した単語(原形)のリストを作る
def words_list(text):
    words = list(set(text.split()))

    for i in range(len(words)):
        words[i] = genkei(words[i])

    words = list(set(words))

    import pickle
    with open('words_list', mode='wb') as f:
        pickle.dump(words , f)


# 共起行列(と単語のリスト)を返す
# w_size: ウィンドウ幅
def c_matrix(text, w_size, w_list):
    import numpy as np
    import pickle

    # i文目のj語目が格納された二次元配列sentence(i, j)
    sentence = text.split('\n')
    for i in range(len(sentence)):
        sentence[i] = sentence[i].split()

    # 登場した単語(原形)のリスト
    with open(w_list, mode='rb') as f:
        words = pickle.load(f)

    # words数サイズのゼロ行列を作る
    matrix = np.zeros((len(words), len(words)))

    for i in range(len(sentence)):
        for j in range(len(sentence[i])):
            number = words.index(genkei(sentence[i][j]))
            # 行列の、窓幅分前/後の単語の部分を+1する
            for d in range(1, w_size+1):
                if j-d >= 0:
                    matrix[number][words.index(genkei(sentence[i][j-d]))] += 1
                if j+d < len(sentence[i]):
                    matrix[number][words.index(genkei(sentence[i][j+d]))] += 1

    with open('c_matrix', mode='wb') as f:
        pickle.dump(matrix , f)


# ベクトルの0でない成分を返す
# wは単語ベクトル
def F(w):
    a = []
    for n, i in enumerate(w):
        if i != 0:
            a.append(n)
    return set(a)


def WeedsP(w1, w2):
    m = 0
    for i in list(F(w1)):
        m += w1[i]

    if m == 0:
        return 0

    c = 0
    for i in list(F(w1)&F(w2)):
        c += w1[i]
    return c / m


def weeds_list(text, w_list, c_matrix):
    import pickle

    # 登場した単語(原形)のリスト
    with open(w_list, mode='rb') as f:
        words = pickle.load(f)

    # matrix: 共起行列
    with open(c_matrix, mode='rb') as f:
        matrix = pickle.load(f)

    # words[i]が下位・words[j]が上位、と仮定してweedsを計算する
    for i in range(len(words)):
        for j in range(len(words)):
            if i!=j and hinshi(words[i])=='名詞' and hinshi(words[j])=='名詞':
                w = WeedsP(matrix[i], matrix[j])
                if w >= 0.5:
                    with open('weeds.txt', mode='a', encoding='utf-8') as f:
                        f.write(', '.join([words[i], words[j], str(w)]))
                        f.write('\n')


# 記号を削除する
def del_kigo(text):
    import string
    kigo = string.punctuation + '❶' + '②' + '｣' + '③' + '❹' + '●' + '■'
    result = text.translate(str.maketrans('', '', kigo))
    return result


# 名詞が連続してたら名詞句として扱う(わかち書かない)
# 名詞・名詞句以外は削除する
def preprocess2(text):
    # 名詞と名詞句とを格納する配列
    nouns = []

    # i文目のj語目が格納された二次元配列sentence(i, j)
    sentence = text.split('\n')
    for i in range(len(sentence)):
        sentence[i] = sentence[i].split()

    for i in range(len(sentence)):
        j = 0
        while j < len(sentence[i]):
            if hinshi(sentence[i][j]) == '名詞':
                w = ''
                while j<len(sentence[i]) and hinshi(sentence[i][j])=='名詞':
                    w += sentence[i][j]
                    j += 1
                nouns.append(w)
            j += 1

    return nouns


# s1, s2 の最長共通部分を返す
def find_longest_substr(s1, s2):
    for length in range(len(s2), 0, -1):
        for p0 in range(len(s2) - length + 1):
            substr = s2[p0:(p0 + length)]
            if substr in s1:
                return(substr)
    return ""


def substr(text):
    # textから名詞と名詞句だけ抽出
    nouns = preprocess2(text)

    # 「s1,s2の共通部分, s1, s2」をtxtに保存
    for i in range(len(nouns)):
        for j in range(i+1, len(nouns)):
            c = find_longest_substr(nouns[i], nouns[j])
            if len(c) >= 2:
                with open('共通部分.txt', mode='a', encoding='utf-8') as f:
                    f.write(', '.join([c, nouns[i], nouns[j]]))
                    f.write('\n')


# pdfをtxtに変換する
def pdf_to_txt(file_name):
    from subprocess import call

    # pdf2txt.py のパス
    path = 'C:/Users/User/anaconda3/envs/w2v/Scripts/pdf2txt.py'

    # pdf2txt.py の呼び出し
    call(["python", path, file_name+".pdf", '-o', file_name+'.txt'])


# unicode正規化をする
def unicode_nfkc(file_name):
    import unicodedata

    with open(file_name+'.txt', mode='r', encoding='utf-8') as f:
        text = f.read()

    text = unicodedata.normalize("NFKC",text)
    with open(file_name+'.txt', mode='w', encoding='utf-8') as f:
        f.write(text)


# pdfからtxtに変換し、正規化・記号削除
def preprocess1(file_name):
    pdf_to_txt(file_name)
    unicode_nfkc(file_name)

    with open(file_name+'.txt', mode='r', encoding='utf-8') as f:
        text = f.read()

    text = del_kigo(text)

    import MeCab
    tagger = MeCab.Tagger("-Owakati")
    tagger.parse('')

    text = text.split('\n')
    for t in text:
        with open(file_name+'_w.txt', mode='a', encoding='utf-8') as f:
            f.write(tagger.parse(t))

    with open(file_name+'_w.txt', mode='r', encoding='utf-8') as f:
        text = f.read()

    return text
