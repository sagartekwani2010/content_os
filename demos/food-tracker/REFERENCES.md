# References

Every entry below was opened and checked on 2026-11-16 (title, authors, venue, year) at the URL given.
Items we could not verify are listed at the end and are **not** cited anywhere else.

**Shaped the implementation** means a specific design decision in `estimate.py` or `eval/` comes from it.
**Context** means we use it only to put our numbers next to published ones, or as background.

## The three papers that shaped the design

| # | Paper | Design decision it drove |
|---|---|---|
| 1 | **Nutrition5k: Towards Automatic Nutritional Understanding of Generic Food.** Quin Thames, Arjun Karpur, Wade Norris, Fangting Xia, Liviu Panait, Tobias Weyand, Jack Sim. CVPR 2021. https://arxiv.org/abs/2103.03375 (dataset: https://github.com/google-research-datasets/Nutrition5k, CC BY 4.0) | **The eval.** Ground truth is measured mass per ingredient times USDA per-gram values, so it tests exactly the two quantities our pipeline separates (grams and nutrient density). We use their official test split (RGB-D subset, `depth_test_ids.txt`), their overhead RGB images, and their metric (MAE and MAE as % of the mean, Table 3). Their human baseline (Sec. 4.6) gives the human comparison. |
| 2 | **Im2Calories: towards an automated mobile vision food diary.** Austin Myers, Nick Johnston, Vivek Rathod, Anoop Korattikara, Alex Gorban, Nathan Silberman, Sergio Guadarrama, George Papandreou, Jonathan Huang, Kevin Murphy. ICCV 2015. https://www.cs.ubc.ca/~murphyk/Papers/im2calories_iccv15.pdf | **The two-step structure.** Recognise foods, estimate size, then look up calorie density in a nutrition database instead of predicting calories end to end. The paper notes prepared foods are better covered by USDA FNDDS than SR, which is why our table merges SR Legacy and FNDDS. |
| 3 | **Decomposing Food Images for Better Nutrition Analysis: A Nutritionist-Inspired Two-Step Multimodal LLM Approach.** Khlaisamniang et al. CVPR Workshops 2025 (MetaFood), pp. 482-491. https://mlanthology.org/cvprw/2025/khlaisamniang2025cvprw-decomposing | **Doing it with a multimodal LLM.** Step 1 the model lists ingredients, portions and cooking details; step 2 computes nutrients; they report two-step beats one-step on a Nutrition5k subset. We keep their step 1 but replace their LLM step 2 with a database lookup (Im2Calories). We could not open their PDF, so we quote none of their numbers. |

## Context: multimodal LLMs estimating nutrition from photos (2025-2026)

- **Tanabe & Yanai. Reasoning-Driven Food Energy Estimation via Multimodal Large Language Models.** Nutrients 2025, 17(7):1128. https://pmc.ncbi.nlm.nih.gov/articles/PMC11990770/ - Zero-shot on 506 Nutrition5k test dishes (Table 3): GPT-4V 80.7 kcal MAE / 55.7% MAPE; GPT-4o 82.7 kcal / 46.7%. *Context: closest published number to our setup.*
- **Mu, Sun, He. Benchmarking and Improving Foundation Model Dietary Estimates from Meal Images.** ACM BCB 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC13401436/ - 505 Nutrition5k images (Table 2): calorie MAPE GPT-4.1 34.6%, Gemini 2.5 Flash 42.9%; protein MAPE 39.3% and 43.5%. *Context.*
- **Fridolfsson, Sjöberg, Thiwång, Pettersson. Performance Evaluation of 3 Large Language Models for Nutritional Content Estimation from Food Images.** Current Developments in Nutrition 2025, 9(10):107556. https://pmc.ncbi.nlm.nih.gov/articles/PMC12513282/ - 52 weighed meal photos: energy MAPE 35.8% (ChatGPT-4o and Claude 3.5 Sonnet), weight MAPE 36-37%; models under-estimate more as portions grow. *Shaped the eval: we report mass error separately and check bias, not just MAE.*
- **O'Hara, Kent, Flynn, Gibney, Timon. An Evaluation of ChatGPT for Nutrient Content Estimation from Meal Photographs.** Nutrients 2025, 17(4):607. https://pmc.ncbi.nlm.nih.gov/articles/PMC11858203/ - 114 photos: weight off by 27.8% on average, under-estimated in 76.3% of photos. *Context; same direction as our bias finding.*
- **Sterling et al. Vision-Language Models for Image-Based Dietary Assessment: A Benchmark of Accuracy, Cost, and Prompt Strategies Across Ten Models.** bioRxiv preprint, 2026 (not peer reviewed). https://www.biorxiv.org/content/10.64898/2026.07.26.740845v1 - 3,229 Nutrition5k images, best model 80.7 kcal MAE. *Context only.*

