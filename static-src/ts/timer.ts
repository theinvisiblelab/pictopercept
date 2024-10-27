class Timer {
	private beginTime: number | null = null;

	isInitialized() {
		return this.beginTime !== null;
	}

	start() {
		this.beginTime = new Date().getTime()
	}

	reset() {
		this.start()
	}

	abort() {
		this.beginTime = null;
	}

	getMillisecondsPassed(): number {
		if (this.beginTime)
			return (new Date().getTime() - this.beginTime)
		return NaN;
	}

	getSecondsPassed(): number {
		return this.getMillisecondsPassed() / 1000.0;
	}
}
