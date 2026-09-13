// Alpine.js component for the concepts page: an accordion of concept cards
// with favorites and an optional "Visualize Prototype" image per concept.

// States for the visualize area of each concept. An object with a "src" key
// means an image is ready to show.
const VISUALIZE_LOADING = "loading";
const VISUALIZE_ERROR = "error";

// Alpine calls this with the list of concepts the server rendered into the page.
function conceptsPage(concepts) {
  return {
    concepts: concepts,
    favorites: [],
    open: {},
    visualize: {},
    visualizeError: {},

    // Favorites first, then everything else, each group in number order.
    // The server already sorted concepts by number.
    sortedConcepts() {
      const favoriteConcepts = [];
      const otherConcepts = [];
      for (const concept of this.concepts) {
        if (this.isFavorite(concept.number)) {
          favoriteConcepts.push(concept);
        } else {
          otherConcepts.push(concept);
        }
      }
      return favoriteConcepts.concat(otherConcepts);
    },

    isFavorite(conceptNumber) {
      return this.favorites.includes(conceptNumber);
    },

    toggleFavorite(conceptNumber) {
      if (this.isFavorite(conceptNumber)) {
        const remaining = [];
        for (const favoriteNumber of this.favorites) {
          if (favoriteNumber !== conceptNumber) {
            remaining.push(favoriteNumber);
          }
        }
        this.favorites = remaining;
      } else {
        this.favorites.push(conceptNumber);
      }
    },

    toggleOpen(conceptNumber) {
      this.open[conceptNumber] = !this.open[conceptNumber];
    },

    isOpen(conceptNumber) {
      return this.open[conceptNumber] === true;
    },

    showVisualizeButton(conceptNumber) {
      const state = this.visualize[conceptNumber];
      return !state || state === VISUALIZE_ERROR;
    },

    isVisualizeLoading(conceptNumber) {
      return this.visualize[conceptNumber] === VISUALIZE_LOADING;
    },

    hasImage(conceptNumber) {
      const state = this.visualize[conceptNumber];
      if (!state) {
        return false;
      }
      return state.src !== undefined;
    },

    // "async" lets us "await" the image request instead of nesting callbacks.
    async visualizePrototype(concept) {
      const conceptNumber = concept.number;
      this.visualize[conceptNumber] = VISUALIZE_LOADING;
      this.visualizeError[conceptNumber] = null;

      const requestBody = {
        image_fields: concept.image_fields,
        title: concept.title,
      };

      try {
        const response = await fetch("/visualize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        });
        const data = await response.json();

        if (!response.ok || data.error) {
          if (data.error) {
            this.visualizeError[conceptNumber] = data.error;
          } else {
            this.visualizeError[conceptNumber] = "Unknown error";
          }
          this.visualize[conceptNumber] = VISUALIZE_ERROR;
        } else {
          this.visualize[conceptNumber] = { src: data.image };
        }
      } catch (error) {
        this.visualizeError[conceptNumber] = "Request failed";
        this.visualize[conceptNumber] = VISUALIZE_ERROR;
      }
    },
  };
}
