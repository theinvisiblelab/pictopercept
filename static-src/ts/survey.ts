// This variables are passed from the HTML <script> tag, as they
// have to come from Flask
declare var surveyQuestionRaw: any;
declare var images: Array<string>;
declare var timeBarEnabled: boolean;
declare var datasetUrl: string;
declare var answerDuration: number;
declare var surveyDuration: number;

interface AnswerImage {
	image: string;
	chosen: boolean;
}

interface Answer {
	index: number;
	variables: { [key: string]: string };
	images: [AnswerImage, AnswerImage];
	timeBarEnabled: boolean;
};

interface SurveyDomElements {
	question: HTMLElement;
	options: HTMLElement;
	surveyEnd: HTMLElement;

	option0: HTMLElement;
	option1: HTMLElement;

	optionImage0: HTMLImageElement;
	optionImage1: HTMLImageElement;
}

//
// Class that holds the Survey data, HTML elements
// and timers.
//
// It handles the option/answer clicks, posting the data,
// image loading, etc.
//
class Survey {
	private readonly domElements: SurveyDomElements = this.initializeDom();
	private readonly surveyTimer: Timer = new Timer();

	timeBar: TimeBar | null = null;
	private barAnimationFrame: number | null = null

	private readonly questionGenerator: QuestionGenerator;
	private currentQuestion: GeneratedQuestion | null = null;

	private answerIndex: number = -2;
	// private readonly answers: Array<[Answer, Answer]> = Array<[Answer, Answer]>();
	private readonly answers: Array<Answer> = Array<Answer>();

	constructor() {
		this.initializeListeners();

		if (timeBarEnabled)
			this.timeBar = new TimeBar(answerDuration);

		this.questionGenerator = new QuestionGenerator(surveyQuestionRaw["format"], surveyQuestionRaw["variables"]);

		if (this.timeBar !== null) {
			const updateTimeBar = () => {
				if (this.timeBar !== null) {
					this.timeBar!.update();
					this.barAnimationFrame = requestAnimationFrame(updateTimeBar)
				}
			}

			this.barAnimationFrame = requestAnimationFrame(updateTimeBar)
		}

		this.advanceSurvey();
	}

	// Adds each HTML references to the class, to make it easier to access them.
	initializeDom(): SurveyDomElements {
		return {
			question: document.getElementById("question")!,
			options: document.getElementById("options")!,
			surveyEnd: document.getElementById("survey-end")!,
			option0: document.getElementById("option0")!,
			option1: document.getElementById("option1")!,
			optionImage0: document.querySelector("#option0 > img")! as HTMLImageElement,
			optionImage1: document.querySelector("#option1 > img")! as HTMLImageElement,
		};
	}

	// Initializes both listeners to each answer button.
	initializeListeners() {
		this.domElements.option0.addEventListener("click", () => {
			this.handleOptionClick(0);

		});
		this.domElements.option1.addEventListener("click", () => {
			this.handleOptionClick(1);

		});
	}

	// Survey is ended if 60 seconds passed, or used completed
	// all the questions.
	shouldTheSurveyEnd(): boolean {
		return ((surveyDuration > -1 && this.surveyTimer.getSecondsPassed() >= surveyDuration)
			|| this.answerIndex >= images.length);
	}

	// Action that gets done when one of the buttons of answer is pressed.
	handleOptionClick(option: number) {
		this.domElements.options.classList.add("loading");

		// Add current answer
		// TODO: Revise this, as we might be able drop most of the information
		this.answers.push({
			index: this.answerIndex / 2,
			variables: this.currentQuestion!.variables,
			timeBarEnabled: timeBarEnabled,
			images: [
				{
					image: images[this.answerIndex],
					chosen: option === 0,
				},
				{
					image: images[this.answerIndex + 1],
					chosen: option == 1
				}
			]
		})

		if (this.timeBar) {
			this.timeBar.reset();
		}

		this.shouldTheSurveyEnd() ? this.endSurvey() : this.advanceSurvey();
	}

