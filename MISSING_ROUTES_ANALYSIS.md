# ROUTE ANALYSIS: webapi.py vs New Blueprint Structure

## SUMMARY
- **Original webapi.py**: 157 routes total
- **New blueprints**: 76 routes implemented
- **MISSING**: 81 routes need to be added

## ✅ IMPLEMENTED ROUTES (76)

### Flashcard Routes (1)
- `/flashcard2`

### Text Processing Routes (8) 
- `/addtext`
- `/getcws`
- `/updatecws` 
- `/deletecws`
- `/changecwsstatus`
- `/getimportedtexts`
- `/get_character_cws`

### AI Routes (11)
- `/generatequestions`
- `/answeraiquestion`
- `/unansweredquestions`
- `/direct_ai_analyze`
- `/direct_ai_analyze_grammar`
- `/direct_ai_summarize`
- `/direct_ai_simplify`
- `/direct_ai_question`
- `/direct_ai_questions`
- `/get_random_ai_question`
- `/ai_simplify_cws`
- `/apply_ai`
- `/ai_summarize_random`
- `/explain_paragraph`

### Audio Routes (10)
- `/audioexample`
- `/audioexample2`
- `/audioexample3`
- `/remove_audio`
- `/addaudiotime`
- `/addoutputexercise`
- `/addlisteningexercise`
- `/gettotalaudiotime`
- `/gettotaloutputtime`
- `/getspokenarticles`
- `/getspokenarticle`

### Dictionary Routes (7)
- `/dictionarylookup`
- `/reactorlookup`
- `/update_dictionary`
- `/get_dictionary_value`
- `/set_dictionary_value`
- `/download_dictionary`
- `/upload_dictionary`

### POE Routes (3)
- `/poefree`
- `/poeexamples`
- `/poeexampleresult`

### Translation Routes (1)
- `/cleanandtranslate`

### Example Routes (5)
- `/getexampleresult`
- `/make_examples_from_chunk`
- `/make_grammar_examples`
- `/make_c1_examples`
- `/makeexamples`

### Cache Routes (2)
- `/add_example_to_cache`
- `/add_examples_to_cache`

### Utility Routes (3)
- `/version`
- `/ping`
- `/dump`

### Misc Routes (25)
- `/lookupposition`
- `/get_cws_vocabulary`
- `/get_a_problem_text`
- `/post_random_pleco`
- `/generate_text`
- `/simplifycws`
- `/set_ai_auth`
- `/set_stored_value`
- `/get_stored_value`
- `/get_word_list`
- `/add_look_up`
- `/get_look_up_history`
- `/get_classification`
- `/getmemorystory`
- `/publishfile`
- `/removefile`
- `/grammartest`
- `/testvocabulary`
- `/testunderstanding`
- `/news`
- `/post_random_ai_response`
- `/commandstream`
- `/stockupdate`
- `/getfailedreadingtests`
- `/tokenize_chinese`
- `/videosegment`

## ❌ MISSING ROUTES (81)

These routes from webapi.py are NOT implemented in the new structure:

1. `/translatechinese`
2. `/makemp3fromtext`
3. `/getexplainationpage`
4. `/simplevocab`
5. `/import_mp3`
6. `/explode_mp3`
7. `/add_background_work`
8. `/get_background_work`
9. `/add_interest_to_stack`
10. `/get_interest_from_stack`
11. `/peek_interest_from_stack`
12. `/explain_sentence_free`
13. `/add_subtitle_chunk`
14. `/explain_sentence_cheap`
15. `/add_subtitles`
16. `/explain_sentence`
17. `/ai_anything`
18. `/ai_perplexity`
19. `/text2mp3`
20. `/text2mp3_small`
21. `/gooutrouter`
22. `/ask_nova`
23. `/coach/start_session`
24. `/coach/input`
25. `/aiclient`
26. `/session`
27. `/chat`
28. `/save_session`
29. `/load_session`
30. `/config`
31. `/get_time`
32. `/add_time`
33. `/remove_time`
34. `/getwritingtime`
35. `/llmentries` (POST)
36. `/llmentries` (GET)
37. `/llmentries/last_24_hours`
38. `/coachfeedback`
39. `/make_lesson_vocabulary`
40. `/jyutpingdict`
41. `/update_jyutping_dict_prio`
42. `/add_jyutping`
43. `/studygoals/set`
44. `/studygoals/get`
45. `/extract_chinese_sentences`
46. `/add_word_orders`
47. `/word_orders`
48. `/get_webm_files`
49. `/get_webm_files_old`
50. `/generate_cloze`
51. `/ask_claude`
52. `/adventure`
53. `/flashcard`
54. `/flashcard_from_text`
55. `/flashcard_from_list`
56. `/install_package`
57. `/audioadventure`
58. `/managelist`
59. `/random_cnn_article`
60. `/queue/create`
61. `/queue/enqueue`
62. `/queue/dequeue`
63. `/queue/peek`
64. `/queue/size`
65. `/feed_back_prompt`
66. `/message/post`
67. `/jobs/add`
68. `/get_txt_files`
69. `/get_txt_content`
70. `/get_search_term`
71. `/stream`
72. `/dmapi/start-session`
73. `/dmapi/chat`
74. `/dmapi/complete-task`
75. `/dmapi/tasks` (GET)
76. `/dmapi/tasks` (POST)
77. `/dmapi/progress`
78. `/poebot1`
79. `/executehomecommand` (removed intentionally)

**CRITICAL**: 81 routes are missing from the refactored application!