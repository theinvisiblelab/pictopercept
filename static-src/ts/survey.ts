class Answer {
	index: number;
	image: string;
	chosen: boolean;
	userId: string;
	job: string;
	timeBarEnabled: boolean;

	constructor(index: number, image: string, chosen: boolean, userId: string, job: string, timeBarEnabled: boolean) {
		this.index = index;
		this.image = image;
		this.chosen = chosen;
		this.userId = userId;
		this.job = job;
		this.timeBarEnabled = timeBarEnabled;
	}
};

// Declare some DOM for easy access 
const elementQuestion = document.getElementById("question")!;
const elementOptions = document.getElementById("options")!;
const elementOption0 = document.getElementById("option0")!;
const elementOption1 = document.getElementById("option1")!;
const elementTimeBarStatus = document.getElementById("time-bar-status")!;
const elementTimeBarTaken = document.getElementById("time-taken")!;
const elementTimeBar = document.getElementById("time-bar")! as HTMLElement;

declare var images: Array<string>; // Value set from HTML
declare var jobs: Array<string>; // Value set from HTML
declare var timeBarEnabled: boolean; // Value set from HTML

const TIME_BAR_MAX_SECONDS: number = 5;
const FORM_MAX_SECONDS: number = 60;

const answers: Array<[Answer, Answer]> = Array<[Answer, Answer]>();

let formBeginTime: number | null = null;
let answerBeginTime: number | null = null;
let answerIndex = 0;
let jobIndex = 0;

function formNext(firstUpdate: boolean = false) {
	// Advance indices
	if (!firstUpdate) {
		answerIndex += 2;
		jobIndex = Math.floor(Math.random() * jobs.length)
	}

	const loadImage = (source: string): Promise<HTMLImageElement> => {
		return new Promise<HTMLImageElement>((resolve, reject) => {
			let image = new Image();
			image.src = source;

			image.onload = () => resolve(image);
			image.onerror = () => reject(new Error("Could not load the image. Error"));
		});
	};

	// Load the new images
	Promise.all([loadImage(images[answerIndex]), loadImage(images[answerIndex + 1])])
		.then(([_image0, _image1]) => {
			let elementImage0 = elementOption0.querySelector("img")! as HTMLImageElement;
			let elementImage1 = elementOption1.querySelector("img")! as HTMLImageElement;

			elementImage0.src = images[answerIndex];
			elementImage1.src = images[answerIndex + 1];

			elementQuestion.innerHTML = `Who of these is <b style="text-transform:uppercase;">${jobs[jobIndex]}</b>?`

			answerBeginTime = new Date().getTime();
			if (!formBeginTime) formBeginTime = new Date().getTime();

			elementOptions.classList.remove("loading")
			elementTimeBar?.classList.add("smooth");
		})
		.catch((error) => {
			console.error(error)
		})
}

function formEnd() {
	elementQuestion.innerText = "Uploading results...";

	const postRequest = new Request("/post-survey", {
		method: "POST",
		body: "temporal_data",
	});

	fetch(postRequest).then((response) => {
		if (response.status == 200)
			console.log("Results posted.");
		else
			console.error("Error posting the results.. Got status: ", response.status);
	}).catch((error) => {
		console.error("Error posting the results...", error);
	});
}

document.querySelectorAll("#options > .option")!.forEach((element) => {
	const clicked0 = element.id === "option0";

	element.addEventListener("click", () => {
		// Hide options
		elementOptions.classList.add("loading");
		elementTimeBar?.classList.remove("smooth");
		elementTimeBar?.style.setProperty("--progress", `0%`);

		const IMG_EXPR = /(train|val)\/\w+\.(jp(e)?g|png)/;
		// Add current answer
		answers.push([
			new Answer(answerIndex, (IMG_EXPR.exec(images[answerIndex]) || [images[answerIndex]])[0], clicked0, "todo", jobs[jobIndex], timeBarEnabled),
			new Answer(answerIndex, (IMG_EXPR.exec(images[answerIndex + 1]) || [images[answerIndex + 1]])[0], clicked0, "todo", jobs[jobIndex], timeBarEnabled)]
		);

		answerBeginTime = null;

		const secondsSpent = formBeginTime ? (new Date().getTime() - formBeginTime) / 1000 : 0;
		const formEnded = secondsSpent >= FORM_MAX_SECONDS || answerIndex >= images.length;

		formEnded ? formEnd() : formNext();
	})
})

formNext(true)

// ### Time bar related ###
function resetTimeBar() {
	elementTimeBar.style.setProperty("--progress", `0%`);
	elementTimeBarTaken.innerText = "";
	elementTimeBarStatus.classList.remove("exceeding");
}

function updateTimeBar() {
	if (!timeBarEnabled) return;
	if (!answerBeginTime) {
		resetTimeBar();
		return;
	}

	// Calculate time spent and bar percent
	const millisecondsPassed = new Date().getTime() - answerBeginTime;
	const secondsPassed = Math.floor(millisecondsPassed / 1000)

	const limitExceeded = secondsPassed >= TIME_BAR_MAX_SECONDS;
	const barPercent = millisecondsPassed * 100 / (TIME_BAR_MAX_SECONDS * 1000);

	// Update time bar text/status and its percentage
	elementTimeBar.style.setProperty("--progress", `${barPercent}%`);
	elementTimeBarStatus.classList.toggle("exceeding", limitExceeded);

	if (secondsPassed > 0) {
		elementTimeBarTaken.innerText = limitExceeded
			? `Time taken: More than ${TIME_BAR_MAX_SECONDS} seconds!`
			: `Time taken: ${secondsPassed} second${secondsPassed > 1 ? 's' : ''}`
	} else {
		elementTimeBarTaken.innerText = "";
	}
}

updateTimeBar();
setInterval(updateTimeBar, 100);
