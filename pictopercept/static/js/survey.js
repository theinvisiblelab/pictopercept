// This variables are passed from the HTML <script> tag, as they
// have to come from Flask

/**
 * @type {ImageSurvey}
 */
var imageSurvey = window.imageSurvey;

/**
 * @type {string}
 */
var surveyPostUrl = window.surveyPostUrl;

/**
 * @typedef {Object} PairQuestion
 * @property {[string, string]} images - Both images of the question.
 * @property {string} text - The text of the question itself.
 */

/**
 * @typedef {Object} ImageSurvey
 * @property {PairQuestion[]} pair_questions - A list of questions of the survey.
 * @property {number | null} time_bar_duration - The duration of the pair question. If null, then it is disabled.
 * @property {number | null} duration_seconds - The duration of the survey. If null, then is unlimited.
 * @property {string} image_url_prefix - The URL prefix to put before each image of the survey.
 * @property {string} accent_color - An accent color to represent the survey (e.g. the buttons).
 */


/**
 * @typedef {Object} AnswerImage
 * @property {string} image - The image of the current answer.
 * @property {boolean} chosen - True if this is the clicked one. False otherwise.
 */

// TODO: Include the time spent answering each pair.
/**
 * @typedef {Object} Answer
 * @property {[AnswerImage, AnswerImage]} images - The pairs of selected answers.
 * @property {number} seconds_taken - The amount of seconds (as float) that the user took to answer.
 */

/**
 * @typedef {Object} SurveyDomElements
 * @property {HTMLElement} question - The question HTML field to write the text to.
 * @property {HTMLElement} options - The parent element of the image/options.
 *
 * @property {HTMLElement} option0 - The parent of the image/option on the left.
 * @property {HTMLElement} option1 - The parent of the image/option on the right.
 *
 * @property {HTMLImageElement} optionImage0 - The image/option on the left.
 * @property {HTMLImageElement} optionImage1 - The image/option on the right.
 */

/**
 * Survey holds the Survey data, DOM elements and timers.
 * It handles the image/option clicks, image loading, data posting, etc.
 */
class Survey {
	/**
	 * The object holding the DOM references.
	 * @type {SurveyDomElements}
	 * @readonly
	*/
	#domElements = this.initializeDom();

	/**
	 * The timer of the survey (not of each pair).
	 * @type {Timer}
	 * @readonly
	*/
	#surveyTimer = new Timer();

	/**
	 * The timer of the current question.
	 * @type {Timer}
	 * @readonly
	*/
	#questionTimer = new Timer();

	/**
	 * The TimeBar that will be used on each pair. If null, then the current survey is not using a TimeBar.
	 * @type {TimeBar | null}
	*/
	#timeBar = null;

	/**
	 * The frame of the animation of HTML. 
	 * @type {number | null}
	*/
	#barAnimationFrame = null;

	/**
	 * The text of the current question.
	 * @type {string | null}
	*/
	#currentQuestion = null;

	/**
	 * The index of the current pair.
	 * @type {number}
	*/
	#answerIndex = 0;

	/**
	 * The answers made by the user.
	 * @type {Answer[]}
	 * @readonly
	*/
	#answers = [];

	constructor() {
		this.initializeListeners();

		if (imageSurvey.time_bar_duration !== null)
			this.#timeBar = new TimeBar(imageSurvey.time_bar_duration);

		if (this.#timeBar !== null) {
			const updateTimeBar = () => {
				if (this.#timeBar !== null) {
					this.#timeBar.update();
					this.#barAnimationFrame = requestAnimationFrame(updateTimeBar)
				}
			}

			this.#barAnimationFrame = requestAnimationFrame(updateTimeBar)
		}

		this.advanceSurvey();
	}

	// Adds each HTML references to the class, to make it easier to access them.
	/**
	 * Initializes the dom, making references to each element needed by the Survey.
	 * @returns {SurveyDomElements} - The object holding the DOM references.
	 */
	initializeDom() {
		const question = document.getElementById("question");
		const options = document.getElementById("options");
		const option0 = document.getElementById("option0");
		const option1 = document.getElementById("option1");
		const optionImage0 = document.querySelector("#option0 > img");
		const optionImage1 = document.querySelector("#option1 > img");

		if (!question || !options || !option0 || !option1 || !optionImage0 || !optionImage1) {
			throw new Error("One or more DOM elements of the Survey are missing. Were they deleted?");
		} else if (!(optionImage0 instanceof HTMLImageElement) || !(optionImage1 instanceof HTMLImageElement)) {
			throw new Error("This should not happen, but needed to assert types.");
		}

		return {
			question,
			options,
			option0,
			option1,
			optionImage0,
			optionImage1,
		};
	}

