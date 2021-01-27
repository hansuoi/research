def mecab_list(text)
    import MeCab
    tagger = MeCab.Tagger(-Ochasen)
    tagger.parse('')    # よくわかんないけどこうするとエラーが出ない
    node = tagger.parseToNode(text)
    word_class = []
    while node
        word = node.surface
        wclass = node.feature.split(',')    # 品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
        if wclass[0] != u'BOSEOS'
            if wclass[6] == None
                word_class.append((word,wclass[0],))
            else
                word_class.append((word,wclass[0],wclass[6]))
        node = node.next
    return word_class
