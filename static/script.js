let currentQuestionIndex = 0;
let questions = [];
let userAnswers = [];
let isProcessing = false;

// Загрузка вопросов при старте
async function loadQuestions() {
    try {
        const response = await fetch('/api/questions');
        const data = await response.json();
        questions = data.questions;
        displayCurrentQuestion();
    } catch (error) {
        console.error('Ошибка загрузки вопросов:', error);
        addBotMessage('Извините, произошла ошибка. Пожалуйста, обновите страницу.');
    }
}

// Отображение текущего вопроса
function displayCurrentQuestion() {
    if (currentQuestionIndex >= questions.length) {
        calculateAndShowResult();
        return;
    }

    const question = questions[currentQuestionIndex];
    addBotMessage(question.text, true);

    // Обновляем прогресс
    updateProgress();
}

// Добавление сообщения бота
function addBotMessage(text, withOptions = false) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    messageDiv.innerHTML = `
        <div class="message-avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <div class="message-text">${formatMessageText(text)}</div>
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();

    if (withOptions && currentQuestionIndex < questions.length) {
        showOptions(questions[currentQuestionIndex].answers);
    }
}

// Форматирование текста сообщения
function formatMessageText(text) {
    if (text.includes('<div')) {
        return text; // Уже HTML
    }
    return escapeHtml(text).replace(/\n/g, '<br>');
}

// Добавление сообщения пользователя
function addUserMessage(text) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-avatar"><i class="fas fa-user"></i></div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Экранирование HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Показать варианты ответов
function showOptions(answers) {
    const optionsContainer = document.getElementById('optionsContainer');
    optionsContainer.innerHTML = '';
    optionsContainer.style.display = 'flex';

    answers.forEach((answer, index) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerHTML = answer.text;
        btn.onclick = () => handleAnswer(answer, index);
        optionsContainer.appendChild(btn);
    });

    document.getElementById('loading').style.display = 'none';
}

// Обработка ответа
async function handleAnswer(answer, index) {
    if (isProcessing) return;
    isProcessing = true;

    // Скрываем кнопки
    document.getElementById('optionsContainer').style.display = 'none';

    // Показываем ответ пользователя
    addUserMessage(answer.text);

    // Сохраняем ответ
    userAnswers.push({
        question_id: questions[currentQuestionIndex].id,
        answer_text: answer.text,
        style_scores: answer.styles
    });

    // Переход к следующему вопросу
    currentQuestionIndex++;

    if (currentQuestionIndex < questions.length) {
        // Показываем следующий вопрос с задержкой
        setTimeout(() => {
            displayCurrentQuestion();
            isProcessing = false;
        }, 500);
    } else {
        // Показываем индикатор загрузки
        showLoading();

        // Отправляем на сервер
        setTimeout(() => {
            calculateAndShowResult();
            isProcessing = false;
        }, 800);
    }
}

// Показать загрузку
function showLoading() {
    const loadingDiv = document.getElementById('loading');
    loadingDiv.style.display = 'flex';
    document.getElementById('optionsContainer').style.display = 'none';
    scrollToBottom();
}

// Рассчёт результата
async function calculateAndShowResult() {
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userAnswers)
        });

        const result = await response.json();
        displayResult(result);

        document.getElementById('loading').style.display = 'none';
    } catch (error) {
        console.error('Ошибка:', error);
        addBotMessage('Извините, произошла ошибка при расчёте. Попробуйте ещё раз.');
    }
}

// Отображение результата
function displayResult(result) {
    const main = result.main_style;
    const secondary = result.secondary_style;

    let resultHTML = `
        <div class="result-card">
            ${main.image ? `<img src="${main.image}" alt="${main.name}" style="width: 100%; border-radius: 16px; margin-bottom: 20px;">` : ''}
            <div class="result-header">
                <div class="result-badge">Ваш стиль</div>
                <div class="result-confidence">${result.confidence}% соответствие</div>
            </div>
            <div class="result-style-name">${escapeHtml(main.name)}</div>
            <div class="result-style-full">${escapeHtml(main.full_name)}</div>
            <div class="result-description">${escapeHtml(main.description)}</div>
    `;

    if (secondary) {
        resultHTML += `
            <div class="result-section">
                <h4>✨ С нотками ${escapeHtml(secondary.name)}</h4>
                <div class="result-description" style="font-size: 14px;">${escapeHtml(secondary.description)}</div>
            </div>
        `;
    }

    resultHTML += `
            <div class="result-section">
                <h4>🎨 Цветовая палитра</h4>
                <div class="tags">
                    ${main.colors.map(color => `<span class="tag">${escapeHtml(color)}</span>`).join('')}
                </div>
            </div>

            <div class="result-section">
                <h4>🪵 Материалы</h4>
                <div class="tags">
                    ${main.materials.map(material => `<span class="tag">${escapeHtml(material)}</span>`).join('')}
                </div>
            </div>

            <div class="result-section">
                <h4>🛍️ Что купить в первую очередь</h4>
                <ul class="shopping-list">
                    ${main.shopping_list.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
                </ul>
            </div>

            <div class="result-section">
                <h4>⚠️ Чего избегать</h4>
                <div class="tags">
                    ${main.avoid.map(item => `<span class="tag">${escapeHtml(item)}</span>`).join('')}
                </div>
            </div>
        </div>
    `;

    addBotMessage(resultHTML, false);
}

// Обновление прогресса
function updateProgress() {
    const progress = (currentQuestionIndex / questions.length) * 100;
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }
}

// Сброс теста
function resetQuiz() {
    currentQuestionIndex = 0;
    userAnswers = [];
    isProcessing = false;

    // Очищаем сообщения
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.innerHTML = `
        <div class="message bot">
            <div class="message-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
                <div class="message-text">
                    Здравствуйте! Я AI-консультант по дизайну интерьера.<br><br>
                    Чтобы подобрать идеальный стиль для вашего пространства, задам 5 вопросов о ваших предпочтениях.
                    Отвечайте интуитивно — здесь нет правильных или неправильных ответов.
                </div>
            </div>
        </div>
    `;

    // Сбрасываем прогресс
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        progressFill.style.width = '0%';
    }

    // Скрываем опции если они есть
    const optionsContainer = document.getElementById('optionsContainer');
    if (optionsContainer) {
        optionsContainer.style.display = 'none';
    }

    // Показываем первый вопрос
    setTimeout(() => {
        displayCurrentQuestion();
    }, 500);
}

// Авто-скролл
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Тема с динамическим обновлением иконок
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        updateThemeIcon('dark');
    } else {
        updateThemeIcon('light');
    }

    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateThemeIcon(isDark ? 'dark' : 'light');

            // Добавляем визуальную обратную связь
            const slider = themeToggle.querySelector('.toggle-slider');
            if (slider) {
                slider.style.transform = isDark ? 'translateX(30px)' : 'translateX(0)';
            }
        });
    }
}

// Обновление иконки темы
function updateThemeIcon(theme) {
    const sunIcon = document.querySelector('.theme-toggle .fa-sun');
    const moonIcon = document.querySelector('.theme-toggle .fa-moon');
    if (sunIcon && moonIcon) {
        if (theme === 'dark') {
            sunIcon.style.opacity = '0.5';
            moonIcon.style.opacity = '1';
        } else {
            sunIcon.style.opacity = '1';
            moonIcon.style.opacity = '0.5';
        }
    }
}

// Мобильное меню
function initMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.querySelector('.sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('open');
        });

        // Закрыть при клике вне
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open')) {
                if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });

        // Закрыть при выборе опции
        const links = sidebar.querySelectorAll('button, a');
        links.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('open');
                }
            });
        });
    }
}

// Мобильное меню
function initMobileMenu() {
    const menuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) &&
                !menuToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    loadQuestions();
    initTheme();
    initMobileMenu();

    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (confirm('Начать тест заново?')) {
                resetQuiz();
            }
        });
    }
});

// Обработка ошибок сети
window.addEventListener('online', () => {
    addBotMessage('Соединение восстановлено! Продолжаем.');
});

window.addEventListener('offline', () => {
    addBotMessage('⚠️ Потеряно соединение с интернетом. Ответы сохранятся локально.');
});