	/**
	 * Initializes two listeners on "click" event, to both image options.
	 */
	initializeListeners() {
		this.#domElements.option0.addEventListener("click", () => {
			this.handleOptionClick(0);
		});
		this.#domElements.option1.addEventListener("click", () => {
			this.handleOptionClick(1);
		});
	}

	/**
	 * Checks if the survey should end.
	 * @returns {boolean} - True if the question list has ended or if the time has exceeded. False otherwise.
	 */
	shouldTheSurveyEnd() {
		return ((imageSurvey.duration_seconds !== null && this.#surveyTimer.getSecondsPassed() >= imageSurvey.duration_seconds)
			|| this.#answerIndex >= imageSurvey.pair_questions.length);
	}

	/**
	 * The function that will get called when the user presses an option/image of the pair.
	 * Will save the answer, reset the timebar and advance or end the survey.
	 * @param {number} option - The option clicked. 0 for the image on the left, 1 for the image on the right.
	 */
	handleOptionClick(option) {
		this.#domElements.options.classList.add("loading");

		this.#answers.push({
			images: [
				{
					image: imageSurvey.pair_questions[this.#answerIndex].images[0],
					chosen: option === 0,
				},
				{
					image: imageSurvey.pair_questions[this.#answerIndex].images[1],
					chosen: option == 1
				}
			],
			seconds_taken: this.#questionTimer.getSecondsPassed(),
		})

		if (this.#timeBar) {
			this.#timeBar.reset();
		}

		this.#answerIndex++;
		this.shouldTheSurveyEnd() ? this.endSurvey() : this.advanceSurvey();
	}

	/**
	 * Advances the survey, obtaining the text question and loading the images.
	 */
	advanceSurvey() {
		this.#currentQuestion = imageSurvey.pair_questions[this.#answerIndex].text;

		// Reset image src's to prevent later flickers
		this.#domElements.optionImage0.src = "";
		this.#domElements.optionImage1.src = "";

		/**
		 * Helper function to load both images, via Promises.
		 * @param {string} source
		 * @returns {Promise<HTMLImageElement>}
		 */
		const loadImage = (source) => {
			return new Promise(async (resolve, reject) => {
				let image = new Image();
				image.src = source;

				image.onload = () => resolve(image);
				image.onerror = () => reject(new Error("Could not load the image. Error"));
			});
		};

		// Create new image source urls
		// const imageSource0 = `${imageSurvey.image_url_prefix}/${imageSurvey.pair_questions[this.#answerIndex].images[0]}`;
		// const imageSource1 = `${imageSurvey.image_url_prefix}/${imageSurvey.pair_questions[this.#answerIndex].images[1]}`;

		const imageSource0 = `/img/${this.#answerIndex}/l`;
		const imageSource1 = `/img/${this.#answerIndex}/r`;

		// Load the new images via promises.
		// Once both images are loaded, their URL source
		// gets put into both images, as they are already
		// downloaded/cached in the user's browser, they
		// get load immediately.
		Promise.all([loadImage(imageSource0), loadImage(imageSource1)])
			.then(([_image0, _image1]) => {
				this.#domElements.optionImage0.src = imageSource0;
				this.#domElements.optionImage1.src = imageSource1;

				if (this.#currentQuestion !== null)
					this.#domElements.question.innerHTML = this.#currentQuestion;

				this.#questionTimer.start();
				this.#timeBar?.start();
				if (!this.#surveyTimer.isInitialized()) this.#surveyTimer.start();

				this.#domElements.options.classList.remove("loading")
			})
			.catch((error) => {
				console.error(error)

				const actions = [
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

	/**
	 * Ends the survey, posting all the answers to the backend and handling/showing errors to the user.
	 */
	endSurvey() {
		// Remove error modal if any
		document.querySelector(".modal-outer")?.remove();

		this.#domElements.question.innerText = "Loading...";
		this.#domElements.question.style.paddingBottom = "0";
		this.#domElements.question.style.opacity = "0.3";
		this.#domElements.options.remove()

		if (this.#timeBar) {
			this.#timeBar.destroy();
			this.#timeBar = null;
			if (this.#barAnimationFrame === null)
				throw new Error("If there is a TimeBar, there will be a BarAnimationFrame, so this should not happen.");
			cancelAnimationFrame(this.#barAnimationFrame)
		}

		const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
		let csrfToken = ""
		if (csrfTokenElement instanceof HTMLInputElement)
			csrfToken = csrfTokenElement.value;

		const postRequest = new Request(surveyPostUrl, {
			method: "POST",
			body: JSON.stringify(this.#answers),

			headers: {
				"content-type": "application/json",
				"X-CSRFToken": csrfToken
			},
			mode: "same-origin"
		});

		/**
		 * Helper function to show the modal and an error.
		 * @param {string} errorText - The text to show in the modal.
		 */
		const showErrorModal = (errorText) => {
			let actions = [
				new ActionButton("Exit survey", () => { window.location.href = "/" }),
			];

			new Modal(
				"Error saving results",
				`There was an unexpected error while saving your survey results: <br><br><b style='font-size:13px'>\"${errorText}\"</b><br><br>Please try taking the survey again in a few moments.`,
				actions
			);
		}

		fetch(postRequest).then(async (response) => {
			const text = await response.text()
			if (response.status == 200) {
				const nextStepUrl = JSON.parse(text)["next_step"]
				window.onbeforeunload = () => { }
				window.location.href = nextStepUrl
			} else {
				showErrorModal(text);
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
