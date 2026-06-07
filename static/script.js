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
        return text;
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
        setTimeout(() => {
            displayCurrentQuestion();
            isProcessing = false;
        }, 500);
    } else {
        showLoading();
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

    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        progressFill.style.width = '0%';
    }

    const optionsContainer = document.getElementById('optionsContainer');
    if (optionsContainer) {
        optionsContainer.style.display = 'none';
    }

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

// Тема
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }

    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
        });
    }
}

// Мобильное меню (только одна кнопка)
function initMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');

    // Создаем overlay
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
    }

    function openSidebar() {
        sidebar.classList.add('open');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (mobileMenuToggle) {
        // Убираем старые обработчики
        mobileMenuToggle.removeEventListener('click', openSidebar);
        mobileMenuToggle.removeEventListener('click', closeSidebar);

        mobileMenuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            if (sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    // Закрыть по клику на overlay
    overlay.addEventListener('click', closeSidebar);

    // Закрыть при изменении размера окна (если открыто и стало больше 768px)
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });
}

// Скрытие/показ окна с вопросами
function initToggleQuestions() {
    const toggleBtn = document.getElementById('toggleQuestionsBtn');
    const optionsContainer = document.getElementById('optionsContainer');
    const toggleText = toggleBtn.querySelector('.toggle-text');
    const toggleIcon = toggleBtn.querySelector('i');

    let isHidden = false;

    // Сохраняем состояние в localStorage
    const savedState = localStorage.getItem('questionsHidden');
    if (savedState === 'true') {
        isHidden = true;
        optionsContainer.style.display = 'none';
        toggleText.textContent = 'Показать';
        toggleIcon.className = 'fas fa-chevron-down';
    }

    toggleBtn.addEventListener('click', () => {
        isHidden = !isHidden;

        if (isHidden) {
            optionsContainer.style.display = 'none';
            toggleText.textContent = 'Показать';
            toggleIcon.className = 'fas fa-chevron-down';
            localStorage.setItem('questionsHidden', 'true');
        } else {
            optionsContainer.style.display = 'flex';
            toggleText.textContent = 'Скрыть';
            toggleIcon.className = 'fas fa-chevron-up';
            localStorage.setItem('questionsHidden', 'false');
        }
    });

    // Показываем кнопку только на мобильных и когда есть активные вопросы
    const checkVisibility = () => {
        if (window.innerWidth <= 768 && optionsContainer.children.length > 0) {
            toggleBtn.style.display = 'flex';
        } else {
            toggleBtn.style.display = 'none';
        }
    };

    // Наблюдаем за изменениями в контейнере опций
    const observer = new MutationObserver(checkVisibility);
    observer.observe(optionsContainer, {
        childList: true,
        attributes: true,
        attributeFilter: ['style']
    });
    checkVisibility();

    window.addEventListener('resize', checkVisibility);
}

// Функция для создания адаптивного изображения в сообщении
function createAdaptiveImage(imageUrl, caption = '') {
    const container = document.createElement('div');
    container.className = 'image-container';

    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = caption || 'Пример интерьера';
    img.className = 'message-image';
    img.loading = 'lazy';  // Ленивая загрузка

    // Добавляем возможность открыть изображение в полном размере
    img.addEventListener('click', (e) => {
        e.stopPropagation();
        openImageModal(imageUrl);
    });

    container.appendChild(img);

    if (caption) {
        const captionDiv = document.createElement('div');
        captionDiv.className = 'image-caption';
        captionDiv.textContent = caption;
        container.appendChild(captionDiv);
    }

    return container;
}

// Функция для открытия модального окна с изображением
function openImageModal(imageUrl) {
    let modal = document.querySelector('.image-modal');

    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <button class="image-modal-close">&times;</button>
            <img src="" alt="Увеличенное изображение">
        `;
        document.body.appendChild(modal);

        // Закрытие по клику
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('image-modal-close')) {
                modal.classList.remove('active');
            }
        });

        // Закрытие по ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                modal.classList.remove('active');
            }
        });
    }

    const modalImg = modal.querySelector('img');
    modalImg.src = imageUrl;
    modal.classList.add('active');
}

// Обновляем функцию addBotMessage для поддержки изображений
function addBotMessage(text, withOptions = false, imageUrl = null, imageCaption = null) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';

    let contentHtml = `<div class="message-avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <div class="message-text">${formatMessageText(text)}</div>`;

    // Добавляем изображение, если оно есть
    if (imageUrl) {
        contentHtml += `<div class="image-container">
            <img src="${imageUrl}" alt="${imageCaption || 'Пример интерьера'}" class="message-image" loading="lazy">
            ${imageCaption ? `<div class="image-caption">${imageCaption}</div>` : ''}
        </div>`;
    }

    contentHtml += `</div>`;
    messageDiv.innerHTML = contentHtml;
    messagesContainer.appendChild(messageDiv);

    // Добавляем обработчик клика для изображения после рендеринга
    if (imageUrl) {
        const img = messageDiv.querySelector('.message-image');
        if (img) {
            img.addEventListener('click', () => openImageModal(imageUrl));
        }
    }

    scrollToBottom();

    if (withOptions && currentQuestionIndex < questions.length) {
        showOptions(questions[currentQuestionIndex].answers);
    }
}

// Обновляем функцию displayResult для адаптивных изображений
function displayResult(result) {
    const main = result.main_style;
    const secondary = result.secondary_style;

    let resultHTML = `
        <div class="result-card">
            ${main.image ? `<div class="image-container" style="margin-bottom: 20px;">
                <img src="${main.image}" alt="${main.name}" class="message-image" loading="lazy" style="width: 100%;">
                <div class="image-caption">${main.full_name}</div>
            </div>` : ''}
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
                <h4>🛠️ Материалы</h4>
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

    // Добавляем обработчики для изображений в результате
    const resultImages = document.querySelectorAll('.result-card .message-image');
    resultImages.forEach(img => {
        img.addEventListener('click', () => openImageModal(img.src));
    });
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    loadQuestions();
    initTheme();
    initMobileMenu();
    initToggleQuestions();

    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (confirm('Начать тест заново?')) {
                resetQuiz();
            }
        });
    }

    // Кнопка меню для десктопа (гамбургер в шапке)
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
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