(function () {
  const STORAGE_KEY = "huiying-language";
  const supportedLanguages = new Set(["en", "zh"]);

  function getPreferredLanguage() {
    const queryLanguage = new URLSearchParams(window.location.search).get("lang");
    if (supportedLanguages.has(queryLanguage)) {
      return queryLanguage;
    }
    const savedLanguage = localStorage.getItem(STORAGE_KEY);
    return supportedLanguages.has(savedLanguage) ? savedLanguage : "en";
  }

  function setLanguage(language) {
    const selectedLanguage = supportedLanguages.has(language) ? language : "en";

    document.documentElement.lang = selectedLanguage === "zh" ? "zh-Hant" : "en";
    document.querySelectorAll("[data-en][data-zh]").forEach((element) => {
      element.textContent = element.dataset[selectedLanguage];
    });
    document.querySelectorAll("[data-en-html][data-zh-html]").forEach((element) => {
      element.innerHTML = element.dataset[`${selectedLanguage}Html`];
    });
    document.querySelectorAll("[data-lang-button]").forEach((button) => {
      const isActive = button.dataset.langButton === selectedLanguage;
      button.classList.toggle("active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
    document.querySelectorAll('a[href$=".html"], a[href*=".html?"]').forEach((link) => {
      const target = new URL(link.getAttribute("href"), window.location.href);
      target.searchParams.set("lang", selectedLanguage);
      link.setAttribute("href", `${target.pathname.split("/").pop()}${target.search}${target.hash}`);
    });

    localStorage.setItem(STORAGE_KEY, selectedLanguage);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-lang-button]").forEach((button) => {
      button.addEventListener("click", () => setLanguage(button.dataset.langButton));
    });
    setLanguage(getPreferredLanguage());
  });
})();
