document.addEventListener("DOMContentLoaded", () => {
  const orderSuccess = new URLSearchParams(window.location.search).get("order_success");
  const profileMenu = document.querySelector(".profile-menu");
  const profileTrigger = document.querySelector(".profile-trigger");
  const profileDropdown = document.querySelector(".profile-dropdown");

  if (orderSuccess) {
    const toast = document.createElement("div");
    toast.className = "toast-notification";
    toast.innerHTML = `
      <span>✓</span>
      <span>Order placed successfully! Thank you for your purchase.</span>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add("toast-show"), 100);
    setTimeout(() => {
      toast.classList.remove("toast-show");
      setTimeout(() => toast.remove(), 400);
    }, 4000);
  }
  const searchInput = document.querySelector(".search input[name='q']");
  const suggestions = document.querySelector(".search-suggestions");
  let suggestionTimer;

  function hideSuggestions() {
    if (suggestions) {
      suggestions.hidden = true;
      suggestions.innerHTML = "";
    }
  }

  if (searchInput && suggestions) {
    searchInput.addEventListener("input", () => {
      clearTimeout(suggestionTimer);
      const query = searchInput.value.trim();
      if (!query) {
        hideSuggestions();
        return;
      }

      suggestionTimer = setTimeout(async () => {
        const response = await fetch(`${searchInput.dataset.suggestUrl}?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        if (!data.results.length) {
          hideSuggestions();
          return;
        }

        suggestions.innerHTML = data.results
          .map(
            (book) => `
              <a class="suggestion-item" href="${book.url}">
                <img src="${book.image_url}" alt="">
                <span>${book.title}</span>
                <strong>${book.price}</strong>
              </a>
            `
          )
          .join("");
        suggestions.hidden = false;
      }, 180);
    });

    searchInput.addEventListener("focus", () => {
      if (suggestions.innerHTML) {
        suggestions.hidden = false;
      }
    });
  }

  document.addEventListener("click", (event) => {

    if (suggestions && !event.target.closest(".search")) {
      suggestions.hidden = true;
    }
  });

  const heroSlider = document.querySelector("[data-hero-slider]");

  if (heroSlider) {
    const track = heroSlider.querySelector(".hero-slider__track");
    const slides = Array.from(heroSlider.querySelectorAll(".hero-slide"));
    const dotsWrap = heroSlider.querySelector(".hero-slider__dots");
    const prevButton = heroSlider.querySelector(".hero-slider__arrow--prev");
    const nextButton = heroSlider.querySelector(".hero-slider__arrow--next");
    const intervalMs = 4500;
    let currentSlide = 0;
    let slideTimer;
    let touchStartX = 0;

    const dots = slides.map((_, index) => {
      const dot = document.createElement("button");
      dot.className = "hero-slider__dot";
      dot.type = "button";
      dot.setAttribute("aria-label", `Show promotion ${index + 1}`);
      dot.addEventListener("click", () => showSlide(index));
      dotsWrap.appendChild(dot);
      return dot;
    });

    function showSlide(index) {
      currentSlide = (index + slides.length) % slides.length;
      track.style.transform = `translateX(-${currentSlide * 100}%)`;
      dots.forEach((dot, dotIndex) => {
        dot.classList.toggle("active", dotIndex === currentSlide);
      });
      window.clearInterval(slideTimer);
      slideTimer = window.setInterval(() => showSlide(currentSlide + 1), intervalMs);
    }

    prevButton.addEventListener("click", () => showSlide(currentSlide - 1));
    nextButton.addEventListener("click", () => showSlide(currentSlide + 1));
    heroSlider.addEventListener("mouseenter", () => window.clearInterval(slideTimer));
    heroSlider.addEventListener("mouseleave", () => {
      slideTimer = window.setInterval(() => showSlide(currentSlide + 1), intervalMs);
    });
    heroSlider.addEventListener("touchstart", (event) => {
      touchStartX = event.touches[0].clientX;
    }, { passive: true });
    heroSlider.addEventListener("touchend", (event) => {
      const deltaX = event.changedTouches[0].clientX - touchStartX;
      if (Math.abs(deltaX) > 42) {
        showSlide(currentSlide + (deltaX < 0 ? 1 : -1));
      }
    });

    showSlide(0);
  }
});
