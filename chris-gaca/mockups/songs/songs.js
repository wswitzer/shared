
// Interactive search and filtering engine for Chris Gaca Song Archive
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('songSearch');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const regionSelect = document.getElementById('filterRegion');
  const countrySelect = document.getElementById('filterCountry');
  const langSelect = document.getElementById('filterLanguage');
  const resourceSelect = document.getElementById('filterResource');
  const resultsCount = document.getElementById('resultsCount');
  const resetBtn = document.getElementById('resetFiltersBtn');
  const emptyState = document.getElementById('emptyState');
  const emptyResetBtn = document.getElementById('emptyResetBtn');
  const cards = document.querySelectorAll('.song-browse-card');

  // Handle URL query parameters (e.g. ?region=Africa)
  const urlParams = new URLSearchParams(window.location.search);
  const regionParam = urlParams.get('region');
  const countryParam = urlParams.get('country');
  const qParam = urlParams.get('q');

  if (regionParam && regionSelect) {
    for (let opt of regionSelect.options) {
      if (opt.value.toLowerCase() === regionParam.toLowerCase()) {
        regionSelect.value = opt.value;
        break;
      }
    }
  }
  if (countryParam && countrySelect) {
    for (let opt of countrySelect.options) {
      if (opt.value.toLowerCase() === countryParam.toLowerCase()) {
        countrySelect.value = opt.value;
        break;
      }
    }
  }
  if (qParam && searchInput) {
    searchInput.value = qParam;
  }

  function filterSongs() {
    const q = (searchInput.value || '').trim().toLowerCase();
    const selRegion = regionSelect.value;
    const selCountry = countrySelect.value;
    const selLang = langSelect.value;
    const selRes = resourceSelect.value;

    if (q.length > 0) {
      clearSearchBtn.style.display = 'block';
    } else {
      clearSearchBtn.style.display = 'none';
    }

    let visibleCount = 0;

    cards.forEach(card => {
      const title = card.getAttribute('data-title') || '';
      const country = card.getAttribute('data-country') || '';
      const region = card.getAttribute('data-region') || '';
      const language = card.getAttribute('data-language') || '';
      const resources = (card.getAttribute('data-resources') || '').split(' ');

      // Query match (searches title, country, language, and region)
      let matchesQuery = true;
      if (q) {
        matchesQuery = title.includes(q) ||
                       country.includes(q) ||
                       language.includes(q) ||
                       region.toLowerCase().includes(q);
      }

      // Region match
      const matchesRegion = (selRegion === 'all' || region === selRegion);

      // Country match
      const matchesCountry = (selCountry === 'all' || country.toLowerCase() === selCountry.toLowerCase());

      // Language match
      const matchesLanguage = (selLang === 'all' || language.toLowerCase().includes(selLang.toLowerCase()));

      // Resource match
      let matchesResource = true;
      if (selRes !== 'all') {
        matchesResource = resources.includes(selRes);
      }

      const isVisible = matchesQuery && matchesRegion && matchesCountry && matchesLanguage && matchesResource;

      if (isVisible) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    // Update count display
    resultsCount.innerHTML = `Showing <strong>${visibleCount}</strong> of ${cards.length} songs`;

    // Toggle reset button
    const isFiltered = (q !== '') ||
                       (selRegion !== 'all') ||
                       (selCountry !== 'all') ||
                       (selLang !== 'all') ||
                       (selRes !== 'all');

    resetBtn.style.display = isFiltered ? 'inline-flex' : 'none';

    // Empty state
    if (visibleCount === 0) {
      emptyState.style.display = 'block';
    } else {
      emptyState.style.display = 'none';
    }
  }

  function resetAll() {
    searchInput.value = '';
    regionSelect.value = 'all';
    countrySelect.value = 'all';
    langSelect.value = 'all';
    resourceSelect.value = 'all';
    filterSongs();
  }

  // Event listeners
  searchInput.addEventListener('input', filterSongs);
  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    filterSongs();
    searchInput.focus();
  });
  regionSelect.addEventListener('change', filterSongs);
  countrySelect.addEventListener('change', filterSongs);
  langSelect.addEventListener('change', filterSongs);
  resourceSelect.addEventListener('change', filterSongs);
  resetBtn.addEventListener('click', resetAll);
  emptyResetBtn.addEventListener('click', resetAll);

  // Initial trigger
  filterSongs();
});
