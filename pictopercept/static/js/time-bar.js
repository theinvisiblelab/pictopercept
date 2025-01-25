/**
 * @typedef {Object} TimeBarDomElements
 * @property {HTMLElement} status - The status element.
 * @property {HTMLElement} timeTaken - The element displaying the time taken.
 * @property {HTMLElement} bar - The progress bar element.
 */

/**
 * A time bar.
 */
class TimeBar {
	/**
	 * The timer used by the TimeBar.
	 * @type {Timer}
	 * @readonly
	 */
	#timer = new Timer();

	/** 
	 * The TimeBar's DOM elements, for direct access.
	 * @type {TimeBarDomElements}
	 * @readonly
	 */
	#domElements = this.initializeDom();

	/** 
	 * The duration of the TimeBar, in seconds.
	 * @type {number}
	 * @readonly
	 */
	#durationSeconds;

	/**
	 * Builds a new TimeBar.
	 * @param {number} durationSeconds - The duration of the TimeBar, in seconds.
	 */
	constructor(durationSeconds) {
		this.#durationSeconds = durationSeconds
	}

	/**
	 * Initializes the dom, making references to each element needed by the TimeBar.
	 * @returns {TimeBarDomElements} - The object holding the DOM references.
	 */
	initializeDom() {
		const status = document.getElementById("time-bar-status");
		const timeTaken = document.getElementById("time-taken");
		const bar = document.getElementById("time-bar");

		if (!status || !timeTaken || !bar) {
			throw new Error("One or more DOM elements of the TimeBar are missing. Were they deleted?");
		}

		return {
			status,
			timeTaken,
			bar,
		};
	}

	/**
	 * Resets the TimeBar.
	 */
	reset() {
		// Reset all the styles and time taken text
		this.#domElements.status.classList.remove("exceeding");
		this.#domElements.bar.classList.remove("smooth");
		this.#domElements.bar.style.setProperty("--progress", `0%`);
		this.#domElements.timeTaken.innerText = "";

		// Set timer to null, just in case
		this.#timer.abort();
	}

	/**
	 * Starts the TimeBar.
	 */
	start() {
		this.#timer.start();
		this.#domElements.bar.classList.add("smooth");
	}

	/**
	 * Updates the TimeBar visually.
	 */
	update() {
		// If timer not initialized, just empty the bar
		if (!this.#timer.isInitialized()) {
			this.reset()
			return;
		}

		// Calculate time spent and bar percent
		const millisecondsPassed = this.#timer.getMillisecondsPassed();
		const secondsPassed = Math.floor(this.#timer.getSecondsPassed())

		const limitExceeded = secondsPassed >= this.#durationSeconds;
		const barPercent = millisecondsPassed * 100 / (this.#durationSeconds * 1000);

		// Update time bar text/status and its percentage
		this.#domElements.bar.style.setProperty("--progress", `${barPercent}%`);
		this.#domElements.status.classList.toggle("exceeding", limitExceeded);

		if (secondsPassed > 0) {
			this.#domElements.timeTaken.innerText = limitExceeded
				? `Time taken: More than ${this.#durationSeconds} seconds!`
				: `Time taken: ${secondsPassed} second${secondsPassed > 1 ? 's' : ''}`
		} else {
			this.#domElements.timeTaken.innerText = "";
		}
	}

	/**
	 * Destroys the TimeBar's main DOM element.
	 */
	destroy() {
		this.#domElements.status.parentElement?.remove()
	}
}

