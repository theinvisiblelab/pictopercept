/**
 * A timer.
 */
class Timer {
	/**
	 * The beging time moment as number.
	 * @type {number | null}
	 */
	#beginTime = null;

	/**
	 * Checks if the Timer is initialized or not.
	 * @returns {boolean} - True if the timer is initialized. False otherwise.
	 */
	isInitialized() {
		return this.#beginTime !== null;
	}

	/**
	 * Starts the Timer.
	 */
	start() {
		this.#beginTime = new Date().getTime()
	}

	/**
	 * Resets the Timer.
	 */
	reset() {
		this.start()
	}

	/**
	 * Aborts the Timer, making it uninitialized again.
	 */
	abort() {
		this.#beginTime = null;
	}

	/**
	 * @returns {number} - Returns the milliseconds passed since the Timer started, or NaN if is uninitialized.
	 */
	getMillisecondsPassed() {
		if (this.#beginTime)
			return (new Date().getTime() - this.#beginTime)
		return NaN;
	}

	/**
	 * @returns {number} - Returns the seconds passed since the Timer started, or NaN if is uninitialized.
	 */
	getSecondsPassed() {
		return this.getMillisecondsPassed() / 1000.0;
	}
}
