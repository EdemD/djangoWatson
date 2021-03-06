from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator


# def post_list(request):
#   posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
#  return render(request, 'blog/post_list.html', {'posts': posts})

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='3570d896-ab16-4c7c-b302-77414005bc53',
        password='Z2au4f48Klkq',
        version='2016-05-19')

    language_translator = LanguageTranslator(
        username='90cbe197-3db2-45e1-8d4b-0a95444275f0',
        password='jxPHFLuHnTra')


    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        posting = post.text
        toneObj= json.dumps(tone_analyzer.tone(posting,"emotion"), indent=2)
        post.toneObj2 = json.loads(toneObj)
        post.angerScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][0]['score']
        post.disgustScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][1]['score']
        post.fearScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][2]['score']
        post.joyScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][3]['score']
        post.sadScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][4]['score']
       
        #data = json.dumps(tone_analyzer.tone(post.text, 'text/plain', sentences=None, tones='emotion', content_language=None, accept_language=None), indent=1)  # converting to string and storing in the data
        #j = json.loads(data);
        #post.info = j['document_tone']['tone_categories'][0]['tones']
        # post.info = json.dumps(post.info);
        #post.angerScore = post.info[0]['score']
        #post.disgustScore = post.info[1]['score']
        #post.fearScore = post.info[2]['score']
        #post.joyScore = post.info[3]['score']
        #post.sadScore = post.info[4]['score']
        # print(post.info[0]['tone_name'])
        
        def word_count(string):
            word_count = {}
            string = string.lower().split(" ")
            counter = 0
            for word in string:
                counter += 1
                if word in word_count:
                    word_count[word] += 1
            return counter

        def char_count(string):
            word_count = {}
            counter = 0
            for word in string:
                if word != ' ':
                    counter += 1
                if word in word_count:
                    word_count[word] = word_count.get(word, 0) + 1
            return counter
        
        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='fr')
        post.translatedText = json.dumps(translation, indent=2, ensure_ascii=False)
        print(json.dumps(translation, indent=2, ensure_ascii=False))
        t = json.loads(post.translatedText)
        
        translations = t
        word_count = word_count(translations)
        character_count = char_count(translations)
        
        post.translatedText = translations
        post.wordcount = word_count
        post.charCount = character_count
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Post.objects.get(pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
