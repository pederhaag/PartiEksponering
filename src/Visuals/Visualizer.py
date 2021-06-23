from wordcloud import WordCloud
import matplotlib.pyplot as plt


class Visualizer:
    @staticmethod
    def wordcloud_from_articles(articles):
        print(f"{len(articles)} articles passed!")

    @staticmethod
    def wordcloud(text):
        text = ' '.join(text)
        wordcloud = WordCloud().generate(text)

        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()

    @staticmethod
    def frequency_from_list(text):
        dict = {}
        for sentence in text:
            for word in sentence.split(' '):
                if word in dict.keys():
                    dict[word] += 1
                else:
                    dict[word] = 1
        return dict
