from content_os.pipeline import textmatch as tm


def cue(text, k=15):
    toks = tm.tokens(text)
    return tm.parse_cue(toks, 0, k)


def test_cue_variants():
    assert cue("Beat 1.") == (1, 2)
    assert cue("beat one") == (1, 2)
    assert cue("beat for") == (4, 2)
    assert cue("bit 3") == (3, 2)
    assert cue("beat number three") == (3, 3)
    assert cue("Beat to") == (2, 2)
    assert cue("beat won") == (1, 2)
    assert cue("B2") == (2, 1)
    assert cue("beat twelve") == (12, 2)
    assert cue("beat 14") == (14, 2)


def test_cue_rejects():
    assert cue("beat the market") is None
    assert cue("beat 40") is None          # beyond the beat count
    assert cue("be for") is None           # weak cue word + homophone
    assert cue("agents are") is None


def test_alignment_order_constrained_and_fuzzy():
    ref = tm.tokens("Most agents are workflows wearing a costume.")
    cov = tm.coverage(tm.tokens("most agents are just workflows in a costume"), ref)
    assert cov["covers_start"] and cov["covers_end"]
    assert 0.8 <= cov["completeness"] < 1.0
    # same words out of order do not count as complete
    shuffled = tm.coverage(tm.tokens("costume a wearing workflows are agents most"), ref)
    assert shuffled["completeness"] < 0.3


def test_numbers_and_wer():
    assert tm.wer(tm.tokens("it was 73 percent faster"), tm.tokens("it was seventy three percent faster")) > 0
    assert tm.wer(tm.tokens("step one is done"), tm.tokens("step 1 is done")) == 0.0
    assert tm.wer([], tm.tokens("a b")) == 1.0


def test_repeated_ngrams():
    ref = tm.tokens("most agents are workflows")
    assert tm.repeated_ngrams(tm.tokens("most agents most agents are workflows"), ref) == ["most agents"]
    assert tm.repeated_ngrams(ref, ref) == []
