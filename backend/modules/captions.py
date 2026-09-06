def generate(filepath: str, filter_profanity: bool):
    try:
        import whisper
        from better_profanity import profanity
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import NMF

        # Load the base model
        model = whisper.load_model("base")

        # Transcribe with word-level timestamps
        result = model.transcribe(filepath, word_timestamps=True)

        captions = []
        chapters = []

        segments = result.get("segments", [])

        profanity_timestamps = []
        for segment in segments:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()

            # NLP Profanity Filter
            if filter_profanity:
                # To find timestamps, we need to iterate over word-level timings
                censored_text = ""
                for word_info in segment.get("words", []):
                    word_text = word_info["word"].strip()
                    if profanity.contains_profanity(word_text):
                        censored_text += "*** "
                        profanity_timestamps.append({
                            "start": word_info["start"],
                            "end": word_info["end"]
                        })
                    else:
                        censored_text += word_text + " "

                text = censored_text.strip()
                if not segment.get("words"): # Fallback if word timings are missing
                    if profanity.contains_profanity(text):
                        text = profanity.censor(text)
                        profanity_timestamps.append({"start": start, "end": end})

            captions.append({
                "text": text,
                "start": start,
                "end": end
            })

        # NLP Topic Modeling for Chapters (using NMF)
        if segments:
            # Group segments into 60-second chunks to analyze topic shifts
            chunks = []
            current_chunk = ""
            current_start = 0.0
            chunk_duration = 60.0

            for seg in segments:
                if seg["start"] - current_start >= chunk_duration:
                    chunks.append({"text": current_chunk, "time": current_start})
                    current_chunk = seg["text"] + " "
                    current_start = seg["start"]
                else:
                    current_chunk += seg["text"] + " "

            if current_chunk:
                 chunks.append({"text": current_chunk, "time": current_start})

            if len(chunks) > 2:
                texts = [c["text"] for c in chunks]
                vectorizer = TfidfVectorizer(stop_words='english')
                tfidf = vectorizer.fit_transform(texts)

                num_topics = max(2, len(chunks) // 3)
                nmf_model = NMF(n_components=num_topics, random_state=1)
                W = nmf_model.fit_transform(tfidf)

                # Assign topics to chunks and detect changes
                prev_topic = -1
                feature_names = vectorizer.get_feature_names_out()

                for i, chunk in enumerate(chunks):
                    dominant_topic = W[i].argmax()

                    if dominant_topic != prev_topic:
                        # Extract top word for topic title
                        topic_words_idx = nmf_model.components_[dominant_topic].argsort()[:-3:-1]
                        title_words = [feature_names[idx] for idx in topic_words_idx]
                        title = " ".join(title_words).title()

                        chapters.append({
                            "title": title if title else f"Chapter {len(chapters)+1}",
                            "time": chunk["time"]
                        })
                        prev_topic = dominant_topic
            else:
                chapters.append({"title": "Intro", "time": 0.0})

        return {"captions": captions, "chapters": chapters, "profanities": profanity_timestamps}
    except Exception as e:
        return {"error": str(e), "captions": [], "chapters": []}