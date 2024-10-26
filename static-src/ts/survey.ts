class Answer {
	index: number;
	image: string;
	chosen: boolean;
	userId: string;
	timeBarEnabled: boolean;
	questionVariables: { [key: string]: string }

	constructor(index: number, image: string, chosen: boolean, userId: string, questionVariables: { [key: string]: string }, timeBarEnabled: boolean) {
		this.index = index;
		this.image = image;
		this.chosen = chosen;
		this.userId = userId;
		this.questionVariables = questionVariables;
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

declare var surveyQuestionRaw: any;
declare var images: Array<string>; // Value set from HTML
declare var timeBarEnabled: boolean; // Value set from HTML
declare var datasetUrl: string; // Value set from HTML

const surveyQuestion = new QuestionGenerator(surveyQuestionRaw["text"], surveyQuestionRaw["variables"]);

const TIME_BAR_MAX_SECONDS: number = 5;
const FORM_MAX_SECONDS: number = 60;

const answers: Array<[Answer, Answer]> = Array<[Answer, Answer]>();

let formBeginTime: number | null = null;
let answerBeginTime: number | null = null;
let answerIndex = 0;
let generatedQuestion: GeneratedQuestion | null = null;

function formNext(firstUpdate: boolean = false) {
	// Advance indices
	generatedQuestion = surveyQuestion.generateQuestion();
	if (!firstUpdate) {
		answerIndex += 2;
	}

	let elementImage0 = elementOption0.querySelector("img")! as HTMLImageElement;
	let elementImage1 = elementOption1.querySelector("img")! as HTMLImageElement;

	elementImage0.src = "";
	elementImage1.src = "";

	const loadImage = (source: string): Promise<HTMLImageElement> => {
		return new Promise<HTMLImageElement>((resolve, reject) => {
			let image = new Image();
			image.src = source;

			image.onload = () => resolve(image);
			image.onerror = () => reject(new Error("Could not load the image. Error"));
		});
	};

	// Load the new images
	const imageSource0 = `${datasetUrl}/${images[answerIndex]}`;
	const imageSource1 = `${datasetUrl}/${images[answerIndex + 1]}`;
	Promise.all([loadImage(imageSource0), loadImage(imageSource1)])
		.then(([_image0, _image1]) => {
			elementImage0.src = imageSource0;
			elementImage1.src = imageSource1;

			elementQuestion.innerHTML = generatedQuestion!.text;

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
	elementTimeBarStatus?.parentElement?.remove()

	const postRequest = new Request("/post-survey", {
		method: "POST",
		body: JSON.stringify(answers),
	});

	fetch(postRequest).then(async (response) => {
		if (response.status == 200) {
			console.log("Results posted.");
		} else {
			const responseText = await response.json();
			console.error("Error posting the results.. Got status: ", response.status);
			console.error(responseText)
		}
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

		// Add current answer
		answers.push([
			new Answer(answerIndex, images[answerIndex], clicked0, "todo", generatedQuestion!.variables, timeBarEnabled),
			new Answer(answerIndex, images[answerIndex + 1], !clicked0, "todo", generatedQuestion!.variables, timeBarEnabled)]
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
