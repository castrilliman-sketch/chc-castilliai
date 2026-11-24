(function () {
  "use strict";

  var QUESTIONS = [
    {
      id: 1,
      question: "Is your relative currently in a care home, hospital, or receiving complex home care?",
      hint: "NHS Continuing Healthcare can be provided in any setting, including a nursing home, a residential home, or a person's own home.",
      options: [
        { label: "Nursing home or residential care home", value: "care_home", weight: 3 },
        { label: "Complex 24-hour care package at home", value: "home_care", weight: 3 },
        { label: "Hospital (awaiting discharge or rehabilitation)", value: "hospital", weight: 2 },
        { label: "Standard domestic care, or living independently", value: "standard", weight: 0 }
      ]
    },
    {
      id: 2,
      question: "Has a CHC Checklist or Decision Support Tool (DST) been completed in the last 6 months?",
      hint: "The Checklist is a screening tool. The DST is the full multidisciplinary assessment used by the integrated care board (ICB).",
      options: [
        { label: "Yes, a full DST assessment was held", value: "full_dst", weight: 3 },
        { label: "Yes, a screening Checklist was completed and did not go forward", value: "checklist", weight: 2 },
        { label: "An assessment was done, but I am not sure which type", value: "unsure", weight: 2 },
        { label: "No assessment has been completed", value: "none", weight: 1 }
      ]
    },
    {
      id: 3,
      question: "Were they refused CHC funding, or told they only qualify for NHS-funded nursing care (FNC)?",
      hint: "FNC is a weekly NHS contribution towards registered nursing in a nursing home. The standard rate from 1 April 2026 is £267.68 a week. Full CHC, if awarded, covers the whole agreed care package, including accommodation.",
      options: [
        { label: "Yes — found not eligible for CHC", value: "refused", weight: 3 },
        { label: "Given FNC only (not full CHC)", value: "fnc_only", weight: 3 },
        { label: "Funding was previously awarded but later withdrawn", value: "withdrawn", weight: 3 },
        { label: "Still awaiting a written outcome letter", value: "awaiting", weight: 1 }
      ]
    },
    {
      id: 4,
      question: "Do they have severe mobility needs, frequent falls, or need two-person hoisting?",
      hint: "Needs around mobility and falls risk are recorded in the Decision Support Tool and can be relevant to the nature and intensity of need.",
      options: [
        { label: "Bedbound, or needs a two-person hoist for transfers", value: "bedbound_2p", weight: 3 },
        { label: "Unstable walking with more than one fall despite supervision", value: "frequent_falls", weight: 3 },
        { label: "Needs help from one person, with or without a walking aid", value: "assisted_1p", weight: 1 },
        { label: "Walks independently without difficulty", value: "independent", weight: 0 }
      ]
    },
    {
      id: 5,
      question: "Do they have continence needs that require clinical intervention or skin protection?",
      hint: "Continence needs, catheters and the risk of skin damage are recorded in the relevant DST domains.",
      options: [
        { label: "Double incontinence plus a high risk of skin breakdown, or open wounds", value: "double_skin_risk", weight: 3 },
        { label: "A catheter with frequent blockages or urine infections", value: "catheter_complications", weight: 3 },
        { label: "Incontinent, managed with routine pads", value: "routine_pads", weight: 1 },
        { label: "Fully continent", value: "continent", weight: 0 }
      ]
    },
    {
      id: 6,
      question: "Do they have nutrition, hydration or swallowing difficulties (for example dysphagia, weight loss, or speech and language therapy input)?",
      hint: "Swallowing risk, modified diets and tube feeding are recorded in the nutrition domain of the DST.",
      options: [
        { label: "Choking episodes, or a puréed diet and thickened fluids following a swallow assessment", value: "severe_dysphagia", weight: 3 },
        { label: "PEG or nasogastric tube feeding, or critical weight loss", value: "enteral_feeding", weight: 3 },
        { label: "Needs help or encouragement to eat and drink", value: "prompting", weight: 1 },
        { label: "Eats and drinks independently", value: "independent_eat", weight: 0 }
      ]
    },
    {
      id: 7,
      question: "Do they have behaviour or cognition needs that require constant supervision or specialist care?",
      hint: "Cognition and behaviour are separate DST domains. Needs can exist in one, the other, or both.",
      options: [
        { label: "Severe dementia, wanders into danger, or has no insight into safety", value: "severe_dementia", weight: 3 },
        { label: "Challenging behaviour, agitation, or resists essential personal care", value: "challenging_behaviour", weight: 3 },
        { label: "Mild confusion or memory lapses, generally cooperative", value: "mild_confusion", weight: 1 },
        { label: "Alert and able to manage day-to-day decisions", value: "lucid", weight: 0 }
      ]
    },
    {
      id: 8,
      question: "Do they need complex medication management (for example injections, a syringe driver, or doses that change according to symptoms)?",
      hint: "Medication needs are recorded in the drug therapies and medication domain.",
      options: [
        { label: "Syringe driver, sliding-scale insulin, or frequent as-needed dose changes that need clinical judgement", value: "complex_titration", weight: 3 },
        { label: "A carer gives medication and monitors side effects", value: "carer_administered", weight: 2 },
        { label: "Stable oral medication, for example in a blister pack", value: "stable_oral", weight: 1 },
        { label: "No medication, or only simple self-managed medication", value: "none_meds", weight: 0 }
      ]
    },
    {
      id: 9,
      question: "Have they had hospital admissions, ambulance call-outs, or unplanned GP visits in the last 6 months?",
      hint: "Unplanned escalations can be relevant to how unpredictable needs are, but they are only one part of the picture.",
      options: [
        { label: "Three or more emergency admissions or 999 call-outs", value: "frequent_emergency", weight: 3 },
        { label: "One or two hospital admissions in recent months", value: "occasional_emergency", weight: 2 },
        { label: "Frequent urgent GP or out-of-hours consultations", value: "frequent_gp", weight: 2 },
        { label: "No unplanned medical attendances", value: "stable", weight: 0 }
      ]
    },
    {
      id: 10,
      question: "Are you within 6 months of the written refusal or eligibility decision letter?",
      hint: "ICBs commonly ask that a local resolution request is made within 6 months of the written decision. Late requests can sometimes still be accepted where there is a good reason and the records can still be obtained. Check the dates and instructions on your letter.",
      options: [
        { label: "Yes — within the last 6 months", value: "within_window", weight: 3 },
        { label: "Very close to the 6-month point, so action is urgent", value: "deadline_approaching", weight: 3 },
        { label: "More than 6 months ago (you may still be able to ask, including for a past period of care)", value: "over_window", weight: 1 },
        { label: "I have not received a formal written decision letter yet", value: "no_letter", weight: 2 }
      ]
    }
  ];

  var VERDICTS = {
    strong: {
      title: "Your answers suggest it is worth a closer look",
      summary: "Based on what you have told us, there are several indicators that may be relevant to a primary health need. That is not a finding of eligibility, and it is not a prediction of what the ICB will decide.",
      recommendation: "The next useful step is usually a Stage 1 evidence review: we read the records you already have and give you a written Yes, No or Maybe verdict before you spend anything on a formal submission."
    },
    possible: {
      title: "There may be a case — the records will decide it",
      summary: "Your answers show some healthcare needs, but whether there is a primary health need depends on the contemporaneous records and how needs interact across the Decision Support Tool domains.",
      recommendation: "A Stage 1 review is designed for this situation. We inspect the records and give you an honest Yes, No or Maybe verdict before any later-stage fee."
    },
    weak: {
      title: "On these answers, a primary health need looks less likely",
      summary: "The preliminary answers suggest that the needs you have described may fall more naturally within social care, but only the records and a full assessment can show that properly.",
      recommendation: "We will not encourage you to spend money if the evidence is weak. If you still think something important was missed, you can book Stage 1 for a definite written view, or write to us first."
    }
  };

  var STRIPE_STAGE1 = "https://buy.stripe.com/6oUeVe2Nia6Y5pDbPFa3u0b";
  var CONTACT = "mailto:danwyatt398@gmail.com?subject=" + encodeURIComponent("CHC eligibility check follow-up");

  var root = document.getElementById("quiz");
  if (!root) return;

  var answers = {};
  var step = 0;

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "className") node.className = attrs[k];
        else if (k === "html") node.innerHTML = attrs[k];
        else if (k.indexOf("on") === 0) node.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
        else if (attrs[k] !== null && attrs[k] !== undefined) node.setAttribute(k, attrs[k]);
      });
    }
    (children || []).forEach(function (c) {
      if (c == null) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function scoreTotal() {
    return QUESTIONS.reduce(function (sum, q) {
      var a = answers[q.id];
      return sum + (a ? a.weight : 0);
    }, 0);
  }

  function tierFor(score) {
    if (score >= 18) return "strong";
    if (score >= 11) return "possible";
    return "weak";
  }

  function render() {
    root.innerHTML = "";
    if (step >= QUESTIONS.length) {
      renderResult();
      return;
    }
    var q = QUESTIONS[step];
    var pct = Math.round((step / QUESTIONS.length) * 100);
    var progress = el("div", { className: "quiz-progress", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(pct), "aria-label": "Question " + (step + 1) + " of " + QUESTIONS.length }, [
      el("span", { style: "width:" + pct + "%" })
    ]);
    var fieldset = el("fieldset", { className: "quiz-q" });
    fieldset.appendChild(el("legend", null, [
      el("p", { className: "small", style: "margin:0 0 .4em" }, ["Question " + (step + 1) + " of " + QUESTIONS.length]),
      el("h2", { style: "font-size:1.25rem;margin:0 0 .6em" }, [q.question])
    ]));
    fieldset.appendChild(el("p", { className: "small", id: "hint-" + q.id }, [q.hint]));
    var list = el("div", { className: "quiz-options", role: "radiogroup", "aria-describedby": "hint-" + q.id });
    q.options.forEach(function (opt, i) {
      var id = "q" + q.id + "-" + opt.value;
      var input = el("input", {
        type: "radio",
        name: "q" + q.id,
        id: id,
        value: opt.value
      });
      if (answers[q.id] && answers[q.id].value === opt.value) input.checked = true;
      input.addEventListener("change", function () {
        answers[q.id] = opt;
        nextBtn.disabled = false;
      });
      var label = el("label", { for: id }, [input, el("span", null, [opt.label])]);
      list.appendChild(label);
    });
    fieldset.appendChild(list);

    var nextBtn = el("button", { type: "button", className: "btn btn-primary", id: "quiz-next" }, [step === QUESTIONS.length - 1 ? "See my result" : "Next question"]);
    nextBtn.disabled = !answers[q.id];
    nextBtn.addEventListener("click", function () {
      if (!answers[q.id]) return;
      step += 1;
      render();
      root.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    var nav = el("div", { className: "quiz-nav" });
    if (step > 0) {
      var back = el("button", { type: "button", className: "btn btn-secondary" }, ["Back"]);
      back.addEventListener("click", function () {
        step -= 1;
        render();
      });
      nav.appendChild(back);
    }
    nav.appendChild(nextBtn);

    root.appendChild(progress);
    root.appendChild(fieldset);
    root.appendChild(nav);
  }

  function renderResult() {
    var score = scoreTotal();
    var tier = tierFor(score);
    var copy = VERDICTS[tier];
    var box = el("div", { className: "quiz-result tier-" + tier });
    box.appendChild(el("p", { className: "tier" }, ["Preliminary indication"]));
    box.appendChild(el("h2", null, [copy.title]));
    box.appendChild(el("p", null, [copy.summary]));
    box.appendChild(el("p", null, [copy.recommendation]));
    box.appendChild(el("p", { className: "small" }, [
      "This is a simple weighted questionnaire, not an official NHS Checklist or Decision Support Tool, and not legal or medical advice. Only the ICB can decide eligibility."
    ]));
    var ctas = el("div", { className: "cta-row" });
    ctas.appendChild(el("a", { className: "btn btn-primary", href: STRIPE_STAGE1 }, ["Start Stage 1 — £349"]));
    ctas.appendChild(el("a", { className: "btn btn-secondary", href: "/pricing/" }, ["See prices"]));
    ctas.appendChild(el("a", { className: "btn btn-secondary", href: CONTACT }, ["Email us first"]));
    box.appendChild(ctas);
    var again = el("button", { type: "button", className: "btn btn-secondary btn-sm", style: "margin-top:12px" }, ["Start the check again"]);
    again.addEventListener("click", function () {
      answers = {};
      step = 0;
      render();
    });
    box.appendChild(again);
    root.appendChild(box);
  }

  render();
})();
