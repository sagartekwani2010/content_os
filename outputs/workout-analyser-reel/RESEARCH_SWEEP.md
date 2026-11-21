TOTAL DISTINCT SOURCES: 225 (papers: 119, tools/repos/apps: 90, reviews: 16)

# Research sweep: AI / computer-vision exercise form analysis

Compiled 20 Nov 2026 from ~45 web searches. Only items that appeared in search results (title + URL) are listed. Takeaways come from search snippets, not full-text reads. Mirrors and versions of the same work (arXiv v1/v2/v3, ar5iv, deepai, App Store regional pages) are counted once. Datasets are counted as papers. Patents, SDKs, apps, repos, product reviews and developer write-ups count as tools.

## Synthesis

### 1. Does the evidence support the two claims?

**"Counting reps is largely solved, judging form is hard": mostly yes, with one caveat.**
- Counting works well under controlled conditions. An on-device app reported 99% squat and push-up counting (#42), and pose-based counters reach a mean absolute error of about 0.2 reps on RepCount (#54, #82). Every hobby repo counts reps with a simple angle threshold (#136-225).
- The caveat: counting is not solved everywhere. In-the-wild benchmarks still get only about 56% of videos within ±1 rep (#82). A 2026 JMIR study of real phone placement found 61% mean detection (#41).
- Judging form is clearly harder. The Fitness-AQA authors (ECCV 2022) found that off-the-shelf pose features "cannot be reliably used for detecting subtle errors in workout form" (#11). The best vision-language model on FormCoach caught 58% of real form issues, with high hallucination (#28). VLMs show a "fundamental difficulty with fine-grained movement quality assessment" (#23, #22). Pose Trainer's rules flagged only 80% of bad reps (#30). Reviews say feedback is accurate only in controlled settings (#129).

**"Camera angle can fool pose-based systems": strongly supported.**
- MediaPipe accuracy "is highly dependent on the camera's viewing angle" (#15).
- In the JMIR study, squats went from 95.5% detection (diagonal, 200 cm) to 0% (side, 90 cm) (#41).
- Knee-angle error grows as the camera rotates from side-on toward frontal (#44).
- Models trained on one viewpoint drop significantly on another (#87).
- What looks like knee valgus on 2D video is partly hip motion in other planes (#77).
- A 3D estimator reported 20° of trunk flexion when lifters were actually extending (#72).

**Most useful insight for a gym-goer building a checker:** the phone's position matters as much as the model. Fix the camera angle first: a diagonal or side view at about 2 m for squats. Count reps from pose geometry, but treat form verdicts as low-confidence, and keep a human or reference clip in the loop.

### 2. Punchy, true lines (<15 words)
1. **"Counting reps is easy. Knowing if they were good reps is hard."**
2. "AI can count your squats. Judging them is the hard part."
3. "Move your phone, and the same squat goes from 95% counted to zero." (#41, across camera setups)
4. "The best AI caught barely half of real form mistakes." (#28, 58%)
5. "Counting is geometry. Coaching is judgment."
6. "From the wrong angle, a good squat looks like a bad one." (#15, #44, #77)

Caveat for the script: say "counting is easy" or "counting is mostly solved," not "solved," because #41 shows phone placement can break it.

## Full source table

Type codes: P = paper/dataset/thesis, T = tool/app/repo/SDK/product/patent/dev write-up, R = review/survey.

| # | Type | Title | URL | Takeaway |
|---|---|---|---|---|
| 1 | P | AI Pose Analysis and Kinematic Profiling of Range-of-Motion Variations in Resistance Training (Diamant) | https://arxiv.org/abs/2510.20012 | Pose pipeline on 303 recordings / 26 participants to quantify upper-body ROM kinematics. |
| 2 | P | A Mobile-Phone Pose Estimation for Gym-Exercise Form Correction (Turner, Appiah, Kwok) | https://eprints.whiterose.ac.uk/id/document/3069641 | Smartphone system compares detected pose with an ideal reference and uses anomaly detection for feedback. |
| 3 | P | ALEX-GYM-1: dataset and hybrid 3D pose vision model | https://www.scitepress.org/publishedPapers/2025/136694/pdf/index.html | Multi-camera dataset with criterion-specific labels for squat, lunge and RDL; compares vision, pose and multimodal approaches. |
| 4 | P | FormPro AI (EngrXiv preprint) | https://engrxiv.org/preprint/download/3953/6952/5640 | Real-time form feedback from MediaPipe joint angles with per-exercise rules. |
| 5 | P | Goswami, ASU FURI poster | https://forge.engineering.asu.edu/wp-content/uploads/2025/03/Ankith_Goswami_FURI.pdf | MediaPipe's 33 landmarks fed to CNN/LSTM to classify correct vs incorrect form (student poster). |
| 6 | P | Belede, Temple University AI project report | https://cis.temple.edu/~wangp/5603-AI/Project/2025F/Belede/Ai%20project%20report.docx | Rule-based biomechanics evaluation of squats, lunges, curls and push-ups (course report). |
| 7 | P | IRJET: Exercise Form Correction using Pose Estimation | https://www.academia.edu/44040367/IRJET_Exercise_Form_Correction_using_Pose_Estimation | PoseNet plus geometric heuristics, trained on 100+ exercise videos. |
| 8 | P | Counting Out Time: Class Agnostic Video Repetition Counting in the Wild (RepNet) | https://arxiv.org/abs/2006.15418 | Temporal self-similarity matrix and synthetic repetition training; Countix dataset; Google blog: https://www.research.google/blog/repnet-counting-repetitions-in-videos/ |
| 9 | P | A Short Note on Evaluating RepNet for Temporal Repetition Counting | https://arxiv.org/pdf/2411.08878 | RepNet performs strongly when evaluated properly (multi-speed); ESCounts beats it on RepCount-A. |
| 10 | P | Intelligent barbell squat coaching system based on CV and ML | https://pdf.arxiv.org/abs/2503.23731 | Diagnoses 6 squat issues with F1 69-100%, under 0.5 s per squat. |
| 11 | P | Domain Knowledge-Informed Self-Supervised Representations for Workout Form Assessment (Fitness-AQA, ECCV 2022) | https://arxiv.org/abs/2202.14019 | Pose estimators falter in gyms (angles, equipment occlusion); pose features can't reliably detect subtle errors. Dataset: https://zenodo.org/records/7310289 |
| 12 | P | Maynooth University squat form analysis (OpenCV + MediaPipe) | https://mural.maynoothuniversity.ie/id/eprint/21329/ | Student project on squat form analysis with MediaPipe. |
| 13 | P | UCSD overhead squat assessment with 3D pose estimation | https://library.ucsd.edu/dc/object/bb46200419/_2_1.pdf | Overhead squat assessment using 3D pose estimation (report). |
| 14 | P | AI Personal Trainer Research (cheung0) | https://cheung0.github.io//files/AI%20Personal%20Trainer%20Research.pdf | AI personal trainer research report citing BlazePose for pose tracking. |
| 15 | P | Accuracy Evaluation of 3D Pose Estimation with MediaPipe Pose for Physical Exercises (CDBME 2023) | https://doaj.org/article/b1b1d4db2666494cacf7bcbcee8cdaa3 | Accuracy depends heavily on camera viewing angle and the exercise; it drops quickly off optimal conditions. |
| 16 | P | Accuracy Evaluation of 3D Pose Reconstruction via Stereo Camera Fusion with MediaPipe (Sensors 2024) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11644880/ | The single-view depth (z) axis is very noisy; stereo fusion is proposed. |
| 17 | P | Comparison of marker-less 2D image-based methods for infant pose estimation | https://arxiv.org/pdf/2410.04980 | MediaPipe performed worst from a diagonal view; retraining didn't fully close the gap. |
| 18 | P | Chalmers master's thesis: MediaPipe vs optical motion capture (squat, rehab) | https://odr.chalmers.se/bitstreams/6e3607e0-8e8c-4f7f-b33e-c92bfab18210/download | Camera view and metric definitions must be chosen carefully; interpret per metric. |
| 19 | P | Cridlig, Bologna MSc thesis (MediaPipe + TCN + RepNet) | https://amslaurea.unibo.it/39099/1/cridlig_nicolasivan_thesis.pdf | Chains MediaPipe landmarks, a classifier and RepNet for counting. |
| 20 | P | Scientific Reports 2025 (Essex): MediaPipe angle-based rep counter | https://repository.essex.ac.uk/42394/1/s41598-025-29062-7.pdf | Joint-angle repetition counter claimed to beat RepNet. |
| 21 | P | FLEX: Large-Scale Multi-Modal Multi-Action Dataset for Fitness AQA | https://arxiv.org/abs/2506.03198 | 20 weighted exercises, 38 subjects, 5 views plus sEMG; multimodal and multi-view inputs improve AQA. |
| 22 | P | FitAQA: Benchmark of Fitness AQA for Multimodal LLMs | https://arxiv.org/pdf/2608.08736 | MLLMs show limited recognition and temporal localisation of quality-relevant posture evidence. |
| 23 | P | Can Vision Language Models Judge Action Quality? An Empirical Evaluation (CVPRW 2026) | https://arxiv.org/abs/2604.08294 | VLMs face a fundamental difficulty with fine-grained movement quality; bias fixes help little. |
| 24 | P | Ital-IA 2025 paper 23 (CEUR) | https://ceur-ws.org/Vol-4121/Ital-IA_2025_paper_23.pdf | Uses Fitness-AQA (3 gym exercises, each with 2 annotated errors). |
| 25 | P | TransRAC: Multi-scale Temporal Correlation with Transformers for Repetitive Action Counting (CVPR 2022) | https://arxiv.org/abs/2204.01018 | Introduces RepCount (1,451 videos, about 20k cycle annotations) with interruptions and variable cycles. Code: https://github.com/SvipRepetitionCounting/TransRAC |
| 26 | P | Efficient Action Counting with Dynamic Queries | https://arxiv.org/pdf/2403.01543 | Follow-up counting method evaluated on RepCount. |
| 27 | P | Repetitive Action Counting with Hybrid Temporal Relation Modeling | https://arxiv.org/pdf/2412.07233 | Follow-up counting method compared with TransRAC. |
| 28 | P | FormCoach: Lift Smarter, Not Harder | https://arxiv.org/abs/2508.07501 | 1,700 expert-labelled pairs, 22 exercises; best VLM (GPT-4.1) 58.2% accuracy, about 74% hallucination; misses subtle errors. |
| 29 | P | BioCoach: From 3D Pose to Prose | https://arxiv.org/pdf/2603.26938 | Feeding 3D kinematics and joint angles to a streaming VLM improves biomechanical correctness (Drexel news: https://drexel.edu/news/archive/2026/june/biocoach-ai-cv-exercise-form-coaching). |
| 30 | P | Pose Trainer: Correcting Exercise Posture using Pose Estimation | https://arxiv.org/abs/2006.11718 | OpenPose plus vector geometry; about 80% of bad-form reps flagged, with misses at the proper/improper fringe. |
| 31 | P | Gym Trainer Application using Machine Learning | https://www.academia.edu/85064636/Gym_Trainer_Application_using_Machine_Learning | Student paper on a pose-based gym trainer app. |
| 32 | P | EgoExo-Fitness (ECCV 2024) | https://arxiv.org/abs/2406.08877 | 32 h of ego and exo fitness video with technical keypoint verification, comments and quality scores. |
| 33 | P | Live Fitness Coaching as a Testbed for Situated Interaction (QEVD) | https://arxiv.org/abs/2407.08101 | 474+ h dataset with live coach feedback, corrections and rep counts; Qualcomm page: https://www.qualcomm.com/developer/software/qevd-dataset |
| 34 | P | Validation of HPE and Human Mesh Recovery for Clinically Relevant Motion Data | https://arxiv.org/pdf/2503.14760 | Validation of video-based pose methods for clinical motion data. |
| 35 | P | JMIR Rehab preprint 102399: lateral-view smartphone squat validity | https://preprints.jmir.org/preprint/102399 | Squat ICC 0.773 with low-confidence frames removed; 0.428 and RMSE 25° when all frames kept. |
| 36 | P | Monocular 3D pose accuracy across movements (arXiv 2512.06783) | https://arxiv.org/abs/2512.06783 | Depth ambiguity makes single-camera accuracy sensitive to viewing angle; a low average error hides per-movement error. |
| 37 | R | A Decade of Action Quality Assessment (survey) | https://arxiv.org/pdf/2502.02817 | Screens 195 papers and 26 datasets across AQA subfields. |
| 38 | R | A Comprehensive Survey of AQA: Method and Benchmark | https://arxiv.org/pdf/2412.11149 | Unified AQA benchmark; earlier surveys missed multimodal work. |
| 39 | R | A Survey of Video-based Action Quality Assessment | https://arxiv.org/pdf/2204.09271 | Methods, datasets and metrics, mostly sports and medical. |
| 40 | R | A Survey of Deep Learning in Sports Applications | https://arxiv.org/pdf/2307.03353 | Broad survey of perception, comprehension and decision in sports DL. |
| 41 | P | Smartphone camera placement and AI rep counting (JMIR mHealth 2026, e82412) | https://mhealth.jmir.org/2026/1/e82412/ | 44 students: about 61% mean detection; squats 95.5% (diagonal, 200 cm) vs 0% (side, 90 cm). Placement matters. |
| 42 | P | Pūioio: On-device smartphone exercise repetition counting | https://arxiv.org/pdf/2308.02420 | About 99.3% squat and 99.3% push-up counting accuracy on a small sample. |
| 43 | P | Intelligent Repetition Counting for Unseen Exercises: Few-Shot with Sensor Signals | https://arxiv.org/pdf/2410.00407 | IMU-based few-shot counting reframed as classification. |
| 44 | P | Markerless Pose Estimation for Resistance Training Technique Assessment | https://arxiv.org/pdf/2608.24384 | Side-on view is most accurate; knee-angle deviation grows in occluded regions toward frontal; viewpoint and occlusion are under-explored. |
| 45 | P | Impact of Patient Orientation in Single- and Multi-View Camera Environments for AI Rehab Monitoring | https://arxiv.org/pdf/2609.35726 | Tests -90° to 90° viewpoints and a two-camera setup for detecting incorrect reps. |
| 46 | P | Monocular Total Capture | https://arxiv.org/pdf/1812.01598 | Errors worsen with elevated views and back views due to self-occlusion and foreshortening. |
| 47 | P | Self-Occluded Human Pose Recovery in Monocular Video Motion Capture | https://research-portal.uea.ac.uk/en/publications/self-occluded-human-pose-recovery-in-monocular-video-motion-captu/ | Addresses self-occlusion in monocular capture. |
| 48 | P | Exercise quantification from single-camera markerless 3D pose (Heliyon 2024) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10951609/ | 2D pose needs precise camera placement and limits the angles that can be analysed. |
| 49 | P | Markerless vs marker-based 3D pose for S&C exercise identification (Stellenbosch) | https://scholar.sun.ac.za/items/d7fe50e3-44e5-476d-9b81-7080b250c5e8 | Markerless is good enough for exercise identification, where accuracy isn't paramount. |
| 50 | R | The Potential of CV-Based Marker-Less Human Motion Analysis for Rehabilitation | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8492027/ | Review of markerless motion analysis for rehab. |
| 51 | R | Commercial vision sensors and AI pose frameworks for markerless analysis in sports/exercise: mini review | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12378739/ | Mini review of commercial sensors and pose frameworks. |
| 52 | P | ProfVLM: proficiency estimation as generative VLM | https://arxiv.org/pdf/2509.26278 | Outputs a proficiency label plus natural-language feedback. |
| 53 | P | LLM-FMS: functional movement screen AQA dataset | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11896072/ | LLMs score FMS from annotated keyframes rather than video. |
| 54 | P | PoseRAC: Joint-Based Repetitive Action Counting | https://arxiv.org/pdf/2308.08632 | Pose-landmark counter: MAE 0.211, OBO 0.599 on RepCount. |
| 55 | P | Abedi et al., segmentation and counting from skeletal joints | https://arxiv.org/abs/2304.09735 | Skeleton-based repetition segmentation and counting. |
| 56 | P | Viewpoint-Invariant Exercise Repetition Counting | https://arxiv.org/pdf/2107.13760 | Skeleton self-similarity to make counting robust to viewpoint. |
| 57 | P | Recognition and Repetition Counting for Complex Physical Exercises with Deep Learning | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6387025/ | DL recognition plus counting of complex exercises. |
| 58 | P | PersonalPT: one-shot skeletal repetitive action counting for physical therapy | https://esdat.ucsd.edu/node/391 | One-shot skeleton counting for PT (Smart Health 2024). |
| 59 | P | Rehab-Pile: Standardized Benchmark for Skeleton-Based Rehab Assessment | https://arxiv.org/pdf/2507.21018 | Benchmark built on UI-PRMD and KIMORE. |
| 60 | P | A Deep Learning Framework for Assessing Physical Rehabilitation Exercises | https://arxiv.org/pdf/1901.10435 | First deep networks for rehab exercise quality (UI-PRMD). |
| 61 | P | Point Cloud Transformer for Remote Rehab Assessment | https://arxiv.org/pdf/2606.30309 | Evaluated on UI-PRMD, KIMORE and IRDS. |
| 62 | P | Error-Guided Pose Augmentation for Rehab Assessment | https://arxiv.org/pdf/2506.09833 | Generates targeted error data to improve assessment. |
| 63 | P | Rehab exercise classification on KIMORE/UI-PRMD (Multimedia Tools & Apps 2024) | https://link.springer.com/article/10.1007/s11042-024-19092-0 | 93.1% (KIMORE) and 99.7% (UI-PRMD) classification accuracy. |
| 64 | P | UI-PRMD dataset | https://webpages.uidaho.edu/ui-prmd/ | 10 PT movements (deep squat, lunge, etc.), 10 healthy subjects, skeletal data. |
| 65 | P | Human Exercise Posture Analysis based on Pose Estimation (IEEE 2021) | https://ieeexplore.ieee.org/document/9390870 | Improved OpenPose plus form definitions to analyse posture. |
| 66 | P | Fitcam (Journal of Big Data 2024) | https://journalofbigdata.springeropen.com/articles/10.1186/s40537-024-00915-8 | OpenPose + LSTM, over 90% on push-up, sit-up, squat and plank. |
| 67 | P | A Study of Human Fitness Pose Classification Using ANNs (CSU Fullerton) | https://par.nsf.gov/servlets/purl/10596878 | GRU on MoveNet keypoints exceeds 95%. |
| 68 | P | Gym workout analysis (University of Moratuwa) | https://dl.lib.uom.lk/bitstreams/9def1111-4962-4447-b412-dc8dc33fe5d8/download | Raw coordinates are sensitive to orientation, distance and framing. |
| 69 | P | Recognizing Exercises and Counting Repetitions in Real Time | https://arxiv.org/pdf/2005.03194 | 98.4% exercise recognition plus a real-time counter. |
| 70 | P | Automated Deadlift Techniques Assessment and Classification Using DL (MDPI AI 2025) | https://mdpi.com/2673-2688/6/7/148 | Single frames are insufficient; temporal information is needed to tell techniques apart. |
| 71 | P | SportRxiv: deadlift form classification from biomechanical linkage | https://sportrxiv.org/index.php/server/preprint/download/471/995/930 | FFNN classifies good vs bad deadlifts; 3 camera angles. |
| 72 | R | Machine Learning Applications in Spine Biomechanics | https://arxiv.org/pdf/2401.06174 | MeTRAbs predicted 20° trunk flexion when deadlifters actually extend: a pose-accuracy caution. |
| 73 | P | DeepLabCut lumbar flexion-extension validity (J Appl Biomech 2022) | https://par.nsf.gov/servlets/purl/10342304 | Acceptable lumbar kinematics vs Vicon. |
| 74 | P | CDC/NIOSH computer-vision trunk flexion from lifting video | https://stacks.cdc.gov/view/cdc/224799/cdc_224799_DS1.pdf | Mean absolute trunk-angle difference of 14.7° vs mocap. |
| 75 | P | Automating Powerlifting Judging through Keypoint Detection (Stanford CS231N 2024) | https://cs231n.stanford.edu/2024/papers/automating-powerlifting-judging-through-keypoint-detection.pdf | MoveNet keypoints vs human judges on meet footage; "first step". |
| 76 | P | Powerlifting Vision (University of Hawaii) | https://huntervt.github.io/pdf/plvision.pdf | Pose pipelines for depth calls "need massive improvement". |
| 77 | P | Janisch et al. 2026, BMC Musculoskeletal Disorders: 2D knee frontal-plane methods | https://www.medicalschool-hamburg.de/files/inhalte/News/2026/2026-janisch_et_al-bmc_musculoskeletal_disorders.pdf | 2D video not supported for frontal-plane kinematics when high accuracy is needed; "valgus" on 2D mixes hip motions. |
| 78 | P | Beta CV app for knee valgus angle: validity and reliability | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10177945/ | Excellent reliability; validity tested against Kinovea, not 3D. |
| 79 | P | Reliability of Frontal Plane Knee Alignment via Remote Protocol | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10681043/ | FPPA reliable between days, but reliability is not validity. |
| 80 | P | LiFT: Lightweight Fitness Transformer | https://arxiv.org/html/2506.06480v1 | Exercise detection plus rep counting across many exercises; prior work did one task at a time. |
| 81 | P | Two-stage rep end-point plus form-error transformer (Choudhary et al.) | https://itzsid.github.io/publications/Choudhary13acvc.pdf | 52 form-error types across 986k reps and 26 exercises, with severity levels. |
| 82 | P | Every Shot Counts (ESCounts) | https://arxiv.org/pdf/2403.18074 | SOTA on RepCount: OBO 0.39 to 0.56, MAE 0.38 to 0.21. |
| 83 | P | Rethinking temporal self-similarity for repetitive action counting | https://arxiv.org/pdf/2407.09431 | Claims SOTA on RepCount, UCFRep and Countix. |
| 84 | P | GMFL-Net: repetitive action counting | https://arxiv.org/html/2409.00330v1 | SOTA on pose-level counting benchmarks (incl. Countix-Fitness-pose). |
| 85 | P | MM-Fit: multimodal exercise dataset (IMWUT 2020) | https://www.research.ed.ac.uk/en/datasets/mm-fit-dataset-physical-exercise-workout-sessions-video/ | Synced wearables plus multi-view RGB-D and pose; recognition and counting baselines. |
| 86 | P | MuJo: Multimodal Joint Feature Space Learning for HAR | https://arxiv.org/html/2406.03857v3 | Macro F1 0.942 on MM-Fit. |
| 87 | P | VI-Net: View-Invariant Quality of Human Movement Assessment | https://mdpi.com/1424-8220/20/18/5258 | Appearance-trained models drop significantly on unseen viewpoints; QMAR multi-view dataset. |
| 88 | P | SkillFormer: multi-view skill assessment | https://arxiv.org/pdf/2505.08665v3 | Multi-view fusion improves exocentric accuracy by 14%. |
| 89 | P | Redundancy-Aware Ego-Exo Fusion for Proficiency Estimation | https://arxiv.org/pdf/2608.25736 | SOTA on EgoExo-Fitness via learned view selection. |
| 90 | P | Parameter-Efficient Multi-View Proficiency Estimation | https://arxiv.org/pdf/2605.03848 | From discriminative classification to generative feedback. |
| 91 | P | View-Invariant Human Movement Assessment (Sardari PhD thesis, Bristol) | https://research-information.bris.ac.uk/en/studentTheses/view-invariant-human-movement-assessment/ | Unsupervised view-invariant 3D posture from 2D RGB. |
| 92 | P | App-Based Feedback for Rehab Exercise Correction in Knee/Hip OA (Kaia Motion Coach, JMIR 2021) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8317029/ | App vs physio agreement 0.828 vs physio-physio 0.833 (n=24). |
| 93 | P | OpenCap: Human movement dynamics from smartphone videos | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10586693/ | Validated vs mocap and force plates; 25x faster than lab. |
| 94 | P | OpenCap Monocular (2026 preprint) | https://arxiv.org/abs/2603.24733 | Single phone validated for walking, squat and sit-to-stand. |
| 95 | R | Video-Based Markerless Motion Capture for Clinical/Rehab Biomechanics: PRISMA-ScR | https://arxiv.org/pdf/2609.18667 | Scoping review of validated architectures and clinical readiness. |
| 96 | R | OpenCap review (Biomechanics, MDPI 2025) | https://www.mdpi.com/2673-7078/5/4/88 | RMSE 4-6° in healthy gait; larger errors in pathological gait. |
| 97 | P | Quantifying gait compensation in knee OA with OpenCap | https://pubmed.ncbi.nlm.nih.gov/41323870/ | OpenCap captures KOA gait abnormalities. |
| 98 | P | An Examination of Wearable Sensors and Video Data Capture for Exercise Classification | https://arxiv.org/abs/2307.04516 | One camera beats one IMU by about 10 pp; 3 IMUs needed to beat video; camera+IMU best. |
| 99 | P | Dibenedetto et al., LLM prompting for posture-based exercise suggestions (CEUR) | https://ceur-ws.org/Vol-3823/9_Dibenedetto_prompting_158.pdf | Angle thresholds from 3D pose trigger LLM corrective-exercise suggestions. |
| 100 | P | SportsGPT | https://arxiv.org/pdf/2512.14121v2 | LLM sports motion assessment from keypoints and joint angles. |
| 101 | P | LLM rehab exercise feedback via prompt engineering | https://arxiv.org/html/2505.18412v1 | LLMs generate rehab quality feedback from body-joint analysis. |
| 102 | P | Pose Tutor: Explainable Pose Correction in the Wild (CVPRW 2022) | https://openaccess.thecvf.com/content/CVPR2022W/CVSports/html/Dittakavi_Pose_Tutor_An_Explainable_System_for_Pose_Correction_in_the_CVPRW_2022_paper.html | Angle-likelihood explains which joints are malformed (yoga, Pilates, Kung Fu). |
| 103 | P | CARE: Counterfactual Algorithmic Recourse for Pose Correction (WACV 2024) | https://openaccess.thecvf.com/content/WACV2024/papers/Dittakavi_CARE_Counterfactual-Based_Algorithmic_Recourse_for_Explainable_Pose_Correction_WACV_2024_paper.pdf | Minimal corrections toward a nearby correct pose. |
| 104 | P | PoseGuru (CVPRW 2025) | https://openaccess.thecvf.com/content/CVPR2025W/XAI4CV/html/Dittakavi_PoseGuru_Landmarks_for_Explainable_Pose_Correction_using_Exemplar-Guided_Algorithmic_Recourse_CVPRW_2025_paper.html | Exemplar-guided landmark recourse, expert-evaluated. |
| 105 | P | PosePilot: Edge-AI Posture Correction | https://arxiv.org/pdf/2505.19186 | Edge-device posture correction for exercises. |
| 106 | P | Pose estimation model comparison: OpenPose, PoseNet, MoveNet, MediaPipe (Future Internet 2022) | https://doaj.org/article/bf062d57dd3c4566ad6a8ab8ac902ca0 | MoveNet best overall for detecting poses in images and video. |
| 107 | P | From Skeletons to Semantics: hybrid edge action detection | https://arxiv.org/pdf/2603.29777 | Chose YOLO-Pose; MediaPipe's top-down pipeline degrades in crowds. |
| 108 | P | Multi-framework HPE benchmark on Panoptic (Croatian journal, 2026) | https://hrcak.srce.hr/350091 | OpenPose, YOLO, RTMPose, Sapiens and MoveNet compared under occlusion and crowding. |
| 109 | P | Newborn video pose estimation comparison | https://arxiv.org/html/2406.15649v1 | RTMPose most accurate; MediaPipe fastest. |
| 110 | P | OpenPose: Realtime Multi-Person 2D Pose Estimation using PAFs | https://arxiv.org/pdf/1812.08008 | Foundational multi-person pose estimator used by many trainers. |
| 111 | P | Action Quality Assessment Across Multiple Actions (AQA-7) | https://arxiv.org/pdf/1812.06367 | 1,189 Olympic samples across 7 actions, overall scores only. |
| 112 | P | FineDiving: procedure-aware AQA | https://arxiv.org/pdf/2204.03646 | Fine-grained diving dataset for procedure-aware scoring. |
| 113 | P | Group-aware Contrastive Regression for AQA | https://arxiv.org/pdf/2108.07797 | AQA method on MTL-AQA and related datasets. |
| 114 | P | MoAKE: All-in-One AQA via Mixture of Action Knowledge Experts | https://arxiv.org/pdf/2607.19826 | Unified AQA across action types. |
| 115 | P | 3D Pose Based Feedback for Physical Exercises | https://arxiv.org/pdf/2208.03257 | Squats, lunges and planks with correct/incorrect labels; about 89-91% accuracy. |
| 116 | P | Muscle Vision: Real-Time Keypoint-Based Pose Classification | https://arxiv.org/pdf/2203.12111 | Keypoint-based exercise pose classification. |
| 117 | P | LiftMate: Gym Exercise Posture Correction and Classification (KES 2025) | https://pure.uj.ac.za/en/publications/liftmate-gym-exercise-posture-correction-and-classification/ | Near-100% on curl, plank and squat with a 3-layer net. |
| 118 | P | Using Learnable Physics for Real-Time Exercise Form Recommendations | https://arxiv.org/pdf/2310.07221 | Physics-informed real-time form recommendations. |
| 119 | P | Real-Time Fitness Exercise Classification and Counting from Video Frames | https://arxiv.org/html/2411.11548 | Over 99% classification on 4 exercises; trained with synthetic InfiniteRep. |
| 120 | P | InfiniteForm: synthetic, minimal-bias fitness dataset | https://arxiv.org/abs/2110.01330 | About 60k synthetic images, 15 pose categories. |
| 121 | P | Benchmarking 3D Human Pose Estimation Models under Occlusions | https://arxiv.org/abs/2504.10350 | Distal joints (wrists, feet) are consistently most vulnerable to occlusion. |
| 122 | P | Malta MSc: powerlifting-specific pose model | https://www.um.edu.mt/library/oar/handle/123456789/138342 | PCK 91.31% on powerlifting footage. |
| 123 | P | Olympic weightlifting barbell detection/lift recognition (SciTePress 2024) | https://www.scitepress.org/Papers/2024/129974/129974.pdf | Bar detection about 90% mAP@50 but lift recognition 74%. |
| 124 | P | Concurrent validity of smartphone apps for barbell velocity in powerlifting (PLOS ONE 2024) | https://pmc.ncbi.nlm.nih.gov/articles/PMC11575817 | Apps can match a linear transducer for mean velocity; Qwik VBT best. |
| 125 | P | Validation of a commercially available mobile app for VBT (Metric, PeerJ 2024) | https://peerj.com/articles/17789 | CV app validated vs 3D mocap for rep detection, ROM and velocity. |
| 126 | P | Validity of the iLOAD app for resistance training monitoring | https://peerj.com/articles/7372 | Validity of a VBT app. |
| 127 | R | Systematic review of smartphone VBT apps (Puppyn & Brughelli, AUT) | https://openrepository.aut.ac.nz/bitstreams/c29c52ac-01ca-46cf-a7b5-df6e6661f9f6/download | 4 apps acceptable; fine for field use, not high-precision research. |
| 128 | P | Deep learning gesture recognition in a vision-based AR smart mirror (Brescia) | https://techxplore.com/news/2022-09-deep-learning-augmented-smart-mirror.amp | Low-cost smart mirror measures arm movements in simple exercises. |
| 129 | R | AI markerless HPE for exercise coaching (PeerJ review) | https://peerj.com/reviewer-match/129606 | Posture, reps, ROM and recognition: correct only in controlled settings; dataset bias; weak at home. |
| 130 | R | CV for physical rehabilitation: PRISMA systematic review (Frontiers 2026) | https://www.frontiersin.org/journals/rehabilitation-sciences/articles/10.3389/fresc.2026.1906327/full | Feedback rarely goes beyond summary "knowledge of results". |
| 131 | R | Yoma et al., reliability/validity of markerless mocap for lower-limb and trunk (J Sports Sci 2025) | https://salford-repository.worktribe.com/OutputFile/4150702 | Results vary by task, system and statistics, making comparison hard. |
| 132 | R | Applications and limitations of markerless mocap for clinical gait (PeerJ 2022) | https://peerj.com/articles/12995 | Joint centres and angles not yet accurate enough for clinical use. |
| 133 | R | Markerless human pose estimation for biomedical applications: a survey | https://arxiv.org/pdf/2308.00519 | Survey of markerless HPE in biomedicine. |
| 134 | P | JMIR 2026 summary: MediaPipe Pose app, 216 participants | https://jmir.org/2026/1/e106128 | 97.2% movement-estimation accuracy, young healthy mostly-male sample. |
| 135 | R | Camera-Based Fitness Workouts (CUNY open textbook chapter) | https://pressbooks.cuny.edu/homefitness/chapter/camera-based-fitness-workouts/ | Counting accuracy varies by configuration; too close crops the body, too far loses it. |
| 136 | T | ATG.AI squat depth judge (GitHub) | https://github.com/RanGlad12/ATG.AI | Deep-learning hip-crease vs knee depth judge. |
| 137 | T | FormCheck (ctsc, GitHub) | https://github.com/ctsc/FormCheck | Squat, deadlift and bench; 4-state rep machine; 0-100 per-rep form score. |
| 138 | T | RepVal (GitHub) | https://github.com/lc-leonardo/RepVal | Real-time form correction plus bulk video processing. |
| 139 | T | APT Fitness Assistant (evintkoo) | https://evintkoo.github.io/projects/apt-fitness.html | Compares joint angles with reference ranges and flags deviations. |
| 140 | T | AutoRep (GitHub) | https://github.com/TylerVenner/AutoRep | Motion-based and pose-based rep counters. |
| 141 | T | ProFitness (GitHub) | https://github.com/RandomForestGump/ProFitness | Pose-based fitness repo. |
| 142 | T | RepDetect (Android, GitHub) | https://github.com/giaongo/RepDetect | Kotlin + MediaPipe real-time form feedback and counting. |
| 143 | T | DeepFit (GitHub) | https://github.com/namanarora42/DeepFit | "Your digital personal trainer" pose project. |
| 144 | T | GitHub topic: rep-counter | https://github.com/topics/rep-counter?l=python | Many Python rep-counter repos. |
| 145 | T | AI Workout Manager (airscholar) | https://github.com/airscholar/AI-Workout-Manager | Counts reps from landmark-angle stages. |
| 146 | T | ShadowCoach FormTracker | https://awesome.ecosyste.ms/projects/github.com%2Fondiekelijah%2Fshadowcoach-formtracker | Push-up form tracking with angle-based stages. |
| 147 | T | Posecheck Pro (GitHub) | https://github.com/Pythonpreran/Posecheck-Pro | Spoken-style cues for arm raises and squats. |
| 148 | T | Exercise-Correction (NgoQuocBao1010) | https://github.com/NgoQuocBao1010/Exercise-Correction | Separate ML models detect errors in curl, plank, squat and lunge. |
| 149 | T | PureStrength / FormCheck AI (iOS) | https://apps.apple.com/app/id1621267448 | AI PT for squat and deadlift; checks shoulder rounding and lockout. |
| 150 | T | FormLens: AI Form Check Coach (iOS) | https://apps.apple.com/app/id6756815264 | Film a lift, get an AI form score and plan. |
| 151 | T | FormLab (iOS) | https://apps.apple.com/us/app/formlab/id6758761079 | Real-time squat coach using Apple Vision. |
| 152 | T | formcheck ai (iOS) | https://apps.apple.com/app/id6741048432 | Squat, bench and deadlift form app. |
| 153 | T | GymSpotter - Lift Form Checker (iOS) | https://apps.apple.com/app/id6758680413 | Rep-by-rep form feedback on filmed lifts. |
| 154 | T | Form Fix: AI Form Check Coach (iOS) | https://apps.apple.com/us/app/id6745452870 | Upload-based form check. |
| 155 | T | FormCoach: Lift Safe & Smart (iOS) | https://apps.apple.com/us/app/formcoach/id6754677989 | Form coaching app. |
| 156 | T | Squat Trainer (iOS) | https://apps.apple.com/sn/app/squat-trainer/id6755944355 | Free squat-only real-time voice coaching. |
| 157 | T | VeraLift: AI Form Check (iOS) | https://apps.apple.com/app/id6767809697 | Conservative, timestamped technique feedback on uploads. |
| 158 | T | FormCheck (iOS, id1563633996) | https://apps.apple.com/ma/app/formcheck/id1563633996 | Form-check app listing. |
| 159 | T | Engadget: "You can't nail the perfect squat with just an iPhone app" (Kaia) | https://www.engadget.com/2018-06-27-the-perfect-squat-app-ai-trainer.html | Couldn't catch every error; one correction per squat. |
| 160 | T | Ultralytics Workouts Monitoring / AIGym | https://docs.ultralytics.com/guides/workouts-monitoring | YOLO-pose keypoint angles count push-ups, pull-ups and ab reps. |
| 161 | T | Ultralytics blog: smart fitness with YOLO11 | https://www.ultralytics.com/blog/smart-fitness-technology-enabled-by-ultralytics-yolo11 | YOLO pose for gym monitoring. |
| 162 | T | Exercise detector/counter with YOLOv8-Pose on NVIDIA Jetson (Hackster) | https://www.hackster.io/yuyoujiang97/exercise-detector-counter-with-yolov8-pose-on-nvidia-jeson-d2da4a | Edge exercise counter. |
| 163 | T | Peloton Guide (TechRadar / Tom's Guide) | https://www.tomsguide.com/reviews/peloton-guide-review | TV camera compares your form with the instructor's. |
| 164 | T | Tempo Move vs Peloton Guide (Reviewed) | https://reviewed.com/health/features/peloton-guide-vs-tempo-move-smart-workout-camera-better | Tempo's AI feedback stood out. |
| 165 | T | Kemtai web fitness app | https://connectthewatts.com/2021/05/12/kemtai-a-new-web-based-fitness-app-and-tempo-competitor/ | Webcam form correction and rep counting in browser. |
| 166 | T | Qwik VBT (iOS) | https://apps.apple.com/uy/app/qwik-vbt/id1660094818 | Velocity, ROM and bar path from video. |
| 167 | T | Metric VBT (iOS) | https://apps.apple.com/us/app/id1595510857 | 60+ exercises; user reported a reversed bar path, later fixed. |
| 168 | T | Keelo Lift (iOS) | https://apps.apple.com/sr/app/keelo-lift/id1444813891 | 60 fps bar tracking coloured by speed. |
| 169 | T | WL Analysis (iOS) | https://apps.apple.com/gb/app/wl-analysis/id1541855037 | Auto barbell detection; metrics are approximations. |
| 170 | T | Iron Path (iOS) | https://apps.apple.com/us/app/iron-path/id955364910 | Reviewer saw partial traces (about half the ROM). |
| 171 | T | FormAI / PushupTracker (MoveNet, browser) | https://kelaenderkoe.pages.dev/Function-https-github.com/nonhorrific/PushupTracker | MoveNet joint angles count push-ups with voice feedback. |
| 172 | T | POSTRA (Devpost) | https://devpost.com/software/phytech | TF.js MoveNet down/up state rep counter. |
| 173 | T | rep-counter library (cybertroniankelvin) | https://cybertroniankelvin.github.io/rep-counter | Angle-threshold counting, no training needed. |
| 174 | T | Graviton push-up counter (PoseNet) | https://perceptronv.github.io/ai/ml/pose-estimation/fitness/2021/01/16/Graviton.html | Browser-only push-up counter. |
| 175 | T | ai-workout-assistant (reevald) | https://github.com/reevald/ai-workout-assistant | MoveNet; 1 rep = Down to Up. |
| 176 | T | Next-Generation Pose Detection with MoveNet and TF.js (TensorFlow blog) | https://blog.tensorflow.org/2021/05/next-generation-pose-detection-with-movenet-and-tensorflowjs.html | MoveNet trained on fitness, dance and yoga poses. |
| 177 | T | VNOpenAI pushup-counter-app | https://www.Github.com/VNOpenAI/pushup-counter-app | Push-up counter app. |
| 178 | T | Activities-Pose-Estimation (hugozanini) | https://www.github.com/hugozanini/Activities-Pose-Estimation | Browser activity pose estimation. |
| 179 | T | Zenia AI yoga (VentureBeat) | https://venturebeat.com/ai/zenia-is-using-computer-vision-to-build-an-ai-driven-fitness-trainer | Front camera tracks joints for real-time yoga feedback. |
| 180 | T | Exer AI coach (VentureBeat) | https://venturebeat.com/ai/exer-launches-ai-based-fitness-coach-on-your-mobile-phone | Edge AI with voice posture coaching (Perfect Plank). |
| 181 | T | Apple Vision: Detecting human body poses in images | https://developer.apple.com/tutorials/data/documentation/vision/detecting-human-body-poses-in-images.md | Subject must fill the frame; loose clothing reduces accuracy. |
| 182 | T | WWDC20 10043: Build an Action Classifier with Create ML | https://developer.apple.com/wwdc20/10043 | Train exercise classifiers on Vision body pose. |
| 183 | T | FormKit (GitHub) | https://github.com/LachPawel/FormKit | Vision + SwiftUI on-device rep-counting template. |
| 184 | T | ML Kit pose classification options | https://developer.google.com/ml-kit/vision/pose-detection/classifying-poses | k-NN pose classifier and rep counting; about 100 samples per class. |
| 185 | T | ML Kit Pose Detection blog | https://developers.googleblog.com/ml-kit-pose-detection-makes-staying-active-at-home-easier/ | 33 landmarks, Fast and Accurate modes. |
| 186 | T | MM-Fit Exercise Recognition (GitHub) | https://github.com/quanghuy0497/MM-Fit_Excercise_Recognition | MM-Fit recognition code. |
| 187 | T | LearnOpenCV: AI Fitness Trainer using MediaPipe | https://learnopencv.com/ai-fitness-trainer-using-mediapipe | Squat state machine with beginner/pro feedback. |
| 188 | T | AI_trainer (Kedyi) | https://github.com/Kedyi/AI_trainer | Curl counting from the shoulder-elbow-wrist angle. |
| 189 | T | How we built an AI gym trainer with MediaPipe, React and RAG (DEV) | https://dev.to/gitmwon/how-we-built-an-ai-gym-trainer-using-mediapipe-react-and-rag-5a61 | Rule-based angle thresholds, no custom training. |
| 190 | T | Exercise_Recognition_AI (chrisprasanna) | https://github.com/chrisprasanna/Exercise_Recognition_AI | BlazePose joint angles track exercise and count reps. |
| 191 | T | AI-Trainer (HARSH-nith) | https://github.com/HARSH-nith/AI-Trainer | Pose-based trainer repo. |
| 192 | T | Sency AI motion (AthleTech News) | https://athletechnews.com/sency-transforms-fitness-market-ai-motion-tracking/ | SDK for posture, reps, real-time feedback and fitness score. |
| 193 | T | REP AI: Workout Rep Counter (Android) | https://play.google.com/store/apps/details?id=app.posedetector | Rep counter app. |
| 194 | T | QuickPose iOS SDK | https://www.github.com/quickpose/quickpose-ios-sdk | MediaPipe/BlazePose SDK with rep counters and form analysis. |
| 195 | T | QuickPose FitCount | https://github.com/quickpose/FitCount | Squat and curl counter demo; custom angle-range engine. |
| 196 | T | RepVision AI Gym Rep Counter (iOS) | https://apps.apple.com/app/id6755109937 | Rep counter app. |
| 197 | T | Reptivity (iOS) | https://apps.apple.com/us/app/reptivity/id6443751070 | Rep tracking app. |
| 198 | T | SquatEye: Squat Depth Check (iOS) | https://apps.apple.com/ca/app/id6758864722 | PASS/FAIL/BORDERLINE depth from hip-crease vs knee. |
| 199 | T | Judge Steely (GitHub) | https://www.github.com/akacaali/Judge-Steely | Training-oriented lift judging tool. |
| 200 | T | InfiniteRep synthetic dataset (Infinity AI) | https://cs.paperswithcode.com/dataset/infiniterep | About 1,000 synthetic avatar videos with frame-level rep counts. |
| 201 | T | NuvoMotion (UCSB capstone smart mirror) | https://web.ece.ucsb.edu/~yoga/capstone/static/img/projects/poster/nuvomotion_poster.pdf | On-device exercise detection, counting and feedback on an NPU. |
| 202 | T | fimi smart mirror (Univ. Hamburg) | https://basecamp-demos.informatik.uni-hamburg.de/expo2020/entries/fimi-a-smart-mirror-application-for-workouts-with-form-and-movement-correction-feedback/ | Flags wrong pose for up to 10 people. |
| 203 | T | YogAI Raspberry Pi smart mirror (MagPi) | https://www.raspberrypi.com/news/yoga-training-with-yogai-and-a-raspberry-pi-smart-mirror-the-magpi-issue-80/ | Real-time pose recognition was harder than building the mirror. |
| 204 | T | From Flab to Ab: Smart Home Gym (Utah) | https://my.ece.utah.edu/~kstevens/4710/reports/flab-to-ab.pdf | OpenPose on Jetson Nano behind a two-way mirror. |
| 205 | T | Magic AI fitness mirror test (Good Housekeeping via Yahoo) | https://uk.style.yahoo.com/fitness-mirror-replace-pt-ghi-112900129.html | Form tracking "hit and miss". |
| 206 | T | AI Fitness Coach with Google AI Studio (DEV) | https://dev.to/shaikhhas/ai-fitness-coach-real-time-exercise-form-analysis-using-google-ai-studio-14i9 | Gemini flags back angle and knee position with timestamps. |
| 207 | T | How to build a real-time AI gym coach with Vision Agents (freeCodeCamp) | https://www.freecodecamp.org/news/how-to-build-a-real-time-ai-gym-coach-with-vision-agents/ | Real-time VLM gym coach tutorial. |
| 208 | T | Hands-free AI fitness applet with Gemini Live API (DEV) | https://dev.to/prema_ananda/building-a-hands-free-ai-fitness-applet-with-gemini-live-api-3fg1 | Live API coaching. |
| 209 | T | Vertex AI prompt gallery: video QA exercise | https://cloud.google.com/vertex-ai/generative-ai/docs/prompt-gallery/samples/answer_question_video_qa_-_exercise | Gemini exercise video QA sample. |
| 210 | T | Sport Sage (Gemini API competition) | https://ai.google.dev/competition/projects/sport-sage | Gemini sports coaching project. |
| 211 | T | Real-time fitness form analysis (DEV) | https://dev.to/svet_62385e9/real-time-fitness-form-analysis-3agn | Structured pose events coach better than raw landmarks. |
| 212 | T | Fitness trainer pose estimation (yakupzengin) | https://relatedrepos.com/gh/yakupzengin/fitness-trainer-pose-estimation | Rep counting plus form feedback for squat, push-up and curl. |
| 213 | T | AI-FinessTrainer (KKopilka) | https://github.com/KKopilka/AI-FinessTrainer | Pose-based trainer repo. |
| 214 | T | AI-Gym-Trainer (rtsh13) | https://github.com/rtsh13/AI-Gym-Trainer | Pose-based gym trainer repo. |
| 215 | T | FitMate (GitHub) | https://github.com/syedalihn/FitMate | Fitness pose repo. |
| 216 | T | AI Coach (eman288) | https://awesome.ecosyste.ms/projects/github.com%2Feman288%2Fai-coach | Push-ups, crunches and squats. |
| 217 | T | AI Personal Trainer (gokulnpc) | https://awesome.ecosyste.ms/projects/github.com%2Fgokulnpc%2Fai-personal-trainer | MediaPipe dumbbell curl counter. |
| 218 | T | Fitness tutor (mahendran-narayanan) | https://awesome.ecosyste.ms/projects/github.com%2Fmahendran-narayanan%2Ffitness-tutor | PoseNet + p5.js skeleton. |
| 219 | T | Patent: Systems and methods for CV and ML based form feedback | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11273343 | Patented CV/ML form feedback system (family incl. 12048868). |
| 220 | T | Patent: Detection and counting of repetitions via a trained network | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10922577 | Patented repetition counting (family incl. 10460194, 11727725). |
| 221 | T | Patent: Automatic extraction of virtual on-body IMUs (self-occlusion check) | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12236616 | Flags self-occlusion when keypoints fall on the wrong body segment. |
| 222 | T | REPS - AI Fitness Coach (iOS) | https://apps.apple.com/app/id6753781872 | AI rep/coach app listing. |
| 223 | T | RepStandard (Product Hunt) | https://producthunt.com/products/repstandard | Rep-standard tracking product. |
| 224 | T | AI Fitness Trainer project portfolio (mmishracode) | https://mmishracode.github.io/AI_Fitness_Trainer_Project.html | Pose-based trainer project. |
| 225 | T | Personal AI trainer: pose estimation and rep counting (DesignSpark) | https://www.rs-online.com/designspark/personal-ai-trainer-body-pose-estimation-and-repetition-counting-part-iii | Build guide for pose rep counting. |
