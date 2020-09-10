import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import re
import datetime
from matplotlib.colors import ListedColormap
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import emoji
from PIL import Image

def main():
    st.set_option('deprecation.showfileUploaderEncoding', False)
    st.title('Análise mensagens Whatsapp')
    st.write('Obs: Nenhuma mensagem será salva ou utilizada, sua privacidade está totalmente segura.')
    st.write('Essa aplicação se trata de um código aberto que pode ser encontrado no Github: ')
    st.write('Meu LinkedIn: https://www.linkedin.com/in/andr%C3%A9-elias/')
    
    st.text("__________________________________________________________________________________________")
    nltk.download('stopwords')
    st.write('Como conseguir o arquivo da conversa:')
    st.image('export.jpeg', width= 250)
    st.write('''Dentro da conversa aperte os '...' e depois clique em Exportar Conversa (SEM MÍDIA)''')
    
    arquivoConversa = st.file_uploader('FAÇA O UPLOAD AQUI')
    if arquivoConversa is not None:
        pat = re.compile(r'^(\d\d\/\d\d\/\d\d\d\d.*?)(?=^^\d\d\/\d\d\/\d\d\d\d|\Z)', re.S | re.M)
        with arquivoConversa as f:
            data = [m.group(1).strip().replace('\n', ' ') for m in pat.finditer(f.read())]

        data.pop(0)
        sender = []; message = []; datetime = []
        for row in data:

            datetime.append(row.split(' - ')[0])
            
            try:
                s = re.search('- (.*?):', row).group(1)
                sender.append(s)
            except:
                sender.append('')

            try:
                message.append(row.split(': ', 1)[1])
            except:
                message.append('')

        df = pd.DataFrame(zip(datetime, sender, message), columns=['datetime', 'sender', 'message'])
        df['datetime'] = pd.to_datetime(df.datetime, format='%d/%m/%Y %H:%M')
        df['date'] = df['datetime'].dt.date
        df['time'] = df['datetime'].dt.time
        df['weekDay'] = df['datetime'].dt.dayofweek
        df['timeHour'] = df['datetime'].dt.hour
        df['weekDay'] = df['weekDay'].replace({0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'})
        df['message'] = df['message'].replace({'<Arquivo de mídia oculto>':'-MÍDIA-'})
        names = df['sender'].unique()
        yourName = names[0]
        hisName = names[1]

        numMessage = df.groupby(['sender'])['message'].count().reset_index()

        st.text("__________________________________________________________________________________________")
        st.subheader('Distribuição de mensagens')
        
        plt.figure(figsize=(15,4))
        ax = sns.barplot(x="message", y="sender", data=numMessage)
        ax.set(xlabel='Mensagens enviadas', ylabel='Remetente')
        sns.set(style="white", context="talk")
        st.pyplot()

        df['characters'] = df.message.apply(len)
        df['words'] = df.message.apply(lambda x: len(x.split()))

        textMean = df.groupby(['sender'])['characters', 'words'].mean().round(2).reset_index()

        ax = sns.barplot(x="characters", y="sender", data=textMean)
        ax.set(xlabel='Média de caracteres por msg', ylabel='Remetente')
        st.pyplot()

        ax = sns.barplot(x="words", y="sender", data=textMean)
        ax.set(xlabel='Média de palavras por msg', ylabel='Remetente')
        st.pyplot()

        numMessageDay = df.groupby(['date'])['message'].count().reset_index()

        st.text("__________________________________________________________________________________________")
        st.subheader('Distribuição tempo')
        plt.figure(figsize=(15,4))
        ax = sns.lineplot(data=numMessageDay, x="date", y="message", linewidth=5)
        ax.set(xlabel='Data', ylabel='Mensagens por dia')
        plt.setp(ax.get_xticklabels(), rotation=45)
        st.pyplot()

        numMessageHour = df.groupby(['timeHour'])['message'].count().reset_index()

        plt.figure(figsize=(7,7))

        ax = sns.barplot(data=numMessageHour, x="timeHour", y="message")
        ax.set(xlabel='Hora do dia', ylabel='Mensagens')
        sns.set(style="white", context="talk")
        st.pyplot()

        numMessageWeek = df.groupby(['weekDay'])['message'].count().reset_index()
        numMessageWeek['weekDay'] = pd.Categorical(numMessageWeek['weekDay'], categories= ['Segunda','Terça','Quarta','Quinta','Sexta','Sábado', 'Domingo'], ordered=True)

        plt.figure(figsize=(15,4))
        sns.set(style="white", context="talk")
        ax = sns.barplot(data=numMessageWeek, x="message", y="weekDay")
        ax.set(xlabel='Dia da semana', ylabel='Mensagens')
        st.pyplot()

        yourWords = []; hisWords = []
        for x in range(len(df['sender'])):
            if df['sender'][x] == yourName:
                yourWords.append(df['message'][x])
            elif df['sender'][x] == hisName:
                hisWords.append(df['message'][x])

        st.text("__________________________________________________________________________________________")
        st.subheader('Mensagens em números')
        st.write('Total Mensagens: ', len(yourWords) + len(hisWords))
        st.write('Suas mensagens: ', len(yourWords))
        st.write('Mensagens do outro: ', len(hisWords))

        s = ' '
        totalYourWords = s.join(yourWords)
        totalHisWords = s.join(hisWords)

        pattern = re.compile('k*|-MÍDIA-|Kk*')
        totalYourWords = pattern.sub('', totalYourWords)
        totalHisWords = pattern.sub('', totalHisWords)

        stopWords = stopwords.words('portuguese')
        newStop = ['pra', 'tô', 'aí', 'tá', 'então', 'deu', 'aqui', 'né', 'vou', 'bem', 'coisa', 'tmb', 'vai']
        for x in newStop:
            stopWords.append(x)

        mapaCores = ListedColormap(['red', 'magenta', 'blue', 'green'])

        mask = np.array(Image.open('mask-cloud.png'))

        st.text("__________________________________________________________________________________________")
        st.subheader('Nuvem de palavras')
        
        nuvem = WordCloud(width=1000, height=600, background_color = 'white', colormap = mapaCores, stopwords = stopWords, max_words = 60,mask = mask)
        nuvem.generate(totalYourWords)
        plt.figure(figsize = (10,10))
        plt.imshow(nuvem)
        st.pyplot()

        mapaCores = ListedColormap(['red', 'magenta', 'blue', 'green'])

        nuvem = WordCloud(width=1000, height=600, background_color = 'white', colormap = mapaCores, stopwords = stopWords, max_words = 60,mask = mask)
        nuvem.generate(totalHisWords)
        plt.figure(figsize = (10,10))
        plt.imshow(nuvem)
        st.pyplot()

        st.text("__________________________________________________________________________________________")
        st.subheader('Emojis')

        yourEmoji = list(''.join(c for c in totalYourWords if c in emoji.UNICODE_EMOJI))

        countYourEmoji = {i:yourEmoji.count(i) for i in yourEmoji}

        hisEmoji = list(''.join(c for c in totalHisWords if c in emoji.UNICODE_EMOJI))

        countHisEmoji = {i:hisEmoji .count(i) for i in hisEmoji }

        dfYourEmoji = pd.DataFrame(countYourEmoji.items(), columns=['Emoji', 'Count'])

        dfYourEmoji = dfYourEmoji.sort_values(by=['Count'], ascending = False)

        st.table(dfYourEmoji)

        dfHisEmoji = pd.DataFrame(countHisEmoji.items(), columns=['Emoji', 'Count'])

        dfHisEmoji = dfHisEmoji.sort_values(by=['Count'], ascending = False)


        st.table(dfHisEmoji)

if __name__ == "__main__":
    main()