	advanceSurvey() {
		// Advance indices
		this.currentQuestion = this.questionGenerator.generateQuestion();
		this.answerIndex += 2;

		// Reset image src's to prevent later flickers
		this.domElements.optionImage0.src = "";
		this.domElements.optionImage1.src = "";

		const loadImage = (source: string): Promise<HTMLImageElement> => {
			return new Promise<HTMLImageElement>((resolve, reject) => {
				let image = new Image();
				image.src = source;

				image.onload = () => resolve(image);
				image.onerror = () => reject(new Error("Could not load the image. Error"));
			});
		};
		// Create new image source urls
		const imageSource0 = `${datasetUrl}/${images[this.answerIndex]}`;
		const imageSource1 = `${datasetUrl}/${images[this.answerIndex + 1]}`;

		// Load the new images via promises.
		// Once both images are loaded, their URL source
		// gets put into both images, as they are already
		// downloaded/cached in the user's browser, they
		// get load immediately.
		Promise.all([loadImage(imageSource0), loadImage(imageSource1)])
			.then(([_image0, _image1]) => {
				this.domElements.optionImage0.src = imageSource0;
				this.domElements.optionImage1.src = imageSource1;

				this.domElements.question.innerHTML = this.currentQuestion!.text;

				this.timeBar?.start();
				if (!this.surveyTimer.isInitialized()) this.surveyTimer.start();

				this.domElements.options.classList.remove("loading")
			})
			.catch((error) => {
				console.error(error)

				let actions: ActionButton[] = [
					new ActionButton("Exit survey", () => { window.location.href = "/" }),
					new ActionButton("Submit", () => { this.endSurvey() }),
				];

				new Modal(
					"Image loading error",
					"We could not load the images of the current question. What do you wish to do now?",
					actions
				);
			})
	}

	// Sends all the survey answer data to the server.
	endSurvey() {
		// Remove error modal if any
		document.querySelector(".modal-outer")?.remove();

		this.domElements.question.innerText = "Thank you!";
		this.domElements.question.style.paddingBottom = "10px";
		//this.domElements.options.style.visibility = "hidden"
		this.domElements.options.remove()

		this.domElements.surveyEnd.classList.add("visible");
		this.domElements.surveyEnd.style.display = "";
		this.domElements.surveyEnd.classList.add("loading");

		if (this.timeBar) {
			this.timeBar.destroy();
			this.timeBar = null;
			cancelAnimationFrame(this.barAnimationFrame!)
		}

		const csrftoken = (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement).value;
		const postRequest = new Request("/survey/end", {
			method: "POST",
			body: JSON.stringify(this.answers),

			headers: {
				"content-type": "application/json",
				"X-CSRFToken": csrftoken
			},
			mode: "same-origin" // Do not send CSRF token to another domain.
		});

		const showErrorModal = (errorText: string) => {
			let actions: ActionButton[] = [
				new ActionButton("Exit survey", () => { window.location.href = "/" }),
			];

			new Modal(
				"Error saving results",
				`There was an unexpected error while saving your survey results: <br><br><b style='font-size:13px'>\"${errorText}\"</b><br><br>Please try taking the survey again in a few moments.`,
				actions
			);
		}

		fetch(postRequest).then(async (response) => {
			if (response.status == 200) {
				this.domElements.surveyEnd.classList.remove("loading");
				this.domElements.surveyEnd.classList.add("done");
				window.onbeforeunload = () => { }
			} else {
				const responseText = await response.text();
				showErrorModal(responseText);
			}
		}).catch((error) => {
			// Handle fetch error
			showErrorModal(error)
		});
	}
}

const surveyInstance = new Survey();

window.onbeforeunload = () => {
	return "The survey has not finished, and all the data will be lost. Are you sure you want to leave?";
}
