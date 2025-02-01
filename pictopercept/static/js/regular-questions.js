/**
 * The survey identifier.
 * @type {string}
 */
var surveyIdentifier = window.surveyIdentifier;

document.querySelectorAll("input[type='checkbox'], input[type='radio']").forEach((element, _) => {
	if (element.id.endsWith("-other")) {
		element.addEventListener("change", (e) => {
			const otherInput = element.parentElement?.querySelector("input[type='text']");
			if (otherInput !== null) {
				if ((/** @type {HTMLInputElement} */(element)).checked) {
					(/** @type {HTMLElement} */(otherInput)).style.display = ""
				} else {
					(/** @type {HTMLElement} */(otherInput)).style.display = "none"
				}
			}
		})
	}
})

const form = document.querySelector("form.regular-question-form");
if (form === null)
	throw new Error("This should not happen.")
form.addEventListener("submit", (e) => {
	e.preventDefault();

	/**
	 * A list of answer map, whose value will be one of the four.
	 * @type {{[key: string] : (number[] | string | number | null)}[]}
	 */
	const answers = [];

	let hasErrors = false;
	form.querySelectorAll(".error, .error2")?.forEach((element) => element.remove())

	form.querySelectorAll(".question-group").forEach((question, questionIndex) => {
		const questionType = /** @type {string} */ question.getAttribute("question-type");

		switch (questionType) {
			case "MultipleChoice": {
				const checkedAnswers = [];
				let otherAnswer = null;
				question.querySelectorAll(".content > ul > li > input[type='checkbox']:checked").forEach((checkbox) => {
					if (checkbox.id.endsWith("-other")) {
						otherAnswer = (/** @type {HTMLInputElement}*/ (question.querySelector(".content > ul > li > input[type='text']"))).value

						if (otherAnswer.trim().length === 0) {
							hasErrors = true;
							addError(questionIndex, "You must fill the \"other\" text field if you selected it.")
							console.warn("An \"other\" answer is empty.")
						}
					} else {
						const checkedIndex = Number(checkbox.id.replace(`question-${questionIndex}-`, ""))
						checkedAnswers.push(checkedIndex)
					}
				})

				if (checkedAnswers.length === 0 && otherAnswer === null) {
					hasErrors = true;
					addError(questionIndex, "You must check at least one option.")
					console.warn("Multiple choice has no answer at all.")
				}

				answers.push({
					"checkedAnswers": checkedAnswers,
					"otherAnswer": otherAnswer,
				})

				break;
			}
			case "SingleChoice": {
				let checkedAnswer = null;
				let otherAnswer = null;
				const checkedRadio = question.querySelector(".content > ul > li > input[type='radio']:checked");
				if (checkedRadio !== null) {
					if (checkedRadio.id.endsWith("-other")) {
						otherAnswer = (/** @type {HTMLInputElement} */(question.querySelector(".content > ul > li > input[type='text']"))).value

						if (otherAnswer.trim().length === 0) {
							hasErrors = true;
							addError(questionIndex, "You must fill the \"other\" text field if you selected it.")
							console.warn("An \"other\" answer is empty.")
						}
					} else {
						checkedAnswer = Number(checkedRadio.id.replace(`question-${questionIndex}-`, ""))
					}
				}

				if (checkedAnswer === null && otherAnswer === null) {
					hasErrors = true;
					addError(questionIndex, "You must check one option.")
					console.warn("Single choice has no answer at all.")
				}

				answers.push({
					"checkedAnswer": checkedAnswer,
					"otherAnswer": otherAnswer,
				})

				break;
			}
			case "Matrix": {
				const rowAnswers = [];
				let rowCount = question.querySelectorAll(".content tbody tr").length;

				question.querySelectorAll(".content tbody tr").forEach((row, rowIndex) => {
					const checkedRadio = row.querySelector("input[type='radio']:checked")
					if (checkedRadio !== null) {
						rowAnswers.push(Number(checkedRadio.id.replace(`question-${questionIndex}-${rowIndex}-`, "")))
					} else {
						hasErrors = true;
						addError(questionIndex, "You must answer all rows.")
						console.warn("There is a row of a matrix which has no answer at all.")
					}
				})

				if (rowAnswers.length !== rowCount) {
					console.warn("Matrix has missing answers.")
				}

				answers.push({
					"checkedAnswers": rowAnswers,
				})

				break;
			}
			case "AgreementScale": {
				let checkedIndex = null;

				const checkedOption = question.querySelector(".content input[type='radio']:checked")
				if (checkedOption !== null) {
					checkedIndex = Number(checkedOption.id.replace(`question-${questionIndex}-`, ""))
				}

				if (checkedIndex === null) {
					hasErrors = true;
					addError(questionIndex, "You must choose one option.")
					console.warn("Agreement scale has no answer at all.")
				}

				answers.push({
					"checkedAnswer": checkedIndex,
				})

				break;
			}
			case "OpenShort":
				const answerText = (/** @type {HTMLInputElement} */(question.querySelector(".content input[type='text']"))).value

				if (answerText.trim().length === 0) {
					hasErrors = true;
					addError(questionIndex, "You must answer this question.")
					console.warn("A free open answer is empty.")
				}

				answers.push({
					"answerText": answerText,
				})

				break;
			default:
				console.log(`Unknown question type \"${questionType}\", ignoring...`)
				break;
		}
	});

	if (!hasErrors) {
		fetch(`/survey/${surveyIdentifier}`, {
			method: "POST",
			body: JSON.stringify(answers),
			headers: {
				"Content-Type": "application/json",
			}
		}).then(async (res) => {
			const text = await res.text()
			if (res.ok) {
				window.location.reload()
			} else {
				const errors = JSON.parse(text);
				Object.entries(errors).forEach(([key, val]) => {
					addError(Number(key), val)
				});
			}
		}).catch((reason) => {
			console.error(reason)
		})
	}
})

/**
 * Adds an error to a question.
 * @param {number} questionIndex - The index of the question to add the error to.
 * @param {string} text - The error content. Optional.
 */
const addError = (questionIndex, text = "There is an error in this answer.") => {
	const questionElement = form.querySelector(`#question-${questionIndex}`);
	if (questionElement === null)
		return;

	const existingErrorMessage = /** @type {HTMLElement} */ (questionElement.querySelector(".error"));
	if (existingErrorMessage === null) {
		const errorMessage = document.createElement("div");
		errorMessage.classList.add("error");
		errorMessage.innerText = text;
		questionElement.insertBefore(errorMessage, questionElement.querySelector(".content"));
	} else {
		existingErrorMessage.innerText = text;
	}

	// Also add a message at the "Continue" button.
	if (form.querySelector(".error2") === null) {
		const continueError = document.createElement("div");
		continueError.classList.add("error2");
		continueError.innerText = "There are one or more errors. Please check your answers carefully.";
		form.insertBefore(continueError, form.querySelector("button"));
	}
}

/**
 * Removes the error of a question, if exists.
 * @param {number} questionIndex - The index of the question to remove the error from.
 */
const removeError = (questionIndex) => {
	form.querySelector(`#question-${questionIndex}`)?.querySelector(".error")?.remove()
}
