interface TimeBarDomElements {
	status: HTMLElement
	timeTaken: HTMLElement
	bar: HTMLElement
}

class TimeBar {
	private readonly timer: Timer = new Timer();
	private readonly domElements: TimeBarDomElements = this.initializeDom();
	private readonly durationSeconds: number;

	constructor(durationSeconds: number) {
		this.durationSeconds = durationSeconds
	}

	initializeDom(): TimeBarDomElements {
		return {
			status: document.getElementById("time-bar-status")!,
			timeTaken: document.getElementById("time-taken")!,
			bar: document.getElementById("time-bar")!,
		};
	}

	reset() {
		// Reset all the styles and time taken text
		this.domElements.status.classList.remove("exceeding");
		this.domElements.bar.classList.remove("smooth");
		this.domElements.bar.style.setProperty("--progress", `0%`);
		this.domElements.timeTaken!.innerText = "";

		// Set timer to null, just in case
		this.timer.abort();
	}

	start() {
		this.timer.start();
		this.domElements.bar.classList.add("smooth");
	}

	update() {
		// If timer not initialized, just empty the bar
		if (!this.timer.isInitialized()) {
			this.reset()
			return;
		}

		// Calculate time spent and bar percent
		const millisecondsPassed = this.timer.getMillisecondsPassed();
		const secondsPassed = Math.floor(this.timer.getSecondsPassed())

		const limitExceeded = secondsPassed >= this.durationSeconds;
		const barPercent = millisecondsPassed * 100 / (this.durationSeconds * 1000);

		// Update time bar text/status and its percentage
		this.domElements.bar!.style.setProperty("--progress", `${barPercent}%`);
		this.domElements.status!.classList.toggle("exceeding", limitExceeded);

		if (secondsPassed > 0) {
			this.domElements.timeTaken!.innerText = limitExceeded
				? `Time taken: More than ${this.durationSeconds} seconds!`
				: `Time taken: ${secondsPassed} second${secondsPassed > 1 ? 's' : ''}`
		} else {
			this.domElements.timeTaken!.innerText = "";
		}
	}

	destroy() {
		this.domElements.status.parentElement?.remove()
	}
}
