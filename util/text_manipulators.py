def split_text(text, length):

    split_list = [".", "!", ";", " and "]

    for split in split_list:

        phrases = split_and_keep(text, split)

        if len(phrases) == 1 and len(phrases[0]) > length:
            continue
        else:
            return phrases

    if len(phrases) == 1 and len(phrases[0]) > length:

        split_phrases = split_and_keep(phrases[0], " ")

        out_phrase = ""
        phrases = []

        for phrase in split_phrases:

            if len(out_phrase) + len(phrase) < length:
                out_phrase = out_phrase + phrase
            else:
                phrases.append(out_phrase)
                out_phrase = phrase

        phrases.append(out_phrase)

    return phrases

def split_and_keep(text, delimiter):

    split_items = text.split(delimiter)

    split_list = [item + delimiter for item in split_items if item != ""]

    split_list[-1] = split_list[-1].replace(delimiter, "")

    return split_list