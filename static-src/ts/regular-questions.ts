document.querySelectorAll("input[type='checkbox'], input[type='radio']").forEach((element, _) => {
	if (element.id.endsWith("-other")) {
		element.addEventListener("change", (e) => {
			const otherInput = element.parentElement!.querySelector("input[type='text']");
			if (otherInput !== null) {
				if ((element as HTMLInputElement).checked) {
					(otherInput as HTMLElement).style.display = "";
				} else {
					(otherInput as HTMLElement).style.display = "none";
				}
			}
		})
	}
})

const form = document.querySelector("form.regular-question-form")!;
form.addEventListener("submit", (e) => {
	e.preventDefault();
	const answers: Array<{
		[key: string]: Array<number> | string | number | null
	}> = Array();

	let hasErrors = false;
	form.querySelectorAll(".error, .error2")?.forEach((element) => element.remove())

	form.querySelectorAll(".question-group").forEach((question, questionIndex) => {
		const questionType = question.getAttribute("question-type")!;

		switch (questionType) {
			case "MultipleChoice": {
				const checkedAnswers: Array<number> = new Array();
				let otherAnswer: string | null = null;
				question.querySelectorAll(".content > ul > li > input[type='checkbox']:checked").forEach((checkbox, i) => {
					if (checkbox.id.endsWith("-other")) {
						otherAnswer = (question.querySelector(".content > ul > li > input[type='text']") as HTMLInputElement).value

						if (otherAnswer.trim().length === 0) {
							hasErrors = true;
							addError(questionIndex, "You must fill the \"other\" text field if you selected it.")
							console.warn("An \"other\" answer is empty.")
						}
					} else {
						checkedAnswers.push(i)
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
				let checkedAnswer: number | null = null;
				let otherAnswer: string | null = null;
				const checkedRadio = question.querySelector(".content > ul > li > input[type='radio']:checked");
				if (checkedRadio !== null) {
					if (checkedRadio.id.endsWith("-other")) {
						otherAnswer = (question.querySelector(".content > ul > li > input[type='text']") as HTMLInputElement).value

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
				const rowAnswers = new Array<number>();
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
				let checkedIndex: number | null = null;

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
				const answerText = (question.querySelector(".content input[type='text']") as HTMLInputElement).value

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
		console.error("[TODO] Post the survey data.")
	}
})

const addError = (questionIndex: number, text: string = "There is an error in this answer.") => {
	const questionElement = form.querySelector(`#question-${questionIndex}`);
	if (questionElement === null)
		return;

	const existingErrorMessage = questionElement.querySelector(".error");
	if (existingErrorMessage === null) {
		const errorMessage = document.createElement("div");
		errorMessage.classList.add("error");
		errorMessage.innerText = text;
		questionElement.insertBefore(errorMessage, questionElement.querySelector(".content")!);
	} else {
		(existingErrorMessage as HTMLElement).innerText = text;
	}

	// Also add a message at the "Continue" button.
	if (form.querySelector(".error2") === null) {
		const continueError = document.createElement("div");
		continueError.classList.add("error2");
		continueError.innerText = "There is one or more errors. Please check your answers carefully.";
		form.insertBefore(continueError, form.querySelector("button")!);
	}
}

const removeError = (questionIndex: number) => {
	form.querySelector(`#question-${questionIndex}`)?.querySelector(".error")?.remove()
}
