document.addEventListener('DOMContentLoaded', function() {
    // Sample job analysis data
    const appData = {
        gongmuwon: {
            title: '공무원',
            description: '국가나 사회를 위해 봉사하는 관직(官職)에 오르는 사주의 특징을 분석합니다. 사주 내 官星(관성)과 印星(인성)의 역할, 그리고 여러 제압 구조를 통해 공무원으로서의 가능성을 탐구합니다.',
            principles: [
                { 
                    title: '공무원의 기본 조건', 
                    content: '年/月柱에 印星(印庫), 官星(官庫)이 있고, 官/印이 財를 끼고 있거나(財生官), 印이 官을 끼고(官生印) 있으면 官/印이 旺하여 공무원의 사주가 될 수 있습니다. 또한 年/月柱의 財가 주위와 관련이 있으면 월급을 받는 공무원의 형상을 가집니다.' 
                },
                { 
                    title: '구조적 특징', 
                    content: '陽이 陰을 포국하거나 반적포 구조로 제압하는 경우, 寅木이 깊이 자리하거나 酉金과 배합되는 경우, 丑土나 辰土가 제압수단으로 작용하는 경우 공직에 오를 가능성이 높습니다.' 
                },
                { 
                    title: '帶象(대상)의 역할', 
                    content: '官統財, 財統官, 官印, 印官 등의 帶象은 사주 주인의 권력이나 직무의 성격을 나타냅니다. 예를 들어, 印이 官帽를 쓴 경우는 권력과 관련된 관직을 의미합니다.' 
                }
            ],
            cases: [
                { 
                    id: 'gongmuwon1',
                    title: '<사례 1> 관직',
                    sajuType: '乾命',
                    pillars: [['甲', '寅'], ['戊', '子'], ['乙', '亥'], ['甲', '辰']],
                    analysis: `
                        <p><strong>제압방식</strong>: 官이 活木, 帶象, 甲/寅木이 제압수단에 참여(관직). 年/月柱에 官과 財가 있고 子辰合으로 주위와 관계가 있어 관직하는 사주입니다.</p>
                        <p><strong><span class="highlight-term" data-chars="寅,亥">寅亥合</span></strong>: 官이 財를 合하나 功이 크지 않아 직급이 높지 못합니다.</p>
                        <p><strong>甲辰帶象</strong>: 財가 官帽를 쓰고 주위와 <span class="highlight-term" data-chars="子,辰">子辰合</span>으로 관계가 있으니 官統財입니다. 주위의 官이 賓位의 財庫로 향하니 본인의 官이 아니고 官의 財를 관리하는 것입니다.</p>
                        <p><strong>庚寅年</strong>: 寅木 食神이 官을 달고 와서 <span class="highlight-term" data-chars="乙,庚">乙庚合</span>으로 戊土 日干이 꺼리는 乙木을 제거하고 <span class="highlight-term" data-chars="寅,亥">寅亥合</span>으로 財인 亥水를 제압하는데 財統官으로 관을 재로 보니 발재하는 길한 운입니다.</p>
                        <p><strong>辛巳運</strong>: 運에서 "辛" 傷官이 출현하니 傷官見官이요, <span class="highlight-term" data-chars="寅,巳">寅巳穿</span>으로 주요 제압수단인 寅木이 傷하며, <span class="highlight-term" data-chars="巳,亥">巳亥沖</span>으로 祿인 巳火가 印星과 다투니 직책과 일이 없어 사직하게 됩니다.</p>
                    `
                }
            ]
        },
        gisuljik: {
            title: '기술 직업인',
            description: '전문적인 기술이나 지식을 바탕으로 직업을 갖는 사주의 특징을 알아봅니다. 食傷(식상)과 印星(인성)이 제압수단으로 작용하는 경우, 특정 오행의 조합을 통해 기술 분야를 유추할 수 있습니다.',
            principles: [
                {
                    title: '기술직의 기본 조건',
                    content: '食傷(식상)은 사상, 두뇌, 말재주, 기예를 의미하며, 한 가지 기술의 전문가임을 나타냅니다. 印星(인성) 역시 조직이나 기술의 상징을 갖습니다. 比劫(비겁)에 印星(인성)이나 食傷(식상)이 붙어 있으면 손기술이나 발기술을 의미합니다.'
                },
                {
                    title: '구조적 특징',
                    content: '食傷(식상)이 제압수단이거나, "火/金" 食傷(식상)으로 조합된 사주, 또는 食傷(식상)이 없으나 印星(인성)이 제압수단인 경우 기술직에 종사할 가능성이 높습니다.'
                }
            ],
            cases: [
                {
                    id: 'gisuljik1',
                    title: '<사례 1> 전신 전화국 기술공',
                    sajuType: '乾命',
                    pillars: [['戊', '寅'], ['乙', '酉'], ['辛', '丑'], ['丙', '辰']],
                    analysis: `
                        <p><strong>제압방식</strong>: 墓格, 帶象(辛丑). 傷官 丙火가 주요 제압수단이라 기술직이고 年/月柱의 財(丑/辰)가 합으로 주위와 관계가 있어 월급을 받는 사람입니다.</p>
                        <p><strong>직업분야</strong>: "丙" 傷官이 제압수단이니 영상매체, 전기통신, 전산분야의 직업입니다.</p>
                        <p><strong><span class="highlight-term" data-chars="丙,辛">丙辛合</span></strong>: 傷官이 財(官이 財)를 취하니 기술을 이용한 취재입니다.</p>
                    `
                }
            ]
        },
        budongsan: {
            title: '부동산/건축업',
            description: '토지와 건물을 다루는 부동산 및 건축업에 종사하는 사주의 특징을 살펴봅니다. 특정 오행(木, 土, 金)의 조합과 財庫(재고)의 역할이 중요한 단서가 됩니다.',
            principles: [
                {
                    title: '부동산/건축업의 象',
                    content: '원국에 戊戌, 己未, 己丑, 己卯, 甲寅 등의 간지나, 卯戌合, 卯未合, 寅丑合 등의 합이 있으면 부동산이나 건축업의 象으로 봅니다.'
                },
                {
                    title: '오행의 조합',
                    content: '木/土가 印星인 경우, 火와 燥土가 제압수단인 경우, 또는 "木, 土, 金"의 조합이 제압수단이 되거나 제압을 당하는 경우, 이 조합이 財가 되는 경우 부동산/건축업과 인연이 깊습니다.'
                }
            ],
            cases: []
        },
        gyoyukja: {
            title: '교육자',
            description: '교육과 관련된 직업을 갖는 사주의 특징을 분석합니다. 印星(인성)의 역할이 핵심적이며, 특정 구조를 통해 교육계 진출 가능성을 살펴볼 수 있습니다.',
            principles: [
                {
                    title: '교육자의 기본 조건',
                    content: '印星(인성)이 강하고 제압수단으로 작용하는 경우, 또는 木火 조합이 있는 경우 교육계와 인연이 있습니다.'
                }
            ],
            cases: []
        },
        jangsa: {
            title: '사업/무역업',
            description: '사업이나 무역업에 종사하는 사주의 특징을 살펴봅니다. 財星(재성)과 食傷(식상)의 조합, 그리고 특정 제압 구조가 중요한 역할을 합니다.',
            principles: [
                {
                    title: '사업가의 기본 조건',
                    content: '食神生財格이나 傷官生財格의 구조를 가지고 있거나, 財星이 강하고 제압수단이 있는 경우 사업에 적합합니다.'
                }
            ],
            cases: []
        }
    };

    // UI Elements
    const mainTabs = document.querySelectorAll('.main-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const jobNavBtns = document.querySelectorAll('.job-nav-btn');
    const jobContentArea = document.getElementById('job-content-area');
    const modal = document.getElementById('modal');
    const closeModalBtn = document.getElementById('close-modal');
    
    // Editor Elements
    const addCaseBtn = document.getElementById('add-case-btn');
    const newCaseTitleInput = document.getElementById('new-case-title');
    const newCaseSajuTypeInput = document.getElementById('new-case-saju-type');
    const newCasePillarsInput = document.getElementById('new-case-pillars');
    const newCaseAnalysisInput = document.getElementById('new-case-analysis');
    const downloadBtn = document.getElementById('download-json-btn');
    const editorNavBtns = document.querySelectorAll('.editor-nav-btn');
    const editorCategoryContent = document.getElementById('editor-category-content');

    let currentJobCategory = 'gongmuwon';

    // Initialize the application
    init();

    function init() {
        setupMainTabListeners();
        setupJobNavListeners();
        setupModalListeners();
        setupEditorListeners();
        renderJobContent(currentJobCategory);
        updateDownloadLink();
    }

    // Main Tab Navigation
    function setupMainTabListeners() {
        mainTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.id.replace('tab-', '');
                switchMainTab(tabId);
            });
        });
    }

    function switchMainTab(tabId) {
        // Update tab buttons
        mainTabs.forEach(tab => tab.classList.remove('active'));
        document.getElementById(`tab-${tabId}`).classList.add('active');

        // Update content
        tabContents.forEach(content => content.classList.add('hidden'));
        document.getElementById(`${tabId}-content`).classList.remove('hidden');
    }

    // Job Category Navigation
    function setupJobNavListeners() {
        jobNavBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const target = btn.dataset.target;
                switchJobCategory(target);
            });
        });
    }

    function switchJobCategory(category) {
        // Update nav buttons
        jobNavBtns.forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-target="${category}"]`).classList.add('active');

        // Update content
        currentJobCategory = category;
        renderJobContent(category);
    }

    function renderJobContent(category) {
        const data = appData[category];
        if (!data) return;

        let contentHtml = `
            <section id="${category}" class="space-y-12">
                <div class="text-center bg-white p-8 rounded-xl shadow-md">
                    <h2 class="text-3xl font-bold mb-2 text-teal-800">${data.title}</h2>
                    <p class="text-lg text-gray-600 max-w-3xl mx-auto">${data.description}</p>
                </div>
        `;

        // Add principles section
        if (data.principles && data.principles.length > 0) {
            contentHtml += `
                <div>
                    <h3 class="text-2xl font-semibold mb-6 text-center text-gray-700">기본 원리</h3>
                    ${createAccordion(data.principles)}
                </div>
            `;
        }

        // Add cases section
        if (data.cases && data.cases.length > 0) {
            contentHtml += `
                <div>
                    <h3 class="text-2xl font-semibold mb-6 text-center text-gray-700">실제 사례</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        ${data.cases.map(createCaseCard).join('')}
                    </div>
                </div>
            `;
        }

        contentHtml += `</section>`;
        jobContentArea.innerHTML = contentHtml;

        // Setup accordion listeners
        setupAccordionListeners();
        setupCaseCardListeners();
    }

    function createAccordion(items) {
        let accordionHtml = '<div class="space-y-4">';
        items.forEach((item, index) => {
            accordionHtml += `
                <div class="bg-white rounded-lg shadow-sm">
                    <button class="w-full text-left p-4 flex justify-between items-center accordion-toggle" data-index="${index}">
                        <span class="font-semibold text-teal-700">${item.title}</span>
                        <svg class="w-6 h-6 transform transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </button>
                    <div class="accordion-content p-4 border-t border-gray-200 text-gray-600 hidden">
                        ${item.content.replace(/\n/g, '<br>')}
                    </div>
                </div>
            `;
        });
        accordionHtml += '</div>';
        return accordionHtml;
    }

    function createCaseCard(caseItem) {
        return `
            <div class="case-card bg-white p-6 rounded-xl shadow-lg cursor-pointer hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between" data-id="${caseItem.id}">
                <div>
                   <h4 class="text-xl font-bold text-teal-800 mb-2">${caseItem.title}</h4>
                   <p class="text-gray-500 text-sm mb-4">${caseItem.sajuType}</p>
                </div>
                <div class="text-right text-teal-600 font-semibold">자세히 보기 →</div>
            </div>
        `;
    }

    function setupAccordionListeners() {
        const accordionToggles = document.querySelectorAll('.accordion-toggle');
        accordionToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                const content = toggle.nextElementSibling;
                const isHidden = content.classList.contains('hidden');
                
                if (isHidden) {
                    content.classList.remove('hidden');
                    toggle.classList.add('active');
                } else {
                    content.classList.add('hidden');
                    toggle.classList.remove('active');
                }
            });
        });
    }

    function setupCaseCardListeners() {
        const caseCards = document.querySelectorAll('.case-card');
        caseCards.forEach(card => {
            card.addEventListener('click', () => {
                const caseId = card.dataset.id;
                openCaseModal(caseId);
            });
        });
    }

    function openCaseModal(caseId) {
        const caseData = findCaseById(caseId);
        if (!caseData) return;

        const modalTitle = document.getElementById('modal-title');
        const modalSaju = document.getElementById('modal-saju');
        const modalAnalysis = document.getElementById('modal-analysis');

        modalTitle.textContent = caseData.title;
        modalSaju.innerHTML = createSajuGrid(caseData);
        modalAnalysis.innerHTML = caseData.analysis;

        showModal();
        setupHighlightListeners();
    }

    function findCaseById(caseId) {
        for (const category in appData) {
            const categoryData = appData[category];
            if (categoryData.cases) {
                const caseData = categoryData.cases.find(c => c.id === caseId);
                if (caseData) return caseData;
            }
        }
        return null;
    }

    function createSajuGrid(caseData) {
        const { pillars, sajuType } = caseData;
        const pillarNames = ['년주', '월주', '일주', '시주'];
        
        let gridHtml = `
            <div class="text-center mb-4">
                <h3 class="text-lg font-bold text-gray-700">${sajuType}</h3>
            </div>
            <div class="saju-grid">
        `;

        // Header row
        pillarNames.forEach(name => {
            gridHtml += `<div class="saju-pillar">${name}</div>`;
        });

        // Character rows
        for (let i = 0; i < 2; i++) {
            pillars.forEach(pillar => {
                gridHtml += `<div class="saju-char" data-char="${pillar[i]}">${pillar[i]}</div>`;
            });
        }

        gridHtml += '</div>';
        return gridHtml;
    }

    function setupHighlightListeners() {
        const highlightTerms = document.querySelectorAll('.highlight-term');
        highlightTerms.forEach(term => {
            term.addEventListener('mouseenter', () => {
                const chars = term.dataset.chars?.split(',') || [];
                highlightSajuChars(chars);
            });

            term.addEventListener('mouseleave', () => {
                clearSajuHighlights();
            });
        });
    }

    function highlightSajuChars(chars) {
        clearSajuHighlights();
        chars.forEach(char => {
            const elements = document.querySelectorAll(`[data-char="${char.trim()}"]`);
            elements.forEach(el => el.classList.add('highlight-saju-char'));
        });
    }

    function clearSajuHighlights() {
        const highlighted = document.querySelectorAll('.highlight-saju-char');
        highlighted.forEach(el => el.classList.remove('highlight-saju-char'));
    }

    // Modal Functions
    function setupModalListeners() {
        closeModalBtn.addEventListener('click', hideModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) hideModal();
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                hideModal();
            }
        });
    }

    function showModal() {
        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
        document.body.style.overflow = 'hidden';
    }

    function hideModal() {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300);
        document.body.style.overflow = '';
    }

    // Editor Functions
    function setupEditorListeners() {
        addCaseBtn.addEventListener('click', addNewCase);
        editorNavBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const category = btn.dataset.category;
                switchEditorCategory(category);
            });
        });
        updateDownloadLink();
    }

    function addNewCase() {
        const title = newCaseTitleInput.value.trim();
        const sajuType = newCaseSajuTypeInput.value.trim();
        const pillarsText = newCasePillarsInput.value.trim();
        const analysis = newCaseAnalysisInput.value.trim();

        if (!title || !sajuType || !pillarsText || !analysis) {
            alert('모든 필드를 입력해주세요.');
            return;
        }

        // Parse pillars (expecting 8 characters)
        if (pillarsText.length !== 8) {
            alert('사주팔자는 정확히 8글자를 입력해주세요.');
            return;
        }

        const pillars = [];
        for (let i = 0; i < 4; i++) {
            pillars.push([pillarsText[i * 2], pillarsText[i * 2 + 1]]);
        }

        const newCase = {
            id: `custom_${Date.now()}`,
            title,
            sajuType,
            pillars,
            analysis: `<p>${analysis}</p>`
        };

        // Add to current category
        if (!appData[currentJobCategory].cases) {
            appData[currentJobCategory].cases = [];
        }
        appData[currentJobCategory].cases.push(newCase);

        // Clear form
        newCaseTitleInput.value = '';
        newCaseSajuTypeInput.value = '';
        newCasePillarsInput.value = '';
        newCaseAnalysisInput.value = '';

        // Refresh display
        renderJobContent(currentJobCategory);
        updateDownloadLink();

        alert('새로운 사례가 추가되었습니다!');
    }

    function switchEditorCategory(category) {
        editorNavBtns.forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-category="${category}"]`).classList.add('active');

        const data = appData[category];
        let contentHtml = `
            <h4 class="text-xl font-bold mb-4 text-gray-700">${data.title} 편집</h4>
            <div class="space-y-4">
                <div>
                    <h5 class="font-semibold text-gray-600 mb-2">설명</h5>
                    <p class="text-gray-600">${data.description}</p>
                </div>
                <div>
                    <h5 class="font-semibold text-gray-600 mb-2">현재 사례 수</h5>
                    <p class="text-gray-600">${data.cases ? data.cases.length : 0}개</p>
                </div>
            </div>
        `;

        editorCategoryContent.innerHTML = contentHtml;
    }

    function updateDownloadLink() {
        const dataStr = JSON.stringify(appData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        downloadBtn.href = url;
        downloadBtn.download = 'saju_data.json';
    }
});