## Context: food recognition and portion size

- **Food-101 - Mining Discriminative Components with Random Forests.** Lukas Bossard, Matthieu Guillaumin, Luc Van Gool. ECCV 2014. https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/ - 101 classes, 101,000 images; the classic recognition benchmark. *Background: recognition is the easier half; portion size is the harder half.*
- **Image-Based Food Classification and Volume Estimation for Dietary Assessment: A Review.** Frank Po Wen Lo, Yingnan Sun, Jianing Qiu, Benny Lo. IEEE JBHI 24(7), 2020. DOI 10.1109/JBHI.2020.2987943 - *Background on volume estimation methods (depth, multi-view, reference objects).*
- **Two-view 3D Reconstruction for Food Volume Estimation.** Joachim Dehais, Marios Anthimopoulos, Sergey Shevchik, Stavroula Mougiakakou. IEEE Transactions on Multimedia, 2017. https://arxiv.org/abs/1701.03330 - Under 10% volume error on 77 dishes from two photos. *Motivates improvement #2 (second photo at an angle).*
- **Portion size estimation in dietary assessment: a systematic review of existing tools, their strengths and limitations.** Amoutzopoulos et al. Nutrition Reviews 78(11), 2020. DOI 10.1093/nutrit/nuz107 - *Background: image-based aids help, few high-quality validations.*

## Data sources

- **USDA FoodData Central.** U.S. Department of Agriculture, Agricultural Research Service. FoodData Central, 2019. fdc.nal.usda.gov. Public domain / CC0 1.0. We use **SR Legacy (April 2018)** and **FNDDS 2021-2023 (released 2024-10-31)**: kcal (nutrient 1008 / 208) and protein (1003 / 203) per 100 g, 13,224 foods, in `data/fdc_compact.csv`. *Shaped the implementation (the lookup table).* Note: Nutrition5k's ground truth used FNDDS 4.1 (2010), a different version, so table differences are part of our error.
- **Indian Food Composition Tables 2017 (IFCT 2017).** Longvah T., Ananthan R., Bhaskarachary K., Venkaiah K. National Institute of Nutrition (ICMR), Hyderabad, 2017. https://nin.res.in/ebooks/IFCT2017.pdf - Free PDF; values are for **raw** foods (528 foods). Terms: reproduction for personal use with acknowledgement; **no electronic storage or reproduction for creating a product without NIN's written permission.** So we do **not** bundle IFCT data in the app. *Not used in code.*
- **Development of an Indian Food Composition Database (INDB).** Vijayakumar A., Dubasi H.B., Awasthi A., Jaacks L.M. Current Developments in Nutrition 2024, 8(7):103790. https://pmc.ncbi.nlm.nih.gov/articles/PMC11277795/ ; data https://github.com/lindsayjaacks/Indian-Nutrient-Databank-INDB- - 1,014 cooked Indian recipes (dal, roti, sabzi). The repo has **no license file**, so we only cite individual values with attribution in `data/indian_reference.csv` (reference estimates for the creator's meals) and keep the spreadsheet outside the repo. *Shaped the Indian reference table, not the estimator.* Some INDB rows look implausible (e.g. besan-suji chilla 758.9 kcal/100 g); we flag and skip those.

## Could not verify (not cited)

- Numeric results of Khlaisamniang et al. 2025 (PDF not reachable).
- Any peer-reviewed study of LLM photo-based estimation on Indian home food: none found.
- Several names floated during search (e.g. "NutriVision", "DietGlance", "FoodSky") were not checked and are not cited.
- NutriBench (Hua et al., arXiv 2407.12843) exists but uses text meal descriptions, not photos, so it is not relevant to photo estimation.
