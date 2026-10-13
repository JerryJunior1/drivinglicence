/**
 * ==============================================================================
 * CODE DE LA ROUTE BÉNIN - INTERACTIVE APPLICATION CONTROLLER
 * ==============================================================================
 */

(function () {
  'use strict';

  // Application State
  const state = {
    data: null,
    activeChapter: null,
    activeSeries: null,
    isExamBlanc: false,
    quizMode: 'training', // 'training' | 'exam'
    currentQIndex: 0,
    userAnswers: {}, // { [qId]: Set(['a', 'b']) }
    validatedQuestions: {}, // { [qIndex]: boolean } (in training mode)
    quizStartTime: null,
    timerInterval: null,
    examSecondsLeft: 20 * 60,
    reviewFilter: 'all', // 'all' | 'mistakes' | 'correct'
    resultsCache: null,
    savedProgress: {} // { [seriesId]: { score, total, passed, timestamp } }
  };

  // DOM Elements
  const dom = {
    appContent: document.getElementById('app-content'),
    // Views
    viewDashboard: document.getElementById('view-dashboard'),
    viewSeries: document.getElementById('view-series'),
    viewMemento: document.getElementById('view-memento'),
    viewQuiz: document.getElementById('view-quiz'),
    viewResults: document.getElementById('view-results'),
    // Header & Global
    btnHomeLogo: document.getElementById('btn-home-logo'),
    headerPassedCount: document.getElementById('header-passed-count'),
    headerTotalSeries: document.getElementById('header-total-series'),
    btnNavMemento: document.getElementById('btn-nav-memento'),
    btnNavExamBlanc: document.getElementById('btn-nav-exam-blanc'),
    themeToggle: document.getElementById('theme-toggle'),
    btnResetProgress: document.getElementById('btn-reset-progress'),
    // Dashboard
    chaptersContainer: document.getElementById('chapters-container'),
    // Series View
    btnBackToChapters: document.getElementById('btn-back-to-chapters'),
    bannerChapterNum: document.getElementById('banner-chapter-num'),
    bannerChapterTitle: document.getElementById('banner-chapter-title'),
    bannerChapterDesc: document.getElementById('banner-chapter-desc'),
    bannerPassedPercent: document.getElementById('banner-passed-percent'),
    seriesContainer: document.getElementById('series-container'),
    pillModeTrain: document.getElementById('pill-mode-train'),
    pillModeExam: document.getElementById('pill-mode-exam'),
    // Memento View
    btnBackFromMemento: document.getElementById('btn-back-from-memento'),
    mementoContainer: document.getElementById('memento-container'),
    // Quiz View
    btnQuizQuit: document.getElementById('btn-quiz-quit'),
    quizCrumbChapter: document.getElementById('quiz-crumb-chapter'),
    quizCrumbSeries: document.getElementById('quiz-crumb-series'),
    quizModeBadge: document.getElementById('quiz-mode-badge'),
    quizTimerBox: document.getElementById('quiz-timer-box'),
    quizTimerDisplay: document.getElementById('quiz-timer-display'),
    quizCurrentQIndex: document.getElementById('quiz-current-q-index'),
    quizTotalQCount: document.getElementById('quiz-total-q-count'),
    quizStepperDots: document.getElementById('quiz-stepper-dots'),
    quizCard: document.getElementById('quiz-card'),
    qOfficialNum: document.getElementById('q-official-num'),
    quizImageBox: document.getElementById('quiz-image-box'),
    quizImageImg: document.getElementById('quiz-image-img'),
    btnZoomImage: document.getElementById('btn-zoom-image'),
    quizPrompt: document.getElementById('quiz-prompt'),
    quizOptionsList: document.getElementById('quiz-options-list'),
    quizFeedbackBanner: document.getElementById('quiz-feedback-banner'),
    feedbackIcon: document.getElementById('feedback-icon'),
    feedbackTitle: document.getElementById('feedback-title'),
    feedbackDesc: document.getElementById('feedback-desc'),
    btnQuizPrev: document.getElementById('btn-quiz-prev'),
    btnQuizNext: document.getElementById('btn-quiz-next'),
    btnNextLabel: document.getElementById('btn-next-label'),
    btnQuizValidate: document.getElementById('btn-quiz-validate'),
    // Results View
    resultHeroCard: document.getElementById('result-hero-card'),
    resultBadgeIcon: document.getElementById('result-badge-icon'),
    resultStatusTag: document.getElementById('result-status-tag'),
    resultHeroHeading: document.getElementById('result-hero-heading'),
    resScoreNum: document.getElementById('res-score-num'),
    resScoreDen: document.getElementById('res-score-den'),
    resThresholdText: document.getElementById('res-threshold-text'),
    resSummaryMessage: document.getElementById('res-summary-message'),
    resMetricCorrect: document.getElementById('res-metric-correct'),
    resMetricWrong: document.getElementById('res-metric-wrong'),
    resMetricPercent: document.getElementById('res-metric-percent'),
    resMetricTime: document.getElementById('res-metric-time'),
    btnResRestart: document.getElementById('btn-res-restart'),
    btnResNextSeries: document.getElementById('btn-res-next-series'),
    btnResBackSeries: document.getElementById('btn-res-back-series'),
    reviewItemsContainer: document.getElementById('review-items-container'),
    countAllFilter: document.getElementById('count-all-filter'),
    countMistakesFilter: document.getElementById('count-mistakes-filter'),
    countCorrectFilter: document.getElementById('count-correct-filter'),
    filterTabs: document.querySelectorAll('.filter-tab'),
    // Modals
    imageLightbox: document.getElementById('image-lightbox'),
    lightboxBackdrop: document.getElementById('lightbox-backdrop'),
    btnCloseLightbox: document.getElementById('btn-close-lightbox'),
    lightboxImg: document.getElementById('lightbox-img'),
    confirmModal: document.getElementById('confirm-modal'),
    confirmBackdrop: document.getElementById('confirm-backdrop'),
    btnConfirmCancel: document.getElementById('btn-confirm-cancel'),
    btnConfirmOk: document.getElementById('btn-confirm-ok')
  };

  // ==============================================================================
  // INITIALIZATION & LOCALSTORAGE
  // ==============================================================================

  function initApp() {
    loadTheme();
    loadProgress();

    // Check data source
    if (window.QCM_DATA) {
      state.data = window.QCM_DATA;
      setupApp();
    } else {
      // Fallback: fetch JSON
      fetch('assets/data/qcm_data.json')
        .then(res => res.json())
        .then(data => {
          state.data = data;
          setupApp();
        })
        .catch(err => {
          console.error("Erreur de chargement des données QCM:", err);
          dom.chaptersContainer.innerHTML = `
            <div style="grid-column: 1/-1; padding: 2rem; background: var(--bg-surface); border-radius: var(--radius-md); text-align: center;">
              <h3>Impossible de charger les questions du Code de la Route</h3>
              <p>Vérifiez que le fichier assets/data/qcm_data.js ou qcm_data.json est accessible.</p>
            </div>
          `;
        });
    }

    bindGlobalEvents();
  }

  function setupApp() {
    renderDashboard();
    renderMemento();
    updateGlobalHeaderStats();
  }

  // Theme Handling
  function loadTheme() {
    const saved = localStorage.getItem('qcm_benin_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('qcm_benin_theme', next);
  }

  // Progress LocalStorage
  function loadProgress() {
    try {
      const raw = localStorage.getItem('qcm_benin_progress');
      if (raw) {
        state.savedProgress = JSON.parse(raw);
      }
    } catch (e) {
      state.savedProgress = {};
    }
  }

  function saveProgress(seriesId, score, total, passed) {
    state.savedProgress[seriesId] = {
      score,
      total,
      passed,
      percentage: Math.round((score / total) * 100),
      timestamp: Date.now()
    };
    try {
      localStorage.setItem('qcm_benin_progress', JSON.stringify(state.savedProgress));
    } catch (e) {
      console.warn("Impossible de sauvegarder la progression locale:", e);
    }
    updateGlobalHeaderStats();
  }

  function resetAllProgress() {
    state.savedProgress = {};
    localStorage.removeItem('qcm_benin_progress');
    updateGlobalHeaderStats();
    if (dom.viewDashboard.classList.contains('active')) {
      renderDashboard();
    } else if (dom.viewSeries.classList.contains('active') && state.activeChapter) {
      renderSeriesView(state.activeChapter);
    }
  }

  function updateGlobalHeaderStats() {
    if (!state.data) return;
    let totalSeries = 0;
    let passedCount = 0;

    state.data.chapters.forEach(ch => {
      ch.series.forEach(s => {
        totalSeries++;
        const prog = state.savedProgress[s.series_id];
        if (prog && prog.passed) {
          passedCount++;
        }
      });
    });

    dom.headerPassedCount.textContent = passedCount;
    dom.headerTotalSeries.textContent = totalSeries;
  }

  // ==============================================================================
  // NAVIGATION & VIEW SWITCHER
  // ==============================================================================

  function showView(viewElement) {
    [dom.viewDashboard, dom.viewSeries, dom.viewMemento, dom.viewQuiz, dom.viewResults].forEach(v => {
      v.classList.remove('active');
    });
    viewElement.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function bindGlobalEvents() {
    // Theme toggle
    dom.themeToggle.addEventListener('click', toggleTheme);

    // Home button
    dom.btnHomeLogo.addEventListener('click', () => {
      if (state.timerInterval) clearInterval(state.timerInterval);
      showView(dom.viewDashboard);
      renderDashboard();
    });

    // Mémento nav
    dom.btnNavMemento.addEventListener('click', () => {
      showView(dom.viewMemento);
    });

    dom.btnBackFromMemento.addEventListener('click', () => {
      showView(dom.viewDashboard);
    });

    // Examen Blanc
    dom.btnNavExamBlanc.addEventListener('click', startExamBlanc);

    // Reset progress confirmation
    dom.btnResetProgress.addEventListener('click', () => {
      dom.confirmModal.classList.add('active');
    });
    dom.btnConfirmCancel.addEventListener('click', () => {
      dom.confirmModal.classList.remove('active');
    });
    dom.confirmBackdrop.addEventListener('click', () => {
      dom.confirmModal.classList.remove('active');
    });
    dom.btnConfirmOk.addEventListener('click', () => {
      dom.confirmModal.classList.remove('active');
      resetAllProgress();
    });

    // Series view back
    dom.btnBackToChapters.addEventListener('click', () => {
      showView(dom.viewDashboard);
      renderDashboard();
    });

    // Mode Selector in Series view
    dom.pillModeTrain.addEventListener('click', () => {
      dom.pillModeTrain.classList.add('active');
      dom.pillModeExam.classList.remove('active');
      state.quizMode = 'training';
    });
    dom.pillModeExam.addEventListener('click', () => {
      dom.pillModeExam.classList.add('active');
      dom.pillModeTrain.classList.remove('active');
      state.quizMode = 'exam';
    });

    // Quiz controls
    dom.btnQuizQuit.addEventListener('click', () => {
      if (confirm("Voulez-vous vraiment quitter ce questionnaire ? Votre progression en cours ne sera pas enregistrée.")) {
        if (state.timerInterval) clearInterval(state.timerInterval);
        if (state.activeChapter) {
          showView(dom.viewSeries);
        } else {
          showView(dom.viewDashboard);
        }
      }
    });

    dom.btnQuizPrev.addEventListener('click', goToPreviousQuestion);
    dom.btnQuizNext.addEventListener('click', goToNextQuestion);
    dom.btnQuizValidate.addEventListener('click', validateCurrentTrainingQuestion);

    // Lightbox Modal
    dom.btnZoomImage.addEventListener('click', openLightbox);
    dom.btnCloseLightbox.addEventListener('click', closeLightbox);
    dom.lightboxBackdrop.addEventListener('click', closeLightbox);

    // Results Actions
    dom.btnResRestart.addEventListener('click', () => {
      startQuiz(state.activeSeries, state.quizMode, state.isExamBlanc);
    });
    dom.btnResNextSeries.addEventListener('click', handleNextSeriesAction);
    dom.btnResBackSeries.addEventListener('click', () => {
      if (state.activeChapter) {
        showView(dom.viewSeries);
        renderSeriesView(state.activeChapter);
      } else {
        showView(dom.viewDashboard);
      }
    });

    // Review Filters
    dom.filterTabs.forEach(tab => {
      tab.addEventListener('click', (e) => {
        dom.filterTabs.forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        state.reviewFilter = e.target.getAttribute('data-filter');
        renderReviewList();
      });
    });

    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboardShortcuts);
  }

  // ==============================================================================
  // VIEW 1: DASHBOARD (CHAPTERS)
  // ==============================================================================

  function renderDashboard() {
    if (!state.data) return;
    dom.chaptersContainer.innerHTML = '';

    state.data.chapters.forEach(ch => {
      const card = document.createElement('div');
      card.className = 'chapter-card';

      // Calculate chapter progress
      let passedInChapter = 0;
      ch.series.forEach(s => {
        const p = state.savedProgress[s.series_id];
        if (p && p.passed) passedInChapter++;
      });
      const percent = ch.total_series > 0 ? Math.round((passedInChapter / ch.total_series) * 100) : 0;

      let statusBadgeText = "Non commencé";
      let statusBadgeClass = "not-started";
      if (ch.total_questions === 0) {
        statusBadgeText = "Guide & Définitions";
        statusBadgeClass = "completed";
      } else if (percent === 100) {
        statusBadgeText = "Chapitre Validé (Admis)";
        statusBadgeClass = "completed";
      } else if (passedInChapter > 0) {
        statusBadgeText = `${passedInChapter}/${ch.total_series} séries admises`;
        statusBadgeClass = "in-progress";
      }

      card.innerHTML = `
        <div>
          <div class="chapter-card-top">
            <span class="chapter-number-pill">Chapitre ${ch.id}</span>
            <span class="chapter-status-badge ${statusBadgeClass}">${statusBadgeText}</span>
          </div>
          <h4 class="chapter-card-title">${ch.title}</h4>
          <div class="chapter-card-meta">
            <span><strong>${ch.total_questions}</strong> questions</span>
            <span>•</span>
            <span><strong>${ch.total_series}</strong> questionnaire${ch.total_series > 1 ? 's' : ''} (20 Q)</span>
          </div>
        </div>

        <div class="chapter-progress-box">
          <div class="progress-info">
            <span>Progression</span>
            <strong>${percent}%</strong>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${percent}%;"></div>
          </div>
        </div>
      `;

      card.addEventListener('click', () => {
        if (ch.total_questions === 0) {
          showView(dom.viewMemento);
        } else {
          state.activeChapter = ch;
          renderSeriesView(ch);
          showView(dom.viewSeries);
        }
      });

      dom.chaptersContainer.appendChild(card);
    });
  }

  // ==============================================================================
  // VIEW 2: SERIES VIEW (20 QUESTIONS EACH)
  // ==============================================================================

  function renderSeriesView(ch) {
    dom.bannerChapterNum.textContent = `Chapitre ${ch.id}`;
    dom.bannerChapterTitle.textContent = ch.title;
    dom.bannerChapterDesc.textContent = `${ch.total_questions} questions réparties en ${ch.total_series} séries de 20 questions (Seuil d'admission : 14/20).`;

    let passedCount = 0;
    ch.series.forEach(s => {
      const p = state.savedProgress[s.series_id];
      if (p && p.passed) passedCount++;
    });
    const percent = ch.total_series > 0 ? Math.round((passedCount / ch.total_series) * 100) : 0;
    dom.bannerPassedPercent.textContent = `${percent}%`;

    dom.seriesContainer.innerHTML = '';

    ch.series.forEach(s => {
      const card = document.createElement('div');
      card.className = 'series-card';

      const prog = state.savedProgress[s.series_id];
      let scoreHtml = `<span class="score-tag none">Pas encore tenté</span>`;
      let statusIcon = "";

      if (prog) {
        if (prog.passed) {
          scoreHtml = `<span class="score-tag admis">🎉 ${prog.score}/${s.question_count} — Admis !</span>`;
          statusIcon = `<span class="badge" style="background: var(--color-success-bg); color: var(--color-success);">Validé</span>`;
        } else {
          scoreHtml = `<span class="score-tag ajourne">❌ ${prog.score}/${s.question_count} — Ajourné (<14)</span>`;
          statusIcon = `<span class="badge" style="background: var(--color-danger-bg); color: var(--color-danger);">À retravailler</span>`;
        }
      }

      card.innerHTML = `
        <div class="series-card-top">
          <div>
            <h4 class="series-title">${s.title}</h4>
            <div class="series-range">${s.range_label} (${s.question_count} questions)</div>
          </div>
          ${statusIcon}
        </div>

        <div class="series-status-box">
          <span style="font-size: 0.8rem; color: var(--text-muted);">Dernier résultat :</span>
          ${scoreHtml}
        </div>

        <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 1rem;">
          Seuil requis pour être admis : <strong>${s.pass_threshold_text}</strong> (14/20)
        </div>

        <div class="series-actions">
          <button class="btn btn-secondary btn-sm btn-train">Entraînement</button>
          <button class="btn btn-primary btn-sm btn-exam">Examen (20min)</button>
        </div>
      `;

      card.querySelector('.btn-train').addEventListener('click', (e) => {
        e.stopPropagation();
        startQuiz(s, 'training', false);
      });

      card.querySelector('.btn-exam').addEventListener('click', (e) => {
        e.stopPropagation();
        startQuiz(s, 'exam', false);
      });

      card.addEventListener('click', () => {
        startQuiz(s, state.quizMode, false);
      });

      dom.seriesContainer.appendChild(card);
    });
  }

  // ==============================================================================
  // VIEW 3: MÉMENTO (CHAPITRE 1)
  // ==============================================================================

  function renderMemento() {
    if (!state.data || !state.data.course_ch1) return;
    dom.mementoContainer.innerHTML = '';

    state.data.course_ch1.forEach(sec => {
      const card = document.createElement('div');
      card.className = 'memento-section-card';

      let itemsHtml = '';
      sec.items.forEach(it => {
        itemsHtml += `
          <div class="memento-item-box">
            <div class="memento-item-term">${it.term}</div>
            <div class="memento-item-def">${it.def}</div>
          </div>
        `;
      });

      card.innerHTML = `
        <h3 class="memento-section-title">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          ${sec.title}
        </h3>
        <div class="memento-items-grid">
          ${itemsHtml}
        </div>
      `;

      dom.mementoContainer.appendChild(card);
    });
  }

  // ==============================================================================
  // VIEW 4: QUIZ INTERACTIF (QCM ENGINE)
  // ==============================================================================

  function startQuiz(series, mode, isExamBlanc = false) {
    state.activeSeries = series;
    state.quizMode = mode;
    state.isExamBlanc = isExamBlanc;
    state.currentQIndex = 0;
    state.userAnswers = {};
    state.validatedQuestions = {};
    state.quizStartTime = Date.now();

    // Mode UI setup
    dom.quizModeBadge.textContent = mode === 'training' ? 'Mode Entraînement' : 'Mode Examen (Chronométré)';
    dom.quizModeBadge.className = `badge mode-badge ${mode}`;

    if (isExamBlanc) {
      dom.quizCrumbChapter.textContent = "Examen Blanc Officiel";
      dom.quizCrumbSeries.textContent = "20 Questions aléatoires";
    } else {
      dom.quizCrumbChapter.textContent = `Chapitre ${state.activeChapter.id}`;
      dom.quizCrumbSeries.textContent = `${series.title} (${series.range_label})`;
    }

    // Timer setup
    if (state.timerInterval) clearInterval(state.timerInterval);
    if (mode === 'exam') {
      dom.quizTimerBox.style.display = 'flex';
      state.examSecondsLeft = 20 * 60; // 20 minutes for 20 questions
      updateTimerDisplay();
      state.timerInterval = setInterval(() => {
        state.examSecondsLeft--;
        updateTimerDisplay();
        if (state.examSecondsLeft <= 0) {
          clearInterval(state.timerInterval);
          alert("Temps écoulé ! Votre examen va être corrigé automatiquement.");
          finishQuiz();
        }
      }, 1000);
    } else {
      dom.quizTimerBox.style.display = 'none';
    }

    renderStepperDots();
    renderCurrentQuestion();
    showView(dom.viewQuiz);
  }

  function updateTimerDisplay() {
    const mins = Math.floor(state.examSecondsLeft / 60);
    const secs = state.examSecondsLeft % 60;
    dom.quizTimerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  function renderStepperDots() {
    dom.quizStepperDots.innerHTML = '';
    const total = state.activeSeries.questions.length;
    dom.quizTotalQCount.textContent = total;

    for (let i = 0; i < total; i++) {
      const pill = document.createElement('div');
      pill.className = 'step-pill';
      pill.title = `Question ${i + 1}`;
      pill.addEventListener('click', () => {
        state.currentQIndex = i;
        renderCurrentQuestion();
      });
      dom.quizStepperDots.appendChild(pill);
    }
    updateStepperDotsClasses();
  }

  function updateStepperDotsClasses() {
    const pills = dom.quizStepperDots.querySelectorAll('.step-pill');
    pills.forEach((p, idx) => {
      p.className = 'step-pill';
      if (idx === state.currentQIndex) {
        p.classList.add('current');
      }

      const q = state.activeSeries.questions[idx];
      const ans = state.userAnswers[q.id];

      if (state.quizMode === 'training' && state.validatedQuestions[idx]) {
        const isCorrect = isQuestionAnswerCorrect(q, ans);
        p.classList.add(isCorrect ? 'correct' : 'wrong');
      } else if (ans && ans.size > 0) {
        p.classList.add('answered');
      }
    });
  }

  function renderCurrentQuestion() {
    const questions = state.activeSeries.questions;
    const q = questions[state.currentQIndex];
    const total = questions.length;

    dom.quizCurrentQIndex.textContent = state.currentQIndex + 1;
    dom.qOfficialNum.textContent = `Question Officielle N° ${q.id}`;


    // Image
    if (q.images && q.images.length > 0) {
      dom.quizImageBox.style.display = 'flex';
      dom.quizImageImg.src = q.images[0];
      dom.lightboxImg.src = q.images[0];
    } else {
      dom.quizImageBox.style.display = 'none';
      dom.quizImageImg.src = '';
    }

    // Prompt
    dom.quizPrompt.textContent = q.question;

    // Options
    dom.quizOptionsList.innerHTML = '';
    const userSelected = state.userAnswers[q.id] || new Set();
    const isValidated = state.quizMode === 'training' && state.validatedQuestions[state.currentQIndex];

    q.options.forEach(opt => {
      const optItem = document.createElement('div');
      optItem.className = 'quiz-option-item';
      const isChecked = userSelected.has(opt.id);

      if (isChecked) {
        optItem.classList.add('selected');
      }

      // If already validated in training mode
      if (isValidated) {
        optItem.classList.add('locked');
        const isOfficialCorrect = q.correct_answers.includes(opt.id);
        if (isOfficialCorrect) {
          optItem.classList.add('correct-revealed');
        } else if (isChecked && !isOfficialCorrect) {
          optItem.classList.add('wrong-selected');
        }
      }

      optItem.innerHTML = `
        <div class="option-indicator">${opt.id.toUpperCase()}</div>
        <div class="option-text">${opt.text}</div>
      `;

      optItem.addEventListener('click', () => {
        if (isValidated) return;
        toggleOptionSelection(q, opt.id);
      });

      dom.quizOptionsList.appendChild(optItem);
    });

    // Feedback Banner in Training Mode
    if (isValidated) {
      dom.quizFeedbackBanner.style.display = 'flex';
      const isCorrect = isQuestionAnswerCorrect(q, userSelected);
      const officialStr = q.correct_answers.map(a => a.toUpperCase()).join(', ');
      const explanationHtml = q.explanation 
        ? `<div class="feedback-explanation"><strong>💡 Règle & Explication :</strong> ${q.explanation}</div>` 
        : '';

      if (isCorrect) {
        dom.quizFeedbackBanner.className = 'feedback-banner success';
        dom.feedbackIcon.textContent = '✅';
        dom.feedbackTitle.textContent = 'Excellente réponse !';
        dom.feedbackDesc.innerHTML = `<div>Bonne réponse officielle : <strong>${officialStr}</strong>.</div>${explanationHtml}`;
      } else {
        dom.quizFeedbackBanner.className = 'feedback-banner danger';
        dom.feedbackIcon.textContent = '❌';
        dom.feedbackTitle.textContent = 'Réponse incorrecte';
        dom.feedbackDesc.innerHTML = `<div>La bonne réponse officielle est : <strong>${officialStr}</strong>.</div>${explanationHtml}`;
      }
      dom.btnQuizValidate.style.display = 'none';
    } else {
      dom.quizFeedbackBanner.style.display = 'none';
      if (state.quizMode === 'training') {
        dom.btnQuizValidate.style.display = 'inline-flex';
        dom.btnQuizValidate.disabled = userSelected.size === 0;
      } else {
        dom.btnQuizValidate.style.display = 'none';
      }
    }

    // Previous / Next button states
    dom.btnQuizPrev.disabled = state.currentQIndex === 0;
    if (state.currentQIndex === total - 1) {
      dom.btnNextLabel.textContent = "Terminer le test";
    } else {
      dom.btnNextLabel.textContent = "Suivante";
    }

    updateStepperDotsClasses();
  }

  function toggleOptionSelection(q, optId) {
    if (!state.userAnswers[q.id]) {
      state.userAnswers[q.id] = new Set();
    }
    const current = state.userAnswers[q.id];

    if (q.is_multiple_choice) {
      // Multiple choices toggle
      if (current.has(optId)) {
        current.delete(optId);
      } else {
        current.add(optId);
      }
    } else {
      // Single choice
      current.clear();
      current.add(optId);
    }

    renderCurrentQuestion();
  }

  function validateCurrentTrainingQuestion() {
    const q = state.activeSeries.questions[state.currentQIndex];
    const userSelected = state.userAnswers[q.id];
    if (!userSelected || userSelected.size === 0) return;

    state.validatedQuestions[state.currentQIndex] = true;
    renderCurrentQuestion();
  }

  function goToPreviousQuestion() {
    if (state.currentQIndex > 0) {
      state.currentQIndex--;
      renderCurrentQuestion();
    }
  }

  function goToNextQuestion() {
    const total = state.activeSeries.questions.length;
    if (state.currentQIndex < total - 1) {
      state.currentQIndex++;
      renderCurrentQuestion();
    } else {
      // Finish quiz
      finishQuiz();
    }
  }

  function isQuestionAnswerCorrect(q, userSet) {
    if (!userSet || userSet.size === 0) return false;
    const userArr = Array.from(userSet).sort();
    const correctArr = [...q.correct_answers].sort();
    if (userArr.length !== correctArr.length) return false;
    return userArr.every((val, idx) => val === correctArr[idx]);
  }

  // ==============================================================================
  // VIEW 5: RESULTS & REVIEW (14/20 PASS THRESHOLD)
  // ==============================================================================

  function finishQuiz() {
    if (state.timerInterval) clearInterval(state.timerInterval);

    const questions = state.activeSeries.questions;
    const total = questions.length;
    let score = 0;

    const reviewData = questions.map((q, idx) => {
      const userSet = state.userAnswers[q.id] || new Set();
      const isCorrect = isQuestionAnswerCorrect(q, userSet);
      if (isCorrect) score++;

      return {
        question: q,
        index: idx + 1,
        userAnswers: Array.from(userSet).sort(),
        correctAnswers: [...q.correct_answers].sort(),
        isCorrect
      };
    });

    // Official Pass threshold: exactly 14/20 for 20 questions, or proportional (70%)
    const passThreshold = state.activeSeries.pass_score || 14;
    const isPassed = score >= passThreshold;

    // Save Progress in LocalStorage (except Exam Blanc which is a random practice)
    if (!state.isExamBlanc) {
      saveProgress(state.activeSeries.series_id, score, total, isPassed);
    }

    // Cache results
    state.resultsCache = {
      score,
      total,
      passThreshold,
      isPassed,
      reviewData,
      timeElapsedSeconds: Math.round((Date.now() - state.quizStartTime) / 1000)
    };

    renderResultsScreen();
    showView(dom.viewResults);
  }

  function renderResultsScreen() {
    const res = state.resultsCache;
    if (!res) return;

    dom.resScoreNum.textContent = res.score;
    dom.resScoreDen.textContent = res.total;
    dom.resMetricCorrect.textContent = res.score;
    dom.resMetricWrong.textContent = res.total - res.score;
    dom.resMetricPercent.textContent = `${Math.round((res.score / res.total) * 100)}%`;

    // Time display
    const mins = Math.floor(res.timeElapsedSeconds / 60);
    const secs = res.timeElapsedSeconds % 60;
    dom.resMetricTime.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

    dom.resThresholdText.innerHTML = `Seuil officiel d'admission : <strong>${res.passThreshold} / ${res.total}</strong> (14/20 requis)`;

    // Check Admission status (14/20 rule)
    if (res.isPassed) {
      dom.resultHeroCard.className = 'result-hero-card admis';
      dom.resultBadgeIcon.textContent = '🎉';
      dom.resultStatusTag.textContent = 'ADMIS !';
      dom.resultHeroHeading.textContent = 'Félicitations, vous avez brillamment réussi cette série !';
      dom.resSummaryMessage.textContent = `Votre score de ${res.score}/${res.total} est supérieur ou égal au seuil exigé de 14/20. Vous êtes fin prêt pour l'épreuve officielle !`;
    } else {
      dom.resultHeroCard.className = 'result-hero-card ajourne';
      dom.resultBadgeIcon.textContent = '❌';
      dom.resultStatusTag.textContent = 'AJOURNÉ !';
      dom.resultHeroHeading.textContent = 'Courage, il vous faut au moins 14/20 pour être admis !';
      dom.resSummaryMessage.textContent = `Vous avez obtenu ${res.score}/${res.total}. Analysez vos erreurs ci-dessous puis recommencez la série pour décrocher les 14/20 !`;
    }

    // Update filter counts
    const mistakeCount = res.total - res.score;
    dom.countAllFilter.textContent = res.total;
    dom.countMistakesFilter.textContent = mistakeCount;
    dom.countCorrectFilter.textContent = res.score;

    state.reviewFilter = 'all';
    dom.filterTabs.forEach(t => {
      t.classList.toggle('active', t.getAttribute('data-filter') === 'all');
    });

    renderReviewList();
  }

  function renderReviewList() {
    const res = state.resultsCache;
    if (!res) return;

    dom.reviewItemsContainer.innerHTML = '';
    const filtered = res.reviewData.filter(item => {
      if (state.reviewFilter === 'mistakes') return !item.isCorrect;
      if (state.reviewFilter === 'correct') return item.isCorrect;
      return true;
    });

    if (filtered.length === 0) {
      dom.reviewItemsContainer.innerHTML = `
        <div style="padding: 2rem; text-align: center; color: var(--text-muted);">
          Aucune question dans cette catégorie.
        </div>
      `;
      return;
    }

    filtered.forEach(item => {
      const q = item.question;
      const card = document.createElement('div');
      card.className = `review-item-card ${item.isCorrect ? 'is-correct' : 'is-wrong'}`;

      let imgHtml = '';
      if (q.images && q.images.length > 0) {
        imgHtml = `
          <div class="review-img-box">
            <img src="${q.images[0]}" alt="Illustration Question">
          </div>
        `;
      }

      const userAnsFormatted = item.userAnswers.length > 0 
        ? item.userAnswers.map(a => a.toUpperCase()).join(', ') 
        : 'Aucune réponse';
      const correctAnsFormatted = item.correctAnswers.map(a => a.toUpperCase()).join(', ');

      card.innerHTML = `
        <div class="review-item-top">
          <span class="review-q-num">Question ${item.index} (Officielle N° ${q.id})</span>
          <span class="review-status-pill ${item.isCorrect ? 'correct' : 'wrong'}">
            ${item.isCorrect ? 'Correcte (+1)' : 'Erreur (0)'}
          </span>
        </div>
        ${imgHtml}
        <div class="review-q-prompt">${q.question}</div>
        <div class="review-answers-box">
          <div class="review-row user-ans">
            <strong>Votre réponse :</strong>
            <span class="val ${item.isCorrect ? 'correct' : 'wrong'}">${userAnsFormatted}</span>
          </div>
          <div class="review-row correct-ans">
            <strong>Bonne réponse :</strong>
            <span class="val">${correctAnsFormatted}</span>
          </div>
          ${q.explanation ? `
          <div class="review-row explanation-row">
            <strong>💡 Explication :</strong>
            <span class="explanation-text">${q.explanation}</span>
          </div>` : ''}
        </div>
      `;

      dom.reviewItemsContainer.appendChild(card);
    });
  }

  function handleNextSeriesAction() {
    if (state.isExamBlanc) {
      startExamBlanc();
      return;
    }

    if (!state.activeChapter) {
      showView(dom.viewDashboard);
      return;
    }

    const seriesList = state.activeChapter.series;
    const currentIndex = seriesList.findIndex(s => s.series_id === state.activeSeries.series_id);

    if (currentIndex >= 0 && currentIndex < seriesList.length - 1) {
      const nextSeries = seriesList[currentIndex + 1];
      startQuiz(nextSeries, state.quizMode, false);
    } else {
      // Find next chapter
      const chList = state.data.chapters;
      const curChIdx = chList.findIndex(c => c.id === state.activeChapter.id);
      if (curChIdx >= 0 && curChIdx < chList.length - 1) {
        const nextCh = chList[curChIdx + 1];
        if (nextCh.series.length > 0) {
          state.activeChapter = nextCh;
          startQuiz(nextCh.series[0], state.quizMode, false);
          return;
        }
      }
      alert("Félicitations ! Vous avez terminé toutes les séries de ce chapitre !");
      showView(dom.viewDashboard);
      renderDashboard();
    }
  }

  // ==============================================================================
  // EXAMEN BLANC (20 QUESTIONS RANDOM DU CODE)
  // ==============================================================================

  function startExamBlanc() {
    if (!state.data) return;
    const allQuestions = [];
    state.data.chapters.forEach(ch => {
      ch.series.forEach(s => {
        allQuestions.push(...s.questions);
      });
    });

    if (allQuestions.length === 0) return;

    // Shuffle and pick 20
    const shuffled = [...allQuestions].sort(() => 0.5 - Math.random());
    const sample = shuffled.slice(0, 20);

    const examBlancSeries = {
      series_id: 'examen_blanc_' + Date.now(),
      series_number: 1,
      title: "Examen Blanc Officiel",
      range_label: "20 Questions tirées au sort",
      question_count: 20,
      pass_score: 14,
      pass_threshold_text: "14/20",
      questions: sample
    };

    startQuiz(examBlancSeries, 'exam', true);
  }

  // ==============================================================================
  // LIGHTBOX & ZOOM
  // ==============================================================================

  function openLightbox() {
    dom.imageLightbox.classList.add('active');
  }

  function closeLightbox() {
    dom.imageLightbox.classList.remove('active');
  }

  // Keyboard Shortcuts (A, B, C, D, Left, Right, Enter, Escape)
  function handleKeyboardShortcuts(e) {
    if (dom.imageLightbox.classList.contains('active')) {
      if (e.key === 'Escape') closeLightbox();
      return;
    }

    if (!dom.viewQuiz.classList.contains('active')) return;

    const q = state.activeSeries.questions[state.currentQIndex];
    if (!q) return;

    const key = e.key.toLowerCase();
    if (['a', 'b', 'c', 'd', 'e'].includes(key)) {
      const matchOpt = q.options.find(o => o.id === key);
      if (matchOpt && (!state.quizMode === 'training' || !state.validatedQuestions[state.currentQIndex])) {
        toggleOptionSelection(q, key);
      }
    } else if (e.key === 'ArrowRight') {
      goToNextQuestion();
    } else if (e.key === 'ArrowLeft') {
      goToPreviousQuestion();
    } else if (e.key === 'Enter') {
      if (state.quizMode === 'training' && !state.validatedQuestions[state.currentQIndex]) {
        validateCurrentTrainingQuestion();
      } else {
        goToNextQuestion();
      }
    }
  }

  // Start on load
  document.addEventListener('DOMContentLoaded', initApp);

})();
