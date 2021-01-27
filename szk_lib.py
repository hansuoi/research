def mecab_list(text):
    import MeCab
    tagger = MeCab.Tagger("-Ochasen")
    tagger.parse('')    # よくわかんないけどこうするとエラーが出ない
    node = tagger.parseToNode(text)
    word_class = []
    while node:
        word = node.surface
        wclass = node.feature.split(',')
        # wclass:品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音

        if wclass[0] != u'BOS/EOS':
            if wclass[6] == None:
                word_class.append((word,wclass[0],""))
            else:
                word_class.append((word,wclass[0],wclass[6]))
        node = node.next

    # word_class: 表層形, 品詞, 原形
    return word_class


# 入力された単語の品詞を返す
def hinshi_check(word):
    return mecab_list(word)[0][1]


# 入力された単語の原型を返す
def genkei(word):
    return mecab_list(word)[0][2]


# 共起行列(と単語のリスト)を返す
# w_size: ウィンドウ幅
def cooccurrence(text, w_size):
    import numpy as np

    # i文目のj語目が格納された二次元配列sentence(i, j)
    sentence = text.split('\n')
    for i in range(len(sentence)):
        sentence[i] = sentence[i].split()

    # 登場した単語のリスト
    words = list(set(text.split()))

    # words数サイズのゼロ行列を作る
    matrix = np.zeros((len(words), len(words)))

    # number番目の単語がw
    for number, w in enumerate(words):
        for i in range(len(sentence)):
            for j in range(len(sentence[i])):
                # wとi文目j単語目とが合致したら
                if w == sentence[i][j]:
                    # 行列の、窓幅分前の単語のところを+1する
                    for d in range(1, w_size+1):
                        if j-d >= 0:
                            matrix[number][words.index(sentence[i][j-d])] += 1
                    # 行列の、窓幅分後の単語のところを+1する
                    for d in range(1, w_size+1):
                        if j+d < len(sentence[i]):
                            matrix[number][words.index(sentence[i][j+d])] += 1

    return words, matrix


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


def weeds_list(text, w_size=1):
    # words: textに登場する単語のリスト
    # matrix: 共起行列
    words, matrix = cooccurrence(text, w_size=1)

    # 下位語候補, 上位語候補, weeds値
    # を格納する配列を用意しておく
    result = []

    for i in range(len(words)):
        for j in range(len(words)):
            if i == j:
                continue
            else:
                result.append([words[i], words[j], WeedsP(matrix[i], matrix[j])])

    # weeds値が大きい順(上位・下位関係がはっきりしている順)に並べ替える
    result = sorted(result, reverse=True, key=lambda x: x[2])

    return result


# 記号を削除する
def preprocess1(text):
    hinshi_check
    #記号を消すコード


# 名詞が連続してたら名詞句として扱う(わかち書かない)
# 名詞・名詞句以外は削除する
def preprocess2(text):
    from szk_lib import hinshi_check

    # 名詞と名詞句とを格納する配列
    nouns = []

    # i文目のj語目が格納された二次元配列sentence(i, j)
    sentence = text.split('\n')
    for i in range(len(sentence)):
        sentence[i] = sentence[i].split()

    for i in range(len(sentence)):
        j = 0
        while j < len(sentence[i]):
            if hinshi_check(sentence[i][j]) == '名詞':
                w = ''
                while j<len(sentence[i]) and hinshi_check(sentence[i][j])=='名詞':
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

    # result: 共通部分, s1, s2
    result = []

    for i in range(len(nouns)):
        for j in range(i+1, len(nouns)):
            result.append([find_longest_substr(nouns[i], nouns[j]), nouns[i], nouns[j]])

    # 共通部分順に並べ替える
    result = sorted(result, reverse=True, key=lambda x: x[0])

    return result


